import shutil
import tempfile
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from catalogo.models import TipoArmacao
from estoque.models import MovimentacaoEstoque
from fornecedores.models import Fornecedor
from produtos.forms import ProdutoForm, VariacaoCorFormSet
from produtos.models import ImportacaoCatalogo, Produto
from produtos.services.catalogo_importacao import analisar_lote, confirmar_importacao, criar_lote
from produtos.services.catalogo_importacao.analisador import (
    _classificar_cor_regiao,
    detectar_layout_visual_imagem,
    detectar_posicoes_variacoes_imagem,
    detectar_variacoes_visuais_imagem,
    detectar_quantidade_variacoes_imagem,
    sugerir_dados,
)
from produtos.services.estoque import salvar_produto_com_cores
from usuarios.models import Usuario


def imagem_upload(nome="catalogo.png"):
    buffer = BytesIO()
    Image.new("RGB", (20, 20), "white").save(buffer, format="PNG")
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type="image/png")


class BaseCatalogoTest(TestCase):
    def setUp(self):
        self.media_dir = tempfile.mkdtemp(prefix="erp-helvi-test-media-")
        self.override = override_settings(MEDIA_ROOT=self.media_dir)
        self.override.enable()
        self.usuario = Usuario.objects.create_user(
            username="admin-catalogo",
            password="senha123",
            perfil="ADM",
        )
        self.fornecedor = Fornecedor.objects.create(
            razao_social="Fornecedor A",
            nome_fantasia="Fornecedor A",
            cpf_cnpj="11.111.111/0001-11",
        )
        self.tipo = TipoArmacao.objects.create(nome="Acetato")

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_dir, ignore_errors=True)

    def criar_lote_analisado(self, *, codigo="4165", modelo="Polarizado"):
        lote = criar_lote(
            dados={
                "fornecedor": self.fornecedor,
                "tipo_armacao": self.tipo,
                "preco_custo": Decimal("25.00"),
                "preco_venda": Decimal("79.90"),
                "estoque_inicial": 1,
                "estoque_minimo": 0,
            },
            arquivos=[imagem_upload()],
            usuario=self.usuario,
        )
        sugestao = {
            "codigo_fornecedor": codigo,
            "modelo": modelo,
            "variacoes": [
                {"nome": "Preto", "codigo": "C1"},
                {"nome": "Marrom", "codigo": "C2"},
            ],
        }
        with patch(
            "produtos.services.catalogo_importacao.service._analisar_arquivo",
            return_value=sugestao,
        ):
            analisar_lote(lote)
        return lote


