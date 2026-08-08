from django.contrib.auth.views import LoginView
from django.urls import reverse

from core.services.operacao_service import limpar_operacao_ativa
from usuarios.forms_login import LoginSeguroForm


class HelviLoginView(LoginView):
    authentication_form = LoginSeguroForm
    template_name = "core/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        limpar_operacao_ativa(self.request)
        return response

    def get_success_url(self):
        return reverse("selecionar_operacao")
