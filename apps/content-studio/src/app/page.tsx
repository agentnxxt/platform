import Link from "next/link"

export default function Home() {
  return (
    <div className="max-w-2xl mx-auto mt-20 text-center">
      <h1 className="text-4xl font-bold text-white mb-4">AutonomyX Content Studio</h1>
      <p className="text-gray-400 mb-10">
        AI agents that research, write, repurpose, and publish content across every channel — autonomously.
      </p>
      <div className="grid grid-cols-2 gap-4">
        <Link href="/create" className="bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-6 py-4 text-sm font-medium transition-colors">
          Create Content
        </Link>
        <Link href="/dashboard" className="bg-gray-800 hover:bg-gray-700 text-white rounded-lg px-6 py-4 text-sm font-medium transition-colors">
          View Dashboard
        </Link>
        <Link href="/library" className="bg-gray-800 hover:bg-gray-700 text-white rounded-lg px-6 py-4 text-sm font-medium transition-colors">
          Content Library
        </Link>
        <Link href="/brand" className="bg-gray-800 hover:bg-gray-700 text-white rounded-lg px-6 py-4 text-sm font-medium transition-colors">
          Brand Memory
        </Link>
      </div>
    </div>
  )
}
