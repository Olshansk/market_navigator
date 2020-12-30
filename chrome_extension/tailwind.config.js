module.exports = {
  future: {},
  purge: [],
  theme: {
    minWidth: {
      '0': '0',
      'popup': '790px',
      full: '100%'
    },
    minHeight: {
      '0': '0',
      'popup': '590px',
      full: '100%'
    },
    extend: {
      colors: {}
    }
  },
  variants: {},
  plugins: [
    require('tailwindcss-tables')(),
  ]
}
