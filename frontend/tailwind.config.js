/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          orange: '#ff7a3d',
          orangeDark: '#f05d22',
          ink: '#252525',
          muted: '#777777',
          line: '#ececec',
          surface: '#f4f4f4',
        },
        medical: {
          teal: '#0f9f9a',
          blue: '#2878d6',
          green: '#39b56a',
          yellow: '#f5bd26',
          red: '#ef4d3f',
        },
      },
      boxShadow: {
        soft: '0 18px 50px rgba(20, 20, 20, 0.08)',
      },
      fontFamily: {
        sans: [
          'Inter',
          'Pretendard',
          'Apple SD Gothic Neo',
          'Noto Sans KR',
          'system-ui',
          'sans-serif',
        ],
      },
    },
  },
  plugins: [],
};
