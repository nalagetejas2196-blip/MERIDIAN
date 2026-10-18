/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        meridian: {
          dark: '#0f172a',     // Deep slate/charcoal
          card: '#1e293b',     // Balanced card slate
          border: '#334155',   // Accessible border
          accent: '#0d9488',   // Muted teal primary accent
          accentHover: '#0f766e',
          text: '#f8fafc',     // Warm off-white
          muted: '#94a3b8'     // Neutral slate text
        }
      }
    },
  },
  plugins: [],
}
