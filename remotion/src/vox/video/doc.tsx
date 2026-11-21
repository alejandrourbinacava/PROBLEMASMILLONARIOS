import React from 'react';
import {AbsoluteFill} from 'remotion';
import {EP, H, W, c01, expo, miles, suave, useMarca} from './base';
import {Metraje} from './capas';
import {Collage} from './collage';
import {EUROPA, EUROPA_H, EUROPA_W} from './europa';

/**
 * Piel DOCUMENTAL. La regla es la de un documental y la de Moatseek cuando no
 * sale el presentador: imagen real a pantalla completa, UNA cosa cada vez, y
 * el grafico solo cuando el dato es el protagonista.
 *
 *  - nada de tarjetas, marcos, giros ni rebotes: todo entra con un fundido corto
 *  - serif para decir (frases, cifras, anios), palo seco en versalitas para rotular
 *  - un solo acento de color; el amarillo queda para la palabra que importa
 */
export const TINTA = '#F5F2EA';
export const GRIS = 'rgba(245,242,234,0.66)';
export const FONDO = '#090B0C';
export const AMAR = '#FFD23F';
export const ROJO_D = '#FF5A4A';
const SERIF = "'M Serif'";
const SANS = "'D Sans'";
const SOMBRA = '0 2px 18px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.5)';
const MX = 110; // margen lateral

const vis = (te: number, ts: number, a = 9, b = 7) => c01(te / a) * (1 - c01(ts / b));

/** Texto que entra palabra a palabra. *asi* o _asi_ va en amarillo. */
export const Palabras: React.FC<{texto: string; t: number; paso?: number; color?: string}> = ({texto, t, paso = 2, color = AMAR}) => {
  const trozos = texto.split(/(\*[^*]+\*|_[^_]+_)/g).filter(Boolean);
  let n = 0;
  return (
    <>
      {trozos.map((tr, i) => {
        const marca = tr.startsWith('*') || tr.startsWith('_');
        const txt = marca ? tr.slice(1, -1) : tr;
        return (
          <span key={i} style={marca ? {color} : undefined}>
            {txt.split(/(\s+)/).map((w, j) => {
              if (!w.trim()) return w;
              const u = suave((t - n++ * paso) / 8);
              return <span key={j} style={{display: 'inline-block', opacity: u, transform: `translateY(${(1 - u) * 16}px)`}}>{w}</span>;
            })}
          </span>
        );
      })}
    </>
  );
};

/** Antetitulo: filete de color y versalitas. */
const Kicker: React.FC<{t: number; children: React.ReactNode; tam?: number; style?: React.CSSProperties}> = ({t, children, tam = 40, style}) => {
  const m = useMarca();
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 20, opacity: c01(t / 9), ...style}}>
      <div style={{width: 64 * suave(t / 14), height: 4, background: m.claro, flex: 'none'}} />
      <div style={{font: `700 ${tam}px ${SANS}`, letterSpacing: tam * 0.12, textTransform: 'uppercase', color: TINTA, transform: `translateX(${(1 - suave(t / 12)) * -18}px)`}}>{children}</div>
    </div>
  );
};

// ------------------------------------------------------------------ plano de metraje
/**
 * Metraje a sangre con, como mucho, tres cosas encima:
 *   rotulos  identifican lo que se ve (arriba a la izquierda)
 *   frases   la idea que dice la voz, en serif (abajo a la izquierda); cada grupo releva al anterior
 *   datos    una cifra grande con su pie (abajo a la derecha); cada una releva a la anterior
 */
