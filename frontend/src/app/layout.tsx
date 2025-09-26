import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { MainNavigation, FloatingActions } from '@/components/navigation';

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
  return (
    <html lang="en">
      <body className={inter.className}>
        <MainNavigation />
        {children}
        <FloatingActions />
      </body>
    </html>
  )
}