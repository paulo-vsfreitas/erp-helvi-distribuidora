from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Sum
from datetime import date, timedelta
import calendar
from urllib.parse import urlencode
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.decorators import perfil_requerido

from .forms import (
    CancelarEventoForm, CategoriaDespesaForm, CompartilharRelatorioForm, DespesaRapidaForm, EquipeEventoForm, ReceitaRapidaForm,
    EventoForm, PessoaEquipeForm, TipoProdutoEventoForm, VendaEventoForm,
)
from .models import DespesaEvento, EquipeEvento, Evento, PessoaEquipe, ReceitaEvento, TipoProdutoEvento
from financeiro.models import CategoriaFinanceira
from .services import (
    cancelar_evento, criar_despesa_evento, criar_receita_evento, criar_venda_evento, obter_contexto_evento,
    montar_relatorio_financeiro, obter_contexto_lista, validar_operacao_use_helvi,
)
from core.communication import enviar_email_com_anexo, gerar_url_whatsapp
from core.services.relatorio_exportacao_service import exportar_pdf


def _exigir_use_helvi(request):
    if not validar_operacao_use_helvi(request):
        raise Http404("Módulo disponível na operação Use Helvi.")


def _mensagens_erros(form):
    return " ".join(erro for erros in form.errors.values() for erro in erros)


@login_required
@perfil_requerido("ADM", "GER")
def agenda(request):
    _exigir_use_helvi(request)
    referencia = request.GET.get("mes", "").split("-")
    try:
        ano, mes = (int(referencia[0]), int(referencia[1])) if len(referencia) == 2 else (None, None)
    except ValueError:
        ano, mes = None, None
    return render(request, "eventos/agenda.html", obter_contexto_lista(ano=ano, mes=mes))


@login_required
@perfil_requerido("ADM", "GER")
def novo(request):
    _exigir_use_helvi(request)
    form = EventoForm(request.POST or None)
    if request.method == "POST":
        with transaction.atomic():
            list(Evento.objects.select_for_update().filter(status__in=[valor for valor, _ in Evento.STATUS_CHOICES]))
            if form.is_valid():
                evento = form.save(commit=False)
                evento.criado_por = request.user
                evento.save()
                form.save_m2m()
                if evento.equipe_id:
                    evento.pessoas_equipe.add(*evento.equipe.pessoas.filter(ativo=True))
                messages.success(request, "Evento cadastrado com sucesso.")
                return redirect("eventos:ficha", pk=evento.pk)
    return render(request, "eventos/form_evento.html", {"form": form, "titulo": "Novo evento"})


@login_required
@perfil_requerido("ADM", "GER")
def editar(request, pk):
    _exigir_use_helvi(request)
    evento = get_object_or_404(Evento, pk=pk)
    form = EventoForm(request.POST or None, instance=evento)
    if request.method == "POST":
        with transaction.atomic():
            list(Evento.objects.select_for_update().filter(status__in=[valor for valor, _ in Evento.STATUS_CHOICES]))
            if form.is_valid():
                form.save()
                messages.success(request, "Evento atualizado com sucesso.")
                return redirect("eventos:ficha", pk=evento.pk)
    return render(request, "eventos/form_evento.html", {"form": form, "titulo": "Editar evento", "evento": evento})


@login_required
@perfil_requerido("ADM", "GER")
def ficha(request, pk):
    _exigir_use_helvi(request)
    try:
        contexto = obter_contexto_evento(pk)
    except Evento.DoesNotExist as erro:
        raise Http404("Evento não encontrado.") from erro
    contexto["despesa_form"] = DespesaRapidaForm()
    contexto["venda_form"] = VendaEventoForm()
    contexto["cancelar_form"] = CancelarEventoForm()
    return render(request, "eventos/ficha.html", contexto)


@login_required
@perfil_requerido("ADM", "GER")
def lancar_despesa(request, pk):
    _exigir_use_helvi(request)
    if request.method != "POST":
        raise Http404
    evento = get_object_or_404(Evento, pk=pk)
    if evento.status == Evento.STATUS_CANCELADO:
        messages.error(request, "Não é possível lançar despesas em um evento cancelado.")
        return redirect("eventos:ficha", pk=pk)
    form = DespesaRapidaForm(request.POST)
    if form.is_valid():
        criar_despesa_evento(evento=evento, dados=form.cleaned_data.copy(), usuario=request.user)
        messages.success(request, "Despesa registrada no evento e no Financeiro.")
    else:
        messages.error(request, "Revise os dados da despesa: " + _mensagens_erros(form))
    return redirect("eventos:ficha", pk=pk)


