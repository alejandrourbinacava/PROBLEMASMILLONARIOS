import React from 'react';
import {Plano} from './capas';
import {AMARILLO, EP, Ficha, Marcado, NEGRO, ROJO, Rico, Salta, Sube, Tarjeta, Titulo, atras, c01, expo, miles, suave, useMarca} from './base';

/**
 * Los tipos de plano. Cada uno recibe sus datos (`d`), el fotograma local
 * (`t`) y `p(k)`: los fotogramas que han pasado desde el paso k, que es
 * cuando la voz dice lo que ese elemento ensena.
 */
const useColor = () => {
  const m = useMarca();
  return (c?: string) =>
    c === 'acento' ? m.acento : c === 'rojo' ? ROJO : c === 'gris' ? 'rgba(255,255,255,0.34)' : c === 'blanco' ? '#FFFFFF' : c === 'amarillo' ? AMARILLO : `linear-gradient(90deg, ${m.color}, ${m.claro})`;
};

// ------------------------------------------------------------------ cifra
const Cifra: React.FC<EP> = ({d, p, ancho}) => {
  const m = useMarca();
  const tv = p(d.pasoValor ?? 0);
  const v = d.valor * expo((tv - 6) / 32);
  const txt = (d.prefijo ?? '') + miles(v, d.dec ?? 0);
  const tam = d.tam ?? Math.round((txt.length > 6 ? 250 : 300) * Math.min(1, ancho / 1700));
  return (
    <>
      <div style={{position: 'absolute', left: 90, top: 190, right: 90, color: '#fff'}}>
        {d.pre && (
          <Sube t={p(0) - 2}>
            <div style={{font: "46px/1.15 'M Semi'", opacity: 0.94, maxWidth: 1500}}>{d.pre}</div>
          </Sube>
        )}
        <div style={{font: `${tam}px/1 'M Archivo'`, letterSpacing: -6, marginTop: 14, opacity: c01((tv - 6) / 4), whiteSpace: 'nowrap'}}>
          <Marcado u={(tv - 40) / 12} grueso={11}>{txt}</Marcado>
          <span style={{font: `${Math.round(tam * 0.45)}px 'M Archivo'`, letterSpacing: 0, marginLeft: 26}}>{d.sufijo}</span>
        </div>
        {d.post && (
          <Sube t={p(d.pasoPost ?? 0) - (d.pasoPost ? 0 : 44)} style={{marginTop: 46}}>
            <div style={{font: "54px/1.15 'M Semi'", maxWidth: 1600}}><Rico texto={d.post} t={p(d.pasoPost ?? 0)} t0={d.pasoPost ? 8 : 56} /></div>
          </Sube>
        )}
      </div>
      {d.fichas && (
        <div style={{position: 'absolute', left: 90, top: 660, display: 'flex', gap: 30}}>
          {d.fichas.map((x: any, i: number) => (
            <Ficha key={i} t={p(x.paso ?? i + 1)} cifra={x.cifra} pie={x.pie} color={x.color === 'acento' ? m.acento : undefined} />
          ))}
        </div>
      )}
    </>
  );
};

// ------------------------------------------------------------------ texto
const Texto: React.FC<EP> = ({d, p}) => {
  const lineas: any[] = d.lineas;
  const largo = Math.max(...lineas.map((l) => l.t.replace(/[*_]/g, '').length));
  const base = d.tam ?? (largo < 20 ? 150 : largo < 30 ? 124 : largo < 44 ? 100 : 82);
  return (
    <div style={{position: 'absolute', left: 90, right: 90, top: 150, bottom: 120, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 22, color: '#fff'}}>
      {lineas.map((l, i) => (
        <Sube key={i} t={p(l.paso ?? i)} dy={80}>
          <div style={{font: `${l.tam ?? base}px/1.06 'M Black'`, letterSpacing: -1.5, opacity: l.tenue ? 0.72 : 1}}>
            <Rico texto={l.t} t={p(l.paso ?? i)} t0={10} />
          </div>
        </Sube>
      ))}
    </div>
  );
};

