from collections import OrderedDict
from contextlib import nullcontext
from decimal import Decimal
from io import BytesIO
import logging
from pathlib import Path

from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from produtos.models import (
    ArquivoImportacaoCatalogo,
    ImagemProduto,
    ImportacaoCatalogo,
    ItemImportacaoCatalogo,
    Produto,
    RecorteImportacaoCatalogo,
    VariacaoImportacaoCatalogo,
)
from produtos.services.importacao import importar_produtos
from .analisador import (
    arquivo_local,
    completar_variacoes_visuais,
    detectar_layout_visual_imagem,
    extrair_texto_imagem,
    extrair_texto_pdf,
    gerar_preview_pdf,
    sugerir_dados,
)


logger = logging.getLogger(__name__)


def _caixa_pixels(caixa, largura, altura):
    x1 = max(0, min(largura - 1, round(largura * caixa["x1"] / 100)))
    y1 = max(0, min(altura - 1, round(altura * caixa["y1"] / 100)))
    x2 = max(x1 + 1, min(largura, round(largura * caixa["x2"] / 100)))
    y2 = max(y1 + 1, min(altura, round(altura * caixa["y2"] / 100)))
    return x1, y1, x2, y2


def _jpeg_visual(imagem):
    visual = imagem.copy()
    visual.thumbnail((1200, 1200), Image.Resampling.LANCZOS, reducing_gap=3.0)
    buffer = BytesIO()
    visual.save(
        buffer,
        format="JPEG",
        quality=82,
        optimize=False,
        progressive=True,
    )
    return buffer.getvalue()


def _excluir_arquivos_storage(storage, nomes):
    for nome in nomes:
        if not nome:
            continue
        try:
            storage.delete(nome)
        except (OSError, ValueError) as erro:
            # A troca dos recortes já foi concluída no banco. Uma falha pontual
            # de limpeza não pode invalidar o conjunto novo e consistente.
            logger.warning("Falha ao remover recorte antigo %s: %s", nome, erro)
            continue


def processar_recursos_visuais(arquivo, *, caminho=None):
    """Gera e troca atomicamente Hero/C1..Cn de um arquivo de staging."""
    if caminho is None:
        campo = (
            arquivo.arquivo
            if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.IMAGEM
            else arquivo.preview
        )
        if not campo:
            return []
        sufixo = (
            Path(arquivo.nome_original).suffix.lower()
            if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.IMAGEM
            else ".jpg"
        )
        with arquivo_local(campo, sufixo=sufixo) as caminho_local:
            return processar_recursos_visuais(arquivo, caminho=caminho_local)

    layout = detectar_layout_visual_imagem(caminho)
    preparados = []
    with Image.open(caminho) as origem:
        imagem = origem.convert("RGB")
        aspecto_imagem = imagem.width / imagem.height
        conteudo_visual = _jpeg_visual(imagem)
        if layout.get("hero"):
            preparados.append({
                "tipo": RecorteImportacaoCatalogo.Tipo.HERO,
                "indice": 0,
                "nome_cor": "",
                "cor_hex": "#6c757d",
                "texto_hex": "#ffffff",
                "layout": {
                    **layout["hero"],
                    "aspecto_imagem": aspecto_imagem,
                },
            })
        for visual in layout.get("variacoes", []):
            caixa = visual.get("caixa")
            if not caixa:
                continue
            preparados.append({
                "tipo": RecorteImportacaoCatalogo.Tipo.VARIACAO,
                "indice": visual["indice"],
                "nome_cor": visual.get("nome", ""),
                "cor_hex": visual.get("cor_hex", "#6c757d"),
                "texto_hex": visual.get("texto_hex", "#ffffff"),
                "layout": {
                    "caixa": caixa,
                    "marcadores": visual.get("marcadores", []),
                    "aspecto_imagem": aspecto_imagem,
                },
            })

    novos_nomes = []
    storage = RecorteImportacaoCatalogo._meta.get_field("imagem").storage
    try:
        with transaction.atomic():
            anteriores = list(
                RecorteImportacaoCatalogo.objects.select_for_update()
                .filter(arquivo=arquivo)
            )
            nomes_anteriores = list({
                recorte.imagem.name for recorte in anteriores if recorte.imagem.name
            })
            RecorteImportacaoCatalogo.objects.filter(arquivo=arquivo).delete()

            novos = []
            nome_visual = ""
            for indice_preparado, dados in enumerate(preparados):
                recorte = RecorteImportacaoCatalogo(arquivo=arquivo, **dados)
                if indice_preparado == 0:
                    nome = f"arquivo_{arquivo.pk}_visual.jpg"
                    recorte.imagem.save(
                        nome, ContentFile(conteudo_visual), save=False
                    )
                    nome_visual = recorte.imagem.name
                    novos_nomes.append(nome_visual)
                else:
                    recorte.imagem.name = nome_visual
                recorte.save()
                novos.append(recorte)

            transaction.on_commit(
                lambda: _excluir_arquivos_storage(storage, nomes_anteriores)
            )
        return novos
    except Exception:
        _excluir_arquivos_storage(storage, novos_nomes)
        raise


