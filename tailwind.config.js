/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './**/*.html',
  ],
  theme: {
    extend: {},
    applyComplexClasses: true, // <-- Agregá esta línea
  },
  plugins: [],
}
