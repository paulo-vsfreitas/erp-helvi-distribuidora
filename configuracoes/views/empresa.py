from django.contrib import messages
from django.shortcuts import redirect, render

from configuracoes.forms import EmpresaForm
from configuracoes.services import (
    obter_empresa,
    salvar_empresa,
)
from usuarios.decorators import permissao_requerida
from usuarios.permissoes import Modulo


@permissao_requerida(Modulo.CONFIGURACOES)
def dados_empresa(request):
    empresa = obter_empresa()

    if request.method == "POST":
        form = EmpresaForm(
            request.POST,
            request.FILES,
            instance=empresa,
        )

        if form.is_valid():
            empresa = salvar_empresa(form)

            messages.success(
                request,
                "Dados da empresa atualizados com sucesso.",
            )

            return redirect(
                "configuracoes:dados_empresa"
            )
    else:
        form = EmpresaForm(
            instance=empresa,
        )

    contexto = {
        "form": form,
        "empresa": empresa,
        "titulo": "Dados da empresa",
        "subtitulo": (
            "Configure as informações institucionais utilizadas "
            "nos documentos, relatórios e comunicações do ERP."
        ),
    }

    return render(
        request,
        "configuracoes/dados_empresa.html",
        contexto,
    )