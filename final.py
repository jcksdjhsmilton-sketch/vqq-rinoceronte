import glob, json, math, os, subprocess
TL = json.load(open("work/timeline.json", encoding="utf-8"))
esperado = math.ceil(TL["n_frames"] / 100)
segs = sorted(glob.glob("segs/seg_*.mp4"))
print("blocos:", len(segs), "de", esperado)
assert len(segs) == esperado, "faltam blocos: rode de novo os jobs que falharam (Re-run failed jobs)"
with open("list.txt", "w") as f:
    for s in segs:
        f.write("file '%s'\n" % os.path.abspath(s))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "list.txt",
                "-i", "work/narracao.mp3", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", "apad", "-shortest", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                "vqq_rinoceronte.mp4"], check=True)
print("Vídeo final:", round(os.path.getsize("vqq_rinoceronte.mp4") / 1e6, 1), "MB")
