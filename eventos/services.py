import calendar
from datetime import datetime, timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from core.formatters import formatar_moeda_br

from core.services.operacao_service import USE_HELVI, obter_operacao_ativa
from financeiro.services.baixa_service import registrar_baixa
from financeiro.services.conta_pagar_service import criar_conta_pagar_manual
from financeiro.services.conta_receber_service import criar_conta_receber_manual
from financeiro.services.recebimento_service import registrar_recebimento

from .models import DespesaEvento, Evento, ReceitaEvento, VendaEvento


def validar_operacao_use_helvi(request):
    return obter_operacao_ativa(request) == USE_HELVI


def validar_agenda_evento(*, dados, evento_id=None):
    inicio, fim = dados.get("inicio"), dados.get("fim")
    if not inicio or not fim or fim < inicio:
        return
    outros = Evento.objects.exclude(status=Evento.STATUS_CANCELADO).filter(
        inicio__date__lte=timezone.localtime(fim).date(),
        fim__date__gte=timezone.localtime(inicio).date(),
    )
    if evento_id:
        outros = outros.exclude(pk=evento_id)
    nome = (dados.get("nome") or "").strip()
    duplicado = outros.filter(nome__iexact=nome).first() if nome else None
    if duplicado:
        raise ValidationError(f"Já existe o evento ‘{duplicado.nome}’ nesse mesmo dia.")

    pessoas = set(dados.get("pessoas_equipe") or [])
    equipe = dados.get("equipe")
    if equipe:
        pessoas.update(equipe.pessoas.filter(ativo=True))
    if pessoas:
        conflito = outros.filter(pessoas_equipe__in=[p.pk for p in pessoas]).distinct().first()
        if conflito:
            nomes = ", ".join(sorted(p.nome for p in pessoas if conflito.pessoas_equipe.filter(pk=p.pk).exists()))
            raise ValidationError(f"{nomes} já está alocado(a) no evento ‘{conflito.nome}’ nesse dia.")

    usuarios = set(dados.get("participantes") or [])
    if dados.get("responsavel"):
        usuarios.add(dados["responsavel"])
    if usuarios:
        conflito = outros.filter(Q(participantes__in=[u.pk for u in usuarios]) | Q(responsavel__in=[u.pk for u in usuarios])).distinct().first()
        if conflito:
            nomes = ", ".join(sorted(str(u) for u in usuarios if conflito.participantes.filter(pk=u.pk).exists() or conflito.responsavel_id == u.pk))
            raise ValidationError(f"{nomes} já está alocado(a) no evento ‘{conflito.nome}’ nesse dia.")


