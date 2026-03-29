"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api"

export default function DashboardPage() {
  const [models, setModels] = useState<string[]>([])

  useEffect(() => {
    api.models().then(res => {
      if (res.data) setModels((res.data as any).models?.map((m: any) => m.name) ?? [])
    })
  }, [])

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <p className="text-sm text-gray-400 mb-1">Available Models</p>
          <p className="text-3xl font-bold">{models.length}</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <p className="text-sm text-gray-400 mb-1">Status</p>
          <p className="text-green-400 font-medium">Operational</p>
        </div>
      </div>
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-sm font-medium text-gray-400 mb-3">Loaded Models</h2>
        {models.length === 0 ? (
          <p className="text-sm text-gray-500">No models loaded or API unreachable</p>
        ) : (
          <ul className="space-y-1">
            {models.map(m => (
              <li key={m} className="text-sm text-gray-200 font-mono bg-gray-800 px-3 py-1 rounded">{m}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