@login_required
@perfil_requerido("ADM", "GER")
def lancar_venda(request, pk):
    _exigir_use_helvi(request)
    if request.method != "POST":
        raise Http404
    evento = get_object_or_404(Evento, pk=pk)
    if evento.status == Evento.STATUS_CANCELADO:
        messages.error(request, "Não é possível registrar vendas em um evento cancelado.")
        return redirect("eventos:ficha", pk=pk)
    form = VendaEventoForm(request.POST)
    if form.is_valid():
        criar_venda_evento(evento=evento, dados=form.cleaned_data, usuario=request.user)
        messages.success(request, "Venda registrada no evento.")
    else:
        messages.error(request, "Revise os dados da venda: " + _mensagens_erros(form))
    return redirect("eventos:ficha", pk=pk)


@login_required
@perfil_requerido("ADM", "GER")
def despesas_gerais(request):
    _exigir_use_helvi(request)
    form = DespesaRapidaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        dados = form.cleaned_data.copy()
        criar_despesa_evento(evento=dados.pop("evento", None), dados=dados, usuario=request.user)
        messages.success(request, "Despesa geral registrada no Financeiro da Use Helvi.")
        return redirect("eventos:despesas_gerais")
    despesas = DespesaEvento.objects.filter(evento__isnull=True).select_related(
        "conta_pagar", "conta_pagar__categoria"
    )
    return render(request, "eventos/despesas_gerais.html", {"form": form, "despesas": despesas})


