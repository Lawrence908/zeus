// zeus/frontend/tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#a8e8ff',
        'primary-container': '#00d4ff',
        'primary-fixed-dim': '#3cd7ff',
        'on-primary': '#003642',
        'on-primary-container': '#00586b',
        secondary: '#d2bbff',
        'secondary-container': '#6001d1',
        'on-secondary': '#3f008e',
        'on-secondary-container': '#c9aeff',
        tertiary: '#d2deff',
        'tertiary-container': '#a7c2ff',
        'on-tertiary': '#002e6a',
        background: '#111319',
        surface: '#111319',
        'surface-dim': '#111319',
        'surface-bright': '#373940',
        'surface-container-lowest': '#0c0e14',
        'surface-container-low': '#191b22',
        'surface-container': '#1e1f26',
        'surface-container-high': '#282a30',
        'surface-container-highest': '#33343b',
        'on-surface': '#e2e2eb',
        'on-surface-variant': '#bbc9cf',
        outline: '#859398',
        'outline-variant': '#3c494e',
        error: '#ffb4ab',
        'error-container': '#93000a',
        'on-error': '#690005',
        // Zeus accent
        accent: '#00d4ff',
      },
      fontFamily: {
        headline: ['"Space Grotesk"', 'sans-serif'],
        body: ['Manrope', 'sans-serif'],
        label: ['"Space Grotesk"', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.125rem',
        sm: '0.125rem',
        md: '0.125rem',
        lg: '0.25rem',
        xl: '0.5rem',
        '2xl': '0.5rem',
        full: '0.75rem',
      },
    },
  },
  plugins: [],
}

export default config