def criar_lote(*, dados, arquivos, usuario):
    lote = ImportacaoCatalogo.objects.create(
        fornecedor=dados["fornecedor"],
        tipo_armacao=dados["tipo_armacao"],
        preco_custo_padrao=dados["preco_custo"],
        preco_venda_padrao=dados["preco_venda"],
        estoque_inicial_padrao=dados["estoque_inicial"],
        estoque_minimo_padrao=dados["estoque_minimo"],
        usuario=usuario,
    )

    for arquivo in arquivos:
        extensao = Path(arquivo.name).suffix.lower()
        tipo = (
            ArquivoImportacaoCatalogo.Tipo.PDF
            if extensao == ".pdf"
            else ArquivoImportacaoCatalogo.Tipo.IMAGEM
        )
        ArquivoImportacaoCatalogo.objects.create(
            lote=lote,
            arquivo=arquivo,
            nome_original=arquivo.name,
            tipo=tipo,
        )
    return lote


def _analisar_arquivo(arquivo, *, caminho_local=None):
    sufixo = Path(arquivo.nome_original).suffix.lower()
    variacoes_visuais = []
    contexto_arquivo = (
        nullcontext(str(caminho_local))
        if caminho_local
        else arquivo_local(arquivo.arquivo, sufixo=sufixo)
    )
    with contexto_arquivo as caminho:
        if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.PDF:
            texto, aviso = extrair_texto_pdf(caminho)
            gerar_preview_pdf(arquivo, caminho)
            if arquivo.preview:
                with arquivo_local(arquivo.preview, sufixo=".jpg") as preview:
                    recortes = processar_recursos_visuais(arquivo, caminho=preview)
                    variacoes_visuais = [
                        {
                            "indice": recorte.indice,
                            "nome": recorte.nome_cor,
                            "cor_hex": recorte.cor_hex,
                            "texto_hex": recorte.texto_hex,
                            **recorte.layout,
                        }
                        for recorte in recortes
                        if recorte.tipo == RecorteImportacaoCatalogo.Tipo.VARIACAO
                    ]
                    if not texto.strip():
                        texto_ocr, aviso_ocr = extrair_texto_imagem(preview)
                        if texto_ocr:
                            texto = texto_ocr
                            aviso = ""
                        elif aviso_ocr:
                            aviso = "; ".join(filter(None, [aviso, aviso_ocr]))
        else:
            texto, aviso = extrair_texto_imagem(caminho)
            recortes = processar_recursos_visuais(arquivo, caminho=caminho)
            variacoes_visuais = [
                {
                    "indice": recorte.indice,
                    "nome": recorte.nome_cor,
                    "cor_hex": recorte.cor_hex,
                    "texto_hex": recorte.texto_hex,
                    **recorte.layout,
                }
                for recorte in recortes
                if recorte.tipo == RecorteImportacaoCatalogo.Tipo.VARIACAO
            ]

    arquivo.texto_extraido = texto
    arquivo.aviso_analise = aviso
    arquivo.save(update_fields=["texto_extraido", "aviso_analise"])
    sugestao = sugerir_dados(texto, arquivo.nome_original)
    nomes_visuais = [v.get("nome", "") for v in variacoes_visuais]
    return completar_variacoes_visuais(sugestao, len(variacoes_visuais), nomes_visuais)


def _chave_sugestao(sugestao, arquivo):
    codigo = (sugestao.get("codigo_fornecedor") or "").strip().upper()
    if codigo:
        return ("codigo", codigo)
    modelo = (sugestao.get("modelo") or "").strip().upper()
    if modelo:
        return ("modelo", modelo)
    return ("arquivo", str(arquivo.pk))


def atualizar_duplicidade(item):
    codigo = item.codigo_fornecedor.strip()
    modelo = item.modelo.strip()
    consulta = Produto.objects.filter(fornecedor=item.lote.fornecedor)

    exato = consulta.filter(codigo_fornecedor__iexact=codigo).first() if codigo else None
    if exato:
        item.duplicidade = ItemImportacaoCatalogo.Duplicidade.EXATA
        item.produto_duplicado = exato
    else:
        possivel = consulta.filter(modelo__iexact=modelo).first() if modelo else None
        if possivel:
            item.duplicidade = ItemImportacaoCatalogo.Duplicidade.POSSIVEL
            item.produto_duplicado = possivel
        else:
            item.duplicidade = ItemImportacaoCatalogo.Duplicidade.NENHUMA
            item.produto_duplicado = None
    item.save(update_fields=["duplicidade", "produto_duplicado"])


