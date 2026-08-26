/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
        ink: {
          50: '#f6f7f4',
          100: '#e8ebe3',
          200: '#d2d8c8',
          700: '#3a4235',
          800: '#2a3127',
          900: '#1a1f18',
          950: '#0f120e',
        },
        accent: {
          500: '#10b981',
          600: '#059669',
        },
      },
      fontFamily: {
        /* Spacewalk marketplace typography — single Poppins stack */
        sans: ['"Poppins"', 'system-ui', 'sans-serif'],
        display: ['"Poppins"', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        hero: [
          'clamp(1.6rem, 1.0333rem + 2.2667vw, 3.3rem)',
          { lineHeight: '1.15', fontWeight: '600' },
        ],
        'hero-sub': [
          'clamp(1.1rem, 0.8293rem + 1.203vw, 1.5rem)',
          { lineHeight: '1.55', fontWeight: '400' },
        ],
        'page-title': [
          'clamp(1.35rem, 1.05rem + 1.1vw, 2rem)',
          { lineHeight: '1.2', fontWeight: '600' },
        ],
      },
      boxShadow: {
        soft: '0 1px 2px rgba(15, 18, 14, 0.04), 0 8px 24px rgba(15, 18, 14, 0.06)',
        lift: '0 12px 40px rgba(4, 120, 87, 0.12)',
        glass: '0 1px 0 rgba(15, 18, 14, 0.04), 0 8px 32px rgba(15, 18, 14, 0.04)',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'soft-pulse': {
          '0%, 100%': { opacity: '0.45' },
          '50%': { opacity: '0.85' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.55s ease-out both',
        'fade-up-delay': 'fade-up 0.65s ease-out 0.12s both',
        'fade-up-late': 'fade-up 0.7s ease-out 0.22s both',
        'fade-in': 'fade-in 0.4s ease-out both',
        'soft-pulse': 'soft-pulse 2.8s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