// ------------------------------------------------------------------ cita
const Cita: React.FC<EP> = ({d, p, ancho}) => {
  const m = useMarca();
  const partes: string[] = d.partes;
  const largo = partes.join(' ').length;
  const compacto = ancho < 1500;
  const tam = Math.round((largo < 70 ? 98 : largo < 130 ? 80 : largo < 200 ? 64 : 54) * (compacto ? 0.92 : 1));
  return (
    <Tarjeta t={p(0)} pad={compacto ? '50px 60px' : '60px 76px'} bajo={d.bajo}>
      <div style={{display: 'flex', gap: 60, height: '100%'}}>
        <div style={{width: 330, flex: 'none', display: compacto ? 'none' : 'flex', flexDirection: 'column', alignItems: 'flex-start'}}>
          <Salta t={p(0) - 3}>
            <div style={{width: 210, height: 210, borderRadius: 105, background: `linear-gradient(135deg, ${m.claro}, ${m.color})`, display: 'flex', alignItems: 'center', justifyContent: 'center', font: "92px 'M Archivo'", color: '#fff', border: '6px solid rgba(255,255,255,0.9)'}}>{d.iniciales}</div>
          </Salta>
          <Sube t={p(0) - 8} style={{marginTop: 30}}>
            <div style={{font: "46px/1.1 'M Black'", color: '#fff'}}>{d.autor}</div>
            <div style={{font: "28px/1.25 'M Medium'", color: 'rgba(255,255,255,0.78)', marginTop: 10}}>{d.cargo}</div>
            <div style={{font: "26px 'M Semi'", color: m.acento, marginTop: 14}}>{d.cuando}</div>
          </Sube>
        </div>
        <div style={{flex: 1, position: 'relative'}}>
          <div style={{font: "260px/0.7 'M Serif'", fontWeight: 900, color: m.claro, height: 110, opacity: c01(p(0) / 6)}}>“</div>
          {d.previo && (
            <div style={{position: 'absolute', left: 0, right: 0, top: 118, font: "58px/1.16 'M Black'", color: 'rgba(255,255,255,0.5)', opacity: c01((p(0) - 4) / 8) * (1 - c01((p(d.desde ?? 0) + 4) / 6)), transform: `translateY(${-c01((p(d.desde ?? 0) + 4) / 8) * 30}px)`}}>{d.previo}</div>
          )}
          {partes.map((parte, k) => {
            let n = 0;
            const t = p(k + (d.desde ?? 0));
            return (
              <div key={k} style={{font: `${tam}px/1.22 'M Semi'`, color: '#fff', marginBottom: 26}}>
                {parte.split(/(\*[^*]+\*)/g).filter(Boolean).map((tro, i) => {
                  const hl = tro.startsWith('*');
                  const pal = (hl ? tro.slice(1, -1) : tro).split(/(\s+)/);
                  return (
                    <span key={i} style={hl ? {background: `linear-gradient(${AMARILLO}, ${AMARILLO}) no-repeat 0 92% / ${c01((t - n * 2 - 14) / 10) * 100}% 18%`} : undefined}>
                      {pal.map((w, j) => {
                        if (!w.trim()) return w;
                        const u = c01((t - n++ * 2) / 5);
                        return <span key={j} style={{opacity: u}}>{w}</span>;
                      })}
                    </span>
                  );
                })}
              </div>
            );
          })}
          {compacto && (
            <div style={{position: 'absolute', left: 170, top: 6, display: 'flex', alignItems: 'center', gap: 20, opacity: c01((p(0) - 8) / 8)}}>
              <div style={{width: 10, height: 74, borderRadius: 5, background: m.acento}} />
              <div>
                <div style={{font: "44px/1.1 'M Black'", color: '#fff'}}>{d.autor}</div>
                <div style={{font: "27px/1.25 'M Medium'", color: 'rgba(255,255,255,0.8)', marginTop: 4}}>{d.cargo} · <span style={{color: m.acento}}>{d.cuando}</span></div>
              </div>
            </div>
          )}
          {d.nota && (
            <div style={{position: 'absolute', left: 0, bottom: 0, font: "44px/1.25 'M Semi'", color: 'rgba(255,255,255,0.86)', opacity: c01(p(d.nota.paso ?? 0) / 8)}}>{d.nota.t}</div>
          )}
        </div>
      </div>
    </Tarjeta>
  );
};

