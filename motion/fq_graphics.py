"""Fintiqa social graphics. 1200x1200 px cards in the Fintiqa brand (navy, mint, amber, paper).
Every function takes already-verified numbers and writes a PNG (or MP4 for bars_video)."""
import math, os, subprocess, shutil, textwrap, tempfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Wedge

_FD = "/usr/share/fonts/opentype/inter"
if os.path.isdir(_FD):
    for f in os.listdir(_FD):
        if f.endswith(".otf"):
            fm.fontManager.addfont(os.path.join(_FD, f))
FONT = "Inter"
NAVY, MINT, AMBER, PAPER = "#0E1A2B", "#0FA37F", "#FFB800", "#F4F3EE"
SAND1, SAND2, SAND3, INK2, MIST, GRID = "#E3E0D6", "#D9D6CC", "#C9C5B8", "#3D4756", "#C9CFD8", "#1C2A3E"
BLUE, ORANGE, VIOLET = "#3B5BDB", "#E8590C", "#7A4DD8"
BADGE = [MINT, BLUE, ORANGE, AMBER, NAVY, VIOLET]
S = 1200


def px(n):
    return n * 72 / 100


def canvas(dark=False):
    fig = plt.figure(figsize=(12, 12), dpi=100)
    fig.patch.set_facecolor(NAVY if dark else PAPER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, S)
    ax.set_ylim(S, 0)
    ax.axis("off")
    return fig, ax


def T(ax, x, y, s, size, color, weight="normal", ha="left", va="baseline", **k):
    s = str(s).replace("$", "\\$")
    return ax.text(x, y, s, fontsize=px(size), color=color, fontweight=weight,
                   ha=ha, va=va, family=FONT, **k)


def logo(ax, x, y, size, dark=False):
    k = size / 64
    box, ink = ("#FFFFFF", NAVY) if dark else (NAVY, MINT)
    ax.add_patch(FancyBboxPatch((x, y), size, size, boxstyle=f"round,pad=0,rounding_size={14*k}", fc=box, ec="none"))
    ax.add_patch(Wedge((x + 26 * k, y + 26 * k), 13.5 * k, 0, 360, width=7 * k, fc=ink, ec="none"))
    ax.add_patch(FancyBboxPatch((x + 32.5 * k, y + 16 * k), 7 * k, 36 * k,
                                boxstyle=f"round,pad=0,rounding_size={3.5*k}", fc=ink, ec="none"))
    ax.add_patch(Circle((x + 47.5 * k, y + 48.5 * k), 4.5 * k, fc=AMBER, ec="none"))


def badge(ax, cx, cy, r, name, logo_png=None):
    """Firm mark. Uses a real logo PNG if one is supplied, otherwise a lettermark badge."""
    if logo_png and os.path.exists(logo_png):
        import matplotlib.image as mpimg
        img = mpimg.imread(logo_png)
        ax.imshow(img, extent=(cx - r, cx + r, cy + r, cy - r), zorder=5)
        ax.set_xlim(0, S); ax.set_ylim(S, 0)
        return
    c = BADGE[sum(map(ord, name)) % len(BADGE)]
    ax.add_patch(Circle((cx, cy), r, fc=c, ec="none"))
    T(ax, cx, cy, name.strip()[0].upper(), r * 1.05, NAVY if c == AMBER else "#FFFFFF", "bold",
      ha="center", va="center_baseline")


def usd(v):
    v = float(v)
    if v >= 1e9:
        return f"${v/1e9:.2f}B".replace(".00B", "B")
    if v >= 1e6:
        m = v / 1e6
        return f"${m:.0f}M" if abs(m - round(m)) < 0.05 else f"${m:.1f}M"
    return f"${v/1e3:.0f}K"


def frame(title, sub, source, dark=False, kicker=None):
    fig, ax = canvas(dark)
    fg = "#FFFFFF" if dark else NAVY
    mute = MIST if dark else INK2
    logo(ax, 72, 60, 52, dark)
    T(ax, 136, 100, "fintiqa", 40, fg, "bold")
    if kicker:
        T(ax, 1128, 98, kicker.upper(), 21, AMBER if dark else MINT, "bold", ha="right")
    t = "\n".join(textwrap.wrap(title, 27))
    nl = t.count("\n") + 1
    T(ax, 72, 190, t, 58, fg, "bold", va="top", linespacing=1.06)
    y = 190 + nl * 64 + 16
    ns = 0
    if sub:
        s = "\n".join(textwrap.wrap(sub, 64))
        ns = s.count("\n") + 1
        T(ax, 72, y, s, 27, mute, va="top", linespacing=1.3)
        y += ns * 36 + 8
    ax.plot([72, 1128], [1118, 1118], color=GRID if dark else SAND2, lw=1.5)
    T(ax, 72, 1156, source, 19, mute)
    T(ax, 1128, 1156, "fintiqa.com", 21, fg, "bold", ha="right")
    return fig, ax, y + 36


