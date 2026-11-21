import React from 'react';
import {EP} from './base';
import {CAP1} from './m_cap1';
import {CAP2} from './m_cap2';
import {CAP3} from './m_cap3';
import {CAP4} from './m_cap4';
import {CAP5} from './m_cap5';
import {CAPAS} from './m_capas';
import {GANCHO} from './m_gancho';
import {VOX} from './m_vox';

/** Registro de escenas animadas de «Por que Mercadona NO quiere crecer fuera de Espana». */
export const ESCENAS: Record<string, React.FC<EP>> = {
  ...GANCHO,
  ...CAP1,
  ...CAP2,
  ...CAP3,
  ...CAP4,
  ...CAP5,
  // las escenas por capas con imagen real pisan a su version dibujada
  ...CAPAS,
  ...VOX,
};
