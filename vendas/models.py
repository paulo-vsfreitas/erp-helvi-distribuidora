from django.db import models
from clientes.models import Cliente
from produtos.models import Produto
from estoque.models import MovimentacaoEstoque


class Venda(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('pix', 'Pix'),
        ('dinheiro', 'Dinheiro'),
        ('cartao', 'Cartão'),
        ('boleto', 'Boleto'),
        ('prazo', 'A prazo'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='vendas'
    )


    data_venda = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='aberta'
    )

    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        blank=True,
        null=True,
    )

    desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    observacoes = models.TextField(
        blank=True,
        null=True
    )

    estoque_baixado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-data_venda']

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente}"

    def total_bruto(self):
        return sum(item.subtotal() for item in self.itens.all())

    def total_liquido(self):
        return self.total_bruto() - self.desconto

    def baixar_estoque(self):
        if self.status == 'finalizada' and not self.estoque_baixado:
            for item in self.itens.all():
                produto = item.produto
                produto.estoque_atual -= item.quantidade
                produto.save()

                MovimentacaoEstoque.objects.create(
                    produto=produto,
                    tipo='saida',
                    motivo='venda',
                    quantidade=item.quantidade,
                    observacao=f"Baixa automática da Venda #{self.id}"
                )

            self.estoque_baixado = True
            self.save()


class ItemVenda(models.Model):
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT
    )

    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"

    def __str__(self):
        return f"{self.produto} x {self.quantidade}"

    def subtotal(self):
        return self.quantidade * self.preco_unitario