def obter_contexto_lista(*, ano=None, mes=None):
    hoje = timezone.localdate()
    ano = ano or hoje.year
    mes = mes or hoje.month
    primeiro = timezone.make_aware(datetime(ano, mes, 1))
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    ultimo = timezone.make_aware(datetime(ano, mes, ultimo_dia, 23, 59, 59))
    eventos_mes = list(
        Evento.objects.filter(inicio__lte=ultimo, fim__gte=primeiro)
        .select_related("responsavel")
        .prefetch_related("pessoas_equipe")
    )
    for evento in eventos_mes:
        _preparar_cores_agenda(evento)
    dias = {dia: [] for dia in range(1, ultimo_dia + 1)}
    for evento in eventos_mes:
        inicio_local = timezone.localtime(evento.inicio).date()
        fim_local = timezone.localtime(evento.fim).date()
        for dia in range(max(1, inicio_local.day if inicio_local.month == mes else 1), min(ultimo_dia, fim_local.day if fim_local.month == mes else ultimo_dia) + 1):
            dias[dia].append(evento)
    calendario = []
    for semana in calendar.Calendar(firstweekday=0).monthdayscalendar(ano, mes):
        calendario.append([{"dia": dia, "eventos": dias.get(dia, [])} for dia in semana])
    proximo_mes = 1 if mes == 12 else mes + 1
    proximo_ano = ano + 1 if mes == 12 else ano
    anterior_mes = 12 if mes == 1 else mes - 1
    anterior_ano = ano - 1 if mes == 1 else ano
    meses = ("", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro")
    proximos_eventos = list(
        Evento.objects.filter(fim__gte=timezone.now())
        .exclude(status=Evento.STATUS_CANCELADO)
        .select_related("responsavel").prefetch_related("pessoas_equipe")[:8]
    )
    for evento in proximos_eventos:
        _preparar_cores_agenda(evento)

    lembretes = []
    candidatos = Evento.objects.filter(
        lembrete_ativo=True, fim__date__gte=hoje,
    ).exclude(status__in=[Evento.STATUS_CANCELADO, Evento.STATUS_CONCLUIDO])
    for evento in candidatos:
        data_inicio = timezone.localtime(evento.inicio).date()
        if hoje >= data_inicio - timedelta(days=evento.lembrete_dias_antes):
            evento.texto_lembrete = evento.lembrete_mensagem or (
                f"O evento {evento.nome} será em {data_inicio.strftime('%d/%m/%Y')}."
            )
            lembretes.append(evento)

    return {
        "calendario": calendario, "mes_nome": meses[mes], "ano": ano,
        "anterior": f"{anterior_ano}-{anterior_mes:02d}", "proximo": f"{proximo_ano}-{proximo_mes:02d}",
        "proximos_eventos": proximos_eventos, "lembretes_eventos": lembretes,
    }


def _preparar_cores_agenda(evento):
    cores = []
    for pessoa in evento.pessoas_equipe.all():
        if pessoa.cor_agenda not in cores:
            cores.append(pessoa.cor_agenda)
    evento.gradiente_agenda = cores[0] if cores else "#D84A8B"


def obter_contexto_evento(pk):
    evento = Evento.objects.select_related("responsavel", "criado_por").prefetch_related(
        "participantes", "vendas", "despesas__conta_pagar__categoria", "despesas__conta_pagar__parcelas"
    ).get(pk=pk)
    return {"evento": evento, "totais": evento.totais}


@transaction.atomic
def criar_despesa_evento(*, evento=None, dados, usuario):
    ja_pago = dados.pop("ja_pago")
    conta_financeira = dados.pop("conta_financeira", None)
    forma_pagamento = dados.pop("forma_pagamento", None)
    valor = dados.pop("valor")
    data = dados.pop("data")
    vencimento = dados.pop("vencimento") or data
    conta = criar_conta_pagar_manual(
        dados={
            "operacao": "use-helvi",
            "descricao": dados["descricao"], "fornecedor": None, "categoria": dados["categoria"],
            "data_emissao": data, "data_competencia": data, "valor_total": valor,
            "observacoes": dados.get("observacoes", ""), "quantidade_parcelas": 1,
            "primeiro_vencimento": vencimento,
        },
        usuario=usuario,
    )
    DespesaEvento.objects.create(evento=evento, conta_pagar=conta, registrado_por=usuario)
    if ja_pago:
        registrar_baixa(
            parcela=conta.parcelas.get(), conta_financeira=conta_financeira,
            valor=valor, data_pagamento=data, forma_pagamento=forma_pagamento, usuario=usuario,
            observacao=(f"Despesa do evento {evento.nome}" if evento else "Despesa geral da Use Helvi"),
        )
    return conta


@transaction.atomic
def criar_venda_evento(*, evento, dados, usuario):
    return VendaEvento.objects.create(evento=evento, registrado_por=usuario, **dados)


@transaction.atomic
def criar_receita_evento(*, evento=None, dados, usuario):
    ja_recebido = dados.pop("ja_recebido")
    conta_financeira = dados.pop("conta_financeira", None)
    forma_recebimento = dados.pop("forma_recebimento", None)
    valor = dados.pop("valor")
    data = dados.pop("data")
    vencimento = dados.pop("vencimento") or data
    conta = criar_conta_receber_manual(dados={
        "operacao": "use-helvi", "descricao": dados["descricao"], "cliente": None,
        "nome_devedor": "", "documento_devedor": "", "categoria": dados["categoria"],
        "data_emissao": data, "data_competencia": data, "valor_total": valor,
        "observacoes": dados.get("observacoes", ""), "quantidade_parcelas": 1,
        "primeiro_vencimento": vencimento,
    }, usuario=usuario)
    ReceitaEvento.objects.create(evento=evento, conta_receber=conta, registrado_por=usuario)
    if ja_recebido:
        registrar_recebimento(
            parcela=conta.parcelas.get(), conta_financeira=conta_financeira,
            data_recebimento=data, valor=valor, forma_recebimento=forma_recebimento,
            observacao=f"Receita da Use Helvi{f' — {evento.nome}' if evento else ''}", usuario=usuario,
        )
    return conta


def montar_relatorio_financeiro(*, inicio, fim, evento_id=None):
    eventos = Evento.objects.filter(inicio__date__lte=fim, fim__date__gte=inicio)
    if evento_id:
        eventos = eventos.filter(pk=evento_id)
    linhas, vendido, recebido, custo, despesas, receitas_eventos = [], Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")
    for evento in eventos.order_by("inicio"):
        totais = evento.totais
        receita_extra = evento.receitas.exclude(conta_receber__status="cancelada").aggregate(total=Sum("conta_receber__valor_total"))["total"] or Decimal("0")
        vendido += totais["vendido"]
        recebido += totais["recebido"]
        custo += totais["custo"]
        despesas += totais["gasto"]
        receitas_eventos += receita_extra
        linhas.append({"valores": [
            evento.nome, timezone.localtime(evento.inicio).strftime("%d/%m/%Y"),
            formatar_moeda_br(totais["vendido"]), formatar_moeda_br(totais["recebido"]),
            formatar_moeda_br(receita_extra), formatar_moeda_br(totais["custo"]), formatar_moeda_br(totais["gasto"]),
            formatar_moeda_br(totais["lucro"] + receita_extra), f"{totais['margem']:.1f}%",
        ]})
    receitas_gerais = ReceitaEvento.objects.filter(evento__isnull=True, conta_receber__data_competencia__range=(inicio, fim)).exclude(conta_receber__status="cancelada").aggregate(total=Sum("conta_receber__valor_total"))["total"] or Decimal("0")
    despesas_gerais = DespesaEvento.objects.filter(evento__isnull=True, conta_pagar__data_competencia__range=(inicio, fim)).exclude(conta_pagar__status="cancelada").aggregate(total=Sum("conta_pagar__valor_total"))["total"] or Decimal("0")
    resultado = vendido + receitas_eventos + receitas_gerais - custo - despesas - despesas_gerais
    return {
        "titulo": "Relatório financeiro — Use Helvi",
        "subtitulo": "Resultado por evento e consolidação das receitas e despesas gerais.",
        "colunas": ["Evento", "Data", "Vendido", "Recebido", "Outras receitas", "Custo", "Despesas", "Lucro", "Margem"],
        "linhas": linhas,
        "kpis": [
            {"titulo": "Vendas", "valor": formatar_moeda_br(vendido)},
            {"titulo": "Outras receitas", "valor": formatar_moeda_br(receitas_eventos + receitas_gerais)},
            {"titulo": "Despesas totais", "valor": formatar_moeda_br(despesas + despesas_gerais)},
            {"titulo": "Resultado", "valor": formatar_moeda_br(resultado)},
        ],
        "totais": {"vendido": vendido, "recebido": recebido, "receitas_gerais": receitas_gerais, "despesas": despesas + despesas_gerais, "resultado": resultado},
    }


@transaction.atomic
def cancelar_evento(*, evento, motivo, usuario):
    evento = Evento.objects.select_for_update().get(pk=evento.pk)
    if evento.status == Evento.STATUS_CANCELADO:
        raise ValueError("Este evento já está cancelado.")
    motivo = (motivo or "").strip()
    if len(motivo) < 5:
        raise ValueError("Informe um motivo válido para o cancelamento.")
    evento.status = Evento.STATUS_CANCELADO
    evento.motivo_cancelamento = motivo
    evento.cancelado_por = usuario
    evento.cancelado_em = timezone.now()
    evento.save(update_fields=[
        "status", "motivo_cancelamento", "cancelado_por", "cancelado_em", "atualizado_em",
    ])
    return evento
