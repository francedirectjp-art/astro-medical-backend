import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Anti-Gravity | 占星術人生経営戦略書',
  description: 'Strategic Life Navigation System - あなたの出生図を人生経営の設計図として読み解く',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-anti-gravity-dark">
                  Anti-Gravity
                </h1>
                <p className="text-sm text-gray-600">
                  Strategic Life Navigation System
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500">
                  占星術人生経営戦略書
                </p>
                <p className="text-xs text-gray-400">
                  Powered by Swiss Ephemeris
                </p>
              </div>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="mt-16 bg-white border-t border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-sm text-gray-500">
              © 2024 Anti-Gravity Strategic Life Navigation System. All rights reserved.
            </p>
          </div>
        </footer>
      </body>
    </html>
  )
}
