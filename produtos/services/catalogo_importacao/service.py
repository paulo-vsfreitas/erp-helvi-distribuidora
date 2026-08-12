from collections import OrderedDict
from decimal import Decimal
from pathlib import Path

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
    VariacaoImportacaoCatalogo,
)
from produtos.services.importacao import importar_produtos
from .analisador import (
    arquivo_local,
    completar_variacoes_visuais,
    detectar_quantidade_variacoes_imagem,
    detectar_variacoes_visuais_imagem,
    extrair_texto_imagem,
    extrair_texto_pdf,
    gerar_preview_pdf,
    sugerir_dados,
)


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


def _analisar_arquivo(arquivo):
    sufixo = Path(arquivo.nome_original).suffix.lower()
    variacoes_visuais = []
    with arquivo_local(arquivo.arquivo, sufixo=sufixo) as caminho:
        if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.PDF:
            texto, aviso = extrair_texto_pdf(caminho)
            gerar_preview_pdf(arquivo, caminho)
            if arquivo.preview:
                with arquivo_local(arquivo.preview, sufixo=".jpg") as preview:
                    variacoes_visuais = detectar_variacoes_visuais_imagem(preview)
                    if not texto.strip():
                        texto_ocr, aviso_ocr = extrair_texto_imagem(preview)
                        if texto_ocr:
                            texto = texto_ocr
                            aviso = ""
                        elif aviso_ocr:
                            aviso = "; ".join(filter(None, [aviso, aviso_ocr]))
        else:
            texto, aviso = extrair_texto_imagem(caminho)
            variacoes_visuais = detectar_variacoes_visuais_imagem(caminho)

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


def analisar_lote(lote):
    if lote.status == ImportacaoCatalogo.Status.IMPORTADO:
        raise ValidationError("Este catálogo já foi importado.")

    grupos = OrderedDict()

    for arquivo in lote.arquivos.all().order_by("id"):
        sugestao = _analisar_arquivo(arquivo)
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


def _copiar_imagens(item, produto):
    principal_definida = produto.imagens.filter(principal=True).exists()
    arquivos = list(item.arquivos.all())
    if item.arquivo_principal_id:
        arquivos.sort(key=lambda arquivo: arquivo.pk != item.arquivo_principal_id)
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
