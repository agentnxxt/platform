"use client"

import { useState } from "react"
import { api } from "@/lib/api"
import type { ContentType, Tone, Length } from "@agentnext/types"

export default function CreatePage() {
  const [topic, setTopic] = useState("")
  const [contentType, setContentType] = useState<ContentType>("blog_post")
  const [tone, setTone] = useState<Tone>("professional")
  const [length, setLength] = useState<Length>("medium")
  const [brandName, setBrandName] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState("")
  const [error, setError] = useState("")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError("")
    setResult("")

    const res = await api.write({ topic, content_type: contentType, tone, length, brand_name: brandName || undefined })
    if (res.error) setError(res.error)
    else setResult((res.data as any)?.content ?? JSON.stringify(res.data))
    setLoading(false)
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Create Content</h1>
      <form onSubmit={handleSubmit} className="space-y-4 bg-gray-900 p-6 rounded-xl border border-gray-800">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Topic</label>
          <input
            value={topic}
            onChange={e => setTopic(e.target.value)}
            required
            placeholder="e.g. AI trends in 2025"
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Type</label>
            <select value={contentType} onChange={e => setContentType(e.target.value as ContentType)}
              className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm">
              <option value="blog_post">Blog Post</option>
              <option value="social_post">Social Post</option>
              <option value="email">Email</option>
              <option value="ad_copy">Ad Copy</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Tone</label>
            <select value={tone} onChange={e => setTone(e.target.value as Tone)}
              className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm">
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="technical">Technical</option>
              <option value="friendly">Friendly</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Length</label>
            <select value={length} onChange={e => setLength(e.target.value as Length)}
              className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm">
              <option value="short">Short</option>
              <option value="medium">Medium</option>
              <option value="long">Long</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Brand Name (optional)</label>
          <input
            value={brandName}
            onChange={e => setBrandName(e.target.value)}
            placeholder="Uses brand memory for RAG context"
            className="w-full bg-gray-800 text-white rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <button type="submit" disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg px-6 py-2 text-sm font-medium transition-colors">
          {loading ? "Generating..." : "Generate"}
        </button>
      </form>

      {error && <p className="mt-4 text-red-400 text-sm">{error}</p>}
      {result && (
        <div className="mt-6 bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-sm font-medium text-gray-400 mb-3">Generated Content</h2>
          <pre className="text-sm text-gray-100 whitespace-pre-wrap leading-relaxed">{result}</pre>
        </div>
      )}
    </div>
  )
}
