import os
BASE = os.environ.get("VQQ_BASE", "/home/runner")
import glob, shutil
# ============ CÉLULA 2 — ROTEIRO + CONFIGURAÇÃO ============
# Mude só o que estiver nesta seção "AJUSTES". O resto pode deixar como está.
import json
from pathlib import Path

# ---------------- AJUSTES ----------------
FPS = 24                 # 30 = mais fluido | 24 = renderiza mais rápido (20% menos frames)
W, H = 720, 1280         # vertical 9:16, igual ao seu vídeo de exemplo
SAMPLES, ESCALA = 15, 100   # qualidade fixa (normal)
PELE_CM = 5              # fonte: rinocerontes têm pele de 1,5 a 5 cm de espessura
# -----------------------------------------

# Tudo é salvo no SEU Google Drive (pasta "vqq_rinoceronte"): frames, timeline e o vídeo final.
# Na primeira vez o Colab vai pedir pra você autorizar o acesso ao Drive.
WORK = Path(BASE) / "vqq"
FRAMES = WORK / "frames"
PREVIEW = WORK / "preview"
for p in (WORK, FRAMES, PREVIEW):
    p.mkdir(parents=True, exist_ok=True)

# Câmera: cada "beat" = (fração da cena, alvo, distância, azimute°, elevação°, deslocamento_vertical)
# alvos: center, head, flank (lado do corpo), horn (chifre)
CAM_HOOK = [(0.0, "pair", 4.6, 10, 9, 0.12), (1.0, "pair", 3.9, 18, 8, 0.10)]
CAM_S1 = [(0.0, "center", 3.4, 14, 8, 0.14), (0.5, "head", 1.5, 28, 8, 0.05), (1.0, "center", 3.2, 10, 8, 0.14)]
CAM_S2 = [(0.0, "center", 3.4, 14, 8, 0.14), (0.55, "center", 2.2, 0, 6, 0.12), (1.0, "center", 3.4, 16, 8, 0.14)]
CAM_S3 = [(0.0, "center", 3.4, 14, 8, 0.14), (0.6, "horn", 1.3, 30, 10, 0.0), (1.0, "center", 3.2, 12, 8, 0.14)]
CAM_S4 = [(0.0, "center", 3.5, 14, 8, 0.14), (0.20, "flank", 1.15, 0, 4, 0.0), (0.50, "flank", 0.95, -6, 6, 0.05),
          (0.62, "center", 3.2, 14, 8, 0.14), (0.80, "horn", 1.2, 32, 10, 0.0), (1.0, "head", 1.9, 25, 8, 0.05)]
CAM_S5 = [(0.0, "center", 3.0, 20, 6, 0.14), (1.0, "center", 4.2, 60, 10, 0.18)]

# Marque com *asteriscos* o que deve aparecer em AMARELO na legenda.
# (fala = exatamente o texto que você vai colar no ElevenLabs, sem os asteriscos)
SCENES = [
    dict(id="hook", criatura="hyrachyus", extra="jacare", cenario="savana", era="???", nome="??????", lv="??", hp=0.0, arm=0.0,
         tick=None, ano="",
         fala="Esse *porco* não tanka o servidor africano. Então a *evolução* mudou ele.",
         cam=CAM_HOOK,
         hud=[(0.05, 1.0, "chat", dict(titulo="CHAT DO SERVIDOR", linhas=[
             ("red", "[SERVIDOR] 4.812 REPORTS: PORCO"),
             ("white", "JACARÉ_01: CARDÁPIO NOVO LIBERADO"),
             ("white", "HIENA_01: ISSO É PORCO??")]))],
         stickers=[]),

    dict(id="hyrachyus", criatura="hyrachyus", cenario="floresta", era="EOCENO", nome="HYRACHYUS", lv="1",
         hp=0.22, arm=0.08, tick=0, ano="HÁ 50 MI DE ANOS",
         fala="Cinquenta milhões de anos atrás. *Hyrachyus:* pequeno, leve e de pele fina. Ele só corre. "
              "Zero chifre, zero tank. *Dica um:* o nariz vai ganhar uma arma.",
         cam=CAM_S1,
         hud=[(0.00, 0.24, "banner", dict(sub="PARENTE ANTIGO DO RINOCERONTE")),
              (0.26, 0.62, "build", dict(titulo="CRIAR BUILD // RINOCERONTE", linhas=[
                  ("kv", "BASE:", "MINI-CORREDOR"), ("slider", "TAMANHO", 0.06),
                  ("toggle", "PELE FINA", "ON"), ("toggle", "CHIFRE", "OFF")])),
              (0.66, 1.0, "dica", dict(n=1, texto="O NARIZ VAI GANHAR UMA ARMA"))],
         stickers=[]),

    dict(id="hyracodon", criatura="hyracodon", cenario="campo", era="OLIGOCENO", nome="HYRACODON", lv="2",
         hp=0.30, arm=0.10, tick=1, ano="HÁ 30 MI DE ANOS",
         fala="Trinta milhões de anos. *Patch dois:* pernas longas, pra fugir, tipo um pônei em disparada. "
              "Perdeu tank. *Dica dois:* ele vai ficar muito pesado.",
         cam=CAM_S2,
         hud=[(0.00, 0.20, "banner", dict(sub="CORREDOR SEM CHIFRE")),
              (0.20, 0.62, "patch", dict(titulo="PATCH 2.0", linhas=[
                  ("+", "PERNAS LONGAS"), ("+", "CORRIDA (FUGIR)"), ("-", "TANK")])),
              (0.66, 1.0, "dica", dict(n=2, texto="ELE VAI FICAR MUITO PESADO"))],
         stickers=[("tag", 0.20, 0.40, "PÔNEI?", 360, 540, -6)]),

    dict(id="teleoceras", criatura="teleoceras", cenario="poente", era="MIOCENO", nome="TELEOCERAS", lv="3",
         hp=0.62, arm=0.45, tick=2, ano="HÁ 12 MI DE ANOS",
         fala="Doze milhões. *Teleoceras:* perna curta, corpo de barril. Peso serve pra ninguém te derrubar. "
              "Primeiro chifrinho liberado. *Dica três:* a pele vira armadura.",
         cam=CAM_S3,
         hud=[(0.00, 0.20, "banner", dict(sub="O TANQUE DE PERNA CURTA")),
              (0.20, 0.64, "patch", dict(titulo="PATCH 3.0", linhas=[
                  ("+", "CORPO DE BARRIL"), ("+", "PESO (NINGUÉM DERRUBA)"), ("+", "CHIFRE PEQUENO"),
                  ("-", "VELOCIDADE")])),
              (0.66, 1.0, "dica", dict(n=3, texto="A PELE VAI VIRAR ARMADURA"))],
         stickers=[]),

    dict(id="branco", criatura="branco", cenario="savana", era="ATUAL", nome="RINOCERONTE BRANCO", lv="4",
         hp=1.0, arm=1.0, tick=3, ano="HOJE",
         fala="*Hoje.* Rinoceronte branco. Pode passar de duas toneladas. "
              "A pele chega a *cinco centímetros*, em camadas de colágeno: segura espinho, mordida e briga. "
              "Mas ela queima no sol, então ele toma banho de lama: o protetor solar dele. "
              "O chifre é queratina, igual sua unha. Serve pra brigar. O da frente tem cerca de *um metro.*",
         cam=CAM_S4,
         hud=[(0.00, 0.18, "banner", dict(sub="O TANQUE DA SAVANA")),
              (0.18, 0.50, "compare", dict(titulo="PELE // ESPESSURA", linhas=[
                  ("MÍNIMA", "1,5 CM", 0.30, "blue"), ("MÁXIMA", "%d CM" % PELE_CM, 1.0, "yellow"),
                  ("SERVE:", "ESPINHO / MORDIDA / BRIGA", None, None)])),
              (0.50, 0.68, "build", dict(titulo="STATUS // PELE", linhas=[
                  ("slider", "ARMADURA", 1.0, "100%"), ("toggle", "BANHO DE LAMA", "ON"),
                  ("kv", "FUNÇÃO:", "PROTETOR SOLAR")])),
              (0.68, 1.0, "compare", dict(titulo="CHIFRE // TAMANHO", linhas=[
                  ("FRENTE", "~100 CM", 1.0, "yellow"), ("TRÁS", "<40 CM", 0.38, "blue"),
                  ("FEITO DE:", "QUERATINA (COMO UNHA)", None, None)]))],
         stickers=[("big", 0.22, 0.48, "%d CM" % PELE_CM, 360, 470, 0),
                   ("big", 0.84, 1.0, "~1 METRO", 360, 470, 0)]),

    dict(id="fim", criatura="branco", cenario="noite", era="ATUAL", nome="RINOCERONTE BRANCO", lv="4",
         hp=1.0, arm=1.0, tick=3, ano="HOJE",
         fala="O jacaré africano tentou morder. *Pele de cinco centímetros.* Morreu esmagado por esse balofo. "
              "Moral da história: nunca chame ele de *porco.*",
         cam=CAM_S5,
         hud=[(0.05, 1.0, "chat", dict(titulo="CHAT DO SERVIDOR", linhas=[
             ("white", "JACARÉ_01: VOU MORDER O PORCO"),
             ("red", "SERVIDOR: JACARÉ_01 ESMAGADO"),
             ("white", "HIENA_01: EU AVISEI")]))],
         stickers=[]),
]
TICKS = ["50", "30", "12", "HOJE"]     # marcas da linha do tempo (milhões de anos)

