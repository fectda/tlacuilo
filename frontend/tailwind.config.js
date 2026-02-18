/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#050505',
                primary: {
                    DEFAULT: '#D4442F',
                    dark: '#A63525',
                    light: '#E06B5A',
                },
                accent: {
                    DEFAULT: '#F09B35', // Amber
                    dark: '#C87E25',
                    light: '#FFB85F',
                },
                success: '#22C55E',
                warning: '#F59E0B',
                error: '#EF4444',
                surface: '#0A0A0A',
                'surface-bright': '#121212',
            },
            boxShadow: {
                'glow-primary': '0 0 15px rgba(212, 68, 47, 0.2)',
                'glow-accent': '0 0 15px rgba(240, 155, 53, 0.2)',
                'glow-success': '0 0 15px rgba(34, 197, 94, 0.2)',
                'glow-warning': '0 0 15px rgba(245, 158, 11, 0.2)',
                'glow-error': '0 0 15px rgba(239, 68, 68, 0.2)',
                'status-on': '0 0 10px rgba(34, 197, 94, 0.4)',
                'status-wait': '0 0 10px rgba(245, 158, 11, 0.4)',
                'status-off': '0 0 10px rgba(239, 68, 68, 0.4)',
                'glass': '0 4px 24px -1px rgba(0, 0, 0, 0.4), 0 2px 8px -1px rgba(0, 0, 0, 0.2)',
            },
            backgroundImage: {
                'gradient-amber': 'linear-gradient(135deg, #F09B35 0%, #A63525 100%)',
                'gradient-refined': 'radial-gradient(circle at top right, rgba(240, 155, 53, 0.1), transparent), radial-gradient(circle at bottom left, rgba(212, 68, 47, 0.05), transparent)',
            },
            fontFamily: {
                sans: ['Outfit', 'Inter', 'sans-serif'],
                mono: ['Fira Code', 'monospace'],
            },
        },
    },
    plugins: [],
}
