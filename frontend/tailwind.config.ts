import type { Config } from 'tailwindcss'

export default {
  content: [
    './components/**/*.{vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './app.vue',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          0: '#07090f',
          1: '#0c0f1e',
          2: '#111628',
          3: '#18203a',
        },
        border: {
          DEFAULT: '#1e2745',
          2: '#2c3d62',
        },
        text: {
          1: '#eaecf5',
          2: '#8892b4',
          3: '#4a5475',
        },
        blue: {
          DEFAULT: '#7c5cfc',
          bg: '#160e38',
          text: '#a78bfa',
        },
        green: {
          DEFAULT: '#3db87a',
          bg: '#0a2018',
          text: '#5dd49a',
        },
        amber: {
          DEFAULT: '#f0a832',
          bg: '#221a08',
          text: '#f5c060',
        },
        red: {
          DEFAULT: '#e05252',
          bg: '#200c0c',
          text: '#f07070',
        },
        purple: {
          DEFAULT: '#9b72f0',
          bg: '#18102c',
          text: '#b99cf5',
        },
        azure: {
          DEFAULT: '#3b8ef0',
          bg: '#0e1c3a',
          text: '#7ab3f8',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '8px',
        lg: '12px',
        xl: '16px',
        '2xl': '20px',
      },
      boxShadow: {
        glow: '0 0 40px -8px rgba(124, 92, 252, 0.3)',
        'glow-sm': '0 0 20px -4px rgba(124, 92, 252, 0.2)',
        card: '0 4px 24px rgba(0, 0, 0, 0.4)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
} satisfies Config
