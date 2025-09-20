/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/*.html",
    "./core/**/*.py"
  ],
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        'brand-deep': '#04606B',
        'brand-accent': '#92DCE5',
      }
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
