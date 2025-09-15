

import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Scentmatch',
  description: 'Find your dream scent today',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // 🔹 Debug API URL
  if (typeof window !== "undefined") {
    console.log("DEBUG API URL:", process.env.NEXT_PUBLIC_API_URL)
  }

  return (
    <html lang="en">
      <body className={inter.className}>
        {/* wraps ALL pages */}
        {children}
      </body>
    </html>
  )
}
