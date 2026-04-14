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
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
} satisfies Config;
