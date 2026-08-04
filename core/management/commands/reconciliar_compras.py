from django.core.management.base import BaseCommand, CommandError

from compras.models import Compra
from compras.services.financeiro_service import gerar_financeiro_compra


class Command(BaseCommand):
    help = (
        "Lista compras recebidas sem Conta a Pagar e, com --aplicar, "
        "gera as integrações financeiras ausentes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--aplicar",
            action="store_true",
            help="Cria as Contas a Pagar ausentes.",
        )

    def handle(self, *args, **options):
        compras = list(
            Compra.objects
            .filter(
                status=Compra.STATUS_RECEBIDA,
                conta_pagar__isnull=True,
            )
            .select_related("criado_por", "recebida_por")
            .order_by("numero")
        )

        if not compras:
            self.stdout.write(
                self.style.SUCCESS("Nenhuma compra exige conciliação.")
            )
            return

        self.stdout.write(
            f"Compras recebidas sem Conta a Pagar: {len(compras)}"
        )
        for compra in compras:
            self.stdout.write(
                f"- Compra #{compra.numero}: R$ {compra.total:.2f}"
            )

        if not options["aplicar"]:
            self.stdout.write(
                self.style.WARNING(
                    "Nenhum dado foi alterado. Revise a lista e execute "
                    "novamente com --aplicar para conciliar."
                )
            )
            return

        erros = []
        for compra in compras:
            usuario = compra.recebida_por or compra.criado_por

            if usuario is None:
                erros.append(
                    f"Compra #{compra.numero}: usuário responsável ausente."
                )
                continue

            try:
                gerar_financeiro_compra(
                    compra=compra,
                    usuario=usuario,
                )
            except Exception as erro:
                erros.append(
                    f"Compra #{compra.numero}: {erro}"
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Compra #{compra.numero} conciliada."
                    )
                )

        if erros:
            raise CommandError("\n".join(erros))
