"""
Gera uma imagem holográfica (holograma digital) a partir de uma foto.

Saídas:
  rainbow_<nome>.png     -> arco-íris holográfico (vista direta)
  gabor_<nome>.png       -> franjas de Gabor (reconstrói a foto com rolagem
                            na tela + óculos vermelho/verde)
  gabor_anaglifo_<nome>.png -> versão anaglifo, 3D imediato

Uso:
  python holo.py foto.jpg
  python holo.py foto.jpg --size 1200 --orders 3 --offset 180 --tilt 0.15 --out-dir saida
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image


# ---------------------------------------------------------------- utilidades
def load_gray(path, size):
    """Carrega a foto em tons de cinza, proporção preservada."""
    img = Image.open(path).convert("L")
    img.thumbnail((size, size), Image.LANCZOS)
    return np.asarray(img, dtype=np.float64) / 255.0


def gaussian_blur(a, sigma):
    """Suaviza com janela gaussiana separável (sem SciPy/OpenCV)."""
    if sigma <= 0:
        return a
    r = max(1, int(round(3 * sigma)))
    x = np.arange(-r, r + 1)
    k = np.exp(-(x ** 2) / (2 * sigma ** 2))
    k /= k.sum()
    for axis in range(a.ndim):
        a = np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), axis, a)
    return a


def fft2(a):
    """FFT 2D centrada, normalizada pela raiz do número de amostras."""
    return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(a))) / np.sqrt(a.size)


def ifft2(a):
    return np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(a))) * np.sqrt(a.size)


def save(arr, path):
    arr = np.clip(arr, 0, 1)
    Image.fromarray((arr * 255.0).astype(np.uint8)).save(path)
    print("gravado:", path)


# ------------------------------------------------- 1) holograma arco-íris
def rainbow_hologram(gray, orders=3, offset=160.0, tilt=0.12):
    """
    Cada comprimento de onda (R, G, B) reconstrói a imagem numa ordem de
    difração diferente e com distância focal diferente, então as reconstruções
    se separam no espaço como num holograma real. O tilt é o que produz o
    efeito visível a olho nu ao girar ou inclinar o holograma.
    """
    h, w = gray.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    A = np.abs(fft2(gray))                 # só amplitude: frente de onda plana

    rgb = []
    for i in range(3):
        m = orders - i                     # ordem de difração decrescente
        f = offset * m                     # foco maior para ordens maiores
        phase = -np.pi * f * (fx ** 2 + fy ** 2) * 4.0
        phase += 2 * np.pi * tilt * (i + 1) * fx   # inclinação dependente da cor
        U = np.abs(ifft2(A * np.exp(1j * phase)).real)
        rgb.append(gaussian_blur(U, 0.8))

    rgb = [c / (c.max() + 1e-9) for c in rgb]
    img = np.power(np.stack(rgb, axis=-1), 0.8)
    return 0.15 + 0.85 * img               # fundo levemente acinzentado


# ------------------------------------------------- 2) holograma de Gabor
def gabor_hologram(gray, period=9.0, theta=np.pi / 6):
    """
    Interferência da imagem com uma portadora plana inclinada:
        H = 1 + a*cos(2*pi*(kx*x + ky*y)) + a*sqrt(I)*cos(...)
    Rolando a imagem na tela, a franja se desloca e o olho/óculos separa o
    termo +1, reconstruindo a fotografia em relevo.
    """
    h, w = gray.shape
    a = 0.75                               # profundidade da modulação
    y, x = np.mgrid[0:h, 0:w].astype(float)
    kx, ky = np.cos(theta) / period, np.sin(theta) / period
    carrier = 2 * np.pi * (kx * x + ky * y)

    amp = gaussian_blur(np.sqrt(np.clip(gray, 0, 1)), 0.6)
    H = 1.0 + a * np.cos(carrier) + a * amp * np.cos(carrier)
    H -= H.min()
    H /= H.max() + 1e-9
    return np.power(H, 1.6)                # aumenta o contraste das franjas


def gabor_anaglyph(gray, period, shift=12):
    """Canal vermelho com a franja deslocada -> profundidade imediata."""
    base = gabor_hologram(gray, period)
    return np.stack([np.roll(base, shift, axis=1), base, base], axis=-1)


# --------------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(description="Holograma digital a partir de uma foto.")
    p.add_argument("foto", help="arquivo da foto de entrada")
    p.add_argument("--size", type=int, default=1000, help="lado máximo em pixels")
    p.add_argument("--orders", type=int, default=3, help="ordens de difração do arco-íris")
    p.add_argument("--offset", type=float, default=160.0, help="separação entre planos")
    p.add_argument("--tilt", type=float, default=0.12, help="inclinação da onda (efeito ao girar)")
    p.add_argument("--period", type=float, default=9.0, help="período da franja de Gabor")
    p.add_argument("--out-dir", default="holo_out", help="pasta de saída")
    args = p.parse_args()

    if not os.path.isfile(args.foto):
        print("Foto não encontrada:", args.foto, file=sys.stderr)
        return 1

    os.makedirs(args.out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.foto))[0]
    gray = load_gray(args.foto, args.size)
    print("Entrada:", args.foto, gray.shape)

    save(rainbow_hologram(gray, args.orders, args.offset, args.tilt),
         os.path.join(args.out_dir, "rainbow_%s.png" % stem))
    save(gabor_hologram(gray, args.period),
         os.path.join(args.out_dir, "gabor_%s.png" % stem))
    save(gabor_anaglyph(gray, args.period),
         os.path.join(args.out_dir, "gabor_anaglifo_%s.png" % stem))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
