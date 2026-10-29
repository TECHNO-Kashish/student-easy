/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: '#F3F4F0',
          surface: '#FFFFFF',
          'sidebar-forest': '#24332D',
          'deep-forest': '#29483A',
          'interactive': '#52796F',
          'interactive-hover': '#43645b',
          'fresh-leaf': '#8EBD78',
          'soft-leaf': '#E9EEE8',
          'sky-mist': '#E5F0E8',
          'sunlight': '#F2D69B',
          'muted-clay': '#C47D57',
          'primary-text': '#252C28',
          'secondary-text': '#747C75',
          'border': '#DEE2DC',
          'warning': '#8A5A00',
          'error': '#B54747',
          'success': '#286B50',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'card': '10px',
        'control': '8px',
      }
    },
  },
  plugins: [],
}
