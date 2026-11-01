"""Fintiqa motion graphics. Same JSON spec as /api/chart, rendered to a 1200x1200 MP4.
Usage: python3 motion/fq_motion.py spec.json out.mp4
Spec keys: t (bars|donut|compare|list|stat|hist|picto), k, title, sub, src, dk, plus the type fields."""
import json, math, os, re, shutil, subprocess, sys, tempfile, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fq_graphics import (canvas, T, badge, frame, save, usd, hbar_logos, FancyBboxPatch, Circle, Polygon,
                         NAVY, MINT, AMBER, PAPER, SAND2, SAND3, INK2, MIST, GRID, BLUE, ORANGE, VIOLET)

DSRC = "Source: company announcements, Fintechbits reporting. Tracked by Fintiqa."


def seg(p, a, b):
    return 0.0 if p <= a else 1.0 if p >= b else (p - a) / (b - a)


def ez(x):
    return 1 - (1 - x) ** 3


def common(s):
    return dict(title=s.get("title", ""), sub=s.get("sub", ""), source=(s.get("src") or DSRC)[:95],
                dark=bool(s.get("dk")), kicker=s.get("k"))


def d_bars(s, p, out):
    c = common(s)
    rows = [dict(name=r["n"], value=float(r["v"]), right=r.get("r", str(r["v"])), tag=r.get("tag", "")) for r in s["rows"][:6]]
    hbar_logos(rows, c["title"], c["sub"], c["source"], out, dark=c["dark"], kicker=c["kicker"], progress=ez(p))


def d_donut(s, p, out):
    c = common(s)
    fig, ax, top = frame(c["title"], c["sub"], c["source"], c["dark"], c["kicker"])
    fg = "#FFFFFF" if c["dark"] else NAVY
    mute = MIST if c["dark"] else INK2
    cols = [MINT, BLUE, AMBER, ORANGE, SAND3, VIOLET]
    sl = s["slices"][:6]
    tot = sum(float(x["v"]) for x in sl)
    cx, cy = 330, top + (1090 - top) / 2
    R = min(270, (1090 - top) / 2 - 6)
    r = R * 0.62
    sweep = ez(seg(p, 0, 0.8))
    a = 0.0
    for i, x in enumerate(sl):
        b = a + float(x["v"]) / tot
        a0 = a + 0.004
        a1 = min(b - 0.004, sweep)
        if a1 > a0 + 0.0005:
            n = max(4, int((a1 - a0) * 240))
            ang = lambda j: 2 * math.pi * (a0 + (a1 - a0) * j / n)
            pts = [(cx + R * math.sin(ang(j)), cy - R * math.cos(ang(j))) for j in range(n + 1)]
            pts += [(cx + r * math.sin(ang(j)), cy - r * math.cos(ang(j))) for j in range(n, -1, -1)]
            ax.add_patch(Polygon(pts, closed=True, fc=cols[i % 6], ec="none"))
        a = b
    al = ez(seg(p, 0.55, 0.9))
    T(ax, cx, cy - 4, s["center"][0], 56, fg, "bold", ha="center", va="center_baseline", alpha=al)
    T(ax, cx, cy + 46, s["center"][1], 22, mute, ha="center", va="center_baseline", alpha=al)
    lh = 92
    y0 = cy - len(sl) * lh / 2 + 10
    for i, x in enumerate(sl):
        al = ez(seg(p, 0.1 + i * 0.1, 0.35 + i * 0.1))
        y = y0 + i * lh
        ax.add_patch(FancyBboxPatch((660, y + 4), 28, 28, boxstyle="round,pad=0,rounding_size=6", fc=cols[i % 6], ec="none", alpha=al))
        T(ax, 706, y + 28, x["l"], 30, fg, "bold", alpha=al)
        T(ax, 706, y + 62, f'{x.get("r", "")}  |  {float(x["v"]) / tot * 100:.1f}%', 23, mute, alpha=al)
    save(fig, out)