@login_required
@perfil_requerido("ADM", "GER")
def financeiro_use(request):
    _exigir_use_helvi(request)
    acao = request.POST.get("acao") if request.method == "POST" else None
    receita_form = ReceitaRapidaForm(request.POST if acao == "receita" else None, prefix="receita")
    despesa_form = DespesaRapidaForm(request.POST if acao == "despesa" else None, prefix="despesa")
    if acao == "receita" and receita_form.is_valid():
        dados = receita_form.cleaned_data.copy()
        criar_receita_evento(evento=dados.pop("evento", None), dados=dados, usuario=request.user)
        messages.success(request, "Receita registrada no Financeiro da Use Helvi.")
        return redirect("eventos:financeiro")
    if acao == "despesa" and despesa_form.is_valid():
        dados = despesa_form.cleaned_data.copy()
        criar_despesa_evento(evento=dados.pop("evento", None), dados=dados, usuario=request.user)
        messages.success(request, "Despesa registrada no Financeiro da Use Helvi.")
        return redirect("eventos:financeiro")
    receitas = ReceitaEvento.objects.select_related("evento", "conta_receber", "conta_receber__categoria")
    despesas = DespesaEvento.objects.select_related("evento", "conta_pagar", "conta_pagar__categoria")
    busca = request.GET.get("busca", "").strip()
    evento_id = request.GET.get("evento", "")
    categoria_id = request.GET.get("categoria", "")
    situacao = request.GET.get("situacao", "")
    tipo_movimento = request.GET.get("tipo", "")
    inicio = request.GET.get("inicio", "")
    fim = request.GET.get("fim", "")
    if busca:
        receitas = receitas.filter(
            Q(conta_receber__descricao__icontains=busca)
            | Q(conta_receber__categoria__nome__icontains=busca)
            | Q(evento__nome__icontains=busca)
        )
        despesas = despesas.filter(
            Q(conta_pagar__descricao__icontains=busca)
            | Q(conta_pagar__categoria__nome__icontains=busca)
            | Q(evento__nome__icontains=busca)
        )
    if evento_id.isdigit():
        receitas = receitas.filter(evento_id=evento_id)
        despesas = despesas.filter(evento_id=evento_id)
    if categoria_id.isdigit():
        receitas = receitas.filter(conta_receber__categoria_id=categoria_id)
        despesas = despesas.filter(conta_pagar__categoria_id=categoria_id)
    for valor, lookup_receita, lookup_despesa in (
        (inicio, "conta_receber__data_emissao__gte", "conta_pagar__data_emissao__gte"),
        (fim, "conta_receber__data_emissao__lte", "conta_pagar__data_emissao__lte"),
    ):
        try:
            data_filtro = date.fromisoformat(valor) if valor else None
        except ValueError:
            data_filtro = None
        if data_filtro:
            receitas = receitas.filter(**{lookup_receita: data_filtro})
            despesas = despesas.filter(**{lookup_despesa: data_filtro})
    if situacao == "pendente":
        receitas = receitas.filter(conta_receber__status__in=["pendente", "parcial"])
        despesas = despesas.filter(conta_pagar__status__in=["pendente", "parcial"])
    elif situacao == "realizado":
        receitas = receitas.filter(conta_receber__status="recebida")
        despesas = despesas.filter(conta_pagar__status="paga")
    elif situacao == "cancelado":
        receitas = receitas.filter(conta_receber__status="cancelada")
        despesas = despesas.filter(conta_pagar__status="cancelada")
    if tipo_movimento == "entrada":
        despesas = despesas.none()
    elif tipo_movimento == "saida":
        receitas = receitas.none()
    totais_receitas = receitas.exclude(conta_receber__status="cancelada").aggregate(
        previsto=Sum("conta_receber__valor_total"), realizado=Sum("conta_receber__valor_recebido"),
    )
    totais_despesas = despesas.exclude(conta_pagar__status="cancelada").aggregate(
        previsto=Sum("conta_pagar__valor_total"), realizado=Sum("conta_pagar__valor_pago"),
    )
    total_receitas = totais_receitas["previsto"] or 0
    total_recebido = totais_receitas["realizado"] or 0
    total_despesas = totais_despesas["previsto"] or 0
    total_pago = totais_despesas["realizado"] or 0
    lancamentos = [
        {
            "tipo": "entrada", "data": item.conta_receber.data_emissao,
            "descricao": item.conta_receber.descricao, "categoria": item.conta_receber.categoria,
            "evento": item.evento, "status": item.conta_receber.get_status_display(),
            "status_codigo": item.conta_receber.status, "previsto": item.conta_receber.valor_total,
            "realizado": item.conta_receber.valor_recebido,
            "pendente": item.conta_receber.valor_total - item.conta_receber.valor_recebido,
        }
        for item in receitas[:100]
    ] + [
        {
            "tipo": "saida", "data": item.conta_pagar.data_emissao,
            "descricao": item.conta_pagar.descricao, "categoria": item.conta_pagar.categoria,
            "evento": item.evento, "status": item.conta_pagar.get_status_display(),
            "status_codigo": item.conta_pagar.status, "previsto": item.conta_pagar.valor_total,
            "realizado": item.conta_pagar.valor_pago,
            "pendente": item.conta_pagar.valor_total - item.conta_pagar.valor_pago,
        }
        for item in despesas[:100]
    ]
    lancamentos.sort(key=lambda item: (item["data"], item["descricao"]), reverse=True)
    return render(request, "eventos/financeiro.html", {
        "receita_form": receita_form, "despesa_form": despesa_form,
        "receitas": receitas[:50], "despesas": despesas[:50],
        "lancamentos": lancamentos[:100], "total_receitas": total_receitas,
        "total_recebido": total_recebido, "total_a_receber": total_receitas - total_recebido,
        "total_despesas": total_despesas, "total_pago": total_pago,
        "total_a_pagar": total_despesas - total_pago,
        "resultado": total_receitas - total_despesas,
        "resultado_caixa": total_recebido - total_pago, "abrir": acao,
        "eventos_filtro": Evento.objects.order_by("-inicio"),
        "categorias_filtro": CategoriaFinanceira.objects.filter(ativo=True).order_by("tipo", "nome"),
        "filtros": {"busca": busca, "evento": evento_id, "categoria": categoria_id, "tipo": tipo_movimento,
                    "situacao": situacao, "inicio": inicio, "fim": fim},
    })


def _filtros_relatorio(request):
    hoje = timezone.localdate()
    inicio_padrao = hoje.replace(day=1)
    mes = request.GET.get("mes")
    if mes:
        try:
            ano, numero_mes = map(int, mes.split("-"))
            evento = request.GET.get("evento")
            return date(ano, numero_mes, 1), date(ano, numero_mes, calendar.monthrange(ano, numero_mes)[1]), int(evento) if evento and evento.isdigit() else None
        except (ValueError, TypeError):
            pass
    try:
        inicio = date.fromisoformat(request.GET.get("inicio") or inicio_padrao.isoformat())
        fim = date.fromisoformat(request.GET.get("fim") or hoje.isoformat())
    except ValueError:
        inicio, fim = inicio_padrao, hoje
    evento = request.GET.get("evento")
    return inicio, fim, int(evento) if evento and evento.isdigit() else None