# ---------------- TEXTO PRONTO PARA COLAR NO ELEVENLABS ----------------
def _limpa(t):
    return t.replace("*", "")

NARRACAO = "\n\n".join(_limpa(s["fala"]) for s in SCENES)
print("=" * 60)
print("COLE ISTO NO ELEVENLABS (voz em português):")
print("=" * 60)
print(NARRACAO)
print("=" * 60)
print("Palavras:", len(NARRACAO.split()), "| duração estimada: ~%d s" % round(len(NARRACAO.split()) / 2.6))


# --- áudio do repositório ---
_mp3 = sorted(glob.glob("*.mp3"))[0]
shutil.copy(_mp3, WORK / "narracao.mp3")
print("Áudio:", _mp3)

# ============ CÉLULA 3 — NARRAÇÃO (opcional) + SINCRONIZAÇÃO ============
# Fluxo: 1) rode a célula 2 e copie o texto pro ElevenLabs  2) baixe o .mp3
#        3) mude ENVIAR_AUDIO para True, rode esta célula e envie o .mp3
# Sem áudio ainda? Deixe False: ela estima os tempos (dá pra renderizar e trocar depois).
ENVIAR_AUDIO = False

import difflib, json, math, re, subprocess, sys, unicodedata

AUDIO = None
for ext in ("mp3", "wav", "m4a"):
    if (WORK / ("narracao." + ext)).exists():
        AUDIO = WORK / ("narracao." + ext)
if ENVIAR_AUDIO and AUDIO is None:
    from google.colab import files
    up = files.upload()
    if up:
        nome = list(up.keys())[0]
        ext = nome.rsplit(".", 1)[-1].lower()
        AUDIO = WORK / ("narracao." + ext)
        AUDIO.write_bytes(up[nome])
print("Áudio:", AUDIO if AUDIO else "nenhum (usando estimativa de tempo)")


def tokenizar(fala):
    out = []
    for i, seg in enumerate(fala.split("*")):
        for w in seg.split():
            out.append((w, i % 2 == 1))
    return out


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", w)


def estimar(palavras):
    """tempos (início, fim) por palavra, sem áudio: ~2,6 palavras/segundo + pausas"""
    t = 0.30
    out = []
    for w in palavras:
        dur = 0.10 + 0.058 * len(norm(w))
        out.append((t, t + dur))
        t += dur + 0.03
        if w[-1] in ".!?":
            t += 0.16
        elif w[-1] == ":":
            t += 0.16
        elif w[-1] == ",":
            t += 0.12
    return out


def alinhar(script, asr):
    """casa as palavras do roteiro com as palavras que o Whisper ouviu; preenche buracos por interpolação"""
    a = [norm(w) for w in script]
    b = [norm(x["word"]) for x in asr]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out = [None] * len(a)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and (i2 - i1) == (j2 - j1)):
            for k in range(i2 - i1):
                out[i1 + k] = (float(asr[j1 + k]["start"]), float(asr[j1 + k]["end"]))
    idx = [i for i, v in enumerate(out) if v]
    if len(idx) < max(3, int(0.4 * len(a))):
        return None
    for i in range(idx[0] - 1, -1, -1):                      # antes da primeira palavra casada
        s = out[i + 1][0] - 0.35
        out[i] = (max(0.0, s), max(0.0, s) + 0.30)
    for i in range(idx[-1] + 1, len(a)):                     # depois da última
        s = out[i - 1][1] + 0.05
        out[i] = (s, s + 0.30)
    for p, q in zip(idx, idx[1:]):                           # buracos no meio
        gap = q - p - 1
        if gap > 0:
            t0, t1 = out[p][1], out[q][0]
            step = (t1 - t0) / (gap + 1)
            for g in range(gap):
                out[p + 1 + g] = (t0 + step * g, t0 + step * (g + 1))
    return out


def transcrever(path):
    """Whisper (faster-whisper) com tempo por palavra. Se algo falhar, devolve None e usamos estimativa."""
    try:
        try:
            import faster_whisper  # noqa
        except ImportError:
            print("instalando faster-whisper (1x)...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "faster-whisper"], check=True)
        from faster_whisper import WhisperModel
        for dev, ct in (("cuda", "float16"), ("cpu", "int8")):
            try:
                model = WhisperModel("small", device=dev, compute_type=ct)
                segs, _ = model.transcribe(str(path), language="pt", word_timestamps=True)
                out = []
                for s in segs:
                    for w in (s.words or []):
                        out.append({"word": w.word, "start": w.start, "end": w.end})
                if out:
                    return out
            except Exception as e:
                print("whisper em", dev, "falhou:", str(e)[:120])
        return None
    except Exception as e:
        print("sincronização automática indisponível:", str(e)[:150])
        return None


def duracao_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                        "default=nw=1:nk=1", str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())