export const Broll: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const frases: any[] = d.frases ?? [];
  const rotulos: any[] = d.rotulos ?? [];
  const datos: any[] = d.datos ?? [];
  const centro = d.pos === 'centro';
  const grupos: number[] = [];
  frases.forEach((l, i) => {
    const g = l.grupo ?? i;
    if (!grupos.includes(g)) grupos.push(g);
  });
  const de = (g: number) => frases.filter((l, i) => (l.grupo ?? i) === g);
  const paso0 = (g: number) => {
    const l = de(g)[0];
    return l.paso ?? frases.indexOf(l);
  };
  const largo = Math.max(1, ...frases.filter((l) => !l.k).map((l) => l.t.replace(/[*_]/g, '').length));
  const base = d.tam ?? (centro ? (largo < 26 ? 140 : largo < 40 ? 116 : 96) : largo < 24 ? 124 : largo < 34 ? 106 : largo < 46 ? 90 : largo < 60 ? 78 : 68);
  return (
    <>
      {centro && <AbsoluteFill style={{background: 'rgba(5,7,8,0.5)'}} />}
      {!centro && (frases.length > 0 || datos.length > 0) && <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(5,7,8,0) 42%, rgba(5,7,8,0.5) 70%, rgba(5,7,8,0.88) 100%)'}} />}
      {rotulos.length > 0 && <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(5,7,8,0.62) 0%, rgba(5,7,8,0.22) 22%, rgba(5,7,8,0) 40%)'}} />}

      {grupos.map((g, gi) => {
        const te = p(paso0(g));
        const sig = grupos[gi + 1];
        const ts = sig !== undefined ? p(paso0(sig)) + 2 : d.frasesSalen !== undefined ? p(d.frasesSalen) : -1;
        if (te < 0 || ts > 9) return null;
        const caja: React.CSSProperties = centro
          ? {left: MX, right: MX, top: 0, bottom: 0, justifyContent: 'center', alignItems: 'center', textAlign: 'center'}
          : {left: MX, right: datos.length ? 760 : 230, bottom: 118, justifyContent: 'flex-end'};
        return (
          <div key={g} style={{position: 'absolute', display: 'flex', flexDirection: 'column', gap: 10, opacity: 1 - c01(ts / 5), ...caja}}>
            {de(g).map((l, i) => {
              const tl = p(l.paso ?? frases.indexOf(l)) - (gi > 0 ? 4 : 0);
              if (l.k) return <div key={i} style={{font: `700 38px ${SANS}`, letterSpacing: 4, textTransform: 'uppercase', color: TINTA, opacity: c01(tl / 9) * 0.92, textShadow: SOMBRA, marginBottom: 4}}>{l.t}</div>;
              return (
                <div key={i} style={{font: `600 ${l.tam ?? base}px/1.08 ${SERIF}`, letterSpacing: -0.5, color: TINTA, textShadow: SOMBRA, visibility: tl < 0 ? 'hidden' : undefined}}>
                  <Palabras texto={l.t} t={tl} />
                </div>
              );
            })}
          </div>
        );
      })}

      {rotulos.map((r, i) => {
        const te = p(r.paso ?? 0);
        const ts = r.sale !== undefined ? p(r.sale) : -1;
        if (te < 0 || ts > 9) return null;
        return (
          <div key={i} style={{position: 'absolute', left: MX, top: 86, maxWidth: 1400, opacity: c01((te - (i > 0 ? 7 : 3)) / 9) * (1 - c01(ts / 5)), transform: `translateX(${(1 - suave((te - 3) / 14)) * -24}px)`}}>
            <div style={{borderLeft: `5px solid ${m.claro}`, paddingLeft: 22}}>
              {r.k && <div style={{font: `700 30px ${SANS}`, letterSpacing: 4, textTransform: 'uppercase', color: m.claro, textShadow: SOMBRA, marginBottom: 4}}>{r.k}</div>}
              <div style={{font: r.serif ? `600 72px/1.1 ${SERIF}` : `700 52px/1.15 ${SANS}`, color: TINTA, textShadow: SOMBRA}}>{r.t}</div>
              {r.sub && <div style={{font: `500 34px/1.25 ${SANS}`, color: 'rgba(245,242,234,0.86)', textShadow: SOMBRA, marginTop: 5}}>{r.sub}</div>}
            </div>
          </div>
        );
      })}

      {datos.map((x, i) => {
        const te = p(x.paso ?? 0);
        const ts = x.sale !== undefined ? p(x.sale) : -1;
        if (te < 0 || ts > 9) return null;
        const txt = x.valor !== undefined ? miles(x.valor * expo((te - 2) / 34), x.dec ?? 0) + (x.sufijo ?? '') : x.t;
        const n = String(x.valor !== undefined ? miles(x.valor, x.dec ?? 0) + (x.sufijo ?? '') : x.t).length;
        const tam = x.tam ?? (n > 9 ? 170 : n > 6 ? 210 : n > 4 ? 260 : 330);
        const izq = x.pos === 'izq';
        return (
          <div key={i} style={{position: 'absolute', left: izq ? MX : undefined, right: izq ? undefined : MX, bottom: 112, textAlign: izq ? 'left' : 'right', opacity: c01((te - (i > 0 ? 5 : 0)) / 8) * (1 - c01(ts / 5)), transform: `translateY(${(1 - suave((te - (i > 0 ? 5 : 0)) / 14)) * 26 - c01(ts / 5) * 14}px)`}}>
            <div style={{font: `600 ${tam}px/0.95 ${SERIF}`, letterSpacing: -4, color: TINTA, textShadow: '0 6px 46px rgba(0,0,0,0.6), 0 2px 4px rgba(0,0,0,0.45)', whiteSpace: 'nowrap', fontVariantNumeric: 'lining-nums'}}>{txt}</div>
            {x.pie && (
              <div style={{font: `600 38px/1.2 ${SANS}`, letterSpacing: 1.5, textTransform: 'uppercase', color: x.color === 'rojo' ? ROJO_D : AMAR, textShadow: SOMBRA, marginTop: 14, maxWidth: 900, marginLeft: izq ? 0 : 'auto', opacity: c01((te - 6) / 8)}}>{x.pie}</div>
            )}
          </div>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------ pantalla partida
const tamCifra = (s: string) => (s.length > 14 ? 92 : s.length > 9 ? 118 : s.length > 6 ? 150 : s.length > 4 ? 200 : 260);
/** Dos imagenes, una frente a otra. La primera llena el cuadro y se aparta cuando entra la segunda. */
export const Duo: React.FC<EP> = ({d, p, t, dur, ctx}) => {
  const m = useMarca();
  if (!ctx) return null;
  const tb = p(d.b.paso ?? 1);
  const u = suave(tb / 16);
  const wa = W - (W / 2 + 3) * u;
  const lados = [
    {x: d.a, left: 0, width: wa, te: p(d.a.paso ?? 0), med: ctx.medios[0]},
    {x: d.b, left: W - (W / 2 - 3) * u, width: W / 2 - 3, te: tb, med: ctx.medios[1]},
  ];
  const zoom = 1.03 + 0.05 * c01(t / Math.max(1, dur));
  return (
    <>
      {lados.map((L, i) => {
        if (!L.med || (i === 1 && tb < -1)) return null;
        const tc = p(L.x.pasoCifra ?? L.x.paso ?? i);
        return (
          <div key={i} style={{position: 'absolute', left: L.left, top: 0, width: L.width, height: H, overflow: 'hidden', background: FONDO}}>
            <div style={{position: 'absolute', inset: 0, transform: `scale(${zoom})`, filter: 'saturate(0.88) contrast(1.06) brightness(0.92)'}}>
              <Metraje m={L.med} abs={ctx.f0 + L.med.en} dur={L.med.sale - L.med.en + 16} fps={ctx.fps} />
            </div>
            <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(5,7,8,0.55) 0%, rgba(5,7,8,0.08) 26%, rgba(5,7,8,0.2) 46%, rgba(5,7,8,0.9) 100%)'}} />
            <div style={{position: 'absolute', left: 70, top: 92, opacity: c01((L.te - 4) / 9)}}>
              <div style={{borderLeft: `5px solid ${i ? m.claro : TINTA}`, paddingLeft: 20, font: `700 42px ${SANS}`, letterSpacing: 4, textTransform: 'uppercase', color: TINTA, textShadow: SOMBRA, whiteSpace: 'nowrap'}}>{L.x.et}</div>
            </div>
            <div style={{position: 'absolute', left: 70, bottom: 118, width: W / 2 - 150, opacity: c01(tc / 9), transform: `translateY(${(1 - suave(tc / 14)) * 24}px)`}}>
              <div style={{font: `600 ${L.x.tam ?? tamCifra(String(L.x.cifra))}px/0.98 ${SERIF}`, letterSpacing: -3, color: TINTA, textShadow: '0 6px 40px rgba(0,0,0,0.6)', fontVariantNumeric: 'lining-nums'}}>{L.x.cifra}</div>
              {L.x.pie && <div style={{font: `600 38px/1.2 ${SANS}`, letterSpacing: 1.5, textTransform: 'uppercase', color: AMAR, textShadow: SOMBRA, marginTop: 14}}>{L.x.pie}</div>}
              {L.x.sub && <div style={{font: `500 34px/1.3 ${SANS}`, color: 'rgba(245,242,234,0.86)', textShadow: SOMBRA, marginTop: 8, opacity: c01((p(L.x.pasoSub ?? L.x.pasoCifra ?? L.x.paso ?? i) - 8) / 9)}}>{L.x.sub}</div>}
            </div>
          </div>
        );
      })}
      {d.sello && p(d.sello.paso) > 0 && (
        <div style={{position: 'absolute', left: 0, right: 0, top: 430, textAlign: 'center', opacity: c01(p(d.sello.paso) / 9)}}>
          <span style={{display: 'inline-block', background: FONDO, color: AMAR, font: `italic 600 66px ${SERIF}`, padding: '12px 40px 18px', boxShadow: '0 20px 60px rgba(0,0,0,0.6)'}}>{d.sello.t}</span>
        </div>
      )}
      {d.nota && <div style={{position: 'absolute', right: 70, bottom: 54, font: `500 22px ${SANS}`, letterSpacing: 1.5, textTransform: 'uppercase', color: 'rgba(245,242,234,0.7)', opacity: c01(p(d.nota.paso ?? 1) / 10)}}>{d.nota.t}</div>}
    </>
  );
};

// ------------------------------------------------------------------ barras
export const BarrasDoc: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const items: any[] = d.items;
  const max = d.max ?? Math.max(...items.map((x) => x.valor));
  const tam = items.length <= 2 ? 170 : items.length === 3 ? 132 : 100;
  const color = (c?: string) => (c === 'acento' ? m.claro : c === 'rojo' ? ROJO_D : c === 'gris' ? 'rgba(245,242,234,0.34)' : TINTA);
  return (
    <div style={{position: 'absolute', left: 150, right: 150, top: 100, bottom: 110, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      <Kicker t={p(0)} style={{marginBottom: items.length > 2 ? 40 : 60}}>{d.titulo}</Kicker>
      {items.map((x, i) => {
        const tt = p(x.paso ?? i);
        const u = expo(tt / 30);
        return (
          <div key={i} style={{marginBottom: items.length > 2 ? 26 : 50, opacity: c01(tt / 8)}}>
            <div style={{font: `500 40px ${SANS}`, color: GRIS, marginBottom: 4}}>{x.et}</div>
            <div style={{display: 'flex', alignItems: 'center', gap: 34}}>
              <div style={{height: Math.round(tam * 0.3), width: Math.max(8, (x.valor / max) * 900 * u), background: color(x.color), flex: 'none'}} />
              <div style={{font: `600 ${tam}px/1 ${SERIF}`, letterSpacing: -2, color: x.color === 'gris' ? 'rgba(245,242,234,0.7)' : x.color === 'acento' ? m.claro : x.color === 'rojo' ? ROJO_D : TINTA, whiteSpace: 'nowrap', fontVariantNumeric: 'lining-nums'}}>{x.texto}</div>
            </div>
          </div>
        );
      })}
      {d.sello && (
        <div style={{position: 'absolute', right: 0, top: d.sello.y ?? 0, textAlign: 'right', opacity: c01(p(d.sello.paso) / 9), transform: `translateY(${(1 - suave(p(d.sello.paso) / 14)) * 20}px)`}}>
          <div style={{font: `italic 600 ${d.sello.tam ?? 150}px/1 ${SERIF}`, color: AMAR, fontVariantNumeric: 'lining-nums'}}>{d.sello.t}</div>
          {d.sello.pie && <div style={{font: `600 32px ${SANS}`, letterSpacing: 2, textTransform: 'uppercase', color: TINTA, marginTop: 8}}>{d.sello.pie}</div>}
        </div>
      )}
      {d.nota && <div style={{font: `500 32px ${SANS}`, color: GRIS, marginTop: 6, opacity: c01(p(d.nota.paso) / 10)}}>{d.nota.t}</div>}
    </div>
  );
};

// ------------------------------------------------------------------ linea de tiempo
export const LineaDoc: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const hitos: any[] = d.hitos;
  const n = hitos.length;
  const x0 = 330;
  const x1 = W - 330;
  const y = 590;
  const paso = n > 1 ? (x1 - x0) / (n - 1) : 0;
  let hasta = 0;
  hitos.forEach((h, i) => {
    if (i > 0) hasta += suave(p(h.paso) / 16);
  });
  const col = (c?: string) => (c === 'rojo' ? ROJO_D : c === 'acento' ? m.claro : TINTA);
  return (
    <>
      <div style={{position: 'absolute', left: 150, top: 130}}><Kicker t={p(0)}>{d.titulo}</Kicker></div>
      <div style={{position: 'absolute', left: x0, top: y - 1, width: x1 - x0, height: 2, background: 'rgba(245,242,234,0.22)'}} />
      <div style={{position: 'absolute', left: x0, top: y - 2, width: paso * hasta, height: 4, background: TINTA}} />
      {hitos.map((h, i) => {
        const t = p(h.paso);
        const cx = x0 + i * paso;
        const ancho = n > 3 ? 400 : 620;
        return (
          <div key={i} style={{position: 'absolute', left: cx - ancho / 2, top: y - 230, width: ancho, textAlign: 'center', opacity: c01(t / 9)}}>
            <div style={{font: `600 ${n > 3 ? 104 : String(h.anio).length > 4 ? 120 : 160}px/1 ${SERIF}`, height: 180, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', color: col(h.color), whiteSpace: 'nowrap', fontVariantNumeric: 'lining-nums', transform: `translateY(${(1 - suave(t / 14)) * 18}px)`}}>{h.anio}</div>
            <div style={{width: 20, height: 20, borderRadius: 10, background: col(h.color), margin: '40px auto 0', boxShadow: `0 0 0 7px ${FONDO}`}} />
            <div style={{font: `500 ${n > 3 ? 34 : 42}px/1.25 ${SANS}`, color: TINTA, marginTop: 30, opacity: c01((t - 5) / 9)}}>{h.t}</div>
          </div>
        );
      })}
      {d.tramo && (
        <div style={{position: 'absolute', left: x0 + d.tramo.de * paso, top: y + 200, width: (d.tramo.a - d.tramo.de) * paso, textAlign: 'center', opacity: c01(p(d.tramo.paso) / 9)}}>
          <div style={{height: 18, borderLeft: `2px solid ${AMAR}`, borderRight: `2px solid ${AMAR}`, borderBottom: `2px solid ${AMAR}`, clipPath: `inset(0 ${(1 - suave(p(d.tramo.paso) / 16)) * 50}% 0 ${(1 - suave(p(d.tramo.paso) / 16)) * 50}%)`}} />
          <div style={{font: `italic 600 112px/1.1 ${SERIF}`, color: AMAR, marginTop: 10, fontVariantNumeric: 'lining-nums'}}>{d.tramo.t}</div>
        </div>
      )}
    </>
  );
};

// ------------------------------------------------------------------ cita
export const CitaDoc: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const partes: string[] = d.partes;
  const largo = partes.join(' ').replace(/[*]/g, '').length;
  const tam = largo < 60 ? 116 : largo < 100 ? 96 : largo < 150 ? 82 : largo < 210 ? 68 : 60;
  const t0 = p(d.desde ?? 0);
  return (
    <div style={{position: 'absolute', left: 200, right: 200, top: 90, bottom: 110, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      {d.previo && <div style={{font: `700 32px ${SANS}`, letterSpacing: 4, textTransform: 'uppercase', color: GRIS, opacity: c01((p(0) - 2) / 10), marginBottom: 6}}>{d.previo}</div>}
      <div style={{font: `700 220px/0.62 ${SERIF}`, color: m.claro, height: 104, marginLeft: -10, opacity: c01(t0 / 8)}}>“</div>
      {partes.map((parte, k) => {
        let n = 0;
        const t = p(k + (d.desde ?? 0));
        return (
          <div key={k} style={{font: `500 ${tam}px/1.2 ${SERIF}`, color: TINTA, marginBottom: 22, visibility: t < 0 ? 'hidden' : undefined}}>
            {parte.split(/(\*[^*]+\*)/g).filter(Boolean).map((tro, i) => {
              const hl = tro.startsWith('*');
              const pal = (hl ? tro.slice(1, -1) : tro).split(/(\s+)/);
              const ini = n;
              return (
                <span key={i} style={hl ? {backgroundImage: `linear-gradient(${AMAR}, ${AMAR})`, backgroundRepeat: 'no-repeat', backgroundPosition: '0 94%', backgroundSize: `${c01((t - ini * 2 - 16) / 12) * 100}% 7%`, boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone'} : undefined}>
                  {pal.map((w, j) => {
                    if (!w.trim()) return w;
                    const u = c01((t - n++ * 2) / 6);
                    return <span key={j} style={{opacity: u}}>{w}</span>;
                  })}
                </span>
              );
            })}
          </div>
        );
      })}
      <div style={{display: 'flex', alignItems: 'center', gap: 22, marginTop: 20, opacity: c01((t0 - 6) / 10)}}>
        <div style={{width: 5, height: 78, background: m.claro}} />
        <div>
          <div style={{font: `700 46px ${SANS}`, color: TINTA}}>{d.autor}</div>
          <div style={{font: `500 32px ${SANS}`, color: GRIS, marginTop: 4}}>{d.cargo} · {d.cuando}</div>
        </div>
      </div>
      {d.nota && <div style={{font: `italic 500 46px/1.25 ${SERIF}`, color: 'rgba(245,242,234,0.86)', marginTop: 40, opacity: c01(p(d.nota.paso) / 10), transform: `translateY(${(1 - suave(p(d.nota.paso) / 14)) * 16}px)`}}>{d.nota.t}</div>}
    </div>
  );
};

// ------------------------------------------------------------------ documento
export const DocumentoDoc: React.FC<EP> = ({d, p, t, dur}) => {
  const te = p(0);
  const u = c01(t / Math.max(1, dur));
  return (
    <>
      <div style={{position: 'absolute', left: 250, right: 250, top: 130, bottom: 170, background: '#F7F4EC', color: '#17191B', padding: '56px 76px', boxShadow: '0 50px 120px rgba(0,0,0,0.7)', opacity: c01(te / 8), transform: `translateY(${(1 - suave(te / 16)) * 40}px) rotate(-0.8deg) scale(${1 + 0.035 * u})`, transformOrigin: '40% 55%'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: '3px solid #17191B', paddingBottom: 16}}>
          <div style={{font: `800 38px ${SANS}`}}>{d.cabecera}</div>
          <div style={{font: `600 26px ${SANS}`, color: '#5B6168', letterSpacing: 2}}>{d.fecha}</div>
        </div>
        <div style={{font: `400 52px/1.46 ${SERIF}`, marginTop: 40, color: '#24282C'}}>
          {d.antes}{' '}
          <span style={{backgroundImage: `linear-gradient(#FFE04A, #FFE04A)`, backgroundRepeat: 'no-repeat', backgroundPosition: '0 62%', backgroundSize: `${c01(p(1) / 22) * 100}% 84%`, boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone', color: '#111', padding: '0 4px'}}>{d.marca}</span>{' '}
          {d.despues}
        </div>
        {d.pie && <div style={{position: 'absolute', left: 76, bottom: 40, font: `500 22px ${SANS}`, color: '#6B7178', letterSpacing: 1.5}}>{d.pie}</div>}
      </div>
      {d.nota && (
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 84, textAlign: 'center', opacity: c01(p(d.nota.paso) / 9)}}>
          <span style={{display: 'inline-block', background: FONDO, padding: '10px 36px 16px', font: `italic 600 60px ${SERIF}`, color: TINTA}}><Palabras texto={d.nota.t} t={p(d.nota.paso)} /></span>
        </div>
      )}
    </>
  );
};

// ------------------------------------------------------------------ mapa real de Europa
const A3: Record<string, string> = {ES: 'ESP', PT: 'PRT', IT: 'ITA', DE: 'DEU', FR: 'FRA', GB: 'GBR'};
export const MapaDoc: React.FC<EP> = ({d, p, t}) => {
  const m = useMarca();
  const luces: Record<string, any> = {};
  (d.luces ?? []).forEach((x: any) => (luces[A3[x.cod] ?? x.cod] = x));
  const esc = d.escala ?? 1.36;
  const alto = EUROPA_H * esc;
  const col = (c?: string) => (c === 'amarillo' ? AMAR : c === 'rojo' ? ROJO_D : m.claro);
  const textos: any[] = d.textos ?? [];
  return (
    <>
      <div style={{position: 'absolute', left: d.mx ?? 750, top: d.my ?? -430, width: EUROPA_W * esc, height: alto, opacity: c01(t / 10), transform: `scale(${1 + 0.03 * c01(t / 300)})`, transformOrigin: '20% 80%'}}>
        <svg viewBox={`0 0 ${EUROPA_W} ${EUROPA_H}`} width={EUROPA_W * esc} height={alto} style={{overflow: 'visible'}}>
          {Object.entries(EUROPA).map(([cod, pais]) => {
            const luz = luces[cod];
            const on = luz ? suave(p(luz.paso) / 14) * (luz.apaga !== undefined ? 1 - suave(p(luz.apaga) / 12) * 0.8 : 1) : 0;
            return <path key={cod} d={pais.d} fill={on > 0.01 ? col(luz.color) : '#1B2125'} fillOpacity={on > 0.01 ? 0.22 + 0.78 * on : 1} stroke={FONDO} strokeWidth={1.3} />;
          })}
          {(d.luces ?? []).map((luz: any, i: number) => {
            const pais = EUROPA[A3[luz.cod] ?? luz.cod];
            if (!pais || !luz.etiqueta) return null;
            const te = p(luz.paso) - 8;
            const ts = luz.apaga !== undefined ? p(luz.apaga) : -1;
            const [cx, cy] = [luz.x ?? pais.c[0], luz.y ?? pais.c[1]];
            const [lx, ly] = [luz.lx ?? cx, luz.ly ?? cy];
            return (
              <g key={i} opacity={c01(te / 9) * (1 - c01(ts / 9) * 0.55)}>
                {(lx !== cx || ly !== cy) && <line x1={cx} y1={cy} x2={lx} y2={ly} stroke={TINTA} strokeWidth={1.4} />}
                <text x={lx} y={ly - 6} textAnchor={luz.ancla ?? 'middle'} style={{font: `700 17px ${SANS}`, letterSpacing: 2, textTransform: 'uppercase'}} fill={luz.dentro && ts <= 0 ? FONDO : TINTA}>{luz.nombre ?? pais.n}</text>
                <text x={lx} y={ly + 30} textAnchor={luz.ancla ?? 'middle'} style={{font: `700 38px ${SERIF}`, textDecoration: ts > 0 ? 'line-through' : undefined}} fill={ts > 0 ? GRIS : luz.dentro ? FONDO : TINTA}>{luz.etiqueta}</text>
              </g>
            );
          })}
        </svg>
      </div>
      <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(9,11,12,0.94) 0%, rgba(9,11,12,0.7) 26%, rgba(9,11,12,0) 44%)'}} />
      <div style={{position: 'absolute', left: MX + 60, top: 150, width: 800}}>
        {d.titulo && <Kicker t={p(0)}>{d.titulo}</Kicker>}
        {d.numero && (
          <div style={{marginTop: 30, opacity: c01(p(d.numero.paso) / 9), transform: `translateY(${(1 - suave(p(d.numero.paso) / 14)) * 24}px)`}}>
            <div style={{font: `600 470px/0.86 ${SERIF}`, color: TINTA, letterSpacing: -8, fontVariantNumeric: 'lining-nums'}}>{d.numero.cifra}</div>
            <div style={{font: `600 60px ${SANS}`, letterSpacing: 6, textTransform: 'uppercase', color: AMAR, marginTop: 6}}>{d.numero.pie}</div>
          </div>
        )}
        {textos.map((x, i) => {
          const te = p(x.paso);
          const sig = textos[i + 1];
          const ts = sig ? p(sig.paso) + 2 : -1;
          if (te < 0 || ts > 9) return null;
          return (
            <div key={i} style={{position: 'absolute', left: 0, top: 90, width: 780, opacity: vis(te, ts)}}>
              {x.anio && <div style={{font: `600 230px/0.95 ${SERIF}`, color: TINTA, letterSpacing: -4, fontVariantNumeric: 'lining-nums'}}>{x.anio}</div>}
              <div style={{font: `600 ${x.anio ? 68 : 84}px/1.1 ${SERIF}`, color: TINTA, marginTop: x.anio ? 14 : 30}}><Palabras texto={x.t} t={te - 3} /></div>
              {x.sub && <div style={{font: `500 34px/1.3 ${SANS}`, color: GRIS, marginTop: 18, opacity: c01((te - 12) / 10)}}>{x.sub}</div>}
            </div>
          );
        })}
      </div>
    </>
  );
};

// ------------------------------------------------------------------ cartela de capitulo
export const CapituloDoc: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const t = p(0);
  const largo = d.titulo.replace(/[*_]/g, '').length;
  return (
    <div style={{position: 'absolute', left: MX + 80, right: MX + 80, top: 0, bottom: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      <div style={{font: `700 30px ${SANS}`, letterSpacing: 10, textTransform: 'uppercase', color: m.claro, opacity: c01((t - 4) / 10)}}>Capítulo {d.num}</div>
      <div style={{width: 150 * suave((t - 6) / 20), height: 3, background: TINTA, margin: '28px 0 34px'}} />
      <div style={{font: `700 ${largo > 26 ? 128 : 160}px/1.02 ${SERIF}`, letterSpacing: -2, color: TINTA}}><Palabras texto={d.titulo} t={t - 8} paso={3} /></div>
      {d.sub && <div style={{font: `500 42px/1.25 ${SANS}`, color: GRIS, marginTop: 36, opacity: c01(p(d.pasoSub ?? 1) / 12)}}>{d.sub}</div>}
    </div>
  );
};

// ------------------------------------------------------------------ dos columnas de cifras
export const ParesDoc: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const Col: React.FC<{x: any; i: number}> = ({x, i}) => {
    const t = p(x.paso ?? i);
    return (
      <div style={{flex: 1, opacity: c01(t / 9), transform: `translateY(${(1 - suave(t / 14)) * 22}px)`}}>
        <div style={{font: `700 40px ${SANS}`, letterSpacing: 6, color: i ? m.claro : GRIS}}>{x.et}</div>
        <div style={{font: `600 ${String(x.cifra).length > 6 ? 170 : 220}px/1 ${SERIF}`, letterSpacing: -4, color: TINTA, marginTop: 10, fontVariantNumeric: 'lining-nums', whiteSpace: 'nowrap'}}>{x.cifra}</div>
        <div style={{font: `600 38px ${SANS}`, letterSpacing: 2, textTransform: 'uppercase', color: TINTA, marginTop: 10}}>{x.pie}</div>
        {(x.subs ?? []).map((s: any, k: number) => (
          <div key={k} style={{font: `600 76px/1.1 ${SERIF}`, color: AMAR, marginTop: 34, opacity: c01(p(s.paso) / 9), fontVariantNumeric: 'lining-nums', whiteSpace: 'nowrap'}}>
            {s.t}
            <span style={{font: `500 30px ${SANS}`, color: GRIS, marginLeft: 18, letterSpacing: 1}}>{s.pie}</span>
          </div>
        ))}
      </div>
    );
  };
  return (
    <div style={{position: 'absolute', left: 190, right: 150, top: 150, bottom: 130, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
      <Kicker t={p(0)} style={{marginBottom: 70}}>{d.titulo}</Kicker>
      <div style={{display: 'flex', gap: 110, alignItems: 'flex-start'}}>
        <Col x={d.a} i={0} />
        <div style={{width: 2, alignSelf: 'stretch', background: 'rgba(245,242,234,0.2)'}} />
        <Col x={d.b} i={1} />
      </div>
    </div>
  );
};

export const TIPOS_DOC: Record<string, React.FC<EP>> = {
  broll: Broll, duo: Duo, barras: BarrasDoc, linea: LineaDoc, cita: CitaDoc, documento: DocumentoDoc, mapa: MapaDoc, capitulo: CapituloDoc, pares: ParesDoc, collage: Collage,
};
