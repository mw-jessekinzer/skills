"use client"

// MW Platform Design System v4 client providers
// 1. next-themes: class strategy, light by default, system opt-in later if wanted
// 2. Phosphor IconContext: every Phosphor icon renders at 16px Light.
//    Exception: 12px icons (badges, breadcrumb separators) pass weight="regular".
//
// Note: icons imported from "@phosphor-icons/react/ssr" (server components)
// do not read IconContext. In server components pass weight="light" explicitly.

import { ThemeProvider } from "next-themes"
import { IconContext } from "@phosphor-icons/react"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false} disableTransitionOnChange>
      <IconContext.Provider value={{ weight: "light", size: 16 }}>
        {children}
      </IconContext.Provider>
    </ThemeProvider>
  )
}
