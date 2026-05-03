/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 兰州大学校徽色系
        'lzu-blue': '#003D7A',
        'lzu-gold': '#C5A572',
        'lzu-light': '#E8F4F8',
      },
    },
  },
  plugins: [],
}