def chunkar(palavras):
    """legendas curtas, como no seu vídeo: até 3 palavras / 20 letras, quebrando na pontuação"""
    chunks, cur = [], []
    for k, (w, hl) in enumerate(palavras):
        if cur and sum(len(x[1]) + 1 for x in cur) + len(w) > 20:
            chunks.append(cur)
            cur = []
        cur.append((k, w, hl))
        if w[-1] in ".!?:," or len(cur) >= 3:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def construir_timeline(audio_path):
    todas = []                                   # (cena, palavra, destaque)
    for si, sc in enumerate(SCENES):
        for (w, hl) in tokenizar(sc["fala"]):
            todas.append((si, w, hl))
    textos = [w for _, w, _ in todas]
    est = estimar(textos)
    tempos, fonte, dur_audio = est, "estimativa", None
    if audio_path:
        dur_audio = duracao_audio(audio_path)
        asr = transcrever(audio_path)
        al = alinhar(textos, asr) if asr else None
        if al:
            tempos, fonte = al, "whisper (tempo real da voz)"
        else:
            k = (dur_audio - 0.3) / est[-1][1]
            tempos, fonte = [(a * k, b * k) for a, b in est], "estimativa escalada pro tamanho do áudio"

    # limites das cenas
    ini = []
    for si in range(len(SCENES)):
        first = next(i for i, (s, _, _) in enumerate(todas) if s == si)
        ini.append(0.0 if si == 0 else max(0.0, tempos[first][0] - 0.18))
    fim_total = tempos[-1][1] + 1.0
    if dur_audio:
        fim_total = max(fim_total, dur_audio + 0.6)
    scenes = []
    for si, sc in enumerate(SCENES):
        d = dict(sc)
        d["start"] = round(ini[si], 3)
        d["end"] = round(ini[si + 1] if si + 1 < len(SCENES) else fim_total, 3)
        scenes.append(d)

    # legendas
    caps = []
    for si in range(len(SCENES)):
        idxs = [i for i, (s, _, _) in enumerate(todas) if s == si]
        pal = [(todas[i][1], todas[i][2]) for i in idxs]
        chunks = chunkar(pal)
        for ci, ch in enumerate(chunks):
            g0 = idxs[ch[0][0]]
            g1 = idxs[ch[-1][0]]
            t0 = tempos[g0][0]
            if ci + 1 < len(chunks):
                nxt = tempos[idxs[chunks[ci + 1][0][0]]][0]
            else:
                nxt = scenes[si]["end"]
            t1 = min(nxt, tempos[g1][1] + 0.30)
            caps.append({"cena": si, "t0": round(t0, 3), "t1": round(max(t1, t0 + 0.25), 3),
                         "palavras": [(w, hl) for _, w, hl in ch]})
    n_frames = int(math.ceil(fim_total * FPS))
    return {"fps": FPS, "w": W, "h": H, "duration": round(fim_total, 3), "n_frames": n_frames,
            "ticks": TICKS, "fonte_tempo": fonte, "scenes": scenes, "captions": caps}


TL = construir_timeline(AUDIO)
(WORK / "timeline.json").write_text(json.dumps(TL, ensure_ascii=False), encoding="utf-8")
print("Tempo baseado em:", TL["fonte_tempo"])
print("Duração: %.1f s | frames: %d (%d fps)" % (TL["duration"], TL["n_frames"], FPS))
for s in TL["scenes"]:
    print("  %-10s %5.1f s → %5.1f s" % (s["id"], s["start"], s["end"]))