@login_required
@perfil_requerido("ADM", "GER")
def relatorio_financeiro(request):
    _exigir_use_helvi(request)
    inicio, fim, evento_id = _filtros_relatorio(request)
    relatorio = montar_relatorio_financeiro(inicio=inicio, fim=fim, evento_id=evento_id)
    periodo = f"{inicio:%d/%m/%Y} a {fim:%d/%m/%Y}"
    if request.GET.get("exportar") == "pdf":
        return exportar_pdf(relatorio, "use-helvi-financeiro", periodo)
    compartilhar = CompartilharRelatorioForm(request.POST or None)
    if request.method == "POST" and compartilhar.is_valid():
        pdf = exportar_pdf(relatorio, "use-helvi-financeiro", periodo).content
        email = compartilhar.cleaned_data.get("email")
        if email:
            enviar_email_com_anexo(destinatario=email, assunto="Relatório financeiro — Use Helvi", mensagem=f"Segue o relatório financeiro da Use Helvi referente ao período {periodo}.", nome_arquivo="relatorio-financeiro-use-helvi.pdf", arquivo=pdf)
            messages.success(request, "Relatório enviado por e-mail com o PDF anexado.")
        whatsapp = compartilhar.cleaned_data.get("whatsapp")
        if whatsapp:
            url_pdf = request.build_absolute_uri(request.path + "?" + urlencode({"inicio": inicio.isoformat(), "fim": fim.isoformat(), "evento": evento_id or "", "exportar": "pdf"}))
            return redirect(gerar_url_whatsapp(telefone=whatsapp, mensagem=f"Relatório financeiro Use Helvi — {periodo}. PDF: {url_pdf}"))
    return render(request, "eventos/relatorio_financeiro.html", {
        "relatorio": relatorio, "inicio": inicio, "fim": fim, "evento_id": evento_id,
        "eventos": Evento.objects.order_by("-inicio"), "periodo": periodo,
        "mes_filtro": request.GET.get("mes", ""), "compartilhar_form": compartilhar,
    })


@login_required
@perfil_requerido("ADM", "GER")
def tipos_produto(request):
    _exigir_use_helvi(request)
    form = TipoProdutoEventoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tipo de produto cadastrado.")
        return redirect("eventos:tipos_produto")
    return render(
        request, "eventos/tipos_produto.html",
        {"form": form, "tipos": TipoProdutoEvento.objects.all()},
    )


@login_required
@perfil_requerido("ADM", "GER")
def editar_tipo_produto(request, pk):
    _exigir_use_helvi(request)
    tipo = get_object_or_404(TipoProdutoEvento, pk=pk)
    form = TipoProdutoEventoForm(request.POST or None, instance=tipo)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tipo de produto atualizado.")
        return redirect("eventos:tipos_produto")
    return render(request, "eventos/form_cadastro.html", {
        "form": form, "titulo": "Editar tipo de produto",
        "voltar": "eventos:tipos_produto",
    })


@login_required
@perfil_requerido("ADM", "GER")
def alternar_tipo_produto(request, pk):
    _exigir_use_helvi(request)
    if request.method != "POST":
        raise Http404
    tipo = get_object_or_404(TipoProdutoEvento, pk=pk)
    tipo.ativo = not tipo.ativo
    tipo.save(update_fields=["ativo"])
    messages.success(
        request,
        "Tipo reativado para novas vendas."
        if tipo.ativo
        else "Tipo excluído das novas vendas; o histórico foi preservado.",
    )
    return redirect("eventos:tipos_produto")


@login_required
@perfil_requerido("ADM", "GER")
def equipes(request):
    _exigir_use_helvi(request)
    pessoa_form = PessoaEquipeForm(prefix="pessoa")
    equipe_form = EquipeEventoForm(prefix="equipe")
    if request.method == "POST":
        if request.POST.get("acao") == "pessoa":
            pessoa_form = PessoaEquipeForm(request.POST, prefix="pessoa")
            if pessoa_form.is_valid():
                pessoa_form.save()
                messages.success(request, "Pessoa cadastrada na equipe.")
                return redirect("eventos:equipes")
        elif request.POST.get("acao") == "equipe":
            equipe_form = EquipeEventoForm(request.POST, prefix="equipe")
            if equipe_form.is_valid():
                equipe_form.save()
                messages.success(request, "Equipe cadastrada.")
                return redirect("eventos:equipes")
    return render(request, "eventos/equipes.html", {
        "pessoa_form": pessoa_form, "equipe_form": equipe_form,
        "pessoas": PessoaEquipe.objects.all(),
        "equipes": EquipeEvento.objects.prefetch_related("pessoas").all(),
    })


