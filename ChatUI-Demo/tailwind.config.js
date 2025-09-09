/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: '#01a669'
      },
      boxShadow: {
        soft: '0 6px 20px rgba(0,0,0,0.06)'
      }
    },
  },
  plugins: [],
}
