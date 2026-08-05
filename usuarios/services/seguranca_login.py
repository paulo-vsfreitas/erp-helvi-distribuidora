from datetime import timedelta
from ipaddress import ip_address

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from usuarios.models import ControleTentativaLogin, EventoLogin


def identificar_ip(request):
    valor = (request.META.get("REMOTE_ADDR") or "").strip()
    try:
        return str(ip_address(valor))
    except ValueError:
        return "0.0.0.0"


def normalizar_username(username):
    return (username or "").strip().casefold()[:150]


def esta_bloqueado(*, username, endereco_ip):
    controle = ControleTentativaLogin.objects.filter(
        username=normalizar_username(username),
        endereco_ip=endereco_ip,
    ).first()
    return bool(
        controle
        and controle.bloqueado_ate
        and controle.bloqueado_ate > timezone.now()
    )


@transaction.atomic
def registrar_falha(*, request, username):
    username = normalizar_username(username)
    endereco_ip = identificar_ip(request)
    controle, _ = ControleTentativaLogin.objects.select_for_update().get_or_create(
        username=username,
        endereco_ip=endereco_ip,
    )
    agora = timezone.now()

    if controle.bloqueado_ate and controle.bloqueado_ate <= agora:
        controle.falhas = 0
        controle.bloqueado_ate = None

    controle.falhas += 1
    if controle.falhas >= settings.LOGIN_MAX_TENTATIVAS:
        controle.bloqueado_ate = agora + timedelta(
            seconds=settings.LOGIN_BLOQUEIO_SEGUNDOS
        )
    controle.save(update_fields=["falhas", "bloqueado_ate", "ultima_tentativa"])
    _registrar_evento(
        request=request,
        username=username,
        endereco_ip=endereco_ip,
        resultado=EventoLogin.FALHA,
    )


@transaction.atomic
def registrar_sucesso(*, request, username, usuario):
    username = normalizar_username(username)
    endereco_ip = identificar_ip(request)
    ControleTentativaLogin.objects.filter(
        username=username,
        endereco_ip=endereco_ip,
    ).update(falhas=0, bloqueado_ate=None)
    _registrar_evento(
        request=request,
        username=username,
        endereco_ip=endereco_ip,
        resultado=EventoLogin.SUCESSO,
        usuario=usuario,
    )


def registrar_bloqueio(*, request, username):
    _registrar_evento(
        request=request,
        username=normalizar_username(username),
        endereco_ip=identificar_ip(request),
        resultado=EventoLogin.BLOQUEADO,
    )


def _registrar_evento(
    *, request, username, endereco_ip, resultado, usuario=None
):
    EventoLogin.objects.create(
        username=username,
        endereco_ip=endereco_ip,
        resultado=resultado,
        usuario=usuario,
        user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:300],
    )
