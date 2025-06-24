/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Terminal colors based on Dracula theme
        'term-bg': '#282a36',
        'term-current': '#44475a',
        'term-fg': '#f8f8f2',
        'term-comment': '#6272a4',
        'term-cyan': '#8be9fd',
        'term-green': '#50fa7b',
        'term-orange': '#ffb86c',
        'term-pink': '#ff79c6',
        'term-purple': '#bd93f9',
        'term-red': '#ff5555',
        'term-yellow': '#f1fa8c',
      },
      fontFamily: {
        'mono': ['Fira Code', 'JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
      },
      animation: {
        'cursor-blink': 'cursor-blink 1.2s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        'cursor-blink': {
          '0%, 50%': { opacity: '1' },
          '51%, 100%': { opacity: '0' },
        },
        'glow': {
          '0%, 100%': { boxShadow: '0 0 10px #50fa7b' },
          '50%': { boxShadow: '0 0 20px #50fa7b, 0 0 30px #50fa7b' },
        },
      },
    },
  },
  plugins: [],
}