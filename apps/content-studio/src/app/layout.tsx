import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "AutonomyX Content Studio",
  description: "Agentic content management — research, write, repurpose, publish",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-gray-100 min-h-screen antialiased">
        <nav className="border-b border-gray-800 px-6 py-3 flex items-center gap-6">
          <span className="font-semibold text-white tracking-tight">AutonomyX</span>
          <a href="/dashboard" className="text-sm text-gray-400 hover:text-white transition-colors">Dashboard</a>
          <a href="/create" className="text-sm text-gray-400 hover:text-white transition-colors">Create</a>
          <a href="/library" className="text-sm text-gray-400 hover:text-white transition-colors">Library</a>
          <a href="/brand" className="text-sm text-gray-400 hover:text-white transition-colors">Brand</a>
        </nav>
        <main className="p-6">{children}</main>
      </body>
    </html>
  )
}
