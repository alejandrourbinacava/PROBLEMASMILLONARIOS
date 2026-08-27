import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('png');
// CRF bajo y preset lento: de aqui sale el master que despues pasa por el
// grade, y cada recodificacion que se ahorra es detalle que no se pierde.
Config.setCrf(16);
Config.setChromiumOpenGlRenderer('angle');
