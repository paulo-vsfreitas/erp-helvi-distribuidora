from decimal import Decimal, InvalidOperation
from io import BytesIO
import mimetypes
from pathlib import Path

from PIL import Image

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from produtos.forms_catalogo import ImportacaoCatalogoForm
from produtos.models import (
    ArquivoImportacaoCatalogo,
    ImportacaoCatalogo,
    ItemImportacaoCatalogo,
    VariacaoImportacaoCatalogo,
)
from produtos.services.catalogo_importacao import (
    analisar_lote,
    atualizar_duplicidade,
    confirmar_importacao,
    criar_lote,
)
from produtos.services.catalogo_importacao.analisador import (
    arquivo_local,
    detectar_layout_visual_imagem,
)


def _decimal(valor, padrao):
    try:
        return Decimal((valor or "").replace(",", "."))
    except (InvalidOperation, AttributeError):
        return padrao


def _inteiro(valor, padrao=0):
    try:
        return max(0, int(valor))
    except (TypeError, ValueError):
        return padrao


@login_required
def importar_catalogo(request):
    if request.method == "POST":
        form = ImportacaoCatalogoForm(request.POST, request.FILES)
        if form.is_valid():
            lote = criar_lote(
                dados=form.cleaned_data,
                arquivos=form.cleaned_data["arquivos"],
                usuario=request.user,
            )
            analisar_lote(lote)
            messages.success(
                request,
                "Arquivos analisados. Confira e edite as sugestões antes de importar.",
            )
            return redirect("produtos:conferir_catalogo", lote_id=lote.pk)
    else:
        form = ImportacaoCatalogoForm()

    return render(request, "produtos/importar_catalogo.html", {"form": form})


@login_required
def conferir_catalogo(request, lote_id):
    lote = get_object_or_404(
        ImportacaoCatalogo.objects.select_related("fornecedor", "tipo_armacao"),
        pk=lote_id,
    )

    if request.method == "POST" and lote.status != ImportacaoCatalogo.Status.IMPORTADO:
        with transaction.atomic():
            itens = lote.itens.prefetch_related("variacoes").all()
            for item in itens:
                prefixo = f"item-{item.pk}-"
                item.incluir = request.POST.get(prefixo + "incluir") == "on"
                item.codigo_fornecedor = request.POST.get(prefixo + "codigo_fornecedor", "").strip().upper()
                item.modelo = request.POST.get(prefixo + "modelo", "").strip()
                item.preco_custo = _decimal(request.POST.get(prefixo + "preco_custo"), item.preco_custo)
                item.preco_venda = _decimal(request.POST.get(prefixo + "preco_venda"), item.preco_venda)
                item.estoque_minimo = _inteiro(request.POST.get(prefixo + "estoque_minimo"), item.estoque_minimo)
                item.estoque_sem_variacao = _inteiro(
                    request.POST.get(prefixo + "estoque_sem_variacao"), item.estoque_sem_variacao
                )
                item.observacoes = request.POST.get(prefixo + "observacoes", "").strip()
                principal_id = request.POST.get(prefixo + "arquivo_principal")
                if principal_id and item.arquivos.filter(pk=principal_id).exists():
                    item.arquivo_principal_id = int(principal_id)
                item.save()

                ids_recebidos = set()
                for variacao in list(item.variacoes.all()):
                    vp = f"var-{variacao.pk}-"
                    if request.POST.get(vp + "delete") == "1":
                        variacao.delete()
                        continue
                    variacao.nome = request.POST.get(vp + "nome", "").strip()
                    variacao.codigo = request.POST.get(vp + "codigo", "").strip().upper()
                    variacao.estoque = _inteiro(request.POST.get(vp + "estoque"), variacao.estoque)
                    variacao.save()
                    ids_recebidos.add(variacao.pk)

                novos_nomes = request.POST.getlist(f"nova-{item.pk}-nome")
                novos_codigos = request.POST.getlist(f"nova-{item.pk}-codigo")
                novos_estoques = request.POST.getlist(f"nova-{item.pk}-estoque")
                total = max(len(novos_nomes), len(novos_codigos), len(novos_estoques))
                for indice in range(total):
                    nome = novos_nomes[indice].strip() if indice < len(novos_nomes) else ""
                    codigo = novos_codigos[indice].strip().upper() if indice < len(novos_codigos) else ""
                    estoque = _inteiro(novos_estoques[indice] if indice < len(novos_estoques) else 0)
                    if nome or codigo:
                        VariacaoImportacaoCatalogo.objects.create(
                            item=item,
                            nome=nome,
                            codigo=codigo,
                            estoque=estoque,
                            ordem=item.variacoes.count() + 1,
                        )

                atualizar_duplicidade(item)

        messages.success(request, "Prévia atualizada. Nenhum produto foi gravado ainda.")
        return redirect("produtos:conferir_catalogo", lote_id=lote.pk)

    itens = list(
        lote.itens.prefetch_related("variacoes", "arquivos")
        .select_related("produto_duplicado", "arquivo_principal")
        .all()
    )
    for item in itens:
        arquivo = item.arquivo_principal or next(iter(item.arquivos.all()), None)
        item.layout_visual = {"hero": None, "variacoes": []}
        item.variacoes_visuais = []
        variacoes_db = list(item.variacoes.all())
        if arquivo:
            campo = arquivo.arquivo if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.IMAGEM else arquivo.preview
            if campo:
                sufixo = Path(arquivo.nome_original).suffix.lower() if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.IMAGEM else ".jpg"
                try:
                    with arquivo_local(campo, sufixo=sufixo) as caminho:
                        item.layout_visual = detectar_layout_visual_imagem(caminho)
                except (OSError, ValueError):
                    item.layout_visual = {"hero": None, "variacoes": []}

        for indice, variacao_db in enumerate(variacoes_db, start=1):
            visual = next((v for v in item.layout_visual.get("variacoes", []) if v.get("indice") == indice), None)
            variacao_db.cor_hex = (visual or {}).get("cor_hex", "#6c757d")
            variacao_db.texto_hex = (visual or {}).get("texto_hex", "#ffffff")

        if arquivo:
            for visual in item.layout_visual.get("variacoes", []):
                indice = visual.get("indice", 0)
                variacao_db = variacoes_db[indice - 1] if 0 < indice <= len(variacoes_db) else None
                item.variacoes_visuais.append({
                    **visual,
                    "codigo": (variacao_db.codigo if variacao_db and variacao_db.codigo else f"C{indice}"),
                    "descricao": (variacao_db.nome if variacao_db else visual.get("nome", "")),
                    "arquivo_id": arquivo.id,
                })
        item.tem_hero_visual = bool(item.layout_visual.get("hero"))
        item.arquivo_visual_id = arquivo.id if arquivo else None
    total_itens = len(itens)
    total_sem_variacao = sum(1 for item in itens if not item.variacoes.all())
    total_duplicidades = sum(1 for item in itens if item.duplicidade != ItemImportacaoCatalogo.Duplicidade.NENHUMA)
    total_prontos = total_itens - total_sem_variacao - total_duplicidades
    return render(
        request,
        "produtos/conferir_catalogo.html",
        {
            "lote": lote,
            "itens": itens,
            "total_itens": total_itens,
            "total_sem_variacao": total_sem_variacao,
            "total_duplicidades": total_duplicidades,
            "total_prontos": max(0, total_prontos),
        },
    )


