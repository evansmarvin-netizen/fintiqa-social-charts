import { ImageResponse } from '@vercel/og';
export const config = { runtime: 'edge' };

const C = { navy:'#0E1A2B', mint:'#0FA37F', amber:'#FFB800', paper:'#F4F3EE', sand:'#C9C4B8', ink2:'#3D4756', blue:'#3B5BDB', orange:'#E8590C', violet:'#7A4DD8', line:'#D9D6CC' };
const PAL = [C.mint, C.blue, C.amber, C.orange, C.violet, C.sand];
const BADGE = [C.mint, C.orange, C.blue, C.violet, C.amber];
const FONT = 'https://cdn.jsdelivr.net/npm/@fontsource/inter@5.0.8/files/inter-latin-';

const h = (type, style, children, extra) => ({ type, props: { style: { display: 'flex', ...style }, children, ...(extra || {}) } });
const col = (style, ch) => h('div', { flexDirection: 'column', ...style }, ch);
const row = (style, ch) => h('div', { flexDirection: 'row', ...style }, ch);
const txt = (s, style) => h('div', style, String(s));

function badge(name, i, size = 68) {
  return row({ width: size, height: size, borderRadius: size, background: BADGE[i % BADGE.length], alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: size * 0.48, fontWeight: 700, flexShrink: 0 }, String(name).trim().charAt(0).toUpperCase());
}

function frame(d, body, fg, bg, sub2) {
  const dark = !!d.dk;
  return col({ width: 1200, height: 1200, background: bg, color: fg, padding: '60px 72px 0', fontFamily: 'Inter' }, [
    row({ justifyContent: 'space-between', alignItems: 'center', height: 64 }, [
      row({ alignItems: 'center' }, [
        row({ width: 52, height: 52, borderRadius: 12, background: dark ? '#16253A' : C.navy, alignItems: 'center', justifyContent: 'center', marginRight: 16 },
          row({ width: 22, height: 22, borderRadius: 22, border: '6px solid ' + C.mint })),
        txt('fintiqa', { fontSize: 42, fontWeight: 700 }),
      ]),
      txt((d.k || '').toUpperCase(), { fontSize: 22, fontWeight: 700, color: C.mint, letterSpacing: 0.5 }),
    ]),
    txt(d.title || '', { fontSize: 58, fontWeight: 700, lineHeight: 1.18, marginTop: 56, maxWidth: 1000 }),
    txt(d.sub || '', { fontSize: 26, color: sub2, marginTop: 14, marginBottom: 12, maxWidth: 1000, lineHeight: 1.4 }),
    col({ flexGrow: 1, marginTop: 24 }, body),
    row({ borderTop: '2px solid ' + (dark ? '#1C2A3E' : C.line), height: 82, alignItems: 'center', justifyContent: 'space-between', fontSize: 21, color: sub2 }, [
      txt((d.src || 'Source: company announcements, Fintechbits reporting. Tracked by Fintiqa.').slice(0, 95)),
      txt('fintiqa.com', { fontWeight: 700, fontSize: 24, color: fg }),
    ]),
  ]);
}

function bars(d, fg, sub2, dark) {
  const rows = d.rows.slice(0, 6), max = Math.max(...rows.map(r => r.v));
  const slot = Math.min(135, 650 / rows.length);
  return rows.map((r, i) => row({ height: slot, alignItems: 'flex-start' }, [
    badge(r.n, i),
    col({ marginLeft: 20, flexGrow: 1 }, [
      txt(r.n, { fontSize: 32, fontWeight: 700 }),
      r.tag ? txt(r.tag, { fontSize: 21, color: sub2, marginTop: 2 }) : txt(' ', { fontSize: 21 }),
      row({ alignItems: 'center', marginTop: 10 }, [
        row({ width: Math.max(18, (r.v / max) * 700), height: 34, borderRadius: 8, background: i === 0 ? C.mint : (dark ? '#2A3B52' : C.sand) }),
        txt(r.r || String(r.v), { fontSize: 30, fontWeight: 700, marginLeft: 18 }),
      ]),
    ]),
  ]));
}

