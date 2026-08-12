from decimal import Decimal
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalogo.models import Colecao, Genero, Marca, TipoArmacao
from clientes.models import Cliente
from fornecedores.models import Fornecedor
from produtos.models import Produto, VariacaoCor
from estoque.models import MovimentacaoEstoque
from comercial.models import Orcamento, ItemOrcamento
from compras.models import Compra, ItemCompra
from vendas.models import Venda, ItemVenda
from financeiro.models import CategoriaFinanceira, ContaFinanceira

PREFIXO = "[HOMOLOGAÇÃO]"


class Command(BaseCommand):
    help = "Popula a base de development/staging com dados fictícios integrados para homologação."

    def add_arguments(self, parser):
        parser.add_argument("--quantidade", type=int, default=18, help="Quantidade de produtos fictícios (padrão: 18).")

    def handle(self, *args, **options):
        ambiente = getattr(settings, "APP_ENV", "development")
        if ambiente == "production":
            raise CommandError("BLOQUEADO: popular_homologacao nunca pode rodar em production.")

        quantidade = max(8, min(options["quantidade"], 60))
        usuario = get_user_model().objects.filter(is_superuser=True).order_by("id").first()
        if not usuario:
            usuario = get_user_model().objects.order_by("id").first()
        if not usuario:
            raise CommandError("Crie ao menos um usuário antes de popular a homologação.")

        with transaction.atomic():
            resumo = self._popular(usuario, quantidade)

        self.stdout.write(self.style.SUCCESS("\nBase de homologação populada com sucesso."))
        for chave, valor in resumo.items():
            self.stdout.write(f"  {chave}: {valor}")
        self.stdout.write(self.style.WARNING("Os registros usam códigos TESTE-/HOMO para facilitar a identificação."))

    def _popular(self, usuario, quantidade):
        marcas = [self._get(Marca, nome=n, defaults={"descricao": f"{PREFIXO} marca fictícia"}) for n in ["Helvi Test", "Urban Test", "Vision Test"]]
        colecoes = [self._get(Colecao, nome=n, defaults={"descricao": f"{PREFIXO} coleção fictícia"}) for n in ["Essencial Test", "Solar Test", "Premium Test"]]
        generos = [self._get(Genero, nome=n, defaults={"descricao": f"{PREFIXO} gênero fictício"}) for n in ["Feminino Test", "Masculino Test", "Unissex Test"]]
        tipos = [self._get(TipoArmacao, nome=n, defaults={"descricao": f"{PREFIXO} tipo fictício"}) for n in ["Acetato Test", "Metal Test", "Solar Test"]]

        fornecedores = []
        for i, nome in enumerate(["OptiMax Test", "Lumi Eyewear Test", "Prime Frames Test"], 1):
            obj, _ = Fornecedor.objects.get_or_create(
                cpf_cnpj=f"99.999.99{i}/0001-{i:02d}",
                defaults={"razao_social": nome + " LTDA", "nome_fantasia": nome, "tipo_pessoa": "PJ", "cidade": "São Paulo", "estado": "SP", "observacoes": PREFIXO},
            )
            fornecedores.append(obj)

        clientes = []
        for i in range(1, 9):
            obj, _ = Cliente.objects.get_or_create(
                cnpj=f"88.888.88{i}/0001-{i:02d}",
                defaults={"razao_social": f"Ótica Homologação {i} LTDA", "nome_fantasia": f"Ótica Teste {i}", "responsavel": f"Cliente Teste {i}", "telefone": f"(11) 4000-{1000+i}", "whatsapp": f"(11) 99990-{1000+i}", "email": f"otica{i}@example.test", "cidade": "São Paulo", "estado": "SP", "limite_credito": Decimal("5000.00"), "condicao_pagamento": "30 dias", "observacoes": PREFIXO},
            )
            clientes.append(obj)

        nomes_cores = ["Preto", "Preto claro", "Rosa", "Marrom", "Azul", "Vinho", "Dourado", "Transparente"]
        produtos = []
        variacoes = []
        for i in range(1, quantidade + 1):
            custo = Decimal("22.00") + Decimal(i % 7) * Decimal("3.50")
            venda = (custo * Decimal("2.25")).quantize(Decimal("0.01"))
            fornecedor = fornecedores[(i - 1) % len(fornecedores)]
            produto, _ = Produto.objects.get_or_create(
                codigo=f"TESTE-{i:04d}",
                defaults={"fornecedor": fornecedor, "codigo_fornecedor": f"HOMO{i:04d}", "modelo": f"Armação Homologação {i:02d}", "marca": marcas[(i-1)%3], "colecao": colecoes[(i-1)%3], "genero": generos[(i-1)%3], "tipo_armacao": tipos[(i-1)%3], "preco_custo": custo, "preco_venda": venda, "estoque_minimo": 2, "observacoes": PREFIXO, "ativo": True},
            )
            total = 0
            for c in range(1, 4):
                estoque = 4 + ((i + c) % 8)
                cor, _ = VariacaoCor.objects.get_or_create(produto=produto, codigo=f"C{c}", defaults={"nome": nomes_cores[(i+c-2)%len(nomes_cores)], "estoque": estoque})
                total += cor.estoque
                variacoes.append(cor)
                MovimentacaoEstoque.objects.get_or_create(produto=produto, variacao_cor=cor, tipo="entrada", origem="SEED-HOMOLOGACAO", defaults={"quantidade": cor.estoque, "saldo_anterior": 0, "saldo_atual": cor.estoque, "usuario": usuario, "observacao": PREFIXO})
            if produto.estoque_atual != total:
                Produto.objects.filter(pk=produto.pk).update(estoque_atual=total)
                produto.estoque_atual = total
            produtos.append(produto)

        hoje = timezone.localdate()
        for i in range(1, 7):
            cliente = clientes[(i-1) % len(clientes)]
            p1, p2 = produtos[(i*2-2)%len(produtos)], produtos[(i*2-1)%len(produtos)]
            v1, v2 = p1.variacoes_cor.first(), p2.variacoes_cor.first()
            subtotal = p1.preco_venda * 2 + p2.preco_venda
            orc, criado = Orcamento.objects.get_or_create(cliente_nome=f"{PREFIXO} {cliente.nome_fantasia} {i}", defaults={"cliente": cliente, "cliente_documento": cliente.cnpj or "", "cliente_telefone": cliente.telefone or "", "cliente_email": cliente.email or "", "vendedor": usuario, "data_emissao": hoje - timedelta(days=i*3), "data_validade": hoje + timedelta(days=15), "status": Orcamento.Status.ENVIADO if i % 2 else Orcamento.Status.APROVADO, "subtotal": subtotal, "total": subtotal, "observacoes": PREFIXO})
            if criado:
                ItemOrcamento.objects.create(orcamento=orc, produto=p1, variacao_cor=v1, quantidade=2, valor_unitario=p1.preco_venda, total=p1.preco_venda*2)
                ItemOrcamento.objects.create(orcamento=orc, produto=p2, variacao_cor=v2, quantidade=1, valor_unitario=p2.preco_venda, total=p2.preco_venda)

        for i in range(1, 6):
            fornecedor = fornecedores[(i-1)%3]
            compra, criado = Compra.objects.get_or_create(numero=900000+i, defaults={"fornecedor": fornecedor, "fornecedor_nome": fornecedor.nome_fantasia or fornecedor.razao_social, "fornecedor_documento": fornecedor.cpf_cnpj, "fornecedor_telefone": fornecedor.telefone, "data_compra": hoje-timedelta(days=i*5), "previsao_entrega": hoje+timedelta(days=5), "status": Compra.STATUS_AGUARDANDO_ENTREGA, "subtotal": Decimal("0"), "total": Decimal("0"), "observacoes": PREFIXO, "criado_por": usuario})
            if criado:
                total = Decimal("0")
                for p in produtos[(i-1)*2:(i-1)*2+2]:
                    item = ItemCompra.objects.create(compra=compra, produto=p, quantidade=5, custo_unitario=p.preco_custo)
                    total += item.total
                Compra.objects.filter(pk=compra.pk).update(subtotal=total, total=total)

        for i in range(1, 9):
            cliente = clientes[(i-1)%len(clientes)]
            p = produtos[(i-1)%len(produtos)]
            var = p.variacoes_cor.first()
            total = p.preco_venda * (1 + i % 3)
            venda, criado = Venda.objects.get_or_create(numero=900000+i, defaults={"cliente": cliente, "status": Venda.STATUS_EM_ABERTO, "status_pagamento": Venda.PAGAMENTO_PENDENTE, "forma_pagamento": Venda.FORMA_PIX, "subtotal": total, "total": total, "valor_recebido": Decimal("0"), "observacoes": PREFIXO, "criada_por": usuario})
            if criado:
                ItemVenda.objects.create(venda=venda, produto=p, variacao_cor=var, quantidade=1+i%3, preco_unitario=p.preco_venda, custo_unitario=p.preco_custo, total=total)

        self._get(CategoriaFinanceira, nome="Vendas Homologação", defaults={"tipo": CategoriaFinanceira.TIPO_RECEITA, "descricao": PREFIXO})
        self._get(CategoriaFinanceira, nome="Compras Homologação", defaults={"tipo": CategoriaFinanceira.TIPO_DESPESA, "descricao": PREFIXO})
        ContaFinanceira.objects.get_or_create(nome="Caixa Homologação", defaults={"tipo": ContaFinanceira.TIPO_CAIXA, "instituicao": "Teste", "saldo_inicial": Decimal("2500.00"), "conta_padrao": False, "observacoes": PREFIXO})

        return {"Marcas": len(marcas), "Coleções": len(colecoes), "Gêneros": len(generos), "Tipos": len(tipos), "Fornecedores": len(fornecedores), "Clientes": len(clientes), "Produtos": len(produtos), "Variações de cor": len(variacoes), "Orçamentos": Orcamento.objects.filter(observacoes__contains=PREFIXO).count(), "Compras": Compra.objects.filter(observacoes__contains=PREFIXO).count(), "Vendas": Venda.objects.filter(observacoes__contains=PREFIXO).count()}

    @staticmethod
    def _get(modelo, **kwargs):
        obj, _ = modelo.objects.get_or_create(**kwargs)
        return obj