@login_required
@perfil_requerido("ADM", "GER")
def editar_pessoa(request, pk):
    _exigir_use_helvi(request)
    pessoa = get_object_or_404(PessoaEquipe, pk=pk)
    form = PessoaEquipeForm(request.POST or None, instance=pessoa)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pessoa atualizada.")
        return redirect("eventos:equipes")
    return render(request, "eventos/form_cadastro.html", {"form": form, "titulo": "Editar pessoa", "voltar": "eventos:equipes"})


@login_required
@perfil_requerido("ADM", "GER")
def editar_equipe(request, pk):
    _exigir_use_helvi(request)
    equipe = get_object_or_404(EquipeEvento, pk=pk)
    form = EquipeEventoForm(request.POST or None, instance=equipe)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Equipe atualizada.")
        return redirect("eventos:equipes")
    return render(request, "eventos/form_cadastro.html", {"form": form, "titulo": "Editar equipe", "voltar": "eventos:equipes"})


@login_required
@perfil_requerido("ADM", "GER")
def alternar_cadastro_equipe(request, tipo, pk):
    _exigir_use_helvi(request)
    if request.method != "POST":
        raise Http404
    modelo = PessoaEquipe if tipo == "pessoa" else EquipeEvento if tipo == "equipe" else None
    if modelo is None:
        raise Http404
    cadastro = get_object_or_404(modelo, pk=pk)
    cadastro.ativo = not cadastro.ativo
    cadastro.save(update_fields=["ativo"])
    messages.success(request, "Cadastro ativado." if cadastro.ativo else "Cadastro excluído das novas seleções.")
    return redirect("eventos:equipes")


@login_required
@perfil_requerido("ADM", "GER")
def categorias_despesa(request):
    _exigir_use_helvi(request)
    form = CategoriaDespesaForm(request.POST or None)
    if request.method == "POST" and request.POST.get("acao") == "criar" and form.is_valid():
        form.save()
        messages.success(request, "Categoria financeira cadastrada.")
        return redirect("eventos:categorias_despesa")
    categorias = CategoriaFinanceira.objects.order_by("tipo", "nome")
    return render(request, "eventos/categorias_despesa.html", {"form": form, "categorias": categorias})


@login_required
@perfil_requerido("ADM", "GER")
def editar_categoria_despesa(request, pk):
    _exigir_use_helvi(request)
    categoria = get_object_or_404(CategoriaFinanceira, pk=pk)
    form = CategoriaDespesaForm(request.POST or None, instance=categoria)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Categoria atualizada.")
        return redirect("eventos:categorias_despesa")
    return render(request, "eventos/form_cadastro.html", {
        "form": form, "titulo": "Editar categoria", "voltar": "eventos:categorias_despesa",
        "tipo_cadastro": "categoria",
        "subtitulo": "Atualize o nome, o tipo e a descrição usados nos lançamentos financeiros.",
    })


@login_required
@perfil_requerido("ADM", "GER")
def alternar_categoria_despesa(request, pk):
    _exigir_use_helvi(request)
    if request.method != "POST":
        raise Http404
    categoria = get_object_or_404(CategoriaFinanceira, pk=pk)
    categoria.ativo = not categoria.ativo
    categoria.save(update_fields=["ativo"])
    messages.success(
        request,
        "Categoria ativada."
        if categoria.ativo
        else "Categoria excluída dos novos lançamentos; o histórico foi mantido.",
    )
    return redirect("eventos:categorias_despesa")


@login_required
@perfil_requerido("ADM", "GER")
def cancelar(request, pk):
    _exigir_use_helvi(request)
    if request.method != "POST":
        raise Http404
    evento = get_object_or_404(Evento, pk=pk)
    form = CancelarEventoForm(request.POST)
    if form.is_valid():
        try:
            cancelar_evento(evento=evento, motivo=form.cleaned_data["motivo"], usuario=request.user)
        except ValueError as erro:
            messages.error(request, str(erro))
        else:
            messages.success(request, "Evento cancelado. O histórico financeiro foi preservado.")
    else:
        messages.error(request, _mensagens_erros(form))
    return redirect("eventos:ficha", pk=pk)