class CatalogoAnalyzerTests(TestCase):
    def test_codigo_preserva_zero_a_esquerda(self):
        sugestao = sugerir_dados("065\n60-13-140")
        self.assertEqual(sugestao["codigo_fornecedor"], "065")

    def test_medida_nao_compete_com_codigo_do_modelo(self):
        sugestao = sugerir_dados("MB904\n60-14-142")
        self.assertEqual(sugestao["codigo_fornecedor"], "MB904")

    def test_polarizado_separa_descricao_do_codigo(self):
        sugestao = sugerir_dados("Polarizado 82044")
        self.assertEqual(sugestao["codigo_fornecedor"], "82044")
        self.assertEqual(sugestao["modelo"], "Polarizado")

    def test_o65_nao_vira_modelo(self):
        sugestao = sugerir_dados("O65")
        self.assertEqual(sugestao["codigo_fornecedor"], "065")
        self.assertEqual(sugestao["modelo"], "")

    def test_detector_visual_paisagem_conta_faixas(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "catalogo.jpg"
            imagem = Image.new("RGB", (600, 450), "white")
            # Duas divisórias cinza criam três linhas/variações.
            for y in (148, 298):
                for linha in range(y, y + 5):
                    for x in range(600):
                        imagem.putpixel((x, linha), (228, 228, 228))
            imagem.save(caminho)
            self.assertEqual(detectar_quantidade_variacoes_imagem(caminho), 3)

    def test_detector_visual_retrato_hero_mais_grade_dupla(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "catalogo.jpg"
            imagem = Image.new("RGB", (450, 600), "white")
            # Hero alto + quatro linhas inferiores => oito variações.
            for y in (210, 305, 400, 495):
                for linha in range(y, y + 5):
                    for x in range(450):
                        imagem.putpixel((x, linha), (228, 228, 228))
            imagem.save(caminho)
            self.assertEqual(detectar_quantidade_variacoes_imagem(caminho), 8)
            marcadores = detectar_posicoes_variacoes_imagem(caminho)
            self.assertEqual(len(marcadores), 8)
            self.assertEqual([m["indice"] for m in marcadores], list(range(1, 9)))
            self.assertLess(marcadores[0]["x"], marcadores[1]["x"])

    def test_layout_visual_retrato_expoe_hero_caixas_e_cor_do_badge(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "catalogo.jpg"
            imagem = Image.new("RGB", (450, 600), "white")
            for y in (210, 305, 400, 495):
                for linha in range(y, y + 5):
                    for x in range(450):
                        imagem.putpixel((x, linha), (228, 228, 228))
            for y in range(220, 295):
                for x in range(20, 205):
                    imagem.putpixel((x, y), (205, 120, 145))
            imagem.save(caminho)

            layout = detectar_layout_visual_imagem(caminho)
            self.assertIsNotNone(layout["hero"])
            self.assertEqual(len(layout["variacoes"]), 8)
            primeira = layout["variacoes"][0]
            self.assertEqual(primeira["indice"], 1)
            self.assertIn("caixa", primeira)
            self.assertRegex(primeira["cor_hex"], r"^#[0-9a-f]{6}$")
            self.assertIn(primeira["texto_hex"], {"#111827", "#ffffff"})

    def test_detector_posicoes_paisagem_repete_codigo_nas_duas_vistas(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "catalogo.jpg"
            imagem = Image.new("RGB", (600, 450), "white")
            for y in (148, 298):
                for linha in range(y, y + 5):
                    for x in range(600):
                        imagem.putpixel((x, linha), (228, 228, 228))
            imagem.save(caminho)
            marcadores = detectar_posicoes_variacoes_imagem(caminho)
            self.assertEqual(len(marcadores), 6)
            self.assertEqual([m["indice"] for m in marcadores], [1, 1, 2, 2, 3, 3])

    def test_classificador_refina_cores_reais_de_armacoes(self):
        casos = [
            ((197, 171, 168), "Rosa"),       # pastel rosado de baixa saturação
            ((84, 106, 133), "Preto claro"), # escuro frio percebido como preto claro
            ((33, 60, 111), "Preto"),        # muito escuro apesar do reflexo azul
            ((108, 45, 38), "Marrom"),       # terroso avermelhado
            ((92, 60, 43), "Marrom escuro"),
            ((92, 55, 108), "Roxo"),         # roxo verdadeiro: azul próximo do vermelho
        ]
        for rgb, esperado in casos:
            with self.subTest(rgb=rgb):
                imagem = Image.new("RGB", (160, 100), rgb)
                self.assertEqual(_classificar_cor_regiao(imagem, (0, 0, 160, 100)), esperado)

    def test_detector_visual_sugere_nome_de_cor_por_celula(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "catalogo.jpg"
            imagem = Image.new("RGB", (450, 600), "white")
            for y in (210, 305, 400, 495):
                for linha in range(y, y + 5):
                    for x in range(450):
                        imagem.putpixel((x, linha), (228, 228, 228))
            # Colore a primeira célula inferior de rosa e a segunda de azul.
            for y in range(220, 295):
                for x in range(20, 205):
                    imagem.putpixel((x, y), (205, 120, 145))
                for x in range(245, 430):
                    imagem.putpixel((x, y), (55, 105, 185))
            imagem.save(caminho)
            variacoes = detectar_variacoes_visuais_imagem(caminho)
            self.assertEqual(len(variacoes), 8)
            self.assertEqual(variacoes[0]["nome"], "Rosa")
            self.assertIn(variacoes[1]["nome"], {"Azul", "Azul escuro"})


class CatalogoStagingTests(BaseCatalogoTest):
    def test_analise_cria_apenas_previa(self):
        lote = self.criar_lote_analisado()

        self.assertEqual(Produto.objects.count(), 0)
        self.assertEqual(lote.itens.count(), 1)
        item = lote.itens.get()
        self.assertEqual(item.codigo_fornecedor, "4165")
        self.assertEqual(item.variacoes.count(), 2)
        self.assertEqual(item.variacoes.get(codigo="C1").estoque, 1)

    def test_confirmacao_cria_produto_variacoes_e_movimentacoes(self):
        lote = self.criar_lote_analisado()

        resultado = confirmar_importacao(lote, usuario=self.usuario)

        produto = Produto.objects.get(
            fornecedor=self.fornecedor,
            codigo_fornecedor="4165",
        )
        self.assertEqual(resultado["produtos_criados"], 1)
        self.assertEqual(produto.tipo_armacao, self.tipo)
        self.assertEqual(produto.variacoes_cor.count(), 2)
        self.assertEqual(produto.estoque_atual, 2)
        self.assertEqual(
            MovimentacaoEstoque.objects.filter(produto=produto, origem="Importação Inicial").count(),
            2,
        )
        self.assertTrue(produto.imagens.exists())
        lote.refresh_from_db()
        self.assertEqual(lote.status, ImportacaoCatalogo.Status.IMPORTADO)

    def test_duplicidade_exata_mesmo_fornecedor_bloqueia_confirmacao(self):
        Produto.objects.create(
            fornecedor=self.fornecedor,
            codigo_fornecedor="4165",
            modelo="Já existente",
            preco_custo=10,
            preco_venda=20,
        )
        lote = self.criar_lote_analisado()

        with self.assertRaises(ValidationError):
            confirmar_importacao(lote, usuario=self.usuario)

        self.assertEqual(Produto.objects.count(), 1)

    def test_mesmo_codigo_em_fornecedores_diferentes_e_permitido(self):
        outro = Fornecedor.objects.create(
            razao_social="Fornecedor B",
            nome_fantasia="Fornecedor B",
            cpf_cnpj="22.222.222/0001-22",
        )
        Produto.objects.create(
            fornecedor=outro,
            codigo_fornecedor="4165",
            modelo="Outro",
            preco_custo=10,
            preco_venda=20,
        )
        lote = self.criar_lote_analisado()

        confirmar_importacao(lote, usuario=self.usuario)

        self.assertEqual(Produto.objects.filter(codigo_fornecedor="4165").count(), 2)


class CatalogoViewTests(BaseCatalogoTest):
    def test_tela_catalogo_abre_para_administrador(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("produtos:importar_catalogo"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Importar Catálogo de Produtos")
        self.assertContains(resposta, "Nada é cadastrado automaticamente")

    def test_vendedor_nao_pode_importar_catalogo(self):
        vendedor = Usuario.objects.create_user(
            username="vendedor-catalogo",
            password="senha123",
            perfil="VEN",
        )
        self.client.force_login(vendedor)
        resposta = self.client.get(reverse("produtos:importar_catalogo"))
        self.assertEqual(resposta.status_code, 403)


class EstoqueCadastroProdutoTests(BaseCatalogoTest):
    def _dados_produto(self, estoque="0"):
        return {
            "categoria_comercial": "armacao",
            "codigo": "",
            "fornecedor": str(self.fornecedor.pk),
            "codigo_fornecedor": "CAD-001",
            "modelo": "Cadastro",
            "marca": "",
            "colecao": "",
            "genero": "",
            "tipo_armacao": str(self.tipo.pk),
            "preco_custo": "10.00",
            "preco_venda": "30.00",
            "estoque_atual": estoque,
            "estoque_minimo": "0",
            "observacoes": "",
            "ativo": "on",
        }

    def test_cadastro_estoque_simples_gera_movimentacao(self):
        dados = self._dados_produto(estoque="4")
        dados.update({
            "cores-TOTAL_FORMS": "1",
            "cores-INITIAL_FORMS": "0",
            "cores-MIN_NUM_FORMS": "0",
            "cores-MAX_NUM_FORMS": "1000",
            "cores-0-nome": "",
            "cores-0-codigo": "",
            "cores-0-estoque": "0",
        })
        form = ProdutoForm(dados)
        formset = VariacaoCorFormSet(dados, prefix="cores")
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(formset.is_valid(), formset.errors)

        produto = salvar_produto_com_cores(form, formset, usuario=self.usuario)

        self.assertEqual(produto.estoque_atual, 4)
        self.assertEqual(MovimentacaoEstoque.objects.filter(produto=produto).count(), 1)

    def test_cadastro_com_cores_soma_estoque_e_gera_historico(self):
        dados = self._dados_produto(estoque="0")
        dados.update({
            "cores-TOTAL_FORMS": "2",
            "cores-INITIAL_FORMS": "0",
            "cores-MIN_NUM_FORMS": "0",
            "cores-MAX_NUM_FORMS": "1000",
            "cores-0-nome": "Preto",
            "cores-0-codigo": "C1",
            "cores-0-estoque": "2",
            "cores-1-nome": "Marrom",
            "cores-1-codigo": "C2",
            "cores-1-estoque": "3",
        })
        form = ProdutoForm(dados)
        formset = VariacaoCorFormSet(dados, prefix="cores")
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(formset.is_valid(), formset.errors)

        produto = salvar_produto_com_cores(form, formset, usuario=self.usuario)

        self.assertEqual(produto.estoque_atual, 5)
        self.assertEqual(produto.variacoes_cor.count(), 2)
        self.assertEqual(MovimentacaoEstoque.objects.filter(produto=produto).count(), 2)
