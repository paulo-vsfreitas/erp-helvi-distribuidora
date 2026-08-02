from django.urls import path

from configuracoes.views import dados_empresa


app_name = "configuracoes"


urlpatterns = [
    path(
        "",
        dados_empresa,
        name="dados_empresa",
    ),
]