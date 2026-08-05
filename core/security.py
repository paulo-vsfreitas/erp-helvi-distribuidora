from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def _destino_local(request, valor):
    if not valor or not url_has_allowed_host_and_scheme(
        valor,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return ""

    partes = urlsplit(valor)
    destino = partes.path or "/"
    if partes.query:
        destino = f"{destino}?{partes.query}"
    return destino


def csrf_failure(request, reason=""):
    """Recupera páginas expiradas sem enfraquecer a validação CSRF."""

    referencia = _destino_local(
        request,
        request.META.get("HTTP_REFERER", ""),
    )

    if request.user.is_authenticated:
        messages.warning(
            request,
            "Esta página ficou desatualizada e foi recarregada com segurança. "
            "Revise os dados antes de enviar novamente.",
        )
        return redirect(referencia or reverse("dashboard"))

    messages.warning(
        request,
        "Sua sessão expirou. Entre novamente para continuar.",
    )
    destino = _destino_local(
        request,
        request.POST.get("next") or request.GET.get("next"),
    )
    if not destino and referencia != reverse("login"):
        destino = referencia
    if not destino:
        destino = resolve_url(settings.LOGIN_REDIRECT_URL)

    login_url = resolve_url(settings.LOGIN_URL)
    return redirect(f"{login_url}?{urlencode({'next': destino})}")
