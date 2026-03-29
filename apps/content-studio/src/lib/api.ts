import type {
  ContentRequest,
  RepurposeRequest,
  ResearchRequest,
  BrandMemoryRequest,
  PipelineInput,
  PipelineResult,
  ApiResponse,
} from "@agentnext/types"

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100"

async function post<T>(path: string, body: unknown): Promise<ApiResponse<T>> {
  try {
    const res = await fetch(`${BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
    if (!res.ok) return { error: await res.text() }
    return { data: await res.json() }
  } catch (e) {
    return { error: String(e) }
  }
}

async function get<T>(path: string): Promise<ApiResponse<T>> {
  try {
    const res = await fetch(`${BASE}${path}`)
    if (!res.ok) return { error: await res.text() }
    return { data: await res.json() }
  } catch (e) {
    return { error: String(e) }
  }
}

export const api = {
  research: (req: ResearchRequest) => post("/agent/research", req),
  write: (req: ContentRequest) => post<{ content: string }>("/agent/write", req),
  repurpose: (req: RepurposeRequest) => post<{ formats: Record<string, string> }>("/agent/repurpose", req),
  brand: {
    add: (req: BrandMemoryRequest) => post("/brand/memory", req),
    search: (brand_name: string, q = "brand voice") =>
      get<{ results: string[] }>(`/brand/memory/${brand_name}?q=${encodeURIComponent(q)}`),
  },
  pipeline: {
    start: (req: PipelineInput) => post<{ workflow_id: string; status: string }>("/workflow/pipeline", req),
    get: (id: string) => get<PipelineResult>(`/workflow/pipeline/${id}`),
  },
  models: () => get<{ models: { name: string }[] }>("/models"),
}