// ------------------------------------------------------------------ mapa de teselas
const PAISES: [string, number, number][] = [
  ['IS', 0, 0], ['NO', 4, 0], ['SE', 5, 0], ['FI', 6, 0],
  ['IE', 1, 1], ['GB', 2, 1], ['DK', 4, 1], ['EE', 6, 1],
  ['BE', 2, 2], ['NL', 3, 2], ['DE', 4, 2], ['PL', 5, 2], ['LV', 6, 2],
  ['FR', 2, 3], ['LU', 3, 3], ['CZ', 4, 3], ['SK', 5, 3], ['LT', 6, 3],
  ['PT', 0, 4], ['ES', 1, 4], ['CH', 3, 4], ['AT', 4, 4], ['HU', 5, 4], ['RO', 6, 4],
  ['IT', 3, 5], ['SI', 4, 5], ['HR', 5, 5], ['BG', 6, 5],
  ['GR', 5, 6],
];
const Mapa: React.FC<EP> = ({d, p, t}) => {
  const m = useMarca();
  const L = 112;
  const G = 14;
  const luces: Record<string, any> = {};
  (d.luces ?? []).forEach((x: any) => (luces[x.cod] = x));
  return (
    <>
      <div style={{position: 'absolute', left: 90, top: 170, width: 780, color: '#fff'}}>
        {d.titulo && <Titulo t={p(0) - 2} tam={62}><Rico texto={d.titulo} t={p(0)} /></Titulo>}
        {d.numero && (
          <>
            <div style={{font: "400px/0.92 'M Archivo'", marginTop: 22, opacity: c01(p(d.numero.paso) / 4), transform: `scale(${0.5 + 0.5 * atras(p(d.numero.paso) / 14, 2.2)})`, transformOrigin: 'left center'}}>
              {d.numero.cifra}
            </div>
            <Sube t={p(d.numero.paso) - 8}>
              <div style={{font: "62px/1.1 'M Black'"}}><Marcado u={(p(d.numero.paso) - 18) / 10}>{d.numero.pie}</Marcado></div>
            </Sube>
          </>
        )}
        {d.panel && (
          <div style={{marginTop: 34, display: 'flex', flexDirection: 'column', gap: 18}}>
            {d.panel.items.map((x: any, i: number) => (
              <Sube key={i} t={p(x.paso)}>
                <div style={{background: 'rgba(8,16,12,0.78)', borderRadius: 22, padding: '20px 28px', borderLeft: `10px solid ${x.color === 'rojo' ? ROJO : m.acento}`}}>
                  <div style={{font: "46px/1.1 'M Black'"}}>{x.t}</div>
                  {x.sub && <div style={{font: "28px/1.25 'M Medium'", opacity: 0.85, marginTop: 6}}>{x.sub}</div>}
                </div>
              </Sube>
            ))}
          </div>
        )}
      </div>
      <div style={{position: 'absolute', left: 940, top: 150, width: 7 * (L + G), height: 7 * (L + G), display: d.sinMapa ? 'none' : undefined}}>
        {PAISES.map(([cod, cx, cy]) => {
          const luz = luces[cod];
          const ti = t - 6 - (cx + cy) * 2;
          const on = luz ? suave(p(luz.paso) / 10) * (luz.apaga !== undefined ? 1 - suave(p(luz.apaga) / 10) * 0.75 : 1) : 0;
          const col = luz?.color === 'acento' ? m.acento : luz?.color === 'rojo' ? ROJO : '#FFFFFF';
          const tinta = luz?.color && luz.color !== 'blanco' ? '#fff' : m.oscuro;
          const apagado = luz?.apaga !== undefined && p(luz.apaga) > 0;
          return (
            <div
              key={cod}
              style={{
                position: 'absolute', left: cx * (L + G), top: cy * (L + G), width: L, height: L, borderRadius: 22,
                background: on > 0.02 ? col : 'rgba(255,255,255,0.13)', opacity: c01(ti / 4) * (on > 0.02 ? 0.25 + 0.75 * on : 1),
                border: '2px solid rgba(255,255,255,0.2)', transform: `scale(${(0.4 + 0.6 * atras(ti / 11, 2)) * (1 + 0.16 * on)})`,
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                color: on > 0.4 ? tinta : 'rgba(255,255,255,0.72)', boxShadow: on > 0.05 ? `0 0 ${46 * on}px rgba(255,255,255,${0.5 * on})` : undefined, zIndex: on > 0 ? 2 : 1,
              }}
            >
              <div style={{font: `${luz?.etiqueta && on > 0.4 ? 26 : 32}px 'M Semi'`, letterSpacing: 2, textDecoration: apagado ? 'line-through' : undefined}}>{cod}</div>
              {luz?.etiqueta && on > 0.4 && <div style={{font: "30px/1 'M Archivo'"}}>{luz.etiqueta}</div>}
            </div>
          );
        })}
      </div>
    </>
  );
};

