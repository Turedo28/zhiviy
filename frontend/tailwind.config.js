/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#070708',
        accent: '#fb923c',
        accentDim: '#f97316',
        accentBg: 'rgba(251,146,60,0.08)',
        accentBorder: 'rgba(251,146,60,0.15)',
        red: '#ef4444',
        green: '#00D26A',
        yellow: '#FFB020',
        blue: '#38bdf8',
        purple: '#a78bfa',
        text: '#ffffff',
        textSec: '#999999',
        textDim: '#555555',
        textMuted: '#333333',
      },
      backgroundColor: {
        bg: '#070708',
        card: 'rgba(255,255,255,0.03)',
      },
      borderColor: {
        cardBorder: 'rgba(255,255,255,0.05)',
      },
      borderRadius: {
        card: '20px',
        sm: '12px',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      backdropFilter: {
        'blur-20': 'blur(20px)',
      },
    },
  },
  darkMode: 'class',
  plugins: [],
}
