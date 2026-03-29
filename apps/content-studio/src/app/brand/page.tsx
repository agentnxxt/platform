"use client"

import { useState } from "react"
import { api } from "@/lib/api"

export default function BrandPage() {
  const [brandName, setBrandName] = useState("")
  const [content, setContent] = useState("")
  const [contentType, setContentType] = useState("guidelines")
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState("")

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setMsg("")
    const res = await api.brand.add({ brand_name: brandName, content, content_type: contentType as any })
    setMsg(res.error ? `Error: ${res.error}` : "Stored in brand memory")
    setLoading(false)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Brand Memory</h1>
      <p className="text-sm text-gray-400 mb-6">
        Upload brand guidelines, voice samples, or past content. Agents use this as RAG context when generating content.
      </p>
      <form onSubmit={handleAdd} className="space-y-4 bg-gray-900 p-6 rounded-xl border border-gray-800">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Brand Name</label>
          <input value={brandName} onChange={e => setBrandName(e.target.value)} required
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Type</label>
          <select value={contentType} onChange={e => setContentType(e.target.value)}
            className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm">
            <option value="guidelines">Brand Guidelines</option>
            <option value="voice_sample">Voice Sample</option>
            <option value="past_content">Past Content</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Content</label>
          <textarea value={content} onChange={e => setContent(e.target.value)} required rows={6}
            placeholder="Paste brand guidelines, tone-of-voice document, or sample content..."
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
        </div>
        <button type="submit" disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg px-6 py-2 text-sm font-medium transition-colors">
          {loading ? "Storing..." : "Add to Memory"}
        </button>
      </form>
      {msg && <p className={`mt-3 text-sm ${msg.startsWith("Error") ? "text-red-400" : "text-green-400"}`}>{msg}</p>}
    </div>
  )
}
