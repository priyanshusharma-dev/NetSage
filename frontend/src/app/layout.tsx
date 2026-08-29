import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'NetSage — Autonomous LLM Network Troubleshooting System',
  description: 'AI-assisted enterprise network diagnostics with RAG vector retrieval, configurable safety gatekeeping, and live topology visualization.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
