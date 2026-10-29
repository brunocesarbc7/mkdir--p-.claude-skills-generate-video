"""Recorta uma grade 3×3 de storyboard em quadros individuais.

Uso:
    python3 recortar_grade.py <grade.png> <pasta_saida> <primeira_cena> <qtd_cenas>

Exemplo (grade 1, cenas 1 a 7):
    python3 recortar_grade.py videos/x/grade_1.png videos/x 1 7
Gera videos/x/quadro_01.png ... quadro_07.png, lendo os painéis da
esquerda para a direita, de cima para baixo. Painéis além de <qtd_cenas>
são ignorados (são os quadros pretos não usados).
"""
import sys

import numpy as np
from PIL import Image

LIMIAR_BORDA = 200      # brilho médio acima disso = linha de borda branca
TAMANHO_MIN = 0.15      # um painel ocupa pelo menos 15% da largura/altura
MARGEM = 2              # pixels descartados em cada lado para tirar o antisserrilhado da borda


def regioes(brilho):
    """Devolve os intervalos (inicio, fim) entre as linhas de borda, incluindo as bordas da imagem."""
    tamanho = len(brilho)
    eh_borda = brilho > LIMIAR_BORDA
    achadas, inicio = [], None
    for i in range(tamanho):
        if not eh_borda[i] and inicio is None:
            inicio = i
        elif eh_borda[i] and inicio is not None:
            achadas.append((inicio, i - 1))
            inicio = None
    if inicio is not None:
        achadas.append((inicio, tamanho - 1))
    achadas = [(a, b) for a, b in achadas if b - a + 1 >= tamanho * TAMANHO_MIN]
    if len(achadas) == 3:
        return achadas, "bordas detectadas"
    # Sem 3 painéis claros (borda fina demais, painel muito claro…): divide em terços iguais.
    terco = tamanho / 3
    return [(round(k * terco), round((k + 1) * terco) - 1) for k in range(3)], "terços iguais"


def main():
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    grade, saida, primeira, qtd = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    if not 1 <= qtd <= 9:
        sys.exit("qtd_cenas deve estar entre 1 e 9")

    img = Image.open(grade).convert("RGB")
    arr = np.asarray(img, dtype=np.float32)
    colunas, metodo_c = regioes(arr.mean(axis=(0, 2)))
    linhas, metodo_l = regioes(arr.mean(axis=(1, 2)))
    print(f"Grade {img.width}x{img.height} — colunas: {colunas} ({metodo_c}); linhas: {linhas} ({metodo_l})")

    for idx in range(qtd):
        y1, y2 = linhas[idx // 3]
        x1, x2 = colunas[idx % 3]
        caixa = (x1 + MARGEM, y1 + MARGEM, x2 + 1 - MARGEM, y2 + 1 - MARGEM)
        caminho = f"{saida}/quadro_{primeira + idx:02d}.png"
        img.crop(caixa).save(caminho)
        print(f"{caminho}: painel {idx + 1}, caixa {caixa}")


if __name__ == "__main__":
    main()
