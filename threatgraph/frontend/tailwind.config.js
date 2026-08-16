/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#0B0F14",
          raised: "#0F151B",
        },
        surface: {
          DEFAULT: "#131A21",
          raised: "#1B242C",
        },
        border: {
          DEFAULT: "#232E37",
          subtle: "#1A232B",
        },
        ink: {
          DEFAULT: "#E7ECF0",
          muted: "#8B98A5",
          faint: "#5C6873",
        },
        accent: {
          cyan: "#4FB6E8",
          amber: "#E8A33D",
          red: "#E5484D",
          green: "#4CAF7D",
        },
      },
      fontFamily: {
        mono: ["'IBM Plex Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
        sans: ["'IBM Plex Sans'", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(79,182,232,0.15), 0 0 24px rgba(79,182,232,0.08)",
      },
    },
  },
  plugins: [],
};
