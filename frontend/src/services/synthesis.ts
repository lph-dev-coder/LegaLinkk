import type { AgentSynthesisResult } from '@/types'
import { api } from './api'

export interface SynthesisJobStatus {
  job_id: string
  document_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  result: AgentSynthesisResult | null
  error: string | null
}

/**
 * Return a cached multi-agent synthesis for a contract, or `null` if none has
 * been generated yet (backend answers 404). Never triggers computation.
 */
export async function fetchCachedSynthesis(
  documentId: string,
): Promise<AgentSynthesisResult | null> {
  try {
    const { data } = await api.get<AgentSynthesisResult>(
      `/agents/synthesis/${documentId}`,
    )
    return data
  } catch (error) {
    if (
      typeof error === 'object' &&
      error !== null &&
      'response' in error &&
      (error as { response?: { status?: number } }).response?.status === 404
    ) {
      return null
    }
    throw error
  }
}

export async function startSynthesisJob(params: {
  documentId: string
  forceRefresh?: boolean
}): Promise<{ job_id: string }> {
  const { data } = await api.post<{ job_id: string }>('/agents/synthesis/jobs', {
    document_id: params.documentId,
    force_refresh: params.forceRefresh ?? false,
    top_k: 15,
    final_k: 5,
  })
  return data
}

export async function fetchSynthesisJob(
  jobId: string,
): Promise<SynthesisJobStatus> {
  const { data } = await api.get<SynthesisJobStatus>(
    `/agents/synthesis/jobs/${jobId}`,
  )
  return data
}
