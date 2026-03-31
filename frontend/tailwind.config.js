/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        display: ['Space Grotesk', 'ui-sans-serif', 'system-ui'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        brand: {
          50:  '#eef4ff',
          100: '#dae6ff',
          200: '#bdd4ff',
          300: '#90baff',
          400: '#5c94ff',
          500: '#3672ff',
          600: '#1e52f5',
          700: '#173ee1',
          800: '#1933b6',
          900: '#1a318f',
          950: '#141f57',
        },
        surface: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
      },
      boxShadow: {
        panel: '0 4px 24px rgba(0, 0, 0, 0.06)',
        'panel-dark': '0 4px 24px rgba(0, 0, 0, 0.3)',
        glow: '0 0 20px rgba(54, 114, 255, 0.15)',
        'glow-dark': '0 0 20px rgba(54, 114, 255, 0.25)',
      },
      keyframes: {
        rise: {
          '0%': { opacity: 0, transform: 'translateY(12px) scale(0.97)' },
          '100%': { opacity: 1, transform: 'translateY(0) scale(1)' },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        pulse3: {
          '0%, 80%, 100%': { transform: 'scale(0)', opacity: 0.4 },
          '40%': { transform: 'scale(1)', opacity: 1 },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100%)', opacity: 0 },
          '100%': { transform: 'translateX(0)', opacity: 1 },
        },
      },
      animation: {
        rise: 'rise 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        fadeIn: 'fadeIn 0.3s ease-out',
        slideIn: 'slideIn 0.3s ease-out',
      },
    },
  },
  plugins: [],
}