@login_required
@require_POST
def confirmar_catalogo(request, lote_id):
    lote = get_object_or_404(ImportacaoCatalogo, pk=lote_id)
    try:
        resultado = confirmar_importacao(lote, usuario=request.user)
    except ValidationError as erro:
        for mensagem in erro.messages:
            messages.error(request, mensagem)
        return redirect("produtos:conferir_catalogo", lote_id=lote.pk)

    messages.success(
        request,
        "Importação concluída: "
        f"{resultado['produtos_criados']} produto(s), "
        f"{resultado['variacoes_criadas']} variação(ões) e "
        f"{resultado['movimentacoes_iniciais']} movimentação(ões) inicial(is).",
    )
    return redirect("produtos:lista_produtos")


@login_required
@require_POST
def reanalisar_catalogo(request, lote_id):
    lote = get_object_or_404(ImportacaoCatalogo, pk=lote_id)
    try:
        analisar_lote(lote)
        messages.success(request, "Catálogo analisado novamente. Confira as novas sugestões.")
    except ValidationError as erro:
        for mensagem in erro.messages:
            messages.error(request, mensagem)
    return redirect("produtos:conferir_catalogo", lote_id=lote.pk)


@login_required
def visualizar_recorte_catalogo(request, lote_id, arquivo_id, tipo, indice=0):
    """Entrega recortes temporários usados somente na conferência visual do catálogo."""
    arquivo = get_object_or_404(ArquivoImportacaoCatalogo, pk=arquivo_id, lote_id=lote_id)
    campo = arquivo.arquivo if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.IMAGEM else arquivo.preview
    if not campo:
        raise Http404("Imagem de origem não disponível.")

    sufixo = Path(arquivo.nome_original).suffix.lower() if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.IMAGEM else ".jpg"
    try:
        with arquivo_local(campo, sufixo=sufixo) as caminho:
            layout = detectar_layout_visual_imagem(caminho)
            with Image.open(caminho) as origem:
                imagem = origem.convert("RGB")
                if tipo == "hero":
                    caixa = layout.get("hero")
                elif tipo == "variacao":
                    visual = next((v for v in layout.get("variacoes", []) if v.get("indice") == indice), None)
                    caixa = visual.get("caixa") if visual else None
                else:
                    caixa = None
                if not caixa:
                    raise Http404("Recorte não identificado.")

                largura, altura = imagem.size
                x1 = max(0, min(largura - 1, round(largura * caixa["x1"] / 100)))
                y1 = max(0, min(altura - 1, round(altura * caixa["y1"] / 100)))
                x2 = max(x1 + 1, min(largura, round(largura * caixa["x2"] / 100)))
                y2 = max(y1 + 1, min(altura, round(altura * caixa["y2"] / 100)))
                recorte = imagem.crop((x1, y1, x2, y2))
                buffer = BytesIO()
                recorte.save(buffer, format="JPEG", quality=91, optimize=True)
                return HttpResponse(buffer.getvalue(), content_type="image/jpeg")
    except Http404:
        raise
    except (OSError, ValueError, KeyError, TypeError):
        raise Http404("Não foi possível gerar o recorte visual.")


@login_required
def visualizar_arquivo_catalogo(request, lote_id, arquivo_id):
    """Entrega a imagem/preview do staging sem depender de MEDIA_URL/DEBUG."""
    arquivo = get_object_or_404(
        ArquivoImportacaoCatalogo,
        pk=arquivo_id,
        lote_id=lote_id,
    )

    if arquivo.tipo == ArquivoImportacaoCatalogo.Tipo.IMAGEM:
        campo = arquivo.arquivo
        nome = arquivo.nome_original
    else:
        campo = arquivo.preview
        nome = f"preview-{arquivo.pk}.jpg"

    if not campo:
        raise Http404("Prévia deste arquivo não está disponível.")

    try:
        campo.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        raise Http404("Arquivo de catálogo não encontrado no storage.")

    content_type = mimetypes.guess_type(nome)[0] or "application/octet-stream"
    return FileResponse(
        campo,
        content_type=content_type,
        as_attachment=False,
        filename=nome,
    )
