/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['Playfair Display', 'Georgia', 'serif'],
        body: ['Crimson Text', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        pearl: {
          50: '#fefefe',
          100: '#fdfdfd',
          200: '#fafafb',
          300: '#f5f5f7',
          400: '#e8e8ec',
          500: '#d1d1d8',
          600: '#a8a8b4',
          700: '#7a7a88',
          800: '#4a4a58',
          900: '#1a1a24',
        },
        obsidian: {
          50: '#f8f8f8',
          100: '#e8e8e8',
          200: '#d1d1d1',
          300: '#b0b0b0',
          400: '#888888',
          500: '#666666',
          600: '#444444',
          700: '#2a2a2a',
          800: '#1a1a1a',
          900: '#0a0a0a',
        },
        // Pearlescent accent - subtle iridescent effect
        iridescent: {
          light: '#f0f0f5',
          DEFAULT: '#e5e5f0',
          dark: '#d8d8e8',
        },
      },
      backgroundImage: {
        'pearlescent': 'linear-gradient(135deg, #fefefe 0%, #f5f5f7 25%, #e8e8ec 50%, #f5f5f7 75%, #fefefe 100%)',
        'pearlescent-hover': 'linear-gradient(135deg, #fff 0%, #f0f0ff 15%, #ffe0f0 30%, #f0fff0 45%, #f0f0ff 60%, #ffe0f0 75%, #f0fff0 90%, #fff 100%)',
        'obsidian-gradient': 'linear-gradient(to bottom, #0a0a0a, #1a1a1a)',
      },
      animation: {
        'shimmer': 'shimmer 3s ease-in-out infinite',
        'shimmer-slow': 'shimmer 5s ease-in-out infinite',
      },
      keyframes: {
        shimmer: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
      boxShadow: {
        'pearl': '0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(255, 255, 255, 0.8)',
        'pearl-lg': '0 4px 6px rgba(0, 0, 0, 0.05), 0 2px 4px rgba(255, 255, 255, 0.8)',
        'obsidian': '0 4px 6px rgba(0, 0, 0, 0.3)',
        'obsidian-lg': '0 10px 15px rgba(0, 0, 0, 0.4)',
      },
    },
  },
  plugins: [],
}
