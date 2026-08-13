import os
import re
import shutil
import subprocess
import tempfile
import colorsys
import math
from urllib.request import urlopen
from contextlib import contextmanager
from pathlib import Path

from django.core.files import File
from PIL import Image, ImageChops, ImageOps


CORES = {
    "preto", "preta", "black", "marrom", "brown", "tartaruga", "azul", "blue",
    "verde", "green", "vermelho", "vermelha", "red", "rosa", "pink", "roxo",
    "purple", "dourado", "dourada", "gold", "prata", "silver", "cinza", "grafite",
    "transparente", "cristal", "bege", "nude", "branco", "branca", "white",
}


@contextmanager
def arquivo_local(campo_arquivo, *, sufixo=""):
    """Materializa um FieldFile em arquivo fechado, compatível com subprocessos no Windows."""
    with tempfile.TemporaryDirectory() as diretorio:
        caminho = Path(diretorio) / f"arquivo{sufixo or '.tmp'}"
        try:
            campo_arquivo.open("rb")
            try:
                with caminho.open("wb") as destino:
                    shutil.copyfileobj(campo_arquivo, destino)
            finally:
                campo_arquivo.close()
        except (FileNotFoundError, OSError, ValueError):
            # Em storages S3 privados, alguns backends podem falhar ao abrir o
            # objeto como arquivo após o upload, embora consigam gerar uma URL
            # assinada válida. Usa essa URL como fallback sem depender de MEDIA_ROOT.
            url = campo_arquivo.url
            with urlopen(url, timeout=30) as origem, caminho.open("wb") as destino:
                shutil.copyfileobj(origem, destino)
        # O arquivo precisa estar fechado antes de Tesseract/Poppler abrirem o caminho
        # no Windows; NamedTemporaryFile aberto pode bloquear acesso de subprocessos.
        yield str(caminho)


