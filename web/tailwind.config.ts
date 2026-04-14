import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Mirrors src/utils/message_utils.py Rich colors
        human: {
          real: '#201ADB',
          sim: '#1A64DB',
        },
        ai: '#24FA00',
        clarify: '#37DB1A',
        brief: '#37DB1A',
        toolcall: '#C026D3', // magenta
        tooloutput: '#EAB308', // yellow
        system: '#EF4444', // red
        terminal: {
          bg: '#0A0A0A',
          surface: '#141414',
          surfaceAlt: '#0F0F0F',
          border: '#1E1E1E',
          borderInput: '#1A1A1A',
          text: '#FFFFFF',
          textPrimary: '#CCCCCC',
          textSecondary: '#DDDDDD',
          muted: '#666666',
          mutedAlt: '#555555',
          tertiary: '#444444',
          accent: '#00FF00',
          running: '#FFB800',
          clarify: '#FF6B00',
        },
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
} satisfies Config;