def d_compare(s, p, out):
    c = common(s)
    fig, ax, top = frame(c["title"], c["sub"], c["source"], c["dark"], c["kicker"])
    fg = "#FFFFFF" if c["dark"] else NAVY
    mute = MIST if c["dark"] else INK2
    ax.plot([600, 600], [top, 1090], color=GRID if c["dark"] else SAND2, lw=1.5)
    for col, e in ((72, s["a"]), (632, s["b"])):
        sh = float(e.get("share", 1))
        win = sh >= 0.999
        badge(ax, col + 32, top + 36, 32, e["name"])
        T(ax, col + 78, top + 48, e["name"], 36, fg, "bold")
        T(ax, col, top + 130, "ROUNDS LED", 20, mute, "bold")
        T(ax, col, top + 214, str(len(e["items"])), 84, fg, "bold", alpha=ez(seg(p, 0, 0.3)))
        T(ax, col, top + 262, "COMBINED SIZE OF ROUNDS LED", 20, mute, "bold")
        T(ax, col, top + 326, e["total"], 64, MINT if win else fg, "bold", alpha=ez(seg(p, 0.15, 0.5)))
        ax.add_patch(FancyBboxPatch((col, top + 346), max(sh * 456 * ez(seg(p, 0.1, 0.7)), 2), 22,
                                    boxstyle="round,pad=0,rounding_size=6",
                                    fc=MINT if win else (SAND3 if not c["dark"] else "#2B3C55"), ec="none"))
        T(ax, col, top + 424, "ROUNDS", 20, mute, "bold")
        for j, (co, st, am) in enumerate(e["items"]):
            al = ez(seg(p, 0.5 + j * 0.12, 0.75 + j * 0.12))
            yy = top + 466 + j * 48
            T(ax, col, yy, co, 27, fg, "bold", alpha=al)
            T(ax, col + 200, yy, st, 24, mute, alpha=al)
            T(ax, col + 456, yy, am, 27, fg, "bold", ha="right", alpha=al)
    save(fig, out)


def d_list(s, p, out):
    c = common(s)
    fig, ax, top = frame(c["title"], c["sub"], c["source"], c["dark"], c["kicker"])
    fg = "#FFFFFF" if c["dark"] else NAVY
    mute = MIST if c["dark"] else INK2
    items = s["items"][:5]
    n = len(items)
    rh = (1090 - top) / n
    for i, (h, t) in enumerate(items):
        a = ez(seg(p, i * 0.15, i * 0.15 + 0.3))
        y = top + i * rh + (1 - a) * 24
        ax.add_patch(Circle((106, y + rh / 2 - 6), 30, fc=MINT, ec="none", alpha=a))
        T(ax, 106, y + rh / 2 - 6, str(i + 1), 30, "#FFFFFF", "bold", ha="center", va="center_baseline", alpha=a)
        T(ax, 164, y + rh / 2 - 14, h, 34, fg, "bold", va="bottom", alpha=a)
        T(ax, 164, y + rh / 2 - 6, "\n".join(textwrap.wrap(t, 58)), 25, mute, va="top", linespacing=1.25, alpha=a)
        if i < n - 1:
            ax.plot([72, 1128], [top + i * rh + rh - 4] * 2, color=GRID if c["dark"] else SAND2, lw=1.2, alpha=a)
    save(fig, out)


def d_stat(s, p, out):
    c = common(s)
    fig, ax, top = frame(s.get("label", c["title"]), s.get("detail", c["sub"]), c["source"], True, c["kicker"])
    big = str(s["big"])
    m = re.match(r"^(\D*?)(\d[\d,]*\.?\d*)(\D*)$", big)
    e = ez(seg(p, 0, 0.8))
    if m:
        num = m.group(2).replace(",", "")
        dec = len(num.split(".")[1]) if "." in num else 0
        v = float(num) * e
        txt = m.group(1) + (f"{v:,.{dec}f}") + m.group(3)
        al = 1
    else:
        txt, al = big, e
    T(ax, 72, top + 150, txt, 190, MINT, "bold", va="top", alpha=al)
    save(fig, out)


