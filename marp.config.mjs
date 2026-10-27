// Configuração compartilhada entre o uso local (npm run pdf) e o CI.
// O formato de saída (pdf/pptx/html) fica nos scripts, não aqui.
export default {
  allowLocalFiles: true,
  html: true,
  themeSet: ['./slides'],
  options: {
    looseYAML: true,
  },
};
