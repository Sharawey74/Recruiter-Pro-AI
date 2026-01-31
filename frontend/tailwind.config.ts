import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: "#0f1729",
          800: "#1a2332",
          700: "#232d3f",
        },
        gray: {
          400: "#8b92a7",
        },
      },
    },
  },
  plugins: [],
};

export default config;
