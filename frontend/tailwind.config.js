/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        palm: {
          50: '#f0f7f0',
          100: '#dceedd',
          200: '#b8ddb9',
          300: '#87c48a',
          400: '#5ba85f',
          500: '#3d8b41',
          600: '#2d6f31',
          700: '#245829',
          800: '#1f4723',
          900: '#1a3b1e',
        },
        soil: {
          50: '#faf6f1',
          100: '#f0e6d6',
          200: '#e0cbab',
          300: '#cdaa79',
          400: '#be8f54',
          500: '#b07a3f',
          600: '#9a6234',
          700: '#7d4b2c',
          800: '#673e29',
          900: '#573425',
        },
        sky: {
          50: '#f0f8ff',
          100: '#dff0ff',
          200: '#b8e0ff',
          300: '#7ac9ff',
          400: '#34adff',
          500: '#0990f0',
          600: '#0072cd',
          700: '#005aa6',
          800: '#024d89',
          900: '#084171',
        },
      },
      fontFamily: {
        display: ['"DM Serif Display"', 'Georgia', 'serif'],
        body: ['"DM Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
