module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/css/*.css',
  ],
  theme: {
    extend: {
      screens: {
        'xs': '475px',
      },
      container: {
        center: true,
        padding: '1rem',
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