// ------------------------------------------------------------------ barras
const Barras: React.FC<EP> = ({d, p, ancho}) => {
  const col = useColor();
  const items: any[] = d.items;
  const max = d.max ?? Math.max(...items.map((x) => x.valor));
  const alto = items.length <= 2 ? 104 : items.length === 3 ? 84 : 66;
  return (
    <Tarjeta t={p(0)} bajo={d.bajo}>
      <Titulo t={p(0) - 3} tam={56} style={{marginBottom: items.length > 3 ? 26 : 40}}><Rico texto={d.titulo} t={p(0)} /></Titulo>
      {items.map((x, i) => {
        const tt = p(x.paso ?? i);
        const u = expo(tt / 26);
        return (
          <div key={i} style={{marginBottom: items.length > 3 ? 24 : 38, opacity: c01(tt / 4)}}>
            <div style={{font: `${items.length > 3 ? 30 : 36}px 'M Semi'`, color: 'rgba(255,255,255,0.86)', marginBottom: 10}}>{x.et}</div>
            <div style={{display: 'flex', alignItems: 'center', gap: 28}}>
              <div style={{height: alto, width: Math.max(12, (x.valor / max) * (ancho - 840) * u), borderRadius: 18, background: col(x.color)}} />
              <div style={{font: `${alto}px/1 'M Archivo'`, color: '#fff', whiteSpace: 'nowrap'}}>{x.texto}</div>
            </div>
          </div>
        );
      })}
      {d.sello && (
        <div style={{position: 'absolute', right: ancho < 1500 ? 50 : 70, top: d.sello.abajo ? undefined : 44, bottom: d.sello.abajo ? 40 : undefined, background: AMARILLO, color: NEGRO, borderRadius: 22, padding: '16px 30px', font: "56px 'M Archivo'", opacity: c01(p(d.sello.paso) / 4), transform: `scale(${0.5 + 0.5 * atras(p(d.sello.paso) / 12, 2.4)}) rotate(-3deg)`}}>{d.sello.t}</div>
      )}
      {d.pregunta && (
        <div style={{position: 'absolute', left: 70, bottom: 46, right: 70, font: "84px/1 'M Black'", color: '#fff', opacity: c01(p(d.pregunta.paso) / 5), transform: `translateY(${(1 - atras(p(d.pregunta.paso) / 14)) * 60}px)`}}>
          <Rico texto={d.pregunta.t} t={p(d.pregunta.paso)} t0={14} />
        </div>
      )}
      {d.nota && <div style={{position: 'absolute', left: 70, bottom: 44, font: "32px 'M Medium'", color: 'rgba(255,255,255,0.8)', opacity: c01(p(d.nota.paso) / 8)}}>{d.nota.t}</div>}
    </Tarjeta>
  );
};

// ------------------------------------------------------------------ versus
const Lado: React.FC<{x: any; t: number; destaca?: boolean}> = ({x, t, destaca}) => {
  const m = useMarca();
  return (
    <div style={{flex: 1, opacity: c01(t / 4), transform: `scale(${0.7 + 0.3 * atras(t / 13, 1.8)})`, background: destaca ? (x.color === 'acento' ? m.acento : '#FFFFFF') : 'rgba(8,16,12,0.8)', color: destaca && x.color !== 'acento' ? m.oscuro : '#fff', borderRadius: 36, padding: '40px 46px', border: '2px solid rgba(255,255,255,0.18)', boxShadow: '0 24px 70px rgba(0,0,0,0.35)', minHeight: 430}}>
      <div style={{font: "34px 'M Semi'", letterSpacing: 4, textTransform: 'uppercase', opacity: 0.85}}>{x.et}</div>
      <div style={{font: `${String(x.cifra).length > 7 ? 104 : String(x.cifra).length > 4 ? 136 : 190}px/1 'M Archivo'`, letterSpacing: -3, marginTop: 16, whiteSpace: 'nowrap'}}>{x.cifra}</div>
      <div style={{font: "42px/1.15 'M Black'", marginTop: 10}}>{x.pie}</div>
      {(x.subs ?? (x.sub ? [{t: x.sub}] : [])).map((s: any, i: number) => (
        <div key={i} style={{font: "32px/1.25 'M Medium'", opacity: 0.86 * c01((s.t0 ?? t) / 6), marginTop: 12}}>{s.t}</div>
      ))}
    </div>
  );
};
const Versus: React.FC<EP> = ({d, p}) => {
  const tb = p(d.b.paso ?? 1);
  return (
    <>
      {d.titulo && <div style={{position: 'absolute', left: 90, top: 160, right: 90}}><Titulo t={p(0) - 2}><Rico texto={d.titulo} t={p(0)} /></Titulo></div>}
      <div style={{position: 'absolute', left: 90, right: 90, top: d.titulo ? 290 : 220, display: 'flex', alignItems: 'center', gap: 34}}>
        <Lado x={{...d.a, subs: d.a.subs?.map((s: any) => ({...s, t0: p(s.paso ?? 0)}))}} t={p(d.a.paso ?? 0)} />
        <div style={{font: "120px 'M Archivo'", color: '#fff', opacity: c01(tb / 4), transform: `scale(${atras(tb / 10, 2.4)})`}}>{d.signo ?? '→'}</div>
        <Lado x={{...d.b, subs: d.b.subs?.map((s: any) => ({...s, t0: p(s.paso ?? d.b.paso ?? 1)}))}} t={tb} destaca />
      </div>
      {d.sello && (
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 150, textAlign: 'center', opacity: c01(p(d.sello.paso) / 4), transform: `scale(${0.5 + 0.5 * atras(p(d.sello.paso) / 12, 2.4)})`}}>
          <span style={{background: AMARILLO, color: NEGRO, borderRadius: 22, padding: '14px 34px', font: "60px 'M Archivo'", display: 'inline-block', transform: 'rotate(-2deg)'}}>{d.sello.t}</span>
        </div>
      )}
    </>
  );
};

