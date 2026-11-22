import React from 'react';
import {EP} from './base';
import {PRIMARK1} from './p_primark1';
import {PRIMARK2} from './p_primark2';

/** Registro de escenas de «Por que Primark NO vende por internet» (tema `primark`). */
export const PRIMARK: Record<string, React.FC<EP>> = {...PRIMARK1, ...PRIMARK2};
