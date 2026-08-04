from django.core.management.base import BaseCommand, CommandError
from django.db.models import Exists, F, OuterRef, Q

from comercial.models import Orcamento
from compras.models import Compra
from financeiro.models import ContaReceber
from produtos.models import Produto
from vendas.models import Venda


class Command(BaseCommand):
    help = (
        "Audita divergências entre documentos, estoque e financeiro "
        "sem alterar dados."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-error",
            action="store_true",
            help="Retorna código de erro quando houver divergências.",
        )

    def handle(self, *args, **options):
        conta_venda = ContaReceber.objects.filter(
            origem=ContaReceber.ORIGEM_VENDA,
            origem_id=OuterRef("pk"),
        )

        verificacoes = {
            "Orçamentos convertidos sem venda": (
                Orcamento.objects.filter(
                    status=Orcamento.Status.CONVERTIDO,
                    venda_gerada__isnull=True,
                ).count()
            ),
            "Vendas finalizadas sem baixa de estoque": (
                Venda.objects.filter(
                    status=Venda.STATUS_FINALIZADA,
                    estoque_baixado=False,
                ).count()
            ),
            "Vendas finalizadas sem conta a receber": (
                Venda.objects.filter(
                    status=Venda.STATUS_FINALIZADA,
                )
                .annotate(tem_conta=Exists(conta_venda))
                .filter(tem_conta=False)
                .count()
            ),
            "Vendas pagas com saldo pendente": (
                Venda.objects.filter(
                    status_pagamento=Venda.PAGAMENTO_PAGO,
                    valor_recebido__lt=F("total"),
                ).count()
            ),
            "Compras recebidas sem entrada de estoque": (
                Compra.objects.filter(
                    status=Compra.STATUS_RECEBIDA,
                    entrada_estoque_realizada=False,
                ).count()
            ),
            "Compras recebidas sem conta a pagar": (
                Compra.objects.filter(
                    status=Compra.STATUS_RECEBIDA,
                    conta_pagar__isnull=True,
                ).count()
            ),
            "Produtos com saldo ou preços negativos": (
                Produto.objects.filter(
                    Q(estoque_atual__lt=0)
                    | Q(estoque_minimo__lt=0)
                    | Q(preco_custo__lt=0)
                    | Q(preco_venda__lt=0)
                ).count()
            ),
        }

        total = sum(verificacoes.values())

        self.stdout.write("Auditoria de integrações do ERP Helvi")
        for descricao, quantidade in verificacoes.items():
            estilo = self.style.SUCCESS if quantidade == 0 else self.style.ERROR
            self.stdout.write(estilo(f"- {descricao}: {quantidade}"))

        if total:
            mensagem = f"Foram encontradas {total} divergência(s)."
            self.stdout.write(self.style.ERROR(mensagem))
            if options["fail_on_error"]:
                raise CommandError(mensagem)
        else:
            self.stdout.write(
                self.style.SUCCESS("Nenhuma divergência encontrada.")
            )
