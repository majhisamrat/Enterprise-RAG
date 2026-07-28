/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          cyan: '#19b5df',
          'cyan-dark': '#1293b6',
          'cyan-light': '#e6f8fc',
          ink: '#141c1b',
          muted: '#687772',
          line: '#dce6e1',
          surface: '#ffffff',
          soft: '#edf7f2',
        },
        dark: {
          sidebar: '#13181a',
          'sidebar-hover': '#1f262a',
          'sidebar-active': '#263035',
          'sidebar-border': '#222c30',
        },
        semantic: {
          danger: '#c94f47',
          success: '#10b981',
          warning: '#f59e0b',
        }
      },
      fontFamily: {
        sans: ['Manrope', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"DM Mono"', 'monospace'],
      },
      fontSize: {
        xs: ['11px', { lineHeight: '16px' }],
        sm: ['13px', { lineHeight: '18px' }],
        base: ['14px', { lineHeight: '20px' }],
        lg: ['16px', { lineHeight: '24px' }],
        xl: ['18px', { lineHeight: '28px' }],
        '2xl': ['22px', { lineHeight: '28px' }],
        '3xl': ['26px', { lineHeight: '32px' }],
        '4xl': ['32px', { lineHeight: '40px' }],
        '5xl': ['44px', { lineHeight: '48px' }],
      },
      letterSpacing: {
        tighter: '-0.06em',
        tight: '-0.05em',
        normal: '0em',
        wider: '0.1em',
      },
      borderRadius: {
        sm: '8px',
        base: '12px',
        lg: '14px',
        xl: '16px',
        '2xl': '20px',
        full: '9999px',
      },
      boxShadow: {
        xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        sm: '0 2px 10px rgba(0, 0, 0, 0.01)',
        base: '0 4px 20px rgba(0, 0, 0, 0.02)',
        lg: '0 8px 24px rgba(0, 0, 0, 0.04)',
        xl: '0 12px 32px rgba(0, 0, 0, 0.06)',
        'cyan': '0 6px 16px rgba(25, 181, 223, 0.3)',
        'inner-cyan': 'inset 0 0 0 2px rgba(25, 181, 223, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'pulse-subtle': 'pulseSubtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounceGentle 1s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      },
      transitionDuration: {
        DEFAULT: '200ms',
        fast: '100ms',
        slow: '300ms',
      },
    },
  },
  plugins: [],
}