def d_hist(s, p, out):
    c = common(s)
    fig, ax, top = frame(c["title"], c["sub"], c["source"], c["dark"], c["kicker"])
    fg = "#FFFFFF" if c["dark"] else NAVY
    mute = MIST if c["dark"] else INK2
    bins = s["bins"][:8]
    mc = max(float(b["v"]) for b in bins) or 1
    base = 1030
    h = base - top - 90
    bw = 1056 / len(bins)
    for i, b in enumerate(bins):
        k = ez(seg(p, i * 0.07, i * 0.07 + 0.6))
        x = 72 + i * bw + 8
        ht = float(b["v"]) / mc * h * k
        top_b = float(b["v"]) == mc
        ax.add_patch(FancyBboxPatch((x, base - ht), bw - 16, max(ht, 2), boxstyle="round,pad=0,rounding_size=8",
                                    fc=MINT if top_b else (SAND3 if not c["dark"] else "#2B3C55"), ec="none"))
        T(ax, x + (bw - 16) / 2, base - ht - 12, b.get("r", str(b["v"])), 30, fg, "bold", ha="center", alpha=k)
        T(ax, x + (bw - 16) / 2, base + 40, b["l"], 22, mute, ha="center")
    ax.plot([72, 1128], [base, base], color=GRID if c["dark"] else SAND3, lw=2)
    save(fig, out)


def d_picto(s, p, out):
    c = common(s)
    fig, ax, top = frame(c["title"], c["sub"], c["source"], c["dark"], c["kicker"])
    fg = "#FFFFFF" if c["dark"] else NAVY
    mute = MIST if c["dark"] else INK2
    rows = s["rows"][:5]
    per = float(s["per"])
    rh = (1060 - top) / len(rows)
    mx = max(min(14, int(round(float(r["v"]) / per))) for r in rows) or 1
    for i, r in enumerate(rows):
        y = top + i * rh
        T(ax, 72, y + 34, r["n"], 30, fg, "bold")
        T(ax, 1128, y + 34, r.get("r", str(r["v"])), 30, MINT, "bold", ha="right", alpha=ez(seg(p, 0.5, 0.9)))
        n = min(14, int(round(float(r["v"]) / per)))
        for j in range(n):
            k = ez(seg(p, j / mx * 0.7, j / mx * 0.7 + 0.25))
            if k > 0:
                ax.add_patch(Circle((90 + j * 62, y + 84), 21 * k, fc=MINT if i == 0 else (AMBER if i == 1 else SAND3), ec="none"))
    T(ax, 72, 1092, f'One circle = {s["unit"]}', 21, mute)
    save(fig, out)


DRAW = dict(bars=d_bars, donut=d_donut, compare=d_compare, list=d_list, stat=d_stat, hist=d_hist, picto=d_picto)


def render(spec, out_mp4, anim=60, hold=3.5, fps=24):
    d = tempfile.mkdtemp()
    fn = DRAW[spec["t"]]
    for i in range(anim + 1):
        fn(spec, i / anim, os.path.join(d, f"f{i:03d}.png"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(d, "f%03d.png"),
                    "-vf", f"tpad=stop_mode=clone:stop_duration={hold},format=yuv420p", "-c:v", "libx264",
                    "-crf", "23", "-movflags", "+faststart", out_mp4], check=True)
    # final still, identical to the last frame, for the fallback image
    shutil.copy(os.path.join(d, f"f{anim:03d}.png"), os.path.splitext(out_mp4)[0] + ".png")
    shutil.rmtree(d, ignore_errors=True)
    return out_mp4


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
    print("wrote", sys.argv[2])
