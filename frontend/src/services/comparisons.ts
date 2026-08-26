import type { ContractComparisonResult } from '@/types'
import { isNotFound } from '@/lib/apiError'
import { api } from './api'

export interface ComparisonJobStatus {
  job_id: string
  base_document_id: string
  target_document_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  message: string
  result: ContractComparisonResult | null
  error: string | null
}

export async function fetchCachedComparison(
  baseDocumentId: string,
  targetDocumentId: string,
): Promise<ContractComparisonResult | null> {
  try {
    const { data } = await api.get<ContractComparisonResult>('/comparisons', {
      params: {
        base_document_id: baseDocumentId,
        target_document_id: targetDocumentId,
      },
    })
    return data
  } catch (error) {
    if (isNotFound(error)) return null
    throw error
  }
}

export async function startComparisonJob(params: {
  baseDocumentId: string
  targetDocumentId: string
  forceRefresh?: boolean
}): Promise<{ job_id: string }> {
  const { data } = await api.post<{ job_id: string }>('/comparisons/jobs', {
    base_document_id: params.baseDocumentId,
    target_document_id: params.targetDocumentId,
    force_refresh: params.forceRefresh ?? false,
  })
  return data
}

export async function fetchComparisonJob(
  jobId: string,
): Promise<ComparisonJobStatus> {
  const { data } = await api.get<ComparisonJobStatus>(
    `/comparisons/jobs/${jobId}`,
  )
  return data
}