function arc(cx, cy, r0, r1, a0, a1) {
  const p = (r, a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  const [x0, y0] = p(r1, a0), [x1, y1] = p(r1, a1), [x2, y2] = p(r0, a1), [x3, y3] = p(r0, a0);
  const big = a1 - a0 > Math.PI ? 1 : 0;
  return 'M' + x0 + ' ' + y0 + ' A' + r1 + ' ' + r1 + ' 0 ' + big + ' 1 ' + x1 + ' ' + y1 + ' L' + x2 + ' ' + y2 + ' A' + r0 + ' ' + r0 + ' 0 ' + big + ' 0 ' + x3 + ' ' + y3 + ' Z';
}
function donut(d, fg, sub2, dark) {
  const s = d.slices.slice(0, 6), tot = s.reduce((a, b) => a + b.v, 0), S = 540;
  let a = -Math.PI / 2;
  const paths = s.map((x, i) => {
    const sweep = (x.v / tot) * Math.PI * 2 - 0.012; const p = arc(S / 2, S / 2, 140, 268, a + 0.006, a + 0.006 + sweep);
    a += (x.v / tot) * Math.PI * 2;
    return { type: 'path', props: { d: p, fill: PAL[i % PAL.length] } };
  });
  return row({ alignItems: 'center', marginTop: 20 }, [
    row({ width: S, height: S, position: 'relative' }, [
      { type: 'svg', props: { width: S, height: S, viewBox: '0 0 ' + S + ' ' + S, style: { position: 'absolute', top: 0, left: 0 }, children: paths } },
      col({ position: 'absolute', top: 0, left: 0, width: S, height: S, alignItems: 'center', justifyContent: 'center' }, [
        txt((d.center || [])[0] || '', { fontSize: 54, fontWeight: 700 }),
        txt((d.center || [])[1] || '', { fontSize: 24, color: sub2 }),
      ]),
    ]),
    col({ marginLeft: 36, flexGrow: 1 }, s.map((x, i) => row({ alignItems: 'center', marginBottom: 26 }, [
      row({ width: 28, height: 28, borderRadius: 7, background: PAL[i % PAL.length], marginRight: 16, flexShrink: 0 }),
      col({}, [txt(x.l, { fontSize: 28, fontWeight: 700 }), txt((x.r || '') + '  |  ' + (x.v / tot * 100).toFixed(1) + '%', { fontSize: 22, color: sub2 })]),
    ]))),
  ]);
}

function compare(d, fg, sub2, dark) {
  const side = (o, win) => col({ width: 480 }, [
    row({ alignItems: 'center' }, [badge(o.name, win ? 4 : 2, 64), txt(o.name, { fontSize: 36, fontWeight: 700, marginLeft: 18 })]),
    txt('ROUNDS LED', { fontSize: 20, fontWeight: 700, color: sub2, marginTop: 44 }),
    txt(String(o.items.length), { fontSize: 64, fontWeight: 700 }),
    txt('COMBINED SIZE OF ROUNDS LED', { fontSize: 20, fontWeight: 700, color: sub2, marginTop: 18 }),
    txt(o.total, { fontSize: 64, fontWeight: 700, color: win ? C.mint : fg }),
    row({ width: Math.max(40, o.share * 456), height: 22, borderRadius: 6, background: win ? C.mint : (dark ? '#2A3B52' : C.sand), marginTop: 10 }),
    txt('ROUNDS', { fontSize: 20, fontWeight: 700, color: sub2, marginTop: 44 }),
    ...o.items.map(it => row({ justifyContent: 'space-between', fontSize: 28, marginTop: 14 }, [
      row({}, [txt(it[0], { fontWeight: 700 }), txt(it[1], { color: sub2, marginLeft: 14, fontSize: 24 })]), txt(it[2], { fontWeight: 700 })])),
  ]);
  const win = d.a.share >= d.b.share;
  return row({ justifyContent: 'space-between', marginTop: 10 }, [side(d.a, win), row({ width: 2, background: dark ? '#1C2A3E' : C.line }), side(d.b, !win)]);
}

function list(d, fg, sub2, dark) {
  return d.items.slice(0, 5).map((it, i) => row({ alignItems: 'center', height: 150, borderBottom: i < d.items.length - 1 ? '2px solid ' + (dark ? '#1C2A3E' : C.line) : 'none' }, [
    row({ width: 62, height: 62, borderRadius: 62, background: C.mint, color: '#fff', fontSize: 28, fontWeight: 700, alignItems: 'center', justifyContent: 'center', marginRight: 26, flexShrink: 0 }, String(i + 1)),
    col({}, [txt(it[0], { fontSize: 36, fontWeight: 700 }), txt(it[1], { fontSize: 26, color: sub2, marginTop: 6, maxWidth: 860, lineHeight: 1.35 })]),
  ]));
}

function stat(d, fg, sub2) {
  return col({ justifyContent: 'center', flexGrow: 1 }, [
    txt(d.big, { fontSize: 230, fontWeight: 700, color: C.mint, lineHeight: 1 }),
    txt(d.label, { fontSize: 44, fontWeight: 700, marginTop: 20, maxWidth: 950, lineHeight: 1.25 }),
    txt(d.detail || '', { fontSize: 28, color: sub2, marginTop: 20, maxWidth: 900, lineHeight: 1.4 }),
  ]);
}

function hist(d, fg, sub2, dark) {
  const b = d.bins, max = Math.max(...b.map(x => x.v)), H = 520;
  return col({ marginTop: 20 }, [
    row({ alignItems: 'flex-end', height: H, borderBottom: '3px solid ' + fg }, b.map((x, i) => col({ flexGrow: 1, alignItems: 'center', justifyContent: 'flex-end', marginLeft: i ? 8 : 0 }, [
      txt(x.r || String(x.v), { fontSize: 26, fontWeight: 700, marginBottom: 8 }),
      row({ width: '100%', height: Math.max(6, (x.v / max) * (H - 50)), background: x.v === max ? C.mint : (dark ? '#2A3B52' : C.sand), borderRadius: '8px 8px 0 0' }),
    ]))),
    row({}, b.map((x, i) => txt(x.l, { flexGrow: 1, flexBasis: 0, justifyContent: 'center', fontSize: 21, color: sub2, marginTop: 12, marginLeft: i ? 8 : 0, textAlign: 'center' }))),
  ]);
}

function picto(d, fg, sub2, dark) {
  const per = d.per || 1, unit = d.unit || '';
  return col({ marginTop: 10 }, [
    ...d.rows.slice(0, 5).map((r, i) => {
      const n = Math.min(14, Math.max(1, Math.round(r.v / per)));
      return row({ alignItems: 'center', height: 118 }, [
        col({ width: 230 }, [txt(r.n, { fontSize: 28, fontWeight: 700 }), txt(r.r || String(r.v), { fontSize: 22, color: sub2 })]),
        row({ flexWrap: 'wrap', width: 760 }, Array.from({ length: n }, (_, k) => row({ width: 44, height: 44, borderRadius: 44, background: i === 0 ? C.mint : (dark ? '#3B4D66' : C.sand), marginRight: 10 }))),
      ]);
    }),
    txt('Each circle = ' + unit, { fontSize: 22, color: sub2, marginTop: 20 }),
  ]);
}

const FN = { bars, donut, compare, list, stat, hist, picto };

export default async function handler(req) {
  try {
    const q = new URL(req.url).searchParams.get('d') || '';
    const d = JSON.parse(decodeURIComponent(escape(atob(q.replace(/-/g, '+').replace(/_/g, '/')))));
    const dark = !!d.dk, fg = dark ? C.paper : C.navy, bg = dark ? C.navy : C.paper, sub2 = dark ? '#B8C0CC' : C.ink2;
    const fonts = await Promise.all([400, 700].map(async (w) => ({
      name: 'Inter', weight: w, style: 'normal', data: await (await fetch(FONT + w + '-normal.woff')).arrayBuffer() })));
    let body = FN[d.t](d, fg, sub2, dark);
    if (!Array.isArray(body)) body = [body];
    return new ImageResponse(frame(d, body, fg, bg, sub2), { width: 1200, height: 1200, fonts, headers: { 'cache-control': 'public, max-age=31536000, immutable' } });
  } catch (e) {
    return new Response('chart error: ' + e.message, { status: 400 });
  }
}
