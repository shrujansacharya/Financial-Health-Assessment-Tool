/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: {
                    deep: "#0B0E14",
                    dark: "#151921",
                    card: "#1E2330",
                    hover: "#2A3040",
                },
                primary: {
                    DEFAULT: "#4F46E5", // Indigo 600
                    glow: "rgba(79, 70, 229, 0.5)",
                },
                secondary: "#8B5CF6", // Violet 500
                accent: "#06B6D4", // Cyan 500
                glass: {
                    bg: "rgba(30, 35, 48, 0.6)",
                    border: "rgba(255, 255, 255, 0.08)",
                    highlight: "rgba(255, 255, 255, 0.03)",
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                heading: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
            },
            backgroundImage: {
                'premium-gradient': "radial-gradient(circle at 15% 50%, rgba(79, 70, 229, 0.08), transparent 25%), radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.08), transparent 25%)",
            },
            animation: {
                'fade-in': 'fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
                'spin-slow': 'spin 3s linear infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                }
            }
        },
    },
    plugins: [],
}
