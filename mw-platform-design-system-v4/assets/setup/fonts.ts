// MW Platform Design System v4 font setup (Next.js App Router)
// Place TT Hoves files in app/fonts/. Regular and Medium ship with this skill.
// TODO: add TT Hoves Bold (700) once the licensed file is in hand.
// Never add TT Hoves Light.

import localFont from "next/font/local"
import { DM_Mono } from "next/font/google"

export const ttHoves = localFont({
  variable: "--font-tt-hoves",
  display: "swap",
  src: [
    { path: "./fonts/TT_Hoves_Regular.otf", weight: "400", style: "normal" },
    { path: "./fonts/TT_Hoves_Medium.otf", weight: "500", style: "normal" },
    // { path: "./fonts/TT_Hoves_Bold.otf",   weight: "700", style: "normal" },
  ],
  fallback: ["DM Sans", "ui-sans-serif", "system-ui", "sans-serif"],
})

// Code snippets only. Never numbers, labels or eyebrows.
export const dmMono = DM_Mono({
  variable: "--font-dm-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
  display: "swap",
})