def save(fig, out):
    fig.savefig(out, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    return out


def hbar_logos(rows, title, sub, source, out, dark=False, kicker=None, progress=1.0, logos=None):
    """rows: [{name, value, right, tag}] ranked bar chart with firm badges."""
    logos = logos or {}
    fig, ax, top = frame(title, sub, source, dark, kicker)
    fg = "#FFFFFF" if dark else NAVY
    mute = MIST if dark else INK2
    n = len(rows)
    rh = min(140, (1090 - top) / n)
    mx = max(r["value"] for r in rows)
    for i, r in enumerate(rows):
        y = top + i * rh
        badge(ax, 106, y + 40, 34, r["name"], logos.get(r["name"]))
        T(ax, 160, y + 30, r["name"], 32, fg, "bold")
        if r.get("tag"):
            T(ax, 160, y + 60, r["tag"], 22, mute)
        bw = max(r["value"] / mx * 680 * progress, 2)
        by = y + 72
        ax.add_patch(FancyBboxPatch((160, by), bw, 34, boxstyle="round,pad=0,rounding_size=8",
                                    fc=MINT if i == 0 else ("#2B3C55" if dark else SAND3), ec="none"))
        T(ax, 160 + bw + 16, by + 17, r["right"], 28, fg, "bold", va="center_baseline", alpha=min(1, progress * 1.3))
    return save(fig, out)


def donut(slices, title, sub, source, out, center_big, center_small, dark=False, kicker=None):
    """slices: [(name, value, right_label)] share of a total."""
    fig, ax, top = frame(title, sub, source, dark, kicker)
    fg = "#FFFFFF" if dark else NAVY
    mute = MIST if dark else INK2
    cols = [MINT, BLUE, AMBER, ORANGE, SAND3, VIOLET]
    tot = sum(s[1] for s in slices)
    cx, cy = 330, top + (1090 - top) / 2
    R = min(270, (1090 - top) / 2 - 6)
    r = R * 0.62
    a = 0.0
    for i, (nm, v, _) in enumerate(slices):
        b = a + v / tot
        g = 0.004
        a0, a1 = a + g, max(b - g, a + g + 0.001)
        steps = max(4, int((a1 - a0) * 240))
        pts = [(cx + R * math.sin(2 * math.pi * (a0 + (a1 - a0) * j / steps)),
                cy - R * math.cos(2 * math.pi * (a0 + (a1 - a0) * j / steps))) for j in range(steps + 1)]
        pts += [(cx + r * math.sin(2 * math.pi * (a0 + (a1 - a0) * j / steps)),
                 cy - r * math.cos(2 * math.pi * (a0 + (a1 - a0) * j / steps))) for j in range(steps, -1, -1)]
        ax.add_patch(Polygon(pts, closed=True, fc=cols[i % len(cols)], ec="none"))
        a = b
    T(ax, cx, cy - 4, center_big, 56, fg, "bold", ha="center", va="center_baseline")
    T(ax, cx, cy + 46, center_small, 22, mute, ha="center", va="center_baseline")
    lh = 92
    y0 = cy - len(slices) * lh / 2 + 10
    for i, (nm, v, right) in enumerate(slices):
        y = y0 + i * lh
        ax.add_patch(FancyBboxPatch((660, y + 4), 28, 28, boxstyle="round,pad=0,rounding_size=6",
                                    fc=cols[i % len(cols)], ec="none"))
        T(ax, 706, y + 28, nm, 30, fg, "bold")
        T(ax, 706, y + 62, f"{right}  |  {v/tot*100:.1f}%", 23, mute)
    return save(fig, out)


def compare(a, b, title, sub, source, out, dark=False, kicker=None):
    """a, b: {name, items:[(company, stage, amount_value)] } side-by-side comparison."""
    fig, ax, top = frame(title, sub, source, dark, kicker)
    fg = "#FFFFFF" if dark else NAVY
    mute = MIST if dark else INK2
    ax.plot([600, 600], [top, 1090], color=GRID if dark else SAND2, lw=1.5)
    sizes = [sum(i[2] for i in e["items"]) for e in (a, b)]
    mx = max(sizes)
    for col, e, sz in ((72, a, sizes[0]), (632, b, sizes[1])):
        badge(ax, col + 32, top + 36, 32, e["name"])
        T(ax, col + 78, top + 48, e["name"], 36, fg, "bold")
        T(ax, col, top + 130, "ROUNDS LED", 20, mute, "bold")
        T(ax, col, top + 214, str(len(e["items"])), 84, fg, "bold")
        T(ax, col, top + 262, "COMBINED SIZE OF ROUNDS LED", 20, mute, "bold")
        T(ax, col, top + 326, usd(sz), 64, MINT if sz == mx else fg, "bold")
        ax.add_patch(FancyBboxPatch((col, top + 346), max(sz / mx * 456, 2), 22, boxstyle="round,pad=0,rounding_size=6",
                                    fc=MINT if sz == mx else (SAND3 if not dark else "#2B3C55"), ec="none"))
        T(ax, col, top + 424, "ROUNDS", 20, mute, "bold")
        for j, (co, st, am) in enumerate(e["items"]):
            yy = top + 466 + j * 48
            T(ax, col, yy, co, 27, fg, "bold")
            T(ax, col + 200, yy, st, 24, mute)
            T(ax, col + 456, yy, usd(am), 27, fg, "bold", ha="right")
    return save(fig, out)


def list_cards(items, title, sub, source, out, dark=False, kicker=None):
    """items: [(heading, text)] numbered breakdown."""
    fig, ax, top = frame(title, sub, source, dark, kicker)
    fg = "#FFFFFF" if dark else NAVY
    mute = MIST if dark else INK2
    n = len(items)
    rh = (1090 - top) / n
    for i, (h, t) in enumerate(items):
        y = top + i * rh
        ax.add_patch(Circle((106, y + rh / 2 - 6), 30, fc=MINT, ec="none"))
        T(ax, 106, y + rh / 2 - 6, str(i + 1), 30, "#FFFFFF", "bold", ha="center", va="center_baseline")
        T(ax, 164, y + rh / 2 - 14, h, 34, fg, "bold", va="bottom")
        T(ax, 164, y + rh / 2 - 6, "\n".join(textwrap.wrap(t, 58)), 25, mute, va="top", linespacing=1.25)
        if i < n - 1:
            ax.plot([72, 1128], [y + rh - 4, y + rh - 4], color=GRID if dark else SAND2, lw=1.2)
    return save(fig, out)


def histogram(values, edges, labels, title, sub, source, out, dark=False, kicker=None):
    """values: raw numbers; edges: bin edges ascending (len = len(labels)+1)."""
    fig, ax, top = frame(title, sub, source, dark, kicker)
    fg = "#FFFFFF" if dark else NAVY
    mute = MIST if dark else INK2
    counts = [sum(1 for v in values if edges[i] <= v < edges[i + 1]) for i in range(len(labels))]
    mc = max(counts) or 1
    base = 1030
    h = base - top - 90
    bw = 1056 / len(labels)
    for i, c in enumerate(counts):
        x = 72 + i * bw + 8
        ht = c / mc * h
        ax.add_patch(FancyBboxPatch((x, base - ht), bw - 16, max(ht, 2), boxstyle="round,pad=0,rounding_size=8",
                                    fc=MINT if c == mc else (SAND3 if not dark else "#2B3C55"), ec="none"))
        T(ax, x + (bw - 16) / 2, base - ht - 12, str(c), 30, fg, "bold", ha="center")
        T(ax, x + (bw - 16) / 2, base + 40, labels[i], 22, mute, ha="center")
    ax.plot([72, 1128], [base, base], color=GRID if dark else SAND3, lw=2)
    return save(fig, out)


def pictogram(rows, unit_label, title, sub, source, out, dark=False, kicker=None, per_icon=1.0):
    """rows: [(label, value)] one coin icon per `per_icon` of value."""
    fig, ax, top = frame(title, sub, source, dark, kicker)
    fg = "#FFFFFF" if dark else NAVY
    mute = MIST if dark else INK2
    rh = (1060 - top) / len(rows)
    for i, (lab, v) in enumerate(rows):
        y = top + i * rh
        T(ax, 72, y + 34, lab, 30, fg, "bold")
        T(ax, 1128, y + 34, f"{v:g}", 30, MINT, "bold", ha="right")
        n = int(round(v / per_icon))
        for j in range(n):
            cx = 90 + (j % 20) * 52
            cy = y + 76 + (j // 20) * 50
            ax.add_patch(Circle((cx, cy), 19, fc=MINT if i == 0 else (AMBER if i == 1 else SAND3), ec="none"))
    T(ax, 72, 1092, f"One icon = {unit_label}", 21, mute)
    return save(fig, out)


def stat(big, label, detail, source, out, kicker=None):
    fig, ax, top = frame(label, detail, source, True, kicker)
    T(ax, 72, top + 150, big, 190, MINT, "bold", va="top")
    return save(fig, out)


def bars_video(rows, title, sub, source, out_mp4, kicker=None, anim=40, hold=2.0, fps=24, logos=None):
    d = tempfile.mkdtemp()
    for i in range(anim + 1):
        t = i / anim
        p = 1 - (1 - t) ** 3
        hbar_logos(rows, title, sub, source, os.path.join(d, f"f{i:03d}.png"), kicker=kicker, progress=p, logos=logos)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(d, "f%03d.png"),
                    "-vf", f"tpad=stop_mode=clone:stop_duration={hold},format=yuv420p", "-c:v", "libx264",
                    "-crf", "22", "-movflags", "+faststart", out_mp4], check=True)
    shutil.rmtree(d, ignore_errors=True)
    return out_mp4
