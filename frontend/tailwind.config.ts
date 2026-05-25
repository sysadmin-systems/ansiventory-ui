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
          0: '#0f1117',
          1: '#161b27',
          2: '#1e2535',
          3: '#252d3d',
        },
        border: {
          DEFAULT: '#2a3349',
          2: '#344060',
        },
        text: {
          1: '#e8eaf0',
          2: '#8b95b0',
          3: '#4e5a78',
        },
        blue: {
          DEFAULT: '#4b8ef0',
          bg: '#162040',
          text: '#7ab3f8',
        },
        green: {
          DEFAULT: '#3db87a',
          bg: '#0f2820',
          text: '#5dd49a',
        },
        amber: {
          DEFAULT: '#f0a832',
          bg: '#281e0a',
          text: '#f5c060',
        },
        red: {
          DEFAULT: '#e05252',
          bg: '#250f0f',
          text: '#f07070',
        },
        purple: {
          DEFAULT: '#9b72f0',
          bg: '#1a1030',
          text: '#b99cf5',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '8px',
        lg: '12px',
        xl: '16px',
      },
    },
  },
} satisfies Config
