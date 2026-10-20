// MW Platform Design System v4 root layout example (app/layout.tsx)
// Replace the preset's DM Sans font import with ttHoves. Keep everything else the preset generated.

import type { Metadata } from "next"
import { ttHoves, dmMono } from "./fonts"
import { Providers } from "./providers"
import "./globals.css"

export const metadata: Metadata = {
  title: "Midwestern Platform",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${ttHoves.variable} ${dmMono.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
