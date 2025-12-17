import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Anti-Gravity | 占星術人生経営戦略書',
  description: 'Strategic Life Navigation System - あなたの人生経営戦略を占星術で読み解く',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="antialiased bg-gray-50 text-gray-900">
        {children}
      </body>
    </html>
  );
}
