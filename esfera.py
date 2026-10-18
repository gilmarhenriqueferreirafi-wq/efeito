# -*- coding: utf-8 -*-
"""
Esferas 3D flutuantes no terminal, corpo inteiro em bloco colorido.
Nao instala nada: usa ctypes para a API do console do Windows.

Uso:
    python esfera.py                       2 esferas, cor solida
    python esfera.py 4 --cores "#1278ff"
    python esfera.py 1 --cor-cheia         cor chapada, sem sombra
    python esfera.py 3 --metaball          fusao entre elas
    python esfera.py 2 --fundo chuva
    Ctrl+C para sair
"""
import ctypes
import math
import sys
import time

try:
    import msvcrt
except ImportError:
    msvcrt = None

# ------------------------------------------------- console do Windows
kernel32 = ctypes.windll.kernel32
handle = kernel32.GetStdHandle(-11)


class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]


class SMALL_RECT(ctypes.Structure):
    _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short),
                ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]


class CSBI(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.c_int),
                ("dwCursorPositionAttribute", ctypes.c_short),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD)]


class CURSOR_INFO(ctypes.Structure):
    _fields_ = [("bVisible", ctypes.c_int), ("dwSize", COORD)]


def enable_vt():
    """Liga o suporte a cores ANSI no console do Windows 10+."""
    mode = ctypes.c_uint32()
    if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)


def hide_cursor():
    kernel32.SetConsoleCursorInfo(handle, ctypes.byref(CURSOR_INFO(0, COORD(0, 0))))


def show_cursor():
    kernel32.SetConsoleCursorInfo(handle, ctypes.byref(CURSOR_INFO(1, COORD(1, 1))))


def screen_size():
    info = CSBI()
    info.dwSize = ctypes.sizeof(CSBI)
    if not kernel32.GetConsoleScreenBufferInfo(handle, ctypes.byref(info)):
        return 120, 40
    return info.srWindow.Right + 1, info.srWindow.Bottom + 1


# ------------------------------------------------- tamanho real da janela
from ctypes import wintypes

STD_INPUT_HANDLE = -10
ENABLE_WINDOW_INPUT = 0x0008


def query_term_size():
    """Pergunta o tamanho da janela ao terminal (CSI 18 t -> CSI 8 ; linhas ; colunas t)."""
    if msvcrt is None:
        return None
    hin = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    old = ctypes.c_uint32()
    if not kernel32.GetConsoleMode(hin, ctypes.byref(old)):
        return None
    kernel32.SetConsoleMode(hin, ENABLE_WINDOW_INPUT)
    try:
        sys.stdout.write("\x1b[18t")
        sys.stdout.flush()
        chunk = ""
        while len(chunk) < 32:
            b = msvcrt.read()
            if not b:
                break
            chunk += bytes([b]).decode("latin-1")
            if chunk.endswith("t"):
                break
        body = chunk.lstrip("\x1b[").rstrip("t")
        parts = body.split(";")
        if len(parts) >= 2:
            return max(40, int(parts[1])), max(12, int(parts[0]))
    except Exception:
        pass
    finally:
        kernel32.SetConsoleMode(hin, old.value)
    return None


