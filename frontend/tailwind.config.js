/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'agri-dark': '#111827',
        'agri-green': '#15803d',
        'agri-emerald': '#047857',
      },
    },
  },
  plugins: [],
}
