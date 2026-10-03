/**
 * Utilidades comunes de los planos de plato.
 *
 * Todo lo de aqui es un PORT de `parallax2/efectos.py`: las mismas curvas, el
 * mismo formato de cifras, los mismos colores. Si algo se ve distinto entre un
 * plano de Pillow y uno de Remotion, se arregla aqui y no en cada grafico.
 */

export type RGB = [number, number, number];

export const clamp01 = (u: number) => Math.min(1, Math.max(0, u));

/** ease-out cubico: la curva que usa todo el motor. */
export const suave = (u: number) => 1 - Math.pow(1 - u, 3);

/** ease-out con rebasamiento: pasa de largo y vuelve. */
export const atras = (u: number, k = 2.2) => {
  const v = u - 1;
  return v * v * ((k + 1) * v + k) + 1;
};

export const rebote = (u: number) => {
  if (u < 4 / 11) return (121 * u * u) / 16;
  if (u < 8 / 11) {
    const v = u - 6 / 11;
    return (4 / 3) * v * v + 0.75;
  }
  if (u < 9 / 10) {
    const v = u - 0.85;
    return 3 * v * v + 0.9375;
  }
  const v = u - 0.96;
  return 12 * v * v + 0.9843;
};

/** Cifra en espanol: punto de miles y coma decimal. Igual que `_fmt`. */
export const fmt = (v: number, dec = 0) => {
  const fijo = Math.abs(v).toFixed(dec);
  const [entera, decimal] = fijo.split('.');
  const miles = entera.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  const signo = v < 0 && Number(fijo) !== 0 ? '-' : '';
  return signo + (decimal ? `${miles},${decimal}` : miles);
};

/** La primera letra en mayuscula, saltando aperturas y el asterisco. */
export const may = (s: string) => {
  const t = s || '';
  for (let i = 0; i < t.length; i++) {
    const c = t[i];
    if (/\p{L}/u.test(c)) return t.slice(0, i) + c.toUpperCase() + t.slice(i + 1);
    if (!'¿¡*"\'( '.includes(c)) return t;
  }
  return t;
};

export const rgb = (c: number[], a = 1) =>
  a >= 1 ? `rgb(${c[0]},${c[1]},${c[2]})` : `rgba(${c[0]},${c[1]},${c[2]},${a})`;

/**
 * `factor_anim`: (u de entrada, u de salida) del fotograma `f` de un tramo de
 * `n` fotogramas. Con `dur_ent` y `dur_sal` en segundos.
 */
export const factorAnim = (
  f: number,
  n: number,
  fps: number,
  durEnt: number,
  durSal: number,
): [number, number] => {
  const ne = Math.max(1, Math.floor(durEnt * fps));
  const ns = Math.max(1, Math.floor(durSal * fps));
  const ue = durEnt > 0 ? Math.min(1, Math.max(0, f / ne)) : 1;
  const us = durSal > 0 ? Math.min(1, (n - 1 - f) / ns) : 1;
  return [ue, us];
};

export type Anim = {
  dx: number;
  dy: number;
  scale: number;
  op: number;
  blur: number;
};

/**
 * `anim_capa`: lo que se mueve una capa al entrar (o al salir) segun el tipo.
 * u = 0 es el instante mas lejano del reposo; u = 1 es el reposo. Las
 * entradas duras rebasan el reposo y vuelven, que es lo que las hace vivas.
 */
export const animCapa = (
  tipo: string | undefined,
  uIn: number,
  W: number,
  H: number,
  saliendo = false,
): Anim => {
  const reposo: Anim = {dx: 0, dy: 0, scale: 1, op: 1, blur: 0};
  if (!tipo || tipo === 'ninguna') return reposo;
  const u = clamp01(uIn);
  const e = suave(u);
  const s = saliendo ? -1 : 1;
  const opRapida = Math.min(1, u * 2.6);
  switch (tipo) {
    case 'fundido':
      return {...reposo, op: e};
    case 'sube':
      return {...reposo, dy: (1 - e) * H * 0.1 * s, op: e};
    case 'baja':
      return {...reposo, dy: -(1 - e) * H * 0.1 * s, op: e};
    case 'izquierda':
      return {...reposo, dx: (1 - e) * W * 0.13 * s, op: e};
    case 'derecha':
      return {...reposo, dx: -(1 - e) * W * 0.13 * s, op: e};
    case 'escala':
      return {...reposo, scale: 1 + (1 - e) * 0.14, op: e};
    case 'escala_atras':
      return {...reposo, scale: 1 - (1 - e) * 0.12, op: e};
    case 'desenfoque':
      return {...reposo, scale: 1 + (1 - e) * 0.03, op: e, blur: (1 - e) * 14};
    case 'golpe': {
      const a = atras(u);
      return {
        ...reposo,
        scale: 1 + (1 - a) * 0.3,
        op: opRapida,
        blur: (1 - Math.min(1, u * 3)) * 9,
      };
    }
    case 'latigo_izq':
    case 'latigo_der': {
      const d = tipo === 'latigo_izq' ? -1 : 1;
      const a = atras(u, 1.6);
      return {
        ...reposo,
        dx: d * (1 - a) * W * 0.42 * s,
        op: opRapida,
        blur: (1 - Math.min(1, u * 2.2)) * 26,
      };
    }
    case 'rebote':
      return {...reposo, dy: -(1 - rebote(u)) * H * 0.22 * s, op: opRapida};
    case 'desplome': {
      const a = atras(u, 1.4);
      return {
        ...reposo,
        dy: -(1 - a) * H * 0.3 * s,
        scale: 1 + (1 - a) * 0.06,
        op: opRapida,
        blur: (1 - Math.min(1, u * 2.6)) * 12,
      };
    }
    default:
      return reposo;
  }
};

/** Suma la animacion de entrada y la de salida, como `compon_texto`. */
export const combina = (a: Anim, b: Anim): Anim => ({
  dx: a.dx + b.dx,
  dy: a.dy + b.dy,
  scale: a.scale * b.scale,
  op: a.op * b.op,
  blur: a.blur + b.blur,
});


// --- curvas del movimiento "pro" ------------------------------------------
/** Frenada larga: sale disparado y se asienta. La de un contador de verdad. */
export const expo = (u: number) => (u >= 1 ? 1 : 1 - Math.pow(2, -10 * clamp01(u)));

/** Pasa de largo y vuelve: el "muelle" de una tarjeta que entra. */
export const atrasK = (u: number, k = 1.45) => {
  const v = clamp01(u) - 1;
  return 1 + (k + 1) * v * v * v + k * v * v;
};

export const dobleSuave = (u: number) => {
  const v = clamp01(u);
  return v < 0.5 ? 4 * v * v * v : 1 - Math.pow(-2 * v + 2, 3) / 2;
};

/** Un pulso que sube y baja una vez: 0 -> 1 -> 0. */
export const pulso = (u: number) => Math.sin(Math.PI * clamp01(u));
