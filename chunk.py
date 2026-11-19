import os
BASE = os.environ.get("VQQ_BASE", "/home/runner")
import sys, json, collections, subprocess
from pathlib import Path

START, END = int(sys.argv[1]), int(sys.argv[2])
WORK = Path(BASE) / "vqq"
FRAMES = WORK / "frames"
PREVIEW = WORK / "preview"
OUT = Path(BASE) / "out"
for _p in (FRAMES, PREVIEW, OUT):
    _p.mkdir(parents=True, exist_ok=True)
SAMPLES, ESCALA = 15, 100
BLENDER = BASE + "/blender/blender"
TL = json.loads((WORK / "timeline.json").read_text(encoding="utf-8"))

# ---------------- 1) render (CPU) ----------------
if not os.environ.get("SKIP_RENDER"):
    cmd = [BLENDER, "-b", "-noaudio", "--factory-startup", "-P", str(WORK / "blender_scene.py"), "--",
           "--timeline", str(WORK / "timeline.json"), "--out", str(FRAMES),
           "--samples", str(SAMPLES), "--scale", str(ESCALA), "--start", str(START), "--end", str(END)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    cauda = collections.deque(maxlen=60)
    feitos = 0
    for linha in proc.stdout:
        cauda.append(linha.rstrip())
        if linha.startswith("Saved:"):
            feitos += 1
            print("frame %d/%d" % (feitos, END - START + 1), flush=True)
    proc.wait()
    faltam = [i for i in range(START, END + 1) if not (FRAMES / ("f_%04d.png" % i)).exists()]
    if proc.returncode != 0 or len(faltam) > 2:
        print("\n".join(cauda))
        raise RuntimeError("Render falhou (faltam %d frames, código %s)" % (len(faltam), proc.returncode))
    print("Render do bloco OK. Frames faltando:", faltam)

# ---------------- 2) HUD + legendas + vídeo do bloco ----------------
# ============ CÉLULA 7 — MOTOR DO HUD (igual ao seu vídeo de exemplo) ============
# Desenha por cima dos frames do Blender: status, ERA, painéis, legenda pixelada, linha do tempo.
# Dá pra rodar ANTES do render grande: se existir preview, mostra o HUD em cima dos stills.
import bisect, json, math, random, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
try:
    from tqdm.auto import tqdm
except ImportError:                      # só pra não quebrar se faltar tqdm
    def tqdm(it, **k):
        return it

TL = json.loads((WORK / "timeline.json").read_text(encoding="utf-8"))
W, H, FPS = TL["w"], TL["h"], TL["fps"]
SC = TL["scenes"]
CAPS = TL["captions"]
STARTS = [s["start"] for s in SC]

NAVY, BLUE, CYAN = (8, 22, 52), (58, 160, 255), (120, 205, 255)
WHITE, YELLOW, RED, BLACK = (255, 255, 255), (255, 205, 64), (255, 92, 92), (0, 0, 0)
FONT_DIR = Path(BASE + "/fonts")
PIXEL = [FONT_DIR / "PressStart2P-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"]
MONO = [FONT_DIR / "ShareTechMono-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
_FC = {}


def font(kind, size):
    size = int(size)
    if (kind, size) in _FC:
        return _FC[(kind, size)]
    f = None
    for p in (PIXEL if kind == "pixel" else MONO):
        try:
            f = ImageFont.truetype(str(p), size)
            break
        except Exception:
            continue
    if f is None:
        try:
            f = ImageFont.load_default(size)
        except TypeError:
            f = ImageFont.load_default()
    _FC[(kind, size)] = f
    return f


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def fill_a(img, box, color, a):
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(img.width, x1), min(img.height, y1)
    if x1 <= x0 or y1 <= y0:
        return
    reg = img.crop((x0, y0, x1, y1))
    img.paste(Image.blend(reg, Image.new("RGB", reg.size, color), a), (x0, y0))


def box(img, x, y, w, h):
    fill_a(img, (x, y, x + w, y + h), NAVY, 0.80)
    d = ImageDraw.Draw(img)
    d.rectangle((x, y, x + w, y + h), outline=BLUE, width=2)
    d.rectangle((x - 3, y - 3, x + 5, y + 5), fill=BLUE)
    return d


def bar(d, x, y, w, h, frac, color=BLUE):
    d.rectangle((x, y, x + w, y + h), fill=(10, 28, 64), outline=(30, 80, 150))
    fw = int((w - 2) * max(0.0, min(1.0, frac)))
    if fw > 0:
        d.rectangle((x + 1, y + 1, x + 1 + fw, y + h - 1), fill=color)


def fit(d, text, kind, size, maxw):
    while size > 10 and d.textlength(text, font=font(kind, size)) > maxw:
        size -= 1
    return font(kind, size)


PX, PY, PW, PWW = 28, 164, 447, 664
ROWH = {"kv": 30, "toggle": 32, "slider": 44}


def p_rows(img, data, p):
    rows = data["linhas"]
    h = 46 + sum(ROWH[r[0]] for r in rows) + 8
    d = box(img, PX, PY, PW, h)
    f, k = font("mono", 15), ease(p / 0.6)
    d.text((PX + 12, PY + 12), data["titulo"], font=f, fill=CYAN)
    y = PY + 44
    for r in rows:
        if r[0] == "kv":
            d.text((PX + 12, y), r[1], font=f, fill=WHITE)
            d.text((PX + PW - 12, y), r[2], font=f, fill=WHITE, anchor="ra")
        elif r[0] == "toggle":
            on = r[2] == "ON"
            bx = PX + PW - 12 - 52
            d.text((PX + 12, y + 2), r[1], font=f, fill=WHITE)
            d.rectangle((bx, y, bx + 52, y + 22), fill=(18, 72, 150) if on else (16, 32, 60),
                        outline=BLUE if on else (60, 90, 130), width=2)
            d.text((bx + 26, y + 11), r[2], font=font("mono", 13), fill=WHITE if on else (130, 150, 180), anchor="mm")
        else:
            txt = r[3] if len(r) > 3 and r[3] else "%d%%" % round(r[2] * 100 * k)
            d.text((PX + 12, y), r[1], font=f, fill=WHITE)
            d.text((PX + PW - 12, y), txt, font=f, fill=YELLOW if (len(r) > 3 and r[3]) else CYAN, anchor="ra")
            bar(d, PX + 12, y + 24, PW - 24, 8, r[2] * k)
        y += ROWH[r[0]]


def p_patch(img, data, p):
    L = data["linhas"]
    d = box(img, PX, PY, PW, 46 + 26 * len(L) + 8)
    f = font("mono", 15)
    d.text((PX + 12, PY + 12), data["titulo"], font=f, fill=CYAN)
    for i, (s, t) in enumerate(L):
        if p >= 0.25 * i:
            d.text((PX + 12, PY + 44 + 26 * i), s + " " + t, font=f, fill=RED if s == "-" else WHITE)


def p_compare(img, data, p):
    L = data["linhas"]
    h = 46 + sum(30 if r[2] is None else 44 for r in L) + 8
    d = box(img, PX, PY, PW, h)
    f, k = font("mono", 15), ease(p / 0.6)
    d.text((PX + 12, PY + 12), data["titulo"], font=f, fill=CYAN)
    y = PY + 44
    for (lab, val, frac, col) in L:
        d.text((PX + 12, y), lab, font=f, fill=WHITE)
        if frac is None:
            d.text((PX + PW - 12, y), val, font=f, fill=WHITE, anchor="ra")
            y += 30
        else:
            c = YELLOW if col == "yellow" else BLUE
            d.text((PX + PW - 12, y), val, font=f, fill=c, anchor="ra")
            bar(d, PX + 12, y + 24, PW - 24, 8, frac * k, c)
            y += 44


def p_dica(img, data, p):
    d = box(img, PX, PY, PWW, 118)
    f = font("mono", 15)
    d.text((PX + 14, PY + 14), "O QUE ELE VAI VIRAR???", font=f, fill=CYAN)
    d.text((PX + PWW - 14, PY + 14), "DICA %d/3" % data["n"], font=f, fill=YELLOW, anchor="ra")
    for i in range(3):
        x = PX + 14 + i * 30
        if i < data["n"]:
            d.rectangle((x, PY + 46, x + 22, PY + 68), fill=BLUE, outline=CYAN)
        else:
            d.rectangle((x, PY + 46, x + 22, PY + 68), outline=BLUE, width=2)
    d.text((PX + 14, PY + 86), data["texto"], font=font("mono", 17), fill=WHITE)


def p_chat(img, data, p):
    L = data["linhas"]
    d = box(img, PX, PY, PWW, 46 + 26 * len(L) + 8)
    f = font("mono", 15)
    d.text((PX + 12, PY + 12), data["titulo"], font=f, fill=CYAN)
    d.text((PX + PWW - 14, PY + 12), "x", font=f, fill=(130, 150, 180), anchor="ra")
    for i, (c, t) in enumerate(L):
        if p >= 0.7 * i:
            d.text((PX + 14, PY + 44 + 26 * i), t, font=f, fill=RED if c == "red" else WHITE)


def p_banner(img, data, p):
    x, y, w, h = 60, 160, 600, 140
    d = box(img, x, y, w, h)
    d.text((W // 2, y + 24), "NOVA BUILD REGISTRADA", font=font("mono", 14), fill=CYAN, anchor="mm")
    d.text((W // 2, y + 70), data["nome"], font=fit(d, data["nome"], "pixel", 30, w - 40), fill=WHITE, anchor="mm")
    d.text((W // 2, y + 114), data["sub"], font=font("mono", 14), fill=YELLOW, anchor="mm")


PANELS = {"build": p_rows, "status": p_rows, "patch": p_patch, "compare": p_compare,
          "dica": p_dica, "chat": p_chat, "banner": p_banner}


def draw_status(img, sc, prev, dt):
    d = box(img, 18, 18, 308, 62)
    k = ease(dt / 0.7)
    hp = prev["hp"] + (sc["hp"] - prev["hp"]) * k
    arm = prev["arm"] + (sc["arm"] - prev["arm"]) * k
    d.text((26, 23), sc["nome"], font=fit(d, sc["nome"], "mono", 17, 210), fill=WHITE)
    d.text((316, 23), "LV." + sc["lv"], font=font("mono", 17), fill=YELLOW, anchor="ra")
    d.text((26, 46), "HP", font=font("mono", 11), fill=CYAN)
    bar(d, 62, 45, 256, 11, hp)
    d.text((26, 62), "ARM", font=font("mono", 11), fill=CYAN)
    bar(d, 62, 61, 256, 11, arm, (110, 205, 255))
    d = box(img, 395, 18, 308, 31)
    d.text((549, 34), "ERA: " + sc["era"], font=font("mono", 15), fill=WHITE, anchor="mm")


def draw_timeline(img, sc, prev, dt):
    if sc["tick"] is None:
        return
    d = ImageDraw.Draw(img)
    ticks = TL["ticks"]
    xs = [72 + (648 - 72) * i / (len(ticks) - 1) for i in range(len(ticks))]
    y, cur = 1017, sc["tick"]
    pt = prev["tick"] if prev["tick"] is not None else cur
    px = xs[pt] + (xs[cur] - xs[pt]) * ease(dt / 0.8)
    label = sc["ano"]
    d.text((W // 2, 984), label, font=font("mono", 15), fill=CYAN, anchor="mm")
    d.line((xs[0], y, xs[-1], y), fill=(30, 70, 140), width=4)
    d.line((xs[0], y, px, y), fill=BLUE, width=4)
    for i, x in enumerate(xs):
        if i < cur:
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=BLUE, outline=CYAN, width=2)
        elif i == cur:
            r = 13 + int(2 * math.sin(dt * 6))
            d.ellipse((x - r - 4, y - r - 4, x + r + 4, y + r + 4), fill=(40, 110, 190))
            d.ellipse((x - r, y - r, x + r, y + r), fill=(130, 215, 255))
        else:
            d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=NAVY, outline=BLUE, width=2)
            d.text((x, y), "?", font=font("mono", 13), fill=WHITE, anchor="mm")
        d.text((x, 1042), ticks[i], font=font("mono", 11), fill=CYAN, anchor="mm")


def draw_dots(img, t):
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for _ in range(26):
        x0, y0, sp, ph, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(12, 40), rnd.uniform(0, 6), rnd.choice((2, 3, 4))
        x = (x0 + 22 * math.sin(t * 0.7 + ph)) % W
        y = (y0 + t * sp) % H
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255))


def draw_caption(img, cap, t):
    d = ImageDraw.Draw(img)
    txt = " ".join(w.upper() for w, _ in cap["palavras"])
    f = fit(d, txt, "pixel", 40, 660)
    sp = d.textlength(" ", font=f)
    x = (W - d.textlength(txt, font=f)) / 2
    y = 832 - 8 * (1 - ease((t - cap["t0"]) / 0.10))
    for w, hl in cap["palavras"]:
        wu = w.upper()
        d.text((x, y), wu, font=f, fill=YELLOW if hl else WHITE, anchor="lm", stroke_width=5, stroke_fill=BLACK)
        x += d.textlength(wu, font=f) + sp


def draw_sticker(img, st, p):
    kind, _, _, text, cx, cy, rot = st
    d = ImageDraw.Draw(img)
    s = ease(p / 0.2)
    if kind == "big":
        size = max(12, int(52 * (0.6 + 0.4 * s)))
        d.text((cx, cy), text, font=fit(d, text, "pixel", size, 660), fill=YELLOW, anchor="mm",
               stroke_width=6, stroke_fill=BLACK)
    else:
        f = font("pixel", 22)
        tw = int(d.textlength(text, font=f)) + 30
        tag = Image.new("RGBA", (tw, 44), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag)
        td.rectangle((0, 0, tw - 1, 43), fill=YELLOW + (255,), outline=(20, 20, 20, 255), width=3)
        td.text((tw // 2, 22), text, font=f, fill=(20, 20, 20, 255), anchor="mm")
        tag = tag.rotate(rot, expand=True, resample=Image.BICUBIC)
        img.paste(tag, (int(cx - tag.width / 2), int(cy - tag.height / 2)), tag)


def compose_frame(bg, f):
    """f = índice do frame (0 = primeiro). bg = imagem do Blender."""
    t = f / FPS
    img = bg.convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    si = max(0, bisect.bisect_right(STARTS, t + 1e-6) - 1)
    sc = SC[si]
    prev = SC[si - 1] if si > 0 else sc
    dur = max(1e-3, sc["end"] - sc["start"])
    dt = t - sc["start"]
    frac = dt / dur
    draw_dots(img, t)
    draw_status(img, sc, prev, dt)
    for (f0, f1, kind, data) in sc["hud"]:
        if f0 <= frac < f1:
            local = (frac - f0) * dur
            a = max(0.0, min(1.0, local / 0.18, (f1 - frac) * dur / 0.12))
            dd = dict(data, nome=sc["nome"])
            if a >= 0.98:
                PANELS[kind](img, dd, local)
            else:
                tmp = img.copy()
                PANELS[kind](tmp, dd, local)
                img = Image.blend(img, tmp, a)
    draw_timeline(img, sc, prev, dt)
    for st in sc["stickers"]:
        if st[1] <= frac < st[2]:
            draw_sticker(img, st, (frac - st[1]) * dur)
    for cap in CAPS:
        if cap["t0"] <= t < cap["t1"]:
            draw_caption(img, cap, t)
            break
    if si > 0 and dt < 0.22:                                   # flash branco na troca de build
        img = Image.blend(img, Image.new("RGB", img.size, WHITE), 0.55 * (1 - dt / 0.22))
    return img


def hud_preview():
    """mostra o HUD em cima dos stills do preview (ou de fundos de teste, se ainda não rodou o preview)"""
    pj = PREVIEW / "preview.json"
    tempos = json.loads(pj.read_text())["tempos"] if pj.exists() else [round(s["start"] + 0.55 * (s["end"] - s["start"]), 2) for s in SC]
    tiles = []
    for k, t in enumerate(tempos):
        p = PREVIEW / ("p_%d.png" % k)
        if p.exists():
            bg = Image.open(p).convert("RGB")
        else:
            bg = Image.new("RGB", (W, H), (30, 70, 40))
        tiles.append(compose_frame(bg, int(t * FPS)).resize((W // 2, H // 2), Image.LANCZOS))
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W // 2, rows * H // 2))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * W // 2, (i // cols) * H // 2))
    out = WORK / "hud_preview.png"
    sheet.save(out)
    try:
        from IPython.display import display
        display(sheet.resize((sheet.width * 2 // 3, sheet.height * 2 // 3)))
    except Exception:
        pass
    return out




# ============ CÉLULA 8 — HUD + LEGENDAS + ÁUDIO → VÍDEO FINAL (com barra de progresso) ============
import subprocess
from pathlib import Path
from PIL import Image
try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(it, **k):
        return it

SAIDA = WORK / "vqq_rinoceronte.mp4"
FRAME_INICIAL, FRAME_FINAL = 1, None        # para testar só um trecho: ex. 1 e 150
PERMITIR_FALTANDO = False                   # True = usa o frame anterior onde faltar (só pra teste)


def compor_video(frames_dir=FRAMES, out=SAIDA, audio=None, f0=FRAME_INICIAL, f1=FRAME_FINAL):
    n = TL["n_frames"]
    f1 = f1 or n
    audio = audio if audio is not None else globals().get("AUDIO")
    faltando = [i for i in range(f0, f1 + 1) if not (Path(frames_dir) / ("f_%04d.png" % i)).exists()]
    if faltando and not PERMITIR_FALTANDO:
        raise RuntimeError("Faltam %d frames (primeiro: %d). Rode a célula de render de novo: ela continua de onde parou."
                           % (len(faltando), faltando[0]))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-i", str(audio), "-af", "apad", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    cmd += ["-c:a", "aac", "-b:a", "192k"] if audio else ["-an"]
    cmd += [str(out)]
    log = open(str(WORK / "ffmpeg.log"), "w")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
    last = None
    try:
        for i in tqdm(range(f0, f1 + 1), desc="HUD + vídeo", unit="frame"):
            p = Path(frames_dir) / ("f_%04d.png" % i)
            if p.exists():
                last = Image.open(p).convert("RGB")
            elif last is None:
                last = Image.new("RGB", (W, H), (20, 40, 80))
            proc.stdin.write(compose_frame(last, i - 1).tobytes())
    finally:
        proc.stdin.close()
        rc = proc.wait()
        log.close()
    if rc != 0:
        raise RuntimeError("ffmpeg falhou:\n" + Path(WORK / "ffmpeg.log").read_text()[-800:])
    return out


if False:
    saida = compor_video()
    print("Vídeo pronto:", saida)


PERMITIR_FALTANDO = True      # no máximo 2 frames repetidos (já checado acima)
seg = OUT / ("seg_%04d.mp4" % START)
compor_video(frames_dir=FRAMES, out=seg, audio=None, f0=START, f1=END)
print("Bloco pronto:", seg, round(seg.stat().st_size / 1e6, 1), "MB")