# ============ CÉLULA 4 — SCRIPT DO BLENDER (modelos 3D, cenários, câmera) ============
# Só grava o arquivo. Não precisa mexer.
BLENDER_SCRIPT = r'''# blender_scene.py
# Rodar com: blender -b -noaudio --factory-startup -P blender_scene.py -- --timeline T.json --out DIR
import bpy
import bmesh
import math
import json
import sys
import os
import random
import argparse
from mathutils import Vector


# ----------------------------------------------------------------------------
# utilidades
# ----------------------------------------------------------------------------
def get_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=0)
    ap.add_argument("--samples", type=int, default=20)
    ap.add_argument("--scale", type=int, default=100)
    ap.add_argument("--stills", default="")
    return ap.parse_args(argv)


def lin(c):
    return tuple(max(0.0, x) ** 2.2 for x in c)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp3(a, b, t):
    return tuple(lerp(x, y, t) for x, y in zip(a, b))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def back_out(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def interp(u, keys):
    if u <= keys[0][0]:
        return keys[0][1]
    for (u0, v0), (u1, v1) in zip(keys, keys[1:]):
        if u <= u1:
            return lerp(v0, v1, (u - u0) / (u1 - u0 if u1 != u0 else 1.0))
    return keys[-1][1]


def make_noise(seed):
    rnd = random.Random(seed)
    waves = []
    for i in range(4):
        k = 1 + i * 0.8
        waves.append((rnd.uniform(0.05, 0.25) * k, rnd.uniform(0.05, 0.25) * k,
                      rnd.uniform(0, 6.28), rnd.uniform(0, 6.28), 1.0 / (1 + i * 0.9)))

    def n(x, y):
        s = 0.0
        tot = 0.0
        for fx, fy, px, py, a in waves:
            s += a * math.sin(fx * x + px) * math.cos(fy * y + py)
            tot += a
        return s / tot
    return n


# ----------------------------------------------------------------------------
# geometria: "loft" = superfície varrida por anéis (formas orgânicas, nada de cubos)
# stations: lista de (t, a, b, ra, rb) -> posição ao longo do eixo, centro (a,b), raios
# ----------------------------------------------------------------------------
def ring_pts(a, b, ra, rb, n, M):
    pts = []
    for k in range(M):
        ang = 2 * math.pi * k / M
        c, s = math.cos(ang), math.sin(ang)
        pts.append((a + ra * math.copysign(abs(c) ** (2.0 / n), c),
                    b + rb * math.copysign(abs(s) ** (2.0 / n), s)))
    return pts


def loft(stations, axis="x", M=12, n=2.3, cap0=True, cap1=True):
    verts = []
    faces = []
    for (t, a, b, ra, rb) in stations:
        for (u, v) in ring_pts(a, b, ra, rb, n, M):
            if axis == "x":
                verts.append((t, u, v))
            else:
                verts.append((u, v, t))
    S = len(stations)
    for i in range(S - 1):
        for k in range(M):
            k2 = (k + 1) % M
            faces.append((i * M + k, i * M + k2, (i + 1) * M + k2, (i + 1) * M + k))
    for flag, idx in ((cap0, 0), (cap1, S - 1)):
        if not flag:
            continue
        t, a, b, ra, rb = stations[idx]
        c = len(verts)
        verts.append((t, a, b) if axis == "x" else (a, b, t))
        base = idx * M
        for k in range(M):
            k2 = (k + 1) % M
            faces.append((c, base + k2, base + k) if idx == 0 else (c, base + k, base + k2))
    return verts, faces


def ellipsoid(rx, ry, rz, rings=6, M=9, n=2.0):
    st = []
    for i in range(rings + 1):
        t = -rz + 2 * rz * i / rings
        f = math.sqrt(max(0.0, 1 - (t / rz) ** 2))
        f = max(f, 0.06)
        st.append((t, 0, 0, rx * f, ry * f))
    return loft(st, "z", M=M, n=n)


def shift(verts, dx=0.0, dy=0.0, dz=0.0):
    return [(x + dx, y + dy, z + dz) for (x, y, z) in verts]


def part(vf, col, belly=None):
    return {"v": vf[0], "f": vf[1], "col": col, "belly": belly}


def merge(parts, jitter=0.06, seed=0):
    rnd = random.Random(seed)
    V, F, C = [], [], []
    for p in parts:
        off = len(V)
        V.extend(p["v"])
        zs = [v[2] for v in p["v"]]
        z0, z1 = min(zs), max(zs)
        lim = z0 + 0.22 * (z1 - z0)
        base = lin(p["col"])
        bel = lin(p["belly"]) if p.get("belly") else None
        for f in p["f"]:
            F.append(tuple(i + off for i in f))
            zc = sum(p["v"][i][2] for i in f) / len(f)
            c = bel if (bel and zc < lim) else base
            j = 1 + (rnd.random() - 0.5) * 2 * jitter
            C.append((clamp(c[0] * j), clamp(c[1] * j), clamp(c[2] * j)))
    return V, F, C


# ----------------------------------------------------------------------------
# objetos / materiais
# ----------------------------------------------------------------------------
def mat_vcol(name, rough=0.9, spec=0.12):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    vc = nt.nodes.new("ShaderNodeVertexColor")
    vc.layer_name = "col"
    nt.links.new(vc.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    for key in ("Specular IOR Level", "Specular"):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = spec
            break
    return m


def mat_flat(name, rgb, rough=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = lin(rgb) + (1.0,)
    bsdf.inputs["Roughness"].default_value = rough
    return m


def new_empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    if parent is not None:
        e.parent = parent
    e.location = loc
    return e


def mesh_obj(name, V, F, C, mat, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), mesh=None):
    if mesh is None:
        me = bpy.data.meshes.new(name)
        me.from_pydata(V, [], F)
        me.update()
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        if C is not None:
            attr = me.color_attributes.new(name="col", type="FLOAT_COLOR", domain="CORNER")
            data = []
            for p in me.polygons:
                c = C[p.index]
                for _ in p.loop_indices:
                    data.extend((c[0], c[1], c[2], 1.0))
            attr.data.foreach_set("color", data)
        for p in me.polygons:
            p.use_smooth = False
        me.materials.append(mat)
    else:
        me = mesh
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    return ob


# ----------------------------------------------------------------------------
# criaturas (mesmo gerador, parâmetros diferentes por era)
# ----------------------------------------------------------------------------
CREATURES = {
    "hyrachyus": dict(L=0.95, H=0.17, W=0.13, hip=0.34, head_len=0.34, head_r=0.08, lip=0.75, neck=-0.02,
                      pitch=0.30, hump=0.0, folds=0.0, horns=[], ear=1.0, tail=0.28, leg_r=0.04, foot=0.045,
                      A=0.55, K=0.9, v=1.5, col=(0.84, 0.60, 0.55), belly=(0.94, 0.77, 0.71), n=2.2),
    "hyracodon": dict(L=1.25, H=0.22, W=0.15, hip=0.62, head_len=0.50, head_r=0.09, lip=0.70, neck=0.16,
                      pitch=0.18, hump=0.0, folds=0.0, horns=[], ear=1.2, tail=0.50, leg_r=0.045, foot=0.05,
                      A=0.55, K=1.0, v=1.9, col=(0.67, 0.50, 0.33), belly=(0.80, 0.68, 0.50), n=2.2),
    "teleoceras": dict(L=2.40, H=0.60, W=0.60, hip=0.50, head_len=0.90, head_r=0.26, lip=1.0, neck=-0.10,
                       pitch=0.55, hump=0.0, folds=0.5, horns=[(0.80, 0.26, 0.065, 0.15)], ear=0.7, tail=0.65,
                       leg_r=0.19, foot=0.20, A=0.34, K=0.7, v=0.95, col=(0.47, 0.41, 0.35),
                       belly=(0.60, 0.54, 0.46), n=2.0),
    "branco": dict(L=2.50, H=0.62, W=0.60, hip=0.78, head_len=1.25, head_r=0.30, lip=1.35, neck=-0.16,
                   pitch=0.62, hump=0.45, folds=1.0, horns=[(0.86, 1.00, 0.11, 0.35), (0.52, 0.40, 0.085, 0.15)],
                   ear=0.9, tail=1.00, leg_r=0.21, foot=0.23, A=0.36, K=0.75, v=1.05, col=(0.60, 0.58, 0.54),
                   belly=(0.70, 0.67, 0.62), n=2.0),
}


def gauss(u, c, w):
    return math.exp(-((u - c) / w) ** 2)


def build_creature(name, P):
    L, H, W, hip = P["L"], P["H"], P["W"], P["hip"]
    zc = hip + 0.55 * H
    objs = []
    mat = mat_vcol(name + "_skin")
    dark = mat_flat(name + "_dark", (0.05, 0.04, 0.04), 0.3)
    horn_mat = mat_vcol(name + "_horn", 0.6)

    root = new_empty(name + "_root")
    objs.append(root)

    # corpo
    keys = [(0.0, 0.50), (0.08, 0.82), (0.22, 0.97), (0.5, 1.0), (0.75, 0.95), (0.9, 0.80), (1.0, 0.64)]
    N = 24
    st = []
    for i in range(N):
        u = i / (N - 1)
        m = interp(u, keys)
        fold = 1 + P["folds"] * (0.07 * gauss(u, 0.60, 0.035) + 0.06 * gauss(u, 0.20, 0.035) + 0.05 * gauss(u, 0.42, 0.03))
        hump = P["hump"] * H * 0.55 * gauss(u, 0.68, 0.13)
        st.append((-L / 2 + u * L, 0, zc + hump * 0.5 - 0.04 * H * m, W * m * fold, H * m * fold + hump * 0.5))
    body_vf = loft(st, "x", M=14, n=P["n"])
    V, F, C = merge([part(body_vf, P["col"], P["belly"])], 0.07, 1)
    body = mesh_obj(name + "_body", V, F, C, mat, parent=root)
    objs.append(body)

    # cabeça
    HL, hr = P["head_len"], P["head_r"]
    head_pivot = new_empty(name + "_head", parent=root, loc=(L / 2 - 0.03 * L, 0, zc + P["neck"] * H * 2.0))
    head_pivot.rotation_euler = (0, P["pitch"], 0)
    objs.append(head_pivot)
    lip = P["lip"]
    hst = [(-0.15 * HL, 0, 0, hr * 0.95, hr * 1.0), (0.15 * HL, 0, 0.01, hr, hr * 1.0),
           (0.50 * HL, 0, 0.0, hr * 0.85, hr * 0.82), (0.85 * HL, 0, -0.03 * hr, hr * 0.78 * lip, hr * 0.64),
           (1.0 * HL, 0, -0.04 * hr, hr * 0.84 * lip, hr * 0.58)]
    head_vf = loft(hst, "x", M=12, n=2.4)
    V, F, C = merge([part(head_vf, P["col"], P["belly"])], 0.07, 2)
    objs.append(mesh_obj(name + "_headmesh", V, F, C, mat, parent=head_pivot))

    def head_top(t):
        # raio vertical da cabeça na posição t (aprox.)
        pts = [(s[0], s[4]) for s in hst]
        return interp(t, pts)

    # olhos
    er = hr * 0.13
    for side in (1, -1):
        ev = ellipsoid(er, er, er, rings=4, M=7)
        V, F, C = merge([part(ev, (0.04, 0.03, 0.03))], 0.0, 3)
        objs.append(mesh_obj(name + "_eye", V, F, C, mat, parent=head_pivot,
                             loc=(0.33 * HL, side * hr * 0.93, hr * 0.22)))

    # orelhas
    el = hr * 0.75 * P["ear"]
    ew = hr * 0.42
    est = [(0, 0, 0, ew * 0.30, ew), (el * 0.6, 0, 0, ew * 0.26, ew * 0.8), (el, 0, 0, 0.004, 0.004)]
    for side in (1, -1):
        ev = loft(est, "z", M=7)
        V, F, C = merge([part(ev, P["col"])], 0.05, 4)
        objs.append(mesh_obj(name + "_ear", V, F, C, mat, parent=head_pivot,
                             loc=(0.05 * HL, side * hr * 0.62, hr * 0.80), rot=(-side * 0.55, 0, -0.2)))

    # chifres
    horn_loc = None
    for (pos, ln, r0, tilt) in P["horns"]:
        hs = []
        for i in range(7):
            f = i / 6.0
            hs.append((ln * f, -0.22 * ln * f * f, 0, max(r0 * (1 - f) ** 0.9, 0.004), max(r0 * 0.9 * (1 - f) ** 0.9, 0.004)))
        hv = loft(hs, "z", M=9)
        V, F, C = merge([part(hv, (0.42, 0.36, 0.30), (0.30, 0.25, 0.21))], 0.08, 5)
        hx = pos * HL
        hz = head_top(hx) - 0.01
        objs.append(mesh_obj(name + "_horn", V, F, C, horn_mat, parent=head_pivot, loc=(hx, 0, hz), rot=(0, tilt, 0)))
        if horn_loc is None:
            horn_loc = (hx, hz + ln * 0.5)

    # cauda
    tail_pivot = new_empty(name + "_tail", parent=root, loc=(-L / 2 + 0.02 * L, 0, zc + 0.15 * H))
    tail_pivot.rotation_euler = (0, -0.55, 0)
    objs.append(tail_pivot)
    tl = P["tail"]
    tr = W * 0.17
    tst = [(0, 0, 0, tr, tr), (-tl * 0.5, 0, 0, tr * 0.75, tr * 0.75), (-tl, 0, 0, tr * 0.5, tr * 0.5)]
    tv = loft(tst, "x", M=7)
    V, F, C = merge([part(tv, P["col"])], 0.05, 6)
    objs.append(mesh_obj(name + "_tailmesh", V, F, C, mat, parent=tail_pivot))

    # pernas (hierarquia quadril -> joelho)
    legs = []
    up, low, fh = 0.46 * hip, 0.42 * hip, 0.12 * hip
    lr = P["leg_r"]
    fw = P["foot"]
    for (lx, fi) in ((L * 0.30, 0), (-L * 0.30, 1)):
        for side in (1, -1):
            hip_e = new_empty(name + "_hip", parent=root, loc=(lx, side * W * 0.60, hip))
            objs.append(hip_e)
            ust = [(0, 0, 0, lr * 1.0, lr * 1.15), (-up * 0.5, 0, 0, lr * 0.85, lr * 0.95), (-up, 0, 0, lr * 0.68, lr * 0.72)]
            V, F, C = merge([part(loft(ust, "z", M=8), P["col"])], 0.06, 7)
            objs.append(mesh_obj(name + "_up", V, F, C, mat, parent=hip_e))
            knee = new_empty(name + "_knee", parent=hip_e, loc=(0, 0, -up))
            objs.append(knee)
            lst = [(0, 0, 0, lr * 0.68, lr * 0.72), (-low * 0.5, 0, 0, lr * 0.6, lr * 0.62), (-low, 0, 0, lr * 0.62, lr * 0.66)]
            fst = [(-low, 0, 0, lr * 0.75, lr * 0.85), (-low - fh * 0.5, 0, 0, fw * 1.0, fw * 1.15),
                   (-low - fh, 0, 0, fw * 1.05, fw * 1.2)]
            V, F, C = merge([part(loft(lst, "z", M=8, cap1=False), P["col"]),
                             part(loft(fst, "z", M=8), (0.28, 0.24, 0.21))], 0.06, 8)
            objs.append(mesh_obj(name + "_low", V, F, C, mat, parent=knee))
            # três dedos
            for ty in (-1, 0, 1):
                tv2 = ellipsoid(fw * 0.32, fw * 0.30, fw * 0.28, rings=4, M=7)
                V, F, C = merge([part(tv2, (0.22, 0.19, 0.17))], 0.0, 9)
                objs.append(mesh_obj(name + "_toe", V, F, C, mat, parent=knee,
                                     loc=(fw * 1.15, ty * fw * 0.62, -low - fh * 0.85)))
            off = 0.0 if (fi == 0) == (side == 1) else math.pi
            legs.append({"hip": hip_e, "knee": knee, "off": off})

    S = 4 * hip * math.sin(P["A"])
    head_world = (L / 2 + 0.5 * HL * math.cos(P["pitch"]), 0, zc + P["neck"] * H * 2.0 - 0.5 * HL * math.sin(P["pitch"]))
    hx, hz = horn_loc if horn_loc else (0.9 * HL, hr)
    anchors = {
        "center": (0.05 * L, 0, zc),
        "head": head_world,
        "flank": (0.05 * L, -W * 0.9, zc),
        "horn": (L / 2 + hx * math.cos(P["pitch"]), 0, zc + P["neck"] * H * 2.0 + hz * 0.8),
        "feet": (0.0, 0.0, 0.25 * hip),
        "pair": (-0.55, 0, zc),
    }
    R = L + 0.8 * HL
    return {"root": root, "body": body, "head": head_pivot, "tail": tail_pivot, "legs": legs, "objs": objs,
            "P": P, "S": S, "anchors": anchors, "R": R, "zc": zc}



# ----------------------------------------------------------------------------
# jacaré escondido no riacho (só aparece nas cenas com extra="jacare")
# ----------------------------------------------------------------------------
def build_croc(name="jacare"):
    objs = []
    root = new_empty(name + "_root")
    objs.append(root)
    mat = mat_vcol(name + "_skin")
    eye_m = mat_flat(name + "_eye", (0.95, 0.80, 0.15), 0.3)
    tooth_m = mat_flat(name + "_teeth", (0.95, 0.93, 0.85), 0.4)
    col, bel, dark = (0.26, 0.33, 0.15), (0.62, 0.64, 0.40), (0.16, 0.21, 0.09)
    zb = 0.11
    keys = [(-1.35, 0.015), (-1.0, 0.05), (-0.5, 0.12), (-0.1, 0.20), (0.3, 0.22), (0.7, 0.18)]

    def sway(x):
        return 0.08 * math.sin((x + 1.35) * 2.4) * (1 - (x + 1.35) / 2.05)

    st = []
    for i in range(16):
        x = -1.35 + i * (0.7 + 1.35) / 15
        r = interp(x, keys)
        st.append((x, sway(x), zb, r, r * 0.55))
    parts = [part(loft(st, "x", M=10, n=2.2), col, bel)]
    for i in range(12):                                    # escamas ao longo das costas
        x = -1.1 + i * 0.16
        r = interp(x, keys)
        sc_v = loft([(0, 0, 0, 0.035, 0.02), (0.05, 0, 0, 0.003, 0.003)], "z", M=4)
        parts.append(part((shift(sc_v[0], x, sway(x), zb + r * 0.55 - 0.01), sc_v[1]), dark))
    V, F, C = merge(parts, 0.08, 61)
    objs.append(mesh_obj(name + "_body", V, F, C, mat, parent=root))

    zh = zb + 0.03
    up_r = [(0.55, 0.17), (0.80, 0.12), (1.15, 0.085), (1.30, 0.10), (1.36, 0.05)]
    ust = [(x, 0, zh, r, r * 0.45) for x, r in up_r]
    V, F, C = merge([part(loft(ust, "x", M=10, n=2.3), col, bel)], 0.08, 62)
    objs.append(mesh_obj(name + "_upper", V, F, C, mat, parent=root))

    jaw = new_empty(name + "_jaw", parent=root, loc=(0.62, 0, zb))
    objs.append(jaw)
    low_r = [(0.0, 0.15), (0.3, 0.11), (0.72, 0.075)]
    lst = [(x, 0, -0.04, r, 0.035) for x, r in low_r]
    V, F, C = merge([part(loft(lst, "x", M=10, n=2.3), col, bel)], 0.08, 63)
    objs.append(mesh_obj(name + "_lower", V, F, C, mat, parent=jaw))

    tv = loft([(0, 0, 0, 0.014, 0.014), (0.045, 0, 0, 0.002, 0.002)], "z", M=5)
    V, F, C = merge([part(tv, (0.95, 0.93, 0.85))], 0.0, 64)
    proto = mesh_obj(name + "_toothproto", V, F, C, tooth_m)
    proto.hide_render = True
    objs.append(proto)
    for k in range(7):
        xu = 0.75 + k * 0.085
        ru = interp(xu, up_r)
        xl = 0.10 + k * 0.085
        rl = interp(xl, low_r)
        for side in (1, -1):
            objs.append(mesh_obj(name + "_tu", None, None, None, None, mesh=proto.data, parent=root,
                                 loc=(xu, side * ru * 0.8, zh - 0.02), rot=(math.pi, 0, 0)))
            objs.append(mesh_obj(name + "_tl", None, None, None, None, mesh=proto.data, parent=jaw,
                                 loc=(xl, side * rl * 0.8, -0.01)))
    for side in (1, -1):                                   # olhos saltados
        ev = ellipsoid(0.032, 0.032, 0.032, rings=4, M=7)
        V, F, C = merge([part(ev, (0.95, 0.80, 0.15))], 0.0, 65)
        objs.append(mesh_obj(name + "_eye", V, F, C, eye_m, parent=root, loc=(0.68, side * 0.10, zh + 0.07)))
    return {"root": root, "jaw": jaw, "objs": objs}

# ----------------------------------------------------------------------------
# cenários
# ----------------------------------------------------------------------------
SETS = {
    "noite": dict(mode="flat", flat=(0.03, 0.06, 0.18), wstr=1.1, sun_col=(0.55, 0.66, 1.0), sun_str=2.4,
                  sun_el=38, sun_az=30, g1=(0.13, 0.21, 0.46), g2=(0.22, 0.32, 0.64), hill=(0.10, 0.16, 0.38),
                  tree="pine", tcol=(0.05, 0.22, 0.30), n_trees=46, tscale=1.0, tuft=(0.20, 0.32, 0.62), amp=1.6),
    "floresta": dict(mode="sky", sun_col=(1.0, 0.95, 0.85), sun_str=3.6, sun_el=34, sun_az=30, dust=1.5, wstr=1.0,
                     g1=(0.24, 0.48, 0.15), g2=(0.36, 0.62, 0.20), hill=(0.20, 0.42, 0.32),
                     tree="broad", tcol=(0.13, 0.44, 0.12), n_trees=40, tscale=1.1, tuft=(0.30, 0.60, 0.16), amp=1.4),
    "campo": dict(mode="sky", sun_col=(1.0, 0.92, 0.72), sun_str=3.8, sun_el=26, sun_az=30, dust=2.0, wstr=1.0,
                  g1=(0.52, 0.56, 0.22), g2=(0.68, 0.66, 0.28), hill=(0.45, 0.50, 0.30),
                  tree="broad", tcol=(0.30, 0.50, 0.16), n_trees=14, tscale=1.1, tuft=(0.66, 0.62, 0.26), amp=1.2),
    "poente": dict(mode="sky", sun_col=(1.0, 0.52, 0.30), sun_str=4.6, sun_el=7, sun_az=40, dust=4.0, wstr=1.0,
                   g1=(0.78, 0.36, 0.22), g2=(0.90, 0.52, 0.30), hill=(0.70, 0.28, 0.26),
                   tree="acacia", tcol=(0.40, 0.30, 0.14), n_trees=12, tscale=1.2, tuft=(0.86, 0.46, 0.26), amp=1.0),
    "savana": dict(mode="sky", sun_col=(1.0, 0.80, 0.52), sun_str=4.0, sun_el=16, sun_az=35, dust=2.5, wstr=1.0,
                   g1=(0.72, 0.60, 0.22), g2=(0.86, 0.74, 0.32), hill=(0.66, 0.46, 0.28),
                   tree="acacia", tcol=(0.34, 0.42, 0.14), n_trees=22, tscale=1.5, tuft=(0.82, 0.70, 0.28), amp=1.1,
                   river=True),
}


def tree_parts(kind, SP, seed):
    rnd = random.Random(seed)
    tc = SP["tcol"]
    jit = (tc[0] * rnd.uniform(0.85, 1.15), tc[1] * rnd.uniform(0.85, 1.15), tc[2] * rnd.uniform(0.85, 1.15))
    trunk = (0.30, 0.20, 0.12)
    if kind == "pine":
        cone = [(0.8, 0, 0, 0.11, 0.11), (0.8, 0, 0, 1.0, 1.0), (1.8, 0, 0, 0.28, 0.28), (1.8, 0, 0, 0.78, 0.78),
                (2.7, 0, 0, 0.2, 0.2), (2.7, 0, 0, 0.52, 0.52), (3.5, 0, 0, 0.02, 0.02)]
        return [part(loft([(0, 0, 0, 0.13, 0.13), (0.8, 0, 0, 0.11, 0.11)], "z", M=6), trunk),
                part(loft(cone, "z", M=8, cap0=False), jit)]
    if kind == "acacia":
        tv = loft([(0, 0, 0, 0.13, 0.13), (1.3, 0.15, 0, 0.10, 0.10), (2.5, 0.45, 0, 0.09, 0.09)], "z", M=6)
        cv = ellipsoid(2.0, 1.7, 0.45, rings=5, M=9)
        return [part(tv, trunk), part((shift(cv[0], 0.45, 0, 2.7), cv[1]), jit)]
    tv = loft([(0, 0, 0, 0.16, 0.16), (2.0, 0, 0, 0.11, 0.11)], "z", M=6)
    c1 = ellipsoid(1.2, 1.2, 1.0, rings=5, M=9)
    c2 = ellipsoid(0.8, 0.8, 0.7, rings=4, M=8)
    return [part(tv, trunk), part((shift(c1[0], 0, 0, 2.7), c1[1]), jit),
            part((shift(c2[0], 0.6, 0.4, 3.3), c2[1]), lerp3(jit, (1, 1, 1), 0.08))]


def build_set(key, SP, ox):
    objs = []
    sd = sum((i + 1) * ord(ch) for i, ch in enumerate(key))
    rnd = random.Random(sd % 1000 + 7)
    noise = make_noise(sd % 997 + 3)
    # terreno em triângulos (facetado)
    x0, x1, y0, y1, cell = -25.0, 70.0, -22.0, 22.0, 1.5
    nx = int((x1 - x0) / cell) + 1
    ny = int((y1 - y0) / cell) + 1
    V = []
    for j in range(ny):
        for i in range(nx):
            x = x0 + i * cell
            y = y0 + j * cell
            ramp = clamp((abs(y) - 3.4) / 7.0)
            edge = (1 - smooth((abs(y) - 14.0) / 8.0)) * (1 - smooth((abs(x - 22.5) - 38.0) / 9.5))
            z = SP["amp"] * noise(x, y) * ramp * ramp * 1.6 * edge
            V.append((ox + x, y, z))
    F, C = [], []
    g1, g2 = lin(SP["g1"]), lin(SP["g2"])
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            b = a + 1
            c = a + nx
            d = c + 1
            for tri in ((a, b, d), (a, d, c)):
                F.append(tri)
                zc = sum(V[k][2] for k in tri) / 3.0
                mix = clamp(0.5 + 0.5 * noise(V[tri[0]][0] * 1.7, V[tri[0]][1] * 1.7) + rnd.uniform(-0.2, 0.2))
                col = lerp3(g1, g2, mix)
                sh = 1 + rnd.uniform(-0.10, 0.10) + clamp(zc * 0.05, -0.1, 0.12)
                C.append(tuple(clamp(v * sh) for v in col))
    mat_g = mat_vcol(key + "_ground", 0.95, 0.05)
    objs.append(mesh_obj(key + "_terrain", V, F, C, mat_g))
    # chão distante (esconde a borda do terreno)
    fc = tuple(clamp(v * 0.8) for v in g1)
    FV = [(ox - 150, -80, -0.03), (ox + 170, -80, -0.03), (ox + 170, 160, -0.03), (ox - 150, 160, -0.03)]
    objs.append(mesh_obj(key + "_far", FV, [(0, 1, 2), (0, 2, 3)], [fc, fc], mat_g))

    # riacho (margem de lama + água)
    if SP.get("river"):
        mud = mat_flat(key + "_mud", (0.30, 0.22, 0.12), 0.95)
        wat = mat_flat(key + "_water", (0.16, 0.42, 0.58), 0.06)
        for (ya, yb, zz, mm) in ((1.5, 5.6, 0.07, mud), (2.0, 5.0, 0.12, wat)):
            sv = [(ox - 60, ya, zz), (ox + 110, ya, zz), (ox + 110, yb, zz), (ox - 60, yb, zz)]
            objs.append(mesh_obj(key + "_river", sv, [(0, 1, 2, 3)], None, mm))

    # árvores (instâncias compartilhando a malha)
    variants = []
    for k in range(3):
        parts = tree_parts(SP["tree"], SP, 11 + k)
        tv, tf, tc = merge(parts, 0.08, 20 + k)
        o = mesh_obj(key + "_treeproto%d" % k, tv, tf, tc, mat_vcol(key + "_tree%d" % k, 0.9, 0.05))
        o.hide_render = True
        variants.append(o)
    for i in range(SP["n_trees"]):
        proto = rnd.choice(variants)
        s = SP["tscale"] * rnd.uniform(0.8, 1.4)
        x = ox + rnd.uniform(-22, 66)
        y = rnd.uniform(5.0, 26.0)
        o = mesh_obj(key + "_tree", None, None, None, None, mesh=proto.data,
                     loc=(x, y, 0), rot=(0, 0, rnd.uniform(0, 6.28)), scale=(s, s, s * rnd.uniform(0.9, 1.2)))
        objs.append(o)

    # tufos de grama / pedras
    tuft_col = SP["tuft"]
    tuft_vf = loft([(0, 0, 0, 0.07, 0.07), (0.28, 0, 0, 0.012, 0.012)], "z", M=5)
    tv, tf, tc = merge([part(tuft_vf, tuft_col)], 0.12, 31)
    tproto = mesh_obj(key + "_tuftproto", tv, tf, tc, mat_vcol(key + "_tuft", 0.9, 0.05))
    tproto.hide_render = True
    for i in range(110):
        x = ox + rnd.uniform(-22, 66)
        y = rnd.uniform(-9.0, -1.6) if rnd.random() < 0.7 else rnd.uniform(1.6, 8.0)
        s = rnd.uniform(0.7, 1.9)
        objs.append(mesh_obj(key + "_tuft", None, None, None, None, mesh=tproto.data,
                             loc=(x, y, 0), rot=(0, 0, rnd.uniform(0, 6.28)), scale=(s, s, s)))
    # montanhas / mesas ao fundo
    for i in range(9):
        sx = rnd.uniform(14, 34)
        h = rnd.uniform(10, 26)
        if SP["tree"] == "acacia":
            st = [(0, 0, 0, sx, sx * 0.8), (h * 0.8, 0, 0, sx * 0.55, sx * 0.45), (h, 0, 0, sx * 0.5, sx * 0.4)]
        else:
            st = [(0, 0, 0, sx, sx * 0.8), (h, 0, 0, sx * 0.07, sx * 0.06)]
        hv = loft(st, "z", M=7)
        c = lerp3(SP["hill"], (0.8, 0.85, 0.95), 0.12 * rnd.random())
        V2, F2, C2 = merge([part(hv, c)], 0.08, 40 + i)
        objs.append(mesh_obj(key + "_hill", V2, F2, C2, mat_vcol(key + "_hillmat%d" % i, 1.0, 0.0),
                             loc=(ox - 20 + i * 14 + rnd.uniform(-5, 5), rnd.uniform(55, 95), -1.0)))
    for o in objs:
        o.hide_render = True
    return objs


# ----------------------------------------------------------------------------
# mundo, sol, câmera
# ----------------------------------------------------------------------------
def build_world():
    scn = bpy.context.scene
    w = bpy.data.worlds.new("VQQWorld")
    scn.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexSky")
    try:
        sky.sky_type = "NISHITA"
        sky.sun_disc = False
    except Exception as e:
        print("sky type fallback:", e)
    mix = nt.nodes.new("ShaderNodeMixRGB")
    flat = nt.nodes.new("ShaderNodeRGB")
    nt.links.new(sky.outputs["Color"], mix.inputs[1])
    nt.links.new(flat.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs[0])
    return {"sky": sky, "mix": mix, "flat": flat, "bg": bg}


def apply_set_look(SP, world, sun):
    if SP["mode"] == "flat":
        world["mix"].inputs[0].default_value = 1.0
        world["flat"].outputs[0].default_value = tuple(SP["flat"]) + (1.0,)
    else:
        world["mix"].inputs[0].default_value = 0.0
        try:
            world["sky"].sun_elevation = math.radians(SP["sun_el"])
            world["sky"].sun_rotation = math.radians(SP["sun_az"])
            world["sky"].dust_density = SP.get("dust", 2.0)
        except Exception as e:
            print("sky params:", e)
    world["bg"].inputs["Strength"].default_value = SP.get("wstr", 1.0)
    el, az = math.radians(SP["sun_el"]), math.radians(SP["sun_az"])
    s = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    sun.rotation_euler = (-s).to_track_quat("-Z", "Y").to_euler()
    sun.data.color = SP["sun_col"]
    sun.data.energy = SP["sun_str"]


def setup_gpu(scn):
    scn.cycles.device = "CPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for dev_type in ("CUDA",):
            try:
                prefs.compute_device_type = dev_type
                prefs.get_devices()
                gpus = [d for d in prefs.devices if d.type == dev_type]
                if gpus:
                    for d in prefs.devices:
                        d.use = (d.type != "CPU")
                    scn.cycles.device = "GPU"
                    print("GPU ativa:", dev_type, [d.name for d in gpus])
                    return dev_type
            except Exception as e:
                print("falha", dev_type, e)
    except Exception as e:
        print("sem GPU:", e)
    print("ATENCAO: renderizando em CPU (bem mais lento)")
    return None


# ----------------------------------------------------------------------------
# principal
# ----------------------------------------------------------------------------
def main():
    args = get_args()
    with open(args.timeline, "r", encoding="utf-8") as fh:
        TL = json.load(fh)
    fps = TL["fps"]
    scenes = TL["scenes"]

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene

    # render
    scn.render.engine = "CYCLES"
    scn.render.resolution_x = TL["w"]
    scn.render.resolution_y = TL["h"]
    scn.render.resolution_percentage = args.scale
    scn.render.fps = fps
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGB"
    scn.render.image_settings.compression = 15
    scn.view_settings.view_transform = "Standard"
    scn.cycles.samples = args.samples
    scn.cycles.use_adaptive_sampling = True
    scn.cycles.adaptive_threshold = 0.04
    scn.cycles.max_bounces = 4
    scn.cycles.diffuse_bounces = 2
    scn.cycles.glossy_bounces = 0
    scn.cycles.transmission_bounces = 0
    scn.cycles.transparent_max_bounces = 2
    scn.cycles.caustics_reflective = False
    scn.cycles.caustics_refractive = False
    scn.cycles.sample_clamp_indirect = 3.0
    scn.render.use_persistent_data = True
    scn.cycles.use_denoising = True
    dev = setup_gpu(scn)
    try:
        scn.cycles.denoiser = "OPENIMAGEDENOISE"
        scn.cycles.denoising_use_gpu = False
    except Exception as e:
        print("denoiser:", e)

    world = build_world()
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.angle = math.radians(3)
    sun = bpy.data.objects.new("Sun", sun_data)
    scn.collection.objects.link(sun)

    # criaturas
    creatures = {}
    used = []
    for sc in scenes:
        if sc["criatura"] not in used:
            used.append(sc["criatura"])
    for key in used:
        C = build_creature(key, CREATURES[key])
        for o in C["objs"]:
            o.hide_render = True
        creatures[key] = C

    croc = None
    if any(sc.get("extra") == "jacare" for sc in scenes):
        croc = build_croc()
        for o in croc["objs"]:
            o.hide_render = True

    # cenários
    set_keys = []
    for sc in scenes:
        if sc["cenario"] not in set_keys:
            set_keys.append(sc["cenario"])
    sets = {}
    set_ox = {}
    for k, key in enumerate(set_keys):
        set_ox[key] = 500.0 * k
        sets[key] = build_set(key, SETS[key], set_ox[key])

    # posição inicial de cada cena (reuso do mesmo cenário -> outro trecho)
    seen = {}
    sx = []
    for sc in scenes:
        n_used = seen.get(sc["cenario"], 0)
        sx.append(set_ox[sc["cenario"]] + 32.0 * n_used)
        seen[sc["cenario"]] = n_used + 1

    # câmera
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 40
    cam_data.sensor_fit = "AUTO"
    cam_data.clip_start = 0.05
    cam_data.clip_end = 600
    cam = bpy.data.objects.new("Cam", cam_data)
    scn.collection.objects.link(cam)
    scn.camera = cam
    target = bpy.data.objects.new("CamTarget", None)
    scn.collection.objects.link(target)
    con = cam.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"

    state = {"scene": -1}

    def anchor_world(C, name, x):
        a = C["anchors"][name]
        return Vector((x + a[0], a[1], a[2]))

    def cam_pose(C, beat, x):
        _, anchor, dist, az, el, lz = beat
        R = C["R"]
        base = anchor_world(C, anchor, x)
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * (R * dist)
        return base + d, base + Vector((0, 0, lz * R))

    def update(scn_, depsgraph=None):
        t = (scn_.frame_current - 1) / fps
        idx = 0
        for i, sc in enumerate(scenes):
            if sc["start"] <= t + 1e-6:
                idx = i
        sc = scenes[idx]
        C = creatures[sc["criatura"]]
        P = C["P"]
        if state["scene"] != idx:
            state["scene"] = idx
            for key, cc in creatures.items():
                for o in cc["objs"]:
                    o.hide_render = (key != sc["criatura"])
            for key, objs in sets.items():
                for o in objs:
                    o.hide_render = (key != sc["cenario"])
            if croc is not None:
                for o in croc["objs"]:
                    o.hide_render = (sc.get("extra") != "jacare") or (o.name.endswith("toothproto"))
            apply_set_look(SETS[sc["cenario"]], world, sun)
        ts, te = sc["start"], sc["end"]
        dt = max(0.0, t - ts)
        d = P["v"] * dt
        x = sx[idx] + d
        # pop-in
        s = max(0.01, back_out(dt / 0.45))
        C["root"].location = (x, 0, 0)
        C["root"].scale = (s, s, s)
        ph = 2 * math.pi * d / C["S"]
        for leg in C["legs"]:
            a = ph + leg["off"]
            leg["hip"].rotation_euler[1] = P["A"] * math.sin(a)
            leg["knee"].rotation_euler[1] = P["K"] * max(0.0, -math.cos(a))
        C["body"].location = (0, 0, 0.012 * math.sin(2 * ph))
        C["head"].rotation_euler[1] = P["pitch"] + 0.05 * math.sin(2 * ph + 0.5)
        C["tail"].rotation_euler[2] = 0.35 * math.sin(ph * 0.5 + 1.0)
        if croc is not None and sc.get("extra") == "jacare":
            croc["root"].location = (x - 2.07, 2.5, 0.10 + 0.010 * math.sin(t * 1.3))
            croc["root"].rotation_euler[2] = -0.45 + 0.04 * math.sin(t * 0.8)
            croc["jaw"].rotation_euler[1] = 0.50 + 0.12 * math.sin(t * 2.4)
        # câmera
        beats = sc["cam"]
        tf = clamp(dt / max(1e-3, te - ts))
        pos, look = None, None
        for k in range(len(beats) - 1):
            if beats[k][0] <= tf <= beats[k + 1][0] or k == len(beats) - 2:
                w = smooth((tf - beats[k][0]) / max(1e-3, beats[k + 1][0] - beats[k][0]))
                p0, l0 = cam_pose(C, beats[k], x)
                p1, l1 = cam_pose(C, beats[k + 1], x)
                pos, look = p0.lerp(p1, w), l0.lerp(l1, w)
                break
        if pos is None:
            pos, look = cam_pose(C, beats[0], x)
        R = C["R"]
        shake = Vector((math.sin(t * 1.7), math.sin(t * 2.3 + 1), math.sin(t * 1.1 + 2))) * (0.004 * R)
        cam.location = pos + shake
        target.location = look

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(update)

    os.makedirs(args.out, exist_ok=True)
    total = int(round(TL["duration"] * fps))
    scn.frame_start = 1
    scn.frame_end = total

    if args.stills:
        scn.render.use_overwrite = True
        for k, sec in enumerate([float(x) for x in args.stills.split(",") if x.strip()]):
            scn.frame_set(int(sec * fps) + 1)
            scn.render.filepath = os.path.join(args.out, "p_%d.png" % k)
            bpy.ops.render.render(write_still=True)
        print("STILLS_OK")
        return

    scn.frame_start = max(1, args.start)
    scn.frame_end = min(total, args.end) if args.end else total
    scn.render.use_overwrite = False
    scn.render.use_placeholder = False
    scn.render.filepath = os.path.join(args.out, "f_")
    bpy.ops.render.render(animation=True)
    print("RENDER_OK")


main()
'''
(WORK / 'blender_scene.py').write_text(BLENDER_SCRIPT, encoding='utf-8')
print('Script do Blender salvo ✅')


# --- divide os frames em blocos (um job do GitHub por bloco) ---
CH = 100
_n = TL["n_frames"]
_chunks = [{"start": s, "end": min(_n, s + CH - 1), "name": "%04d" % s} for s in range(1, _n + 1, CH)]
print("blocos:", len(_chunks), "| frames:", _n)
_gh = os.environ.get("GITHUB_OUTPUT")
if _gh:
    open(_gh, "a").write("matrix=" + json.dumps(_chunks) + "\n")
