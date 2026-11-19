/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#fff8f1',
        surface: {
          DEFAULT: '#fff8f1',
          container: {
            DEFAULT: '#f3ede5',
            low: '#f9f3eb',
            lowest: '#ffffff',
            high: '#ede7e0',
            highest: '#e8e2da',
          },
          dim: '#dfd9d2',
          bright: '#fff8f1',
          variant: '#e8e2da',
        },
        primary: {
          DEFAULT: '#914d00',
          container: '#f28c28',
          fixed: {
            DEFAULT: '#ffdcc3',
            dim: '#ffb77d',
          },
        },
        'on-primary': {
          DEFAULT: '#ffffff',
          container: '#5d2f00',
          fixed: {
            DEFAULT: '#2f1500',
            variant: '#6e3900',
          },
        },
        secondary: {
          DEFAULT: '#5f5e5e',
          container: '#e4e2e1',
          fixed: {
            DEFAULT: '#e4e2e1',
            dim: '#c8c6c5',
          },
        },
        'on-secondary': {
          DEFAULT: '#ffffff',
          container: '#656464',
          fixed: {
            DEFAULT: '#1b1c1c',
            variant: '#474746',
          },
        },
        tertiary: {
          DEFAULT: '#904d00',
          container: '#f38b23',
          fixed: {
            DEFAULT: '#ffdcc3',
            dim: '#ffb77d',
          },
        },
        'on-tertiary': {
          DEFAULT: '#ffffff',
          container: '#5d2f00',
          fixed: {
            DEFAULT: '#2f1500',
            variant: '#6e3900',
          },
        },
        'on-surface': {
          DEFAULT: '#1d1b17',
          variant: '#554336',
        },
        'on-background': '#1d1b17',
        outline: {
          DEFAULT: '#887364',
          variant: '#dbc2b0',
        },
        error: {
          DEFAULT: '#ba1a1a',
          container: '#ffdad6',
        },
        'on-error': {
          DEFAULT: '#ffffff',
          container: '#93000a',
        },
        'inverse-surface': '#33302b',
        'inverse-on-surface': '#f6f0e8',
        'inverse-primary': '#ffb77d',
        success: '#2e7d32',
        'success-container': '#c8e6c9',
        warning: '#f9a825',
        'warning-container': '#fff9c4',
      },
      fontFamily: {
        headline: ['Manrope', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        'headline-xl': ['3rem', { lineHeight: '1.15', letterSpacing: '-0.03em', fontWeight: '700' }],
        'headline-lg': ['2rem', { lineHeight: '1.25', letterSpacing: '-0.02em', fontWeight: '600' }],
        'headline-md': ['1.375rem', { lineHeight: '1.35', letterSpacing: '-0.01em', fontWeight: '600' }],
        'headline-sm': ['1.125rem', { lineHeight: '1.4', letterSpacing: '0em', fontWeight: '600' }],
        'body-lg': ['1.125rem', { lineHeight: '1.6', letterSpacing: '-0.01em', fontWeight: '400' }],
        'body-md': ['0.9375rem', { lineHeight: '1.55', letterSpacing: '0em', fontWeight: '400' }],
        'body-sm': ['0.8125rem', { lineHeight: '1.5', letterSpacing: '0.005em', fontWeight: '400' }],
        'label-md': ['0.875rem', { lineHeight: '1.4', letterSpacing: '0em', fontWeight: '500' }],
        'label-sm': ['0.75rem', { lineHeight: '1.35', letterSpacing: '0.02em', fontWeight: '500' }],
        'mono-tag': ['0.6875rem', { lineHeight: '1.2', letterSpacing: '0.06em', fontWeight: '500' }],
        'mono-code': ['0.875rem', { lineHeight: '1.6', letterSpacing: '-0.01em', fontWeight: '400' }],
        'mono-stat': ['1.25rem', { lineHeight: '1.2', letterSpacing: '-0.02em', fontWeight: '500' }],
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
      },
      spacing: {
        'space-xxs': '0.125rem',
        'space-xs': '0.25rem',
        'space-sm': '0.5rem',
        'space-md': '1rem',
        'space-lg': '1.5rem',
        'space-xl': '2.5rem',
        'space-xxl': '4rem',
        gutter: '1.5rem',
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.03)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.06), 0 2px 4px -2px rgba(0, 0, 0, 0.04)',
        'elevated': '0 10px 15px -3px rgba(0, 0, 0, 0.06), 0 4px 6px -4px rgba(0, 0, 0, 0.04)',
      },
    },
  },
  plugins: [],
};
