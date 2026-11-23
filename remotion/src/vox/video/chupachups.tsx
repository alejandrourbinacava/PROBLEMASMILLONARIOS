import React from 'react';
import {EP} from './base';
import {CHUPA1} from './c_chupa1';
import {CHUPA2} from './c_chupa2';
import {CHUPA3} from './c_chupa3';

/** Registro de escenas de «Por que Chupa Chups vende MAS fuera de Espana que dentro» (tema `chupachups`). */
export const CHUPA: Record<string, React.FC<EP>> = {...CHUPA1, ...CHUPA2, ...CHUPA3};