// ------------------------------------------------------------------ linea de tiempo
const Linea: React.FC<EP> = ({d, p, ancho}) => {
  const m = useMarca();
  const hitos: any[] = d.hitos;
  const n = hitos.length;
  const x0 = 280;
  const x1 = ancho - 280;
  const y = 600;
  const paso = n > 1 ? (x1 - x0) / (n - 1) : 0;
  const ultimo = Math.max(...hitos.map((h) => (p(h.paso) > 0 ? hitos.indexOf(h) : -1)));
  const avance = c01(ultimo / Math.max(1, n - 1));
  const chico = n > 5;
  return (
    <>
      {d.titulo && <div style={{position: 'absolute', left: 90, top: 160, right: 90}}><Titulo t={p(0) - 2}><Rico texto={d.titulo} t={p(0)} /></Titulo></div>}
      <div style={{position: 'absolute', left: x0, top: y - 5, width: x1 - x0, height: 10, borderRadius: 5, background: 'rgba(255,255,255,0.25)'}} />
      <div style={{position: 'absolute', left: x0, top: y - 5, width: (x1 - x0) * avance, height: 10, borderRadius: 5, background: '#fff'}} />
      {hitos.map((h, i) => {
        const t = p(h.paso);
        const cx = x0 + i * paso;
        const col = h.color === 'rojo' ? ROJO : h.color === 'acento' ? m.acento : '#FFFFFF';
        return (
          <div key={i} style={{position: 'absolute', left: cx - (chico ? 115 : 170), top: y - 190, width: chico ? 230 : 340, textAlign: 'center', color: '#fff', opacity: c01(t / 4)}}>
            <div style={{font: `${chico || String(h.anio).length > 4 ? 62 : 86}px/1 'M Archivo'`, whiteSpace: 'nowrap', height: chico ? 62 : 86, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', transform: `translateY(${(1 - atras(t / 12)) * 40}px)`, color: h.color ? col : '#fff', textDecoration: h.tachado ? 'line-through' : undefined}}>{h.anio}</div>
            <div style={{width: 46, height: 46, borderRadius: 23, background: col, border: `8px solid ${m.oscuro}`, margin: `${chico ? 53 : 29}px auto 0`, transform: `scale(${atras(t / 10, 2.6)})`}} />
            <div style={{font: `${chico ? 28 : 36}px/1.2 'M Semi'`, marginTop: 26, opacity: c01((t - 6) / 6)}}>{h.t}</div>
          </div>
        );
      })}
      {d.tramo && (
        <div style={{position: 'absolute', left: x0 + d.tramo.de * paso, top: y + 220, width: (d.tramo.a - d.tramo.de) * paso, textAlign: 'center', opacity: c01(p(d.tramo.paso) / 5), transform: `scale(${0.7 + 0.3 * atras(p(d.tramo.paso) / 12, 2)})`}}>
          <div style={{height: 22, borderLeft: '6px solid #fff', borderRight: '6px solid #fff', borderBottom: '6px solid #fff', borderRadius: '0 0 14px 14px'}} />
          <span style={{display: 'inline-block', marginTop: 16, background: AMARILLO, color: NEGRO, borderRadius: 20, padding: '10px 30px', font: "60px 'M Archivo'"}}>{d.tramo.t}</span>
        </div>
      )}
    </>
  );
};

// ------------------------------------------------------------------ lista
const Lista: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const items: any[] = d.items;
  const dos = d.columnas === 2;
  const tam = items.length > 4 && !dos ? 38 : 48;
  return (
    <>
      <div style={{position: 'absolute', left: 90, top: 160, right: 90}}><Titulo t={p(0) - 2} tam={64}><Rico texto={d.titulo} t={p(0)} /></Titulo></div>
      <div style={{position: 'absolute', left: 90, right: 90, top: items.length > 4 ? 262 : 290, display: 'grid', gridTemplateColumns: dos ? '1fr 1fr' : '1fr', gap: items.length > 4 ? 12 : 24}}>
        {items.map((x, i) => {
          const t = p(x.paso ?? i);
          return (
            <div key={i} style={{opacity: c01(t / 4), transform: `translateX(${(1 - atras(t / 12, 1.2)) * -70}px)`, background: 'rgba(8,16,12,0.78)', borderRadius: 26, padding: items.length > 4 ? '13px 28px' : '26px 34px', display: 'flex', alignItems: 'center', gap: 28, border: '2px solid rgba(255,255,255,0.12)'}}>
              <div style={{flex: 'none', width: 64, height: 64, borderRadius: 32, background: x.color === 'rojo' ? ROJO : x.color === 'acento' ? m.acento : m.claro, color: '#fff', font: "36px 'M Archivo'", display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{x.icono ?? i + 1}</div>
              <div style={{flex: 1, color: '#fff'}}>
                <div style={{font: `${tam}px/1.12 'M Black'`}}><Rico texto={x.t} t={t} t0={10} /></div>
                {x.sub && <div style={{font: `${items.length > 4 ? 26 : 30}px/1.25 'M Medium'`, opacity: 0.84, marginTop: items.length > 4 ? 2 : 6}}>{x.sub}</div>}
              </div>
              {x.etiqueta && <div style={{flex: 'none', background: AMARILLO, color: NEGRO, borderRadius: 18, padding: '8px 22px', font: "40px 'M Archivo'"}}>{x.etiqueta}</div>}
            </div>
          );
        })}
      </div>
    </>
  );
};

// ------------------------------------------------------------------ documento
const Documento: React.FC<EP> = ({d, p, ancho}) => {
  const m = useMarca();
  const t = p(0);
  return (
    <>
      <div style={{position: 'absolute', left: ancho < 1500 ? 90 : 230, right: ancho < 1500 ? 40 : 230, top: 150, bottom: d.bajo ?? 130, background: '#FBFAF6', borderRadius: 26, padding: '54px 70px', color: '#16181A', boxShadow: '0 40px 100px rgba(0,0,0,0.45)', opacity: c01(t / 4), transform: `translateY(${(1 - atras(t / 14, 1.2)) * 120}px) rotate(${-1.2 + (1 - suave(t / 14)) * 3}deg)`}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: '4px solid #16181A', paddingBottom: 16}}>
          <div style={{font: "44px 'M Black'"}}>{d.cabecera}</div>
          <div style={{font: "28px 'M Semi'", color: '#5B6168', letterSpacing: 2}}>{d.fecha}</div>
        </div>
        {d.titular && <div style={{font: "900 58px/1.1 'M Serif'", marginTop: 30}}>{d.titular}</div>}
        <div style={{font: "48px/1.42 'M Medium'", marginTop: 36, color: '#2A2E33'}}>
          {d.antes}{' '}
          <span style={{background: `linear-gradient(${AMARILLO}, ${AMARILLO}) no-repeat 0 60% / ${c01(p(1) / 18) * 100}% 88%`, boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone', color: '#111', padding: '0 4px'}}>{d.marca}</span>{' '}
          {d.despues}
        </div>
        {d.pie && <div style={{position: 'absolute', left: 70, bottom: 40, font: "24px 'M Medium'", color: '#6B7178', letterSpacing: 1.5}}>{d.pie}</div>}
      </div>
      {d.nota && (
        <div style={{position: 'absolute', right: 150, bottom: 170, background: m.acento, color: '#fff', borderRadius: 26, padding: '22px 36px', font: "54px/1.1 'M Black'", maxWidth: 760, opacity: c01(p(d.nota.paso) / 4), transform: `scale(${0.5 + 0.5 * atras(p(d.nota.paso) / 12, 2.2)}) rotate(-3deg)`, boxShadow: '0 20px 50px rgba(0,0,0,0.4)'}}>{d.nota.t}</div>
      )}
    </>
  );
};

// ------------------------------------------------------------------ capitulo
const Capitulo: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const t = p(0);
  return (
    <div style={{position: 'absolute', left: 90, right: 90, top: 150, bottom: 120, display: 'flex', flexDirection: 'column', justifyContent: 'center', color: '#fff'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 26, opacity: c01(t / 5), transform: `translateX(${(1 - suave(t / 12)) * -80}px)`}}>
        <div style={{background: m.acento, borderRadius: 20, padding: '8px 28px', font: "44px 'M Archivo'"}}>{d.num}</div>
        <div style={{height: 6, width: 300 * suave((t - 4) / 16), background: '#fff', borderRadius: 3}} />
      </div>
      <Sube t={t - 5} dy={90} style={{marginTop: 30}}>
        <div style={{font: `${d.tam ?? (d.titulo.length > 26 ? 128 : 160)}px/1.02 'M Black'`, letterSpacing: -3}}><Rico texto={d.titulo} t={t} t0={18} /></div>
      </Sube>
      {d.sub && (
        <Sube t={p(d.pasoSub ?? 1)} style={{marginTop: 34}}>
          <div style={{font: "52px/1.2 'M Semi'", opacity: 0.92, maxWidth: 1500}}>{d.sub}</div>
        </Sube>
      )}
    </div>
  );
};

// ------------------------------------------------------------------ flujo
const Flujo: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const nodos: any[] = d.nodos;
  return (
    <>
      <div style={{position: 'absolute', left: 90, top: 170, right: 90, color: '#fff'}}>
        {d.tachado && (
          <div style={{font: "92px/1.05 'M Black'", position: 'relative', display: 'inline-block', opacity: c01(p(0) / 5) * (1 - 0.45 * c01(p(1) / 10))}}>
            {d.tachado}
            <div style={{position: 'absolute', left: -10, top: '52%', height: 12, width: `${c01(p(1) / 10) * 104}%`, background: ROJO, borderRadius: 6}} />
          </div>
        )}
        {d.titulo && <Titulo t={p(d.pasoTitulo ?? 0) - 2} tam={d.tachado ? 76 : 64} style={{marginTop: d.tachado ? 26 : 0}}><Rico texto={d.titulo} t={p(d.pasoTitulo ?? 0)} /></Titulo>}
      </div>
      <div style={{position: 'absolute', left: 90, right: 90, top: d.tachado ? 520 : 400, display: 'flex', alignItems: 'stretch', gap: 0}}>
        {nodos.map((x, i) => {
          const t = p(x.paso ?? i);
          const ult = i === nodos.length - 1;
          return (
            <React.Fragment key={i}>
              <div style={{flex: 1, opacity: c01(t / 4), transform: `scale(${0.6 + 0.4 * atras(t / 12, 2)})`, background: x.color === 'acento' ? m.acento : x.color === 'blanco' ? '#fff' : 'rgba(8,16,12,0.82)', color: x.color === 'blanco' ? m.oscuro : '#fff', borderRadius: 30, padding: '34px 30px', textAlign: 'center', border: '2px solid rgba(255,255,255,0.16)', boxShadow: '0 20px 60px rgba(0,0,0,0.3)'}}>
                <div style={{font: `${nodos.length > 3 ? 44 : 56}px/1.1 'M Black'`}}>{x.t}</div>
                {x.sub && <div style={{font: "30px/1.25 'M Medium'", opacity: 0.86, marginTop: 10}}>{x.sub}</div>}
              </div>
              {!ult && (
                <div style={{flex: 'none', width: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', font: "80px 'M Archivo'", color: '#fff', opacity: c01(p(nodos[i + 1].paso ?? i + 1) / 4)}}>→</div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </>
  );
};

// ------------------------------------------------------------------ anillos
const Anillos: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const items: any[] = d.items;
  const R = items.length > 1 ? 150 : 190;
  const C = 2 * Math.PI * R;
  return (
    <>
      {d.titulo && <div style={{position: 'absolute', left: 90, top: 160, right: 90}}><Titulo t={p(0) - 2}><Rico texto={d.titulo} t={p(0)} /></Titulo></div>}
      <div style={{position: 'absolute', left: 90, right: 90, top: d.titulo ? 290 : 220, display: 'flex', justifyContent: items.length > 1 ? 'space-around' : 'flex-start', gap: 80, alignItems: 'center'}}>
        {items.map((x, i) => {
          const t = p(x.paso ?? i);
          const u = suave(t / 34);
          const fr = c01(x.valor / (x.max ?? 100)) * u;
          const col = x.color === 'acento' ? m.acento : x.color === 'rojo' ? ROJO : '#FFFFFF';
          return (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 50, opacity: c01(t / 4), color: '#fff'}}>
              <div style={{position: 'relative', width: (R + 50) * 2, height: (R + 50) * 2, flex: 'none'}}>
                <svg width={(R + 50) * 2} height={(R + 50) * 2} style={{transform: 'rotate(-90deg)'}}>
                  <circle cx={R + 50} cy={R + 50} r={R} fill="none" stroke="rgba(8,16,12,0.55)" strokeWidth={70} />
                  <circle cx={R + 50} cy={R + 50} r={R} fill="none" stroke={col} strokeWidth={70} strokeDasharray={`${C * fr} ${C}`} />
                </svg>
                <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', font: `${items.length > 1 ? 62 : String(x.texto).length > 4 ? 80 : 104}px 'M Archivo'`, whiteSpace: 'nowrap'}}>{x.texto}</div>
              </div>
              <div style={{maxWidth: items.length > 1 ? 330 : 820}}>
                <div style={{font: `${items.length > 1 ? 52 : 72}px/1.08 'M Black'`}}><Rico texto={x.pie} t={t} t0={16} /></div>
                {x.sub && <div style={{font: "36px/1.25 'M Medium'", opacity: 0.88, marginTop: 14}}>{x.sub}</div>}
              </div>
            </div>
          );
        })}
      </div>
      {d.chips && (
        <div style={{position: 'absolute', left: 90, bottom: 150, display: 'flex', gap: 24}}>
          {d.chips.map((x: any, i: number) => (
            <Salta key={i} t={p(x.paso)}>
              <div style={{background: '#fff', color: m.oscuro, borderRadius: 22, padding: '14px 34px', font: "50px 'M Black'"}}>{x.t}</div>
            </Salta>
          ))}
        </div>
      )}
      {d.nota && <div style={{position: 'absolute', left: 90, bottom: 150, font: "38px 'M Semi'", color: '#fff', background: 'rgba(8,16,12,0.7)', borderRadius: 18, padding: '12px 26px', opacity: c01(p(d.nota.paso) / 8)}}>{d.nota.t}</div>}
    </>
  );
};

// ------------------------------------------------------------------ tarjetas
const Tarjetas: React.FC<EP> = ({d, p, ancho: an}) => {
  const m = useMarca();
  const items: any[] = d.items;
  const cols = d.cols ?? (items.length === 4 ? 2 : items.length);
  const ancho = Math.floor((an - 180 - (cols - 1) * 30) / cols);
  return (
    <>
      {d.titulo && <div style={{position: 'absolute', left: 90, top: 160, right: 90}}><Titulo t={p(0) - 2} tam={66}><Rico texto={d.titulo} t={p(0)} /></Titulo></div>}
      <div style={{position: 'absolute', left: 90, top: d.titulo ? 300 : 230, width: an - 180, display: 'flex', flexWrap: 'wrap', gap: 30}}>
        {items.map((x, i) => (
          <Ficha key={i} t={p(x.paso ?? i)} cifra={x.cifra} pie={x.pie} ancho={ancho} grande color={x.color === 'acento' ? m.acento : x.color === 'oscuro' ? 'rgba(8,16,12,0.8)' : undefined} />
        ))}
      </div>
    </>
  );
};

// ------------------------------------------------------------------ columnas
const Columnas: React.FC<EP> = ({d, p}) => {
  const m = useMarca();
  const Col: React.FC<{x: any; destaca?: boolean}> = ({x, destaca}) => {
    const t = p(x.paso ?? 0);
    return (
      <div style={{flex: 1, opacity: c01(t / 4), transform: `translateY(${(1 - atras(t / 13)) * 70}px)`, background: destaca ? '#FFFFFF' : 'rgba(8,16,12,0.82)', color: destaca ? m.oscuro : '#fff', borderRadius: 36, padding: '40px 46px', border: '2px solid rgba(255,255,255,0.16)', boxShadow: '0 24px 70px rgba(0,0,0,0.35)'}}>
        {x.et && <div style={{font: "30px 'M Semi'", letterSpacing: 4, textTransform: 'uppercase', opacity: 0.75}}>{x.et}</div>}
        <div style={{font: "64px/1.06 'M Black'", marginTop: 8, marginBottom: 26}}>{x.titulo}</div>
        {x.items.map((it: any, i: number) => {
          const ti = p(it.paso ?? x.paso ?? 0);
          return (
            <div key={i} style={{display: 'flex', gap: 20, alignItems: 'baseline', font: "42px/1.2 'M Semi'", marginBottom: 16, opacity: c01(ti / 5), transform: `translateX(${(1 - suave(ti / 10)) * -30}px)`}}>
              <span style={{color: destaca ? m.color : m.acento, font: "42px 'M Archivo'"}}>{it.signo ?? '•'}</span>
              <span>{it.t}</span>
            </div>
          );
        })}
      </div>
    );
  };
  return (
    <>
      {d.titulo && <div style={{position: 'absolute', left: 90, top: 160, right: 90}}><Titulo t={p(0) - 2}><Rico texto={d.titulo} t={p(0)} /></Titulo></div>}
      <div style={{position: 'absolute', left: 90, right: 90, top: d.titulo ? 290 : 200, display: 'flex', gap: 40, alignItems: 'stretch'}}>
        <Col x={d.a} />
        <Col x={d.b} destaca />
      </div>
    </>
  );
};

export const TIPOS: Record<string, React.FC<EP>> = {
  cifra: Cifra, texto: Texto, cita: Cita, mapa: Mapa, barras: Barras, versus: Versus, linea: Linea, lista: Lista,
  documento: Documento, capitulo: Capitulo, flujo: Flujo, anillos: Anillos, tarjetas: Tarjetas, columnas: Columnas, plano: Plano,
};