def analisar_lote(lote, *, caminhos_locais=None):
    if lote.status == ImportacaoCatalogo.Status.IMPORTADO:
        raise ValidationError("Este catálogo já foi importado.")

    grupos = OrderedDict()

    caminhos_locais = caminhos_locais or {}
    for arquivo in lote.arquivos.all().order_by("id"):
        sugestao = _analisar_arquivo(
            arquivo,
            caminho_local=caminhos_locais.get(arquivo.pk),
        )
        chave = _chave_sugestao(sugestao, arquivo)
        grupos.setdefault(chave, {"sugestao": sugestao, "arquivos": [], "variacoes": []})
        grupos[chave]["arquivos"].append(arquivo)
        for variacao in sugestao["variacoes"]:
            assinatura = ((variacao["nome"] or "").upper(), (variacao["codigo"] or "").upper())
            if assinatura not in {((v["nome"] or "").upper(), (v["codigo"] or "").upper()) for v in grupos[chave]["variacoes"]}:
                grupos[chave]["variacoes"].append(variacao)

    with transaction.atomic():
        lote.itens.all().delete()

        for ordem, grupo in enumerate(grupos.values(), start=1):
            sugestao = grupo["sugestao"]
            item = ItemImportacaoCatalogo.objects.create(
                lote=lote,
                codigo_fornecedor=sugestao["codigo_fornecedor"],
                modelo=sugestao["modelo"],
                preco_custo=lote.preco_custo_padrao,
                preco_venda=lote.preco_venda_padrao,
                estoque_minimo=lote.estoque_minimo_padrao,
                estoque_sem_variacao=lote.estoque_inicial_padrao,
                ordem=ordem,
            )
            item.arquivos.set(grupo["arquivos"])
            if grupo["arquivos"]:
                item.arquivo_principal = grupo["arquivos"][0]
                item.save(update_fields=["arquivo_principal"])
            for indice, variacao in enumerate(grupo["variacoes"], start=1):
                VariacaoImportacaoCatalogo.objects.create(
                    item=item,
                    nome=variacao["nome"],
                    codigo=variacao["codigo"],
                    estoque=lote.estoque_inicial_padrao,
                    ordem=indice,
                )
            atualizar_duplicidade(item)
        lote.status = ImportacaoCatalogo.Status.ANALISADO
        lote.save(update_fields=["status", "atualizado_em"])
    return lote


def _linhas_item(item, *, numero_inicial):
    base = {
        "categoria_comercial": "armacao",
        "codigo_fornecedor": item.codigo_fornecedor.strip().upper(),
        "codigo": "",
        "modelo": item.modelo.strip(),
        "marca": "",
        "colecao": "",
        "genero": "",
        "tipo_armacao": item.lote.tipo_armacao.nome,
        "custo": item.preco_custo,
        "venda": item.preco_venda,
        "estoque_minimo": item.estoque_minimo,
        "observacoes": item.observacoes,
        "erros": [],
    }
    variacoes = list(item.variacoes.all())
    if not variacoes:
        return [{
            **base,
            "linha": numero_inicial,
            "sem_variacao": True,
            "cor_variacao": "",
            "codigo_variacao": "",
            "estoque": item.estoque_sem_variacao,
        }]

    linhas = []
    for deslocamento, variacao in enumerate(variacoes):
        if not variacao.codigo.strip():
            raise ValidationError(
                f"{item}: informe o código de todas as variações antes de importar."
            )
        linhas.append({
            **base,
            "linha": numero_inicial + deslocamento,
            "sem_variacao": False,
            "cor_variacao": variacao.nome.strip(),
            "codigo_variacao": variacao.codigo.strip().upper(),
            "estoque": variacao.estoque,
        })
    return linhas


