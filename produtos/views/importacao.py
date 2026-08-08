from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import redirect, render

from produtos.forms_importacao import ImportacaoProdutosForm
from produtos.services.importacao import (
    ErroImportacaoProdutos,
    gerar_modelo_importacao_produtos,
    importar_produtos as executar_importacao_produtos,
    ler_arquivo_produtos,
    simular_importacao_produtos,
)


CHAVE_ARQUIVO_SESSAO = "importacao_produtos_arquivo"


def _limpar_arquivo_temporario(request):
    caminho = request.session.pop(
        CHAVE_ARQUIVO_SESSAO,
        None,
    )

    if caminho and default_storage.exists(caminho):
        default_storage.delete(caminho)


def _montar_simulacao_com_erros(resultado_parser):
    return {
        "total_linhas": len(
            resultado_parser.get("linhas", [])
        ),
        "total_produtos": 0,
        "total_variacoes": 0,
        "total_acessorios": 0,
        "erros": resultado_parser.get(
            "erros",
            [],
        ),
    }


@login_required
def importar_produtos(request):
    simulacao = None
    acao = request.POST.get("acao")

    #
    # IMPORTAÇÃO DEFINITIVA
    #
    if (
        request.method == "POST"
        and acao == "importar"
    ):
        caminho = request.session.get(
            CHAVE_ARQUIVO_SESSAO
        )

        if (
            not caminho
            or not default_storage.exists(caminho)
        ):
            messages.error(
                request,
                (
                    "A planilha temporária não está mais "
                    "disponível. Selecione o arquivo e faça "
                    "uma nova simulação."
                ),
            )

            return redirect(
                "produtos:importar_produtos"
            )

        try:
            with default_storage.open(
                caminho,
                "rb",
            ) as arquivo:
                resultado_parser = (
                    ler_arquivo_produtos(
                        arquivo
                    )
                )

            if resultado_parser["erros"]:
                simulacao = (
                    _montar_simulacao_com_erros(
                        resultado_parser
                    )
                )

            else:
                simulacao = (
                    simular_importacao_produtos(
                        resultado_parser["linhas"]
                    )
                )

                if not simulacao["erros"]:
                    resultado = (
                        executar_importacao_produtos(
                            linhas=resultado_parser[
                                "linhas"
                            ],
                            usuario=request.user,
                        )
                    )

                    _limpar_arquivo_temporario(
                        request
                    )

                    messages.success(
                        request,
                        (
                            "Importação concluída com sucesso. "
                            f"{resultado['produtos_criados']} "
                            "produtos, "
                            f"{resultado['variacoes_criadas']} "
                            "variações e "
                            f"{resultado['acessorios_criados']} "
                            "acessórios foram cadastrados."
                        ),
                    )

                    return redirect(
                        "produtos:lista_produtos"
                    )

        except ErroImportacaoProdutos as erro:
            simulacao = simulacao or {
                "total_linhas": 0,
                "total_produtos": 0,
                "total_variacoes": 0,
                "total_acessorios": 0,
                "erros": [],
            }

            simulacao["erros"] = (
                erro.messages
                if hasattr(erro, "messages")
                else [str(erro)]
            )

        form = ImportacaoProdutosForm()

        return render(
            request,
            "produtos/importar_produtos.html",
            {
                "form": form,
                "simulacao": simulacao,
                "arquivo_simulado": True,
            },
        )

    #
    # SIMULAÇÃO
    #
    if request.method == "POST":
        form = ImportacaoProdutosForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            arquivo = form.cleaned_data["arquivo"]

            resultado_parser = (
                ler_arquivo_produtos(
                    arquivo
                )
            )

            if resultado_parser["erros"]:
                simulacao = (
                    _montar_simulacao_com_erros(
                        resultado_parser
                    )
                )

                _limpar_arquivo_temporario(
                    request
                )

            else:
                simulacao = (
                    simular_importacao_produtos(
                        resultado_parser["linhas"]
                    )
                )

                if simulacao["erros"]:
                    _limpar_arquivo_temporario(
                        request
                    )

                else:
                    #
                    # Remove uma eventual simulação anterior.
                    #
                    _limpar_arquivo_temporario(
                        request
                    )

                    arquivo.seek(0)

                    extensao = (
                        ".xlsx"
                        if arquivo.name.lower().endswith(
                            ".xlsx"
                        )
                        else ".csv"
                    )

                    caminho = default_storage.save(
                        (
                            "importacoes_temporarias/"
                            f"produtos_{uuid4().hex}"
                            f"{extensao}"
                        ),
                        arquivo,
                    )

                    request.session[
                        CHAVE_ARQUIVO_SESSAO
                    ] = caminho

    else:
        form = ImportacaoProdutosForm()

    return render(
        request,
        "produtos/importar_produtos.html",
        {
            "form": form,
            "simulacao": simulacao,
            "arquivo_simulado": bool(
                request.session.get(
                    CHAVE_ARQUIVO_SESSAO
                )
            ),
        },
    )


@login_required
def baixar_modelo_importacao_produtos(request):
    arquivo = gerar_modelo_importacao_produtos()

    resposta = HttpResponse(
        arquivo.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    resposta["Content-Disposition"] = (
        'attachment; '
        'filename="modelo_importacao_produtos_helvi.xlsx"'
    )

    return resposta