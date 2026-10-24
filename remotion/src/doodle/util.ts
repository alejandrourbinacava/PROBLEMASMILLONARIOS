export const clamp01 = (u: number) => Math.min(1, Math.max(0, u));
export const suave = (u: number) => 1 - Math.pow(1 - clamp01(u), 3);
/** Entrada con rebasamiento: sube por encima de 1 y vuelve. */
export const atras = (u: number, k = 1.9) => {
  const x = clamp01(u) - 1;
  return 1 + (k + 1) * x * x * x + k * x * x;
};

/** Cifra en espanol: punto de miles y coma decimal. */
export const fmt = (v: number, dec = 0) => {
  const fijo = Math.abs(v).toFixed(dec);
  const [entera, decimal] = fijo.split('.');
  const miles = entera.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  const signo = v < 0 && Number(fijo) !== 0 ? '-' : '';
  return signo + (decimal ? `${miles},${decimal}` : miles);
};

export const may = (s: string) => {
  const t = s || '';
  for (let i = 0; i < t.length; i++) {
    const c = t[i];
    if (/\p{L}/u.test(c)) return t.slice(0, i) + c.toUpperCase() + t.slice(i + 1);
    if (!'¿¡*"\'( '.includes(c)) return t;
  }
  return t;
};

/** Parte un texto en lineas de como mucho `max` caracteres, sin partir palabras. */
export const parte = (texto: string, max: number): string[] => {
  const pal = texto.split(/\s+/).filter(Boolean);
  const lineas: string[] = [];
  let cur = '';
  for (const p of pal) {
    const sin = (cur + ' ' + p).replace(/\*/g, '').trim();
    if (cur && sin.length > max) {
      lineas.push(cur);
      cur = p;
    } else {
      cur = cur ? cur + ' ' + p : p;
    }
  }
  if (cur) lineas.push(cur);
  return lineas;
};

/** Hash estable de un texto a entero sin signo. */
export const hash = (s: string) => Array.from(s).reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7);

/** Generador pseudoaleatorio determinista. */
export const azar = (semilla: number) => {
  let s = semilla >>> 0 || 1;
  return () => {
    s ^= s << 13;
    s >>>= 0;
    s ^= s >>> 17;
    s ^= s << 5;
    s >>>= 0;
    return (s % 100000) / 100000;
  };
};