def criar_destaque_produto_importado(item, produto, *, arquivo_principal=None):
    arquivo_principal = arquivo_principal or item.arquivo_principal
    recorte_destaque = None
    if arquivo_principal:
        recorte_destaque = arquivo_principal.recortes.filter(
            tipo=RecorteImportacaoCatalogo.Tipo.HERO,
            indice=0,
        ).first()
        if not recorte_destaque:
            recorte_destaque = arquivo_principal.recortes.filter(
                tipo=RecorteImportacaoCatalogo.Tipo.VARIACAO,
            ).order_by("indice").first()
    if not recorte_destaque or produto.imagens.filter(
        descricao__startswith="Destaque do catálogo"
    ).exists():
        return None
    try:
        recorte_destaque.imagem.open("rb")
        with Image.open(recorte_destaque.imagem) as origem:
            imagem = origem.convert("RGB")
            caixa = recorte_destaque.layout.get(
                "caixa", recorte_destaque.layout
            )
            destaque = imagem.crop(
                _caixa_pixels(caixa, *imagem.size)
            )
            destaque.thumbnail(
                (1200, 720), Image.Resampling.LANCZOS, reducing_gap=3.0
            )
            buffer = BytesIO()
            destaque.save(
                buffer,
                format="JPEG",
                quality=86,
                optimize=False,
                progressive=True,
            )
    finally:
        recorte_destaque.imagem.close()

    produto.imagens.filter(principal=True).update(principal=False)
    imagem_destaque = ImagemProduto(
        produto=produto,
        descricao=f"Destaque do catálogo {arquivo_principal.nome_original}"[:100],
        principal=True,
    )
    imagem_destaque.imagem.save(
        f"destaque_{produto.pk}_{arquivo_principal.pk}.jpg",
        ContentFile(buffer.getvalue()),
        save=True,
    )
    produto.foto = imagem_destaque.imagem
    produto.save(update_fields=["foto"])
    return imagem_destaque


def _copiar_imagens(item, produto):
    principal_definida = produto.imagens.filter(principal=True).exists()
    arquivos = list(item.arquivos.all())
    if item.arquivo_principal_id:
        arquivos.sort(key=lambda arquivo: arquivo.pk != item.arquivo_principal_id)

    arquivo_principal = arquivos[0] if arquivos else None
    if criar_destaque_produto_importado(
        item, produto, arquivo_principal=arquivo_principal
    ):
        principal_definida = True

    for arquivo in arquivos:
        campo = arquivo.arquivo if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.IMAGEM else arquivo.preview
        if not campo:
            continue
        campo.open("rb")
        conteudo = campo.read()
        campo.close()
        nome = Path(campo.name).name
        imagem = ImagemProduto(
            produto=produto,
            descricao=f"Importado de {arquivo.nome_original}"[:100],
            principal=not principal_definida,
        )
        imagem.imagem.save(nome, ContentFile(conteudo), save=True)
        if imagem.principal:
            produto.foto = imagem.imagem
            produto.save(update_fields=["foto"])
            principal_definida = True


@transaction.atomic
def confirmar_importacao(lote, *, usuario):
    lote = ImportacaoCatalogo.objects.select_for_update().get(pk=lote.pk)
    if lote.status == ImportacaoCatalogo.Status.IMPORTADO:
        raise ValidationError("Este catálogo já foi importado.")

    itens = list(lote.itens.filter(incluir=True).prefetch_related("variacoes", "arquivos"))
    if not itens:
        raise ValidationError("Selecione pelo menos um produto para importar.")

    linhas = []
    numero = 2
    for item in itens:
        if not item.codigo_fornecedor.strip() and not item.modelo.strip():
            raise ValidationError("Todo item selecionado precisa ter código do fornecedor ou modelo.")
        if item.preco_custo < 0 or item.preco_venda < 0:
            raise ValidationError(f"{item}: preços não podem ser negativos.")
        if item.preco_venda < item.preco_custo:
            raise ValidationError(f"{item}: o preço de venda não pode ser menor que o custo.")

        atualizar_duplicidade(item)
        if item.duplicidade == ItemImportacaoCatalogo.Duplicidade.EXATA:
            raise ValidationError(
                f"{item}: já existe um produto com este código para o fornecedor selecionado."
            )
        novas = _linhas_item(item, numero_inicial=numero)
        linhas.extend(novas)
        numero += len(novas)

    resultado = importar_produtos(
        linhas=linhas,
        usuario=usuario,
        fornecedor=lote.fornecedor,
        criar_referencias_catalogo=False,
        tipo_armacao_padrao=lote.tipo_armacao,
    )

    for item in itens:
        consulta = Produto.objects.filter(fornecedor=lote.fornecedor)
        if item.codigo_fornecedor.strip():
            produto = consulta.get(codigo_fornecedor__iexact=item.codigo_fornecedor.strip())
        else:
            produto = consulta.filter(modelo__iexact=item.modelo.strip()).order_by("-id").first()
        if produto:
            _copiar_imagens(item, produto)

    lote.status = ImportacaoCatalogo.Status.IMPORTADO
    lote.confirmado_em = timezone.now()
    lote.save(update_fields=["status", "confirmado_em", "atualizado_em"])
    return resultado