def window_size():
    """Tamanho da janela em caracteres, medindo o pixel da janela e o da fonte."""
    try:
        u = ctypes.windll.user32
        cw = u.GetSystemMetrics(16) or 8
        ch = u.GetSystemMetrics(17) or 16
        r = wintypes.RECT()
        u.GetWindowRect(u.GetForegroundWindow(), ctypes.byref(r))
        if r.right > r.left and r.bottom > r.top:
            return ((r.right - r.left) // max(1, cw),
                    (r.bottom - r.top) // max(1, ch) - 3)
    except Exception:
        pass
    return None


def pick_size():
    W, H = query_term_size() or screen_size()
    if W < 60 or H < 24:
        w = window_size()
        if w:
            W, H = max(W, w[0]), max(H, w[1])
    return max(40, W), max(20, H)


# ------------------------------------------------- geometria
SOLID = "\u2588"           # bloco cheio: a esfera e feita disto, nao de simbolos
RAINBOW = "\u2584\u2580"   # meia-celula, usada so no modo chuva


def sphere_field(cx, cy, radius, light, aspect=2.2):
    """Devolve (brilho, normal_z) por celula. aspect compensa caractere alto."""
    out = {}
    lx, ly, lz = light
    n = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / n, ly / n, lz / n

    for py in range(int(cy - radius) - 1, int(cy + radius) + 2):
        dy = (py - cy) / radius
        if abs(dy) > 1:
            continue
        for px in range(int(cx - radius * aspect) - 1, int(cx + radius * aspect) + 2):
            dx = (px - cx) / (radius * aspect)
            d2 = dx * dx + dy * dy
            if d2 > 1:
                continue
            nz = math.sqrt(1 - d2)
            diff = max(0.0, dx * lx + (-dy) * ly + nz * lz)
            bright = 0.25 + 0.75 * diff + 0.9 * diff ** 24
            out[(px, py)] = (bright, nz)
    return out


def metaball_field(blobs, aspect=2.2):
    """Potencial somado: acima do limiar as esferas se fundem."""
    xs = [b[0] for b in blobs]
    ys = [b[1] for b in blobs]
    rs = [b[2] for b in blobs]
    pad = max(rs) * 1.6
    field = {}
    for py in range(int(min(ys) - pad), int(max(ys) + pad) + 2):
        for px in range(int(min(xs) - pad * aspect), int(max(xs) + pad * aspect) + 2):
            s = gx = gy = 0.0
            for (cx, cy, r) in blobs:
                dx = (px - cx) / aspect
                dy = py - cy
                d2 = dx * dx + dy * dy + 1e-6
                s += (r * r) / d2
                gx += -2 * (r * r) * dx / (d2 * d2)
                gy += -2 * (r * r) * dy / (d2 * d2)
            if s > 1.0:
                g = math.hypot(gx, gy) + 1e-6
                diff = max(0.0, (gx / g) * -0.5 + (gy / g) * -0.6 + 0.62)
                field[(px, py)] = (0.2 + 0.8 * diff, min(1.0, (s - 1.0) * 0.6))
    return field


# ------------------------------------------------- cores
DEFAULT_PALETTE = [
    (18, 120, 255),    # azul eletrico
    (255, 60, 170),    # magenta
    (60, 240, 200),    # ciano
    (255, 190, 40),    # ambar
    (160, 90, 255),    # violeta
]


def parse_hex(spec):
    """
    '#fb2b2b,#2b33fb' -> [(251,43,43), (43,51,251)]
    Aceita com ou sem #, forma curta (#f00) e separador , ou ;
    """
    out = []
    for tok in spec.replace(";", ",").split(","):
        tok = tok.strip().lstrip("#")
        if not tok:
            continue
        if len(tok) == 3:
            tok = "".join(c * 2 for c in tok)
        if len(tok) != 6 or any(c not in "0123456789abcdefABCDEF" for c in tok):
            raise ValueError("cor invalida: %r  (use #rrggbb)" % tok)
        out.append(tuple(int(tok[i:i + 2], 16) for i in (0, 2, 4)))
    if not out:
        raise ValueError("nenhuma cor informada")
    return out


PALETTE = DEFAULT_PALETTE[:]
SHADE = True
BG_MODE = "gradiente"


def rgb(c):
    return "\x1b[38;2;%d;%d;%dm" % (min(255, c[0]), min(255, c[1]), min(255, c[2]))


def bgrgb(c):
    return "\x1b[48;2;%d;%d;%dm" % (min(255, c[0]), min(255, c[1]), min(255, c[2]))


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


# ------------------------------------------------- fundo
def bg_color(x, y, W, H, t):
    if BG_MODE != "gradiente":
        return (0, 0, 0)
    d = math.hypot((x - W * 0.5) / max(1.0, W * 0.55),
                   (y - H * 0.5) / max(1.0, H * 0.75))
    pulse = 0.75 + 0.25 * math.sin(t * 0.8)
    base = (10 + 34 * max(0.0, 1.0 - d)) * pulse
    return (int(base * 0.35), int(base * 0.5), int(base * 1.15))


def rain_cell(x, y, H, t):
    col = (x * 7919 + 11) % 97
    head = (t * (9.0 + col % 11) + col * 13.0) % (H * 1.8)
    d = head - y
    if d < 0 or d > 22:
        return None
    if d < 1.2:
        return (190, 255, 205)
    fade = 1.0 - d / 22.0
    return (int(20 * fade), int(200 * fade + 30), int(70 * fade))


# ------------------------------------------------- renderizacao
def build_frame(t, W, H, n_balls, metaball_mode):
    grid = [[" "] * W for _ in range(H)]
    fg = [[None] * W for _ in range(H)]
    bg = [[(0, 0, 0)] * W for _ in range(H)]

    centers = []
    for i in range(n_balls):
        ph = i * (2 * math.pi / n_balls)
        cx = W / 2 + (W * 0.22) * math.sin(t * 0.7 + ph)
        cy = H / 2 + (H * 0.26) * math.sin(t * 1.1 + ph * 1.7)
        rad = min(W, H) * 0.16 * (1 + 0.12 * math.sin(t * 1.9 + ph))
        centers.append((cx, cy, rad))

    if BG_MODE == "chuva":
        for y in range(H):
            for x in range(W):
                c = rain_cell(x, y, H, t)
                if c:
                    grid[y][x] = RAINBOW[y % 2]
                    fg[y][x] = c
    elif BG_MODE == "gradiente":
        for y in range(H):
            row = bg[y]
            for x in range(W):
                row[x] = bg_color(x, y, W, H, t)

    if metaball_mode:
        field = metaball_field([(c[0], c[1], c[2] * 0.9) for c in centers])
        for (px, py), (lum, _) in field.items():
            if not (0 <= py < H and 0 <= px < W):
                continue
            ds = [math.hypot(px - c[0], (py - c[1]) * 2.2) / (c[2] + 1e-6)
                  for c in centers]
            order = sorted(range(len(ds)), key=lambda k: ds[k])
            a, b = order[0], order[1]
            ca = PALETTE[a % len(PALETTE)]
            cb = PALETTE[b % len(PALETTE)]
            tint = mix(ca, cb, ds[b] / (ds[a] + ds[b] + 1e-6))
            grid[py][px] = SOLID
            fg[py][px] = tint
            bg[py][px] = mix(tint, (0, 0, 0), 0.72)
    else:
        light = (math.sin(t * 0.6) * 0.6 - 0.3, -0.7, 0.8)
        for i, (cx, cy, rad) in enumerate(centers):
            cy += 1.6 * math.sin(t * 1.4 + i)
            tint = PALETTE[i % len(PALETTE)]
            for (px, py), (lum, nz) in sphere_field(cx, cy, rad, light).items():
                if not (0 <= py < H and 0 <= px < W):
                    continue
                lum = 1.0 if not SHADE else min(1.15, 0.55 + 0.60 * lum)
                grid[py][px] = SOLID
                fg[py][px] = mix((0, 0, 0), tint, lum)
                bg[py][px] = mix(tint, (0, 0, 0), 0.78)
    return grid, fg, bg


def draw(grid, fg, bg, W, H):
    """Sem newline nenhum: o cursor anda so por posicionamento absoluto."""
    buf = []
    lf = lb = object()
    for y in range(H):
        row, frow, brow = grid[y], fg[y], bg[y]
        for x in range(W):
            b = brow[x]
            if b != lb:
                buf.append(bgrgb(b))
                lb = b
            ch = row[x]
            if ch == " ":
                if lf is not None:
                    buf.append("\x1b[39m")
                    lf = None
                buf.append(" ")
                continue
            f = frow[x]
            if f != lf:
                buf.append(rgb(f))
                lf = f
            buf.append(ch)
        if y != H - 1:
            buf.append("\x1b[%d;1H" % (y + 2))
    sys.stdout.write("".join(buf))
    sys.stdout.flush()


# ------------------------------------------------- execucao
def run(n_balls, metaball_mode, palette, banner_out=True):
    global PALETTE
    PALETTE = palette

    enable_vt()
    hide_cursor()

    W, H = pick_size()

    if banner_out:
        sys.stdout.write("\x1b[2J\x1b[H\x1b[0mesferas: %d | cores: %s | %s | fundo: %s\x1b[K"
                         % (n_balls,
                            " ".join("#%02x%02x%02x" % c for c in palette),
                            "metaball" if metaball_mode else
                            ("cor cheia" if not SHADE else "cor solida"),
                            BG_MODE))
        sys.stdout.flush()
        time.sleep(0.9)

    OFF = 1                                   # linha do banner, fora da area de desenho
    H = max(10, H - OFF)

    t0 = time.time()
    try:
        while True:
            grid, fg, bg = build_frame(time.time() - t0, W, H, n_balls, metaball_mode)
            sys.stdout.write("\x1b[%d;1H" % (OFF + 1))
            draw(grid, fg, bg, W, H)
            time.sleep(1 / 30)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\x1b[0m\x1b[2J\x1b[H")
        kernel32.SetConsoleCursorPosition(handle, COORD(0, 0))
        show_cursor()
        print("fim.")
    return 0


# ------------------------------------------------- linha de comando
USAGE = """uso: python esfera.py [numero] [--cores LISTA] [--metaball]
       -c / --cores LISTA   cores em #rrggbb separadas por , ou ;
       --cor-cheia          cor 100%% chapada, sem sombra
       --fundo MODO         gradiente (padrao), preto ou chuva
       numero: 1 a 8 esferas (padrao 2). Ctrl+C para sair."""

MENU = [
    ("1", "azul",       1, False, ["#1278ff"]),
    ("2", "vermelho",   1, False, ["#ff2b2b"]),
    ("3", "duas cores", 2, False, ["#ff2d2d", "#2df0ff"]),
    ("4", "fusao",      3, True,  ["#1278ff", "#ff3caa", "#3cf0c8"]),
    ("5", "cor cheia",  1, False, ["#ffbe28"]),
    ("6", "chuva",      2, False, ["#00ff66"]),
    ("7", "suas cores", 2, False, None),
]


def menu():
    global SHADE, BG_MODE
    print("efeitos:")
    for k, nome, _, _, _ in MENU:
        print("  %s - %s" % (k, nome))
    escolha = input("opcao: ").strip()
    alvo = {k: v for k, v in MENU}.get(escolha)
    if alvo is None:
        print("opcao invalida:", escolha)
        return 1
    _, _, n, meta, cores = alvo
    if cores is None:
        try:
            cores = parse_hex(input("cores (ex: #ff0000,#00ff00): ").strip())
        except ValueError as e:
            print("erro nas cores:", e)
            return 1
    SHADE = escolha != "5"
    BG_MODE = "chuva" if escolha == "6" else "gradiente"
    return run(n, meta, cores)


def main():
    global SHADE, BG_MODE

    if len(sys.argv) == 1:
        return menu()

    n_balls = 2
    metaball_mode = False
    palette = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("-h", "--ajuda", "/?"):
            print(USAGE)
            return 0
        elif a == "--metaball":
            metaball_mode = True
        elif a == "--cor-cheia":
            SHADE = False
        elif a == "--fundo":
            i += 1
            if i >= len(args) or args[i] not in ("gradiente", "preto", "chuva"):
                print("fundo invalido (use: gradiente, preto, chuva)")
                return 1
            BG_MODE = args[i]
        elif a in ("--cores", "-c"):
            i += 1
            if i >= len(args):
                print("falta a lista de cores depois de", a)
                return 1
            try:
                palette = parse_hex(args[i])
            except ValueError as e:
                print("erro nas cores:", e)
                return 1
        elif "#" in a or (all(c in "0123456789abcdefABCDEF,;# \t" for c in a)
                          and any(c in "0123456789abcdefABCDEF" for c in a)
                          and not a.isdigit()):
            try:
                palette = parse_hex(a)
            except ValueError as e:
                print("erro nas cores:", e)
                return 1
        elif a.isdigit():
            n_balls = max(1, min(8, int(a)))
        else:
            print("argumento ignorado:", a)
        i += 1

    if palette is None:
        palette = DEFAULT_PALETTE[:max(1, n_balls)]

    return run(n_balls, metaball_mode, palette)


if __name__ == "__main__":
    sys.exit(main())