def _executar(comando, *, timeout=25):
    try:
        return subprocess.run(
            comando,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def localizar_tesseract():
    """Localiza o Tesseract no PATH, por configuração ou nos caminhos comuns do Windows."""
    configurado = (os.environ.get("TESSERACT_CMD") or "").strip().strip('"')
    candidatos = [
        configurado,
        shutil.which("tesseract"),
    ]

    if os.name == "nt":
        program_files = os.environ.get("ProgramFiles", r"C:\\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)")
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        candidatos.extend([
            str(Path(program_files) / "Tesseract-OCR" / "tesseract.exe"),
            str(Path(program_files_x86) / "Tesseract-OCR" / "tesseract.exe"),
            str(Path(local_appdata) / "Programs" / "Tesseract-OCR" / "tesseract.exe") if local_appdata else "",
        ])

    for candidato in candidatos:
        if not candidato:
            continue
        caminho = Path(candidato)
        if caminho.is_file():
            return str(caminho)
    return None


def _ocr_tesseract(tesseract, caminho, *, psm=11, somente_codigo=False):
    comando = [tesseract, caminho, "stdout", "-l", "por+eng", "--psm", str(psm)]
    if somente_codigo:
        comando.extend(["-c", "tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ- "])
    resultado = _executar(comando)
    if resultado is None:
        comando = [tesseract, caminho, "stdout", "--psm", str(psm)]
        if somente_codigo:
            comando.extend(["-c", "tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ- "])
        resultado = _executar(comando)
    return resultado.stdout.strip() if resultado is not None else ""


def _mascara_texto_vermelho(caminho, destino):
    """Destaca o padrão mais comum dos catálogos: código vermelho em fundo claro."""
    try:
        with Image.open(caminho).convert("RGB") as imagem:
            vermelho, verde, azul = imagem.split()
            maior_gb = ImageChops.lighter(verde, azul)
            predominancia = ImageChops.subtract(vermelho, maior_gb).point(
                lambda valor: 255 if valor >= 45 else 0
            )
            luminosidade = vermelho.point(lambda valor: 255 if valor >= 105 else 0)
            mascara = ImageChops.multiply(predominancia, luminosidade)
            caixa = mascara.getbbox()
            if not caixa:
                return False
            margem_x = max(12, round((caixa[2] - caixa[0]) * 0.08))
            margem_y = max(8, round((caixa[3] - caixa[1]) * 0.18))
            caixa = (
                max(0, caixa[0] - margem_x),
                max(0, caixa[1] - margem_y),
                min(mascara.width, caixa[2] + margem_x),
                min(mascara.height, caixa[3] + margem_y),
            )
            mascara = ImageOps.invert(mascara.crop(caixa))
            if mascara.width < 900:
                escala = min(3, max(1, round(900 / max(1, mascara.width))))
                if escala > 1:
                    mascara = mascara.resize(
                        (mascara.width * escala, mascara.height * escala),
                        Image.Resampling.NEAREST,
                    )
            mascara.save(destino, format="PNG", compress_level=1)
        return True
    except (OSError, ValueError):
        return False


def _combinar_textos(*textos):
    linhas = []
    vistos = set()
    for texto in textos:
        for linha in _limpar_linhas(texto or ""):
            chave = linha.casefold()
            if chave not in vistos:
                vistos.add(chave)
                linhas.append(linha)
    return "\n".join(linhas)


def extrair_texto_imagem(caminho):
    tesseract = localizar_tesseract()
    if not tesseract:
        return (
            "",
            "OCR automático indisponível: Tesseract não encontrado. "
            "Instale o Tesseract-OCR ou configure TESSERACT_CMD e reanalise o lote.",
        )

    texto_vermelho = ""
    with tempfile.TemporaryDirectory() as diretorio:
        processada = Path(diretorio) / "texto_vermelho.png"
        if _mascara_texto_vermelho(caminho, processada):
            texto_vermelho = _ocr_tesseract(
                tesseract,
                str(processada),
                psm=11,
                somente_codigo=True,
            )

    # Nos catálogos visuais homologados, o código e a medida aparecem em
    # vermelho. Quando o passe especializado já encontra um código confiável,
    # evita um segundo processo Tesseract sobre a imagem inteira.
    texto_geral = ""
    if not _extrair_codigo_fornecedor(texto_vermelho):
        with tempfile.TemporaryDirectory() as diretorio:
            reduzida = Path(diretorio) / "ocr_geral.jpg"
            try:
                with Image.open(caminho).convert("RGB") as imagem:
                    imagem.thumbnail(
                        (1800, 1800),
                        Image.Resampling.LANCZOS,
                        reducing_gap=3.0,
                    )
                    imagem.save(reduzida, format="JPEG", quality=84, optimize=False)
                texto_geral = _ocr_tesseract(tesseract, str(reduzida), psm=11)
            except (OSError, ValueError):
                texto_geral = _ocr_tesseract(tesseract, caminho, psm=11)

    texto = _combinar_textos(texto_vermelho, texto_geral)
    if not texto:
        return "", "Não foi possível extrair texto legível desta imagem."
    return texto, ""


def extrair_texto_pdf(caminho):
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        return "", "Leitura automática de PDF indisponível neste servidor; confira os dados manualmente."

    resultado = _executar([pdftotext, "-layout", caminho, "-"])
    if resultado is None:
        return "", "Não foi possível extrair texto do PDF."
    return resultado.stdout.strip(), ""


def gerar_preview_pdf(arquivo_model, caminho_pdf):
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        return False

    with tempfile.TemporaryDirectory() as tmp:
        prefixo = str(Path(tmp) / "pagina")
        resultado = _executar([
            pdftoppm, "-f", "1", "-singlefile", "-jpeg", "-r", "130",
            caminho_pdf, prefixo,
        ])
        jpg = Path(prefixo + ".jpg")
        if resultado is None or not jpg.exists():
            return False
        with jpg.open("rb") as handle:
            arquivo_model.preview.save(
                f"preview_{arquivo_model.pk}.jpg",
                File(handle),
                save=True,
            )
    return True


def _limpar_linhas(texto):
    return [re.sub(r"\s+", " ", linha).strip() for linha in texto.splitlines() if linha.strip()]


def _nome_arquivo_descritivo(nome_arquivo):
    """Usa nome do arquivo apenas quando ele parece informação humana, não UUID/hash."""
    stem = Path(nome_arquivo or "").stem.strip()
    if not stem:
        return ""

    compacto = re.sub(r"[^A-Za-z0-9]", "", stem)
    grupos = [grupo for grupo in re.split(r"[-_ ]+", stem) if grupo]
    parece_uuid = (
        len(grupos) >= 4
        and len(compacto) >= 20
        and all(re.fullmatch(r"[0-9A-Fa-f]+", grupo) for grupo in grupos)
    )
    parece_hash = len(compacto) >= 24 and bool(re.fullmatch(r"[0-9A-Fa-f]+", compacto))
    if parece_uuid or parece_hash:
        return ""

    return stem.replace("_", " ").strip()


def _faixas_separadoras_horizontais(imagem):
    """Detecta gutters horizontais claros usados nos mosaicos dos fornecedores.

    A heurística trabalha em miniatura e usa apenas Pillow. Ela procura linhas
    estreitas, neutras e claras que atravessam praticamente toda a imagem.
    Regiões brancas grandes do fundo são ignoradas para evitar falsos positivos.
    """
    largura_original, altura_original = imagem.size
    if largura_original <= 0 or altura_original <= 0:
        return [], 0

    largura = min(420, largura_original)
    altura = max(1, round(altura_original * largura / largura_original))
    reduzida = imagem.resize((largura, altura)).convert("RGB")
    pixels = reduzida.load()

    candidatas = []
    for y in range(altura):
        neutros_claros = 0
        soma_luminosidade = 0.0
        for x in range(largura):
            r, g, b = pixels[x, y]
            maior = max(r, g, b)
            menor = min(r, g, b)
            luminosidade = (r + g + b) / 3
            soma_luminosidade += luminosidade
            if maior - menor <= 12 and 210 <= luminosidade <= 242:
                neutros_claros += 1
        fracao = neutros_claros / largura
        media = soma_luminosidade / largura
        candidatas.append(fracao >= 0.85 and media <= 245)

    faixas = []
    indice = 0
    limite_faixa = max(3, round(altura * 0.04))
    while indice < altura:
        if not candidatas[indice]:
            indice += 1
            continue
        fim = indice + 1
        while fim < altura and candidatas[fim]:
            fim += 1
        # Gutter do catálogo é estreito. Uma faixa extensa normalmente é apenas
        # fundo branco/cinza sem produto, e não deve dividir o mosaico.
        if 1 <= fim - indice <= limite_faixa:
            centro = (indice + fim - 1) // 2
            if altura * 0.08 < centro < altura * 0.92:
                faixas.append(centro)
        indice = fim

    # Une detecções muito próximas que pertencem ao mesmo divisor visual.
    mescladas = []
    distancia = max(2, round(altura * 0.018))
    for centro in faixas:
        if mescladas and centro - mescladas[-1] <= distancia:
            mescladas[-1] = round((mescladas[-1] + centro) / 2)
        else:
            mescladas.append(centro)
    return mescladas, altura


def detectar_quantidade_variacoes_imagem(caminho):
    """Estima quantas variações aparecem em um catálogo visual.

    Retorna 0 quando o layout não oferece confiança suficiente. Os padrões
    reconhecidos são os observados nos catálogos reais homologados:
      * paisagem: cada faixa horizontal representa uma cor em duas vistas;
      * retrato: uma faixa hero no topo + grade inferior de duas cores por linha.
    A função nunca tenta nomear a cor; apenas estima a quantidade para gerar
    C1..Cn, sempre editáveis antes da importação definitiva.
    """
    try:
        with Image.open(caminho) as origem:
            imagem = origem.convert("RGB")
            largura, altura = imagem.size
            if largura < 100 or altura < 100:
                return 0

            separadores, altura_reduzida = _faixas_separadoras_horizontais(imagem)
            proporcao = largura / altura
            limites = [0, *separadores, altura_reduzida]
            alturas_faixas = [
                limites[indice + 1] - limites[indice]
                for indice in range(len(limites) - 1)
                if limites[indice + 1] - limites[indice] > 0
            ]

            # Catálogo em paisagem: duas vistas da mesma cor ocupam a mesma linha.
            if proporcao >= 1.15:
                quantidade = len(alturas_faixas)
                return quantidade if 1 <= quantidade <= 20 else 0

            # Catálogo vertical: primeira faixa é uma apresentação/modelo e as
            # demais formam uma grade de duas cores diferentes por linha.
            if proporcao < 1.15 and len(alturas_faixas) >= 4:
                inferiores = alturas_faixas[1:]
                ordenadas = sorted(inferiores)
                mediana = ordenadas[len(ordenadas) // 2]
                primeira = alturas_faixas[0]
                if mediana > 0 and primeira >= mediana * 1.45:
                    quantidade = len(inferiores) * 2
                    return quantidade if 2 <= quantidade <= 30 else 0
    except (OSError, ValueError):
        return 0
    return 0




def _resumir_amostras_cor(amostras):
    if not amostras:
        return None

    total = sum(a[6] for a in amostras) or 1.0
    r = sum(a[0] * a[6] for a in amostras) / total
    g = sum(a[1] * a[6] for a in amostras) / total
    b = sum(a[2] * a[6] for a in amostras) / total
    sat = sum(a[4] * a[6] for a in amostras) / total
    val = sum(a[5] * a[6] for a in amostras) / total
    seno = sum(math.sin(2 * math.pi * a[3]) * a[6] for a in amostras)
    cosseno = sum(math.cos(2 * math.pi * a[3]) * a[6] for a in amostras)
    hue = (math.atan2(seno, cosseno) % (2 * math.pi)) / (2 * math.pi) if seno or cosseno else 0.0

    return {
        "r": r, "g": g, "b": b,
        "h": hue, "s": sat, "v": val,
        "escuros": sum(a[6] for a in amostras if a[5] < 0.36) / total,
        "muito_escuros": sum(a[6] for a in amostras if a[5] < 0.25) / total,
        "neutros": sum(a[6] for a in amostras if a[4] < 0.18) / total,
        "quentes": sum(a[6] for a in amostras if (a[3] < 0.16 or a[3] > 0.96)) / total,
        "azuis": sum(a[6] for a in amostras if 0.52 <= a[3] < 0.72) / total,
        "roxos": sum(a[6] for a in amostras if 0.72 <= a[3] < 0.94) / total,
    }


def _estatisticas_cor_regiao(imagem, caixa):
    """Resume a cor útil da peça ignorando o fundo do catálogo.

    O classificador de armações/lentes precisa distinguir tons escuros muito
    próximos. Por isso usamos RGB + HSV e descartamos pixels de fundo claros,
    reflexos quase brancos e áreas sem informação cromática relevante.
    """
    esquerda, topo, direita, base = caixa
    largura = max(1, direita - esquerda)
    altura = max(1, base - topo)
    margem_x = max(2, int(largura * 0.08))
    margem_y = max(2, int(altura * 0.10))
    recorte = imagem.crop((
        esquerda + margem_x, topo + margem_y,
        direita - margem_x, base - margem_y,
    ))
    recorte.thumbnail((220, 150))

    amostras = []
    superiores = []
    inferiores = []
    limite_superior = recorte.height / 3
    limite_inferior = recorte.height * 2 / 3
    for posicao, (r, g, b) in enumerate(recorte.getdata()):
        rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
        h, sat, val = colorsys.rgb_to_hsv(rf, gf, bf)
        # Fundo branco/cinza claro e reflexos de estúdio.
        if val >= 0.94 and sat <= 0.12:
            continue
        if val >= 0.88 and sat <= 0.07:
            continue
        # Pixels quase brancos muito saturados também costumam ser reflexos.
        if val >= 0.97:
            continue
        # Peso privilegia a própria lente/armação sem deixar um reflexo azul
        # isolado dominar a classificação de uma peça preta ou marrom.
        peso = max(0.10, sat) * max(0.18, 1.04 - val)
        if val < 0.45:
            peso *= 1.25
        amostra = (r, g, b, h, sat, val, peso)
        amostras.append(amostra)
        y = posicao // recorte.width
        if y < limite_superior:
            superiores.append(amostra)
        elif y >= limite_inferior:
            inferiores.append(amostra)

    resumo = _resumir_amostras_cor(amostras)
    if resumo:
        resumo["superior"] = _resumir_amostras_cor(superiores)
        resumo["inferior"] = _resumir_amostras_cor(inferiores)
    return resumo


def _classificar_estatisticas_cor(e):
    """Classifica estatísticas já calculadas, sem reler pixels da imagem."""
    if not e:
        return ""

    r, g, b = e["r"], e["g"], e["b"]
    hue, sat, val = e["h"], e["s"], e["v"]
    max_rgb, min_rgb = max(r, g, b), min(r, g, b)
    dispersao = (max_rgb - min_rgb) / 255.0

    # ROSA/ROSÉ PASTEL: lentes claras têm saturação baixa e antes acabavam
    # tratadas como cinza. A dominância suave de vermelho é suficiente quando
    # a peça é clara e o hue permanece na família quente/rosada.
    if val >= 0.68 and r >= g + 12 and r >= b + 9:
        if hue < 0.055 or hue >= 0.94:
            return "Rosa"
        if hue < 0.10:
            return "Rosé"

    # TRANSPARENTE / DOURADO: regiões muito claras e pouco saturadas só são
    # cinza quando realmente neutras. Um viés quente visível indica dourado.
    if val >= 0.72 and sat < 0.20:
        if r >= b + 18 and g >= b + 10:
            return "Dourado / transparente"
        if abs(r - g) < 10 and abs(g - b) < 10:
            return "Transparente"

    # PRETOS/NEUTROS. "Preto claro" é a nomenclatura visual usada na operação
    # para peças escuras que ainda preservam bastante luminosidade.
    if sat < 0.20:
        if val < 0.34:
            return "Preto"
        if val < 0.60:
            return "Preto claro"
        if val < 0.76:
            return "Cinza"
        return "Transparente"

    # FAMÍLIAS TERROSAS antes de roxo. Marrom costuma manter R > G e R > B,
    # mesmo quando reflexos frios elevam o canal azul.
    razao_rg = r / max(g, 1)
    razao_rb = r / max(b, 1)
    razao_gb = g / max(b, 1)
    if r > g and r > b and razao_rg >= 1.12:
        if razao_rb >= 1.08:
            if val < 0.40:
                return "Marrom escuro"
            if val < 0.62:
                # Vermelho muito dominante e azul ainda presente tende a vinho;
                # caso contrário o resultado visual é marrom.
                if r > g * 1.42 and b > g * 1.05 and b >= r * 0.78:
                    return "Vinho"
                return "Marrom"
            return "Caramelo" if hue < 0.14 else "Rosé"

    if r > g > b and razao_rg >= 1.07 and razao_gb >= 1.02:
        if val < 0.40:
            return "Marrom escuro"
        if val < 0.66:
            return "Marrom"
        return "Caramelo" if sat >= 0.25 else "Dourado / transparente"

    # ROXO verdadeiro exige que vermelho e azul estejam próximos. Se o vermelho
    # se distancia demais do azul, a família terrosa/vinho é mais provável.
    if 0.72 <= hue < 0.96 or e["roxos"] >= 0.56:
        if r > b * 1.10 and r > g * 1.16:
            return "Marrom" if val >= 0.36 else "Marrom escuro"
        if abs(r - b) <= max(18, r * 0.20) and b > g * 1.08:
            return "Roxo"

    # AZUL MUITO ESCURO: para a conferência visual do catálogo, luminosidade
    # baixa prevalece sobre um reflexo azulado. Essa calibração evita chamar de
    # "Azul escuro" peças que o usuário percebe como preto.
    if 0.52 <= hue < 0.72 or e["azuis"] >= 0.58:
        if val < 0.48:
            return "Preto"
        if val < 0.58:
            return "Preto claro"
        return "Azul" if val >= 0.68 else "Azul escuro"

    # Preto residual em regiões cromáticas pouco confiáveis.
    if val <= 0.27 or e["muito_escuros"] >= 0.58:
        return "Preto"
    if val <= 0.38 and dispersao < 0.18:
        return "Preto"

    # Demais famílias por matiz.
    if hue < 0.035 or hue >= 0.96:
        if val < 0.52:
            return "Vinho"
        return "Vermelho" if sat > 0.48 else "Rosa"
    if hue < 0.075:
        return "Marrom" if val < 0.68 else "Rosé"
    if hue < 0.16:
        if val > 0.72 and sat < 0.42:
            return "Dourado / transparente"
        return "Dourado" if val > 0.64 else "Marrom"
    if hue < 0.30:
        return "Verde"
    if hue < 0.52:
        return "Verde / azul"
    if hue < 0.70:
        return "Azul"
    if hue < 0.83:
        return "Roxo"
    if hue < 0.96:
        return "Rosa" if val > 0.60 else "Roxo"
    return ""


def _familia_cor(nome):
    return (nome or "").replace(" escuro", "").replace(" claro", "")


def _descricao_degrade(e, nome_base):
    superior = e.get("superior")
    inferior = e.get("inferior")
    if not superior or not inferior:
        return nome_base

    nome_superior = _classificar_estatisticas_cor(superior)
    nome_inferior = _classificar_estatisticas_cor(inferior)
    familia_superior = _familia_cor(nome_superior)
    familia_inferior = _familia_cor(nome_inferior)
    diferenca_luz = abs(superior["v"] - inferior["v"])
    cromatico = max(superior["s"], inferior["s"]) >= 0.18
    familias_validas = {
        "Azul", "Cinza", "Preto", "Marrom", "Rosa", "Roxo", "Dourado",
        "Dourado / transparente", "Transparente",
    }

    neutro_degrade = {
        familia_superior, familia_inferior
    }.issubset({"Preto", "Cinza", "Transparente"})
    if (not cromatico and not neutro_degrade) or diferenca_luz < 0.13:
        return nome_base
    if neutro_degrade:
        return "Cinza degradê"
    if familia_superior == familia_inferior and familia_superior in familias_validas:
        return f"{familia_superior} degradê"
    if familia_superior in familias_validas and familia_inferior in familias_validas:
        return f"{familia_superior} / {familia_inferior} degradê"
    return f"{_familia_cor(nome_base)} degradê" if nome_base else nome_base


def _classificar_cor_regiao(imagem, caixa):
    """Sugere a cor percebida, incluindo lentes com degradê vertical relevante."""
    estatisticas = _estatisticas_cor_regiao(imagem, caixa)
    nome = _classificar_estatisticas_cor(estatisticas)
    return _descricao_degrade(estatisticas, nome) if estatisticas else ""

def _cor_representativa_regiao(imagem, caixa, *, estatisticas=None, nome=None):
    """Retorna HEX representativo da peça e uma cor de texto legível."""
    e = estatisticas or _estatisticas_cor_regiao(imagem, caixa)
    if not e:
        return "#6c757d", "#ffffff"

    r = round(e["r"])
    g = round(e["g"])
    b = round(e["b"])

    # Para peças classificadas como preto/grafite, neutraliza pequenas
    # dominâncias azuis/roxas causadas pelo reflexo do estúdio. O badge fica
    # visualmente mais fiel ao que o usuário enxerga na armação/lente.
    nome = nome or _classificar_estatisticas_cor(e)
    if nome == "Preto":
        nivel = max(24, min(54, round((r + g + b) / 3)))
        r = g = b = nivel
    elif nome == "Preto claro":
        nivel = max(64, min(105, round((r + g + b) / 3)))
        r = g = b = nivel

    if r > 225 and g > 225 and b > 225:
        r, g, b = 205, 178, 105
    hex_cor = f"#{r:02x}{g:02x}{b:02x}"
    luminancia = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    texto = "#111827" if luminancia > 0.62 else "#ffffff"
    return hex_cor, texto


def _detectar_variacoes_visuais(imagem, separadores, altura_reduzida):
    """Retorna regiões C1..Cn, posição do badge e sugestão de cor.

    Usa exatamente os mesmos layouts já homologados pelo contador visual, para
    manter quantidade e associação espacial sincronizadas.
    """
    largura, altura = imagem.size
    if largura < 100 or altura < 100 or not altura_reduzida:
        return []
    limites_reduzidos = [0, *separadores, altura_reduzida]
    faixas_reduzidas = [
        (limites_reduzidos[i], limites_reduzidos[i + 1])
        for i in range(len(limites_reduzidos) - 1)
        if limites_reduzidos[i + 1] - limites_reduzidos[i] > 0
    ]
    escala_y = altura / altura_reduzida
    proporcao = largura / altura
    variacoes = []

    if proporcao >= 1.15 and 1 <= len(faixas_reduzidas) <= 20:
        regioes = [
            (indice, 0, int(inicio * escala_y), largura, int(fim * escala_y), [25, 75])
            for indice, (inicio, fim) in enumerate(faixas_reduzidas, start=1)
        ]
    elif proporcao < 1.15 and len(faixas_reduzidas) >= 4:
        inferiores = [fim - inicio for inicio, fim in faixas_reduzidas[1:]]
        mediana = sorted(inferiores)[len(inferiores) // 2]
        primeira = faixas_reduzidas[0][1] - faixas_reduzidas[0][0]
        if not mediana or primeira < mediana * 1.45:
            return []
        regioes = []
        indice = 1
        for inicio_r, fim_r in faixas_reduzidas[1:]:
            inicio, fim = int(inicio_r * escala_y), int(fim_r * escala_y)
            for esq, dire, x in ((0, largura // 2, 25), (largura // 2, largura, 75)):
                regioes.append((indice, esq, inicio, dire, fim, [x]))
                indice += 1
    else:
        return []

    for indice, esq, inicio, dire, fim, marcadores_x in regioes:
        caixa = (esq, inicio, dire, fim)
        estatisticas = _estatisticas_cor_regiao(imagem, caixa)
        nome_base = _classificar_estatisticas_cor(estatisticas)
        nome = _descricao_degrade(estatisticas, nome_base) if estatisticas else ""
        cor_hex, texto_hex = _cor_representativa_regiao(
            imagem, caixa, estatisticas=estatisticas, nome=nome_base
        )
        y = round(((inicio + fim) / 2) / altura * 100, 2)
        variacoes.append({
            "indice": indice, "nome": nome,
            "cor_hex": cor_hex, "texto_hex": texto_hex,
            "caixa": {
                "x1": round(esq / largura * 100, 3),
                "y1": round(inicio / altura * 100, 3),
                "x2": round(dire / largura * 100, 3),
                "y2": round(fim / altura * 100, 3),
            },
            "marcadores": [{"x": x, "y": y} for x in marcadores_x],
        })
    return variacoes if len(variacoes) <= 30 else []


def detectar_variacoes_visuais_imagem(caminho):
    try:
        with Image.open(caminho) as origem:
            imagem = origem.convert("RGB")
            separadores, altura_reduzida = _faixas_separadoras_horizontais(imagem)
            return _detectar_variacoes_visuais(imagem, separadores, altura_reduzida)
    except (OSError, ValueError):
        return []

def detectar_layout_visual_imagem(caminho):
    """Retorna hero (quando houver) e as regiões das variações para a UI."""
    try:
        with Image.open(caminho) as origem:
            imagem = origem.convert("RGB")
            largura, altura = imagem.size
            separadores, altura_reduzida = _faixas_separadoras_horizontais(imagem)
            if not altura_reduzida:
                return {"hero": None, "variacoes": []}
            limites = [0, *separadores, altura_reduzida]
            faixas = [(limites[i], limites[i + 1]) for i in range(len(limites) - 1) if limites[i + 1] > limites[i]]
            hero = None
            if largura / altura < 1.15 and len(faixas) >= 4:
                inferiores = [fim - inicio for inicio, fim in faixas[1:]]
                mediana = sorted(inferiores)[len(inferiores) // 2] if inferiores else 0
                primeira = faixas[0][1] - faixas[0][0]
                if mediana and primeira >= mediana * 1.45:
                    escala_y = altura / altura_reduzida
                    hero_fim = int(faixas[0][1] * escala_y)
                    hero = {"x1": 0.0, "y1": 0.0, "x2": 100.0, "y2": round(hero_fim / altura * 100, 3)}
            return {
                "hero": hero,
                "variacoes": _detectar_variacoes_visuais(
                    imagem, separadores, altura_reduzida
                ),
            }
    except (OSError, ValueError):
        return {"hero": None, "variacoes": []}


def detectar_posicoes_variacoes_imagem(caminho):
    """Compatibilidade: achata os marcadores das variações visuais."""
    marcadores = []
    for variacao in detectar_variacoes_visuais_imagem(caminho):
        for marcador in variacao.get("marcadores", []):
            marcadores.append({
                "indice": variacao["indice"],
                "x": marcador["x"],
                "y": marcador["y"],
            })
    return marcadores


def completar_variacoes_visuais(sugestao, quantidade, nomes_visuais=None):
    """Completa C1..Cn e usa nomes visuais somente quando não há nome por OCR."""
    nomes_visuais = nomes_visuais or []
    variacoes = list(sugestao.get("variacoes", []))
    if quantidade and quantidade > len(variacoes):
        codigos_usados = {(v.get("codigo") or "").strip().upper() for v in variacoes}
        proximo = 1
        while len(variacoes) < quantidade:
            while f"C{proximo}" in codigos_usados:
                proximo += 1
            codigo = f"C{proximo}"
            indice = len(variacoes)
            nome = nomes_visuais[indice] if indice < len(nomes_visuais) else ""
            variacoes.append({"nome": nome, "codigo": codigo})
            codigos_usados.add(codigo)
            proximo += 1
    # Também completa nomes vazios das variações já criadas pelo OCR.
    for indice, variacao in enumerate(variacoes):
        if not (variacao.get("nome") or "").strip() and indice < len(nomes_visuais):
            variacao["nome"] = nomes_visuais[indice]
    sugestao["variacoes"] = variacoes
    return sugestao

def _limpar_linhas(texto):
    return [re.sub(r"\s+", " ", linha).strip() for linha in texto.splitlines() if linha.strip()]


def _nome_arquivo_descritivo(nome_arquivo):
    """Usa nome do arquivo apenas quando ele parece informação humana, não UUID/hash."""
    stem = Path(nome_arquivo or "").stem.strip()
    if not stem:
        return ""

    compacto = re.sub(r"[^A-Za-z0-9]", "", stem)
    grupos = [grupo for grupo in re.split(r"[-_ ]+", stem) if grupo]
    parece_uuid = (
        len(grupos) >= 4
        and len(compacto) >= 20
        and all(re.fullmatch(r"[0-9A-Fa-f]+", grupo) for grupo in grupos)
    )
    parece_hash = len(compacto) >= 24 and bool(re.fullmatch(r"[0-9A-Fa-f]+", compacto))
    if parece_uuid or parece_hash:
        return ""

    return stem.replace("_", " ").strip()


PADRAO_MEDIDA_OPTICA = re.compile(
    r"(?<!\d)\d{2,3}\s*[-–—/]\s*\d{2,3}\s*[-–—/]\s*\d{2,3}(?!\d)"
)


def _normalizar_token_codigo(token):
    """Corrige confusões usuais do OCR apenas em tokens predominantemente numéricos."""
    compacto = re.sub(r"[^A-Z0-9-]", "", token.upper())
    if not compacto or PADRAO_MEDIDA_OPTICA.fullmatch(compacto):
        return ""

    sem_hifen = compacto.replace("-", "")
    quantidade_digitos = sum(caractere.isdigit() for caractere in sem_hifen)
    if quantidade_digitos < 2:
        return ""

    mapa_ocr = str.maketrans({"O": "0", "I": "1", "L": "1"})
    normalizado = sem_hifen.translate(mapa_ocr)
    if re.fullmatch(r"\d{3,8}", normalizado):
        return normalizado
    if re.fullmatch(r"[A-Z]{1,4}\d{2,8}[A-Z]?", normalizado):
        return normalizado
    return ""


def _extrair_codigo_fornecedor(base):
    """Escolhe um identificador de produto sem aceitar medidas ópticas."""
    sem_medidas = PADRAO_MEDIDA_OPTICA.sub(" ", base.upper())
    candidatos = []
    padrao_token = re.compile(
        r"\b(?:[A-Z]{1,4}-?)?[0-9OIL]{3,8}[A-Z]?\b|"
        r"(?<![A-Z0-9])(?:[0-9OIL]\s+){2,7}[0-9OIL](?![A-Z0-9])"
    )
    for ordem, token in enumerate(padrao_token.findall(sem_medidas)):
        # Espaços inseridos entre algarismos pelo OCR não mudam o identificador.
        normalizado = _normalizar_token_codigo(re.sub(r"(?<=\d)\s+(?=[\dOIL])", "", token))
        if not normalizado:
            continue
        somente_numeros = normalizado.isdigit()
        # Catálogos observados usam principalmente 4–6 dígitos. Prefixos
        # alfanuméricos continuam aceitos, mas não superam um código numérico
        # claro encontrado no texto vermelho.
        tamanho_ideal = 4 <= len(normalizado) <= 6
        pontuacao = (3 if somente_numeros else 2) + (2 if tamanho_ideal else 0) - ordem * 0.01
        candidatos.append((pontuacao, normalizado))
    return max(candidatos, default=(0, ""))[1]


def sugerir_dados(texto, nome_arquivo=""):
    base = texto.strip()
    if not base:
        base = _nome_arquivo_descritivo(nome_arquivo)
    linhas = _limpar_linhas(base)

    codigo = _extrair_codigo_fornecedor(base)

    # Prefere a linha que contém o código. Isso evita usar ruído do OCR como modelo.
    linha_modelo = ""
    if codigo:
        codigo_flex = r"\s*".join(map(re.escape, codigo))
        for linha in linhas:
            if re.search(codigo_flex, linha, flags=re.IGNORECASE):
                linha_modelo = linha
                break
    if not linha_modelo:
        linha_modelo = linhas[0] if linhas else base.strip()

    modelo = linha_modelo
    if codigo:
        # OCR confunde frequentemente zero e letra O (ex.: O65 -> 065).
        # Remove o código da descrição de forma tolerante a essa confusão.
        partes_codigo = ["[O0]" if caractere == "0" else re.escape(caractere) for caractere in codigo]
        padrao_codigo = "".join(partes_codigo)
        modelo = re.sub(padrao_codigo, "", modelo, count=1, flags=re.IGNORECASE).strip(" -–—:/")
    modelo = PADRAO_MEDIDA_OPTICA.sub("", modelo).strip(" -–—:/")
    # Se sobrou somente pontuação/números, é mais seguro deixar em branco para revisão.
    if not re.search(r"[A-Za-zÀ-ÿ]", modelo):
        modelo = ""
    modelo = modelo[:100]

    palavras = re.findall(r"[A-Za-zÀ-ÿ]+", base.lower())
    cores = []
    for palavra in palavras:
        if palavra in CORES and palavra not in cores:
            cores.append(palavra.title())

    codigos_cor = []
    for valor in re.findall(r"\bC\s*[0-9IIL]{1,3}\b", base.upper()):
        normalizado = re.sub(r"\s+", "", valor).replace("I", "1").replace("L", "1")
        if normalizado not in codigos_cor:
            codigos_cor.append(normalizado)

    variacoes = []
    total = max(len(cores), len(codigos_cor))
    for indice in range(total):
        variacoes.append({
            "nome": cores[indice] if indice < len(cores) else "",
            "codigo": codigos_cor[indice] if indice < len(codigos_cor) else f"C{indice + 1}",
        })

    return {"codigo_fornecedor": codigo, "modelo": modelo, "variacoes": variacoes}
