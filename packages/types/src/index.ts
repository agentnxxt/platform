// ── Content Types ─────────────────────────────────────────────────────────

export type ContentType = "blog_post" | "social_post" | "email" | "ad_copy"
export type Tone = "professional" | "casual" | "technical" | "friendly"
export type Length = "short" | "medium" | "long"
export type Platform = "twitter" | "linkedin" | "instagram" | "facebook" | "newsletter" | "email_subject" | "ad_headline"
export type PipelineStatus = "pending" | "researching" | "writing" | "repurposing" | "publishing" | "completed" | "failed"

export interface ContentRequest {
  topic: string
  content_type: ContentType
  brand_name?: string
  tone: Tone
  length: Length
  target_audience?: string
  model?: string
}

export interface ResearchRequest {
  topic: string
  depth?: "quick" | "standard" | "deep"
  model?: string
}

export interface RepurposeRequest {
  content: string
  target_formats: Platform[]
  brand_name?: string
  model?: string
}

export interface BrandMemoryRequest {
  brand_name: string
  content: string
  content_type?: "guidelines" | "past_content" | "voice_sample"
}

// ── Pipeline Types ─────────────────────────────────────────────────────────

export interface PipelineInput {
  topic: string
  content_type: ContentType
  brand_name?: string
  tone: Tone
  length: Length
  target_audience?: string
  repurpose_formats?: Platform[]
  publish_destinations?: string[]
  model?: string
}

export interface PipelineResult {
  workflow_id: string
  status: PipelineStatus
  research?: string
  content?: string
  repurposed?: Record<Platform, string>
  published?: Record<string, boolean>
  error?: string
  created_at: string
  updated_at: string
}

// ── Brand Types ────────────────────────────────────────────────────────────

export interface BrandMemory {
  id: string
  brand_name: string
  content_type: string
  preview: string
  created_at: string
}

// ── API Response Types ────────────────────────────────────────────────────

export interface ApiResponse<T> {
  data?: T
  error?: string
}
