/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg:            '#FAFAF8',
        surface:       '#F4F3F0',
        border:        '#E8E6E1',
        'text-primary':'#1A1A1A',
        'text-secondary':'#6B6B6B',
        accent:        '#A9683D',
        'accent-hover':'#8C5530',
        navy:          '#1B2838',
        // Legacy aliases from Django design system
        cream:         '#FAFAF8',
        linen:         '#F4F3F0',
        sand:          '#E8E6E1',
        tobacco:       '#6B6B6B',
        espresso:      '#1A1A1A',
        tuxedo:        '#1A1A1A',
        brass:         '#A9683D',
        'brass-muted': '#8C5530',
        cognac:        '#1A1A1A',
        'cognac-light':'#333333',
      },
      fontFamily: {
        display:  ['"Instrument Serif"', 'Georgia', 'serif'],
        serif:    ['"Instrument Serif"', 'Georgia', 'serif'],
        label:    ['"Outfit"', 'system-ui', 'sans-serif'],
        sans:     ['"Outfit"', 'system-ui', 'sans-serif'],
      },
      transitionTimingFunction: {
        'luxury': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
      animation: {
        'pulse-subtle': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-up': 'slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
