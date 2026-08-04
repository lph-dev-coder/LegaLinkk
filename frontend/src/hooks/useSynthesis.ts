import { useCallback, useEffect, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import type { AgentSynthesisResult } from '@/types'
import {
  fetchCachedSynthesis,
  fetchSynthesisJob,
  startSynthesisJob,
} from '@/services/synthesis'

const SYNTHESIS_JOB_PREFIX = 'legallink.synthesis-job.v1'

function jobKey(userId: string, documentId: string) {
  return `${SYNTHESIS_JOB_PREFIX}.${userId}.${documentId}`
}

function isNotFound(error: unknown) {
  return (
    typeof error === 'object' &&
    error !== null &&
    'response' in error &&
    (error as { response?: { status?: number } }).response?.status === 404
  )
}

async function pause(ms: number) {
  await new Promise<void>((resolve) => window.setTimeout(resolve, ms))
}

async function followJob(
  jobId: string,
  onProgress: (progress: number, message: string) => void,
): Promise<AgentSynthesisResult> {
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const job = await fetchSynthesisJob(jobId)
    onProgress(job.progress, job.message)
    if (job.status === 'completed' && job.result) return job.result
    if (job.status === 'failed') {
      throw new Error(
        job.error ?? "La synthèse n'a pas pu être terminée. Veuillez réessayer.",
      )
    }
    await pause(1500)
  }
}

export function synthesisKey(documentId: string | undefined) {
  return ['synthesis', documentId] as const
}

/**
 * Persisted, Redis-resumable multi-agent synthesis for one contract.
 *
 * - A cached result (if any) loads instantly and is never recomputed.
 * - `generate()` starts a durable background job (or resumes the one recorded
 *   in localStorage), polling progress. It survives a page leave/refresh: on
 *   remount, an unfinished job is automatically resumed.
 */
export function useContractSynthesis(documentId: string | undefined) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [isGenerating, setGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('')
  const [error, setError] = useState<string | null>(null)
  const runningRef = useRef(false)

  const cached = useQuery({
    queryKey: synthesisKey(documentId),
    queryFn: () => fetchCachedSynthesis(documentId as string),
    enabled: Boolean(documentId && user?.id),
    staleTime: 30 * 60_000,
    retry: 0,
  })

  const setCache = useCallback(
    (result: AgentSynthesisResult) => {
      queryClient.setQueryData(synthesisKey(documentId), result)
    },
    [queryClient, documentId],
  )

  const drive = useCallback(
    async (jobId: string, key: string) => {
      setGenerating(true)
      setError(null)
      try {
        const result = await followJob(jobId, (p, m) => {
          setProgress(p)
          setMessage(m)
        })
        localStorage.removeItem(key)
        setCache(result)
      } catch (err) {
        if (isNotFound(err)) {
          localStorage.removeItem(key)
        } else {
          setError(
            err instanceof Error
              ? err.message
              : 'La synthèse a échoué. Veuillez réessayer.',
          )
        }
      } finally {
        setGenerating(false)
        runningRef.current = false
      }
    },
    [setCache],
  )

  const generate = useCallback(
    async (forceRefresh = false) => {
      if (!documentId || !user?.id || runningRef.current) return
      runningRef.current = true
      const key = jobKey(user.id, documentId)
      setGenerating(true)
      setError(null)
      setProgress(5)
      setMessage('Démarrage de la synthèse…')
      try {
        if (!forceRefresh) {
          const existing = localStorage.getItem(key)
          if (existing) {
            await drive(existing, key)
            return
          }
        }
        const job = await startSynthesisJob({ documentId, forceRefresh })
        localStorage.setItem(key, job.job_id)
        await drive(job.job_id, key)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'La synthèse n’a pas pu être démarrée. Veuillez réessayer.',
        )
        setGenerating(false)
        runningRef.current = false
      }
    },
    [documentId, user?.id, drive],
  )

  // Resume (never auto-start) an unfinished job after a page leave/refresh.
  useEffect(() => {
    if (!documentId || !user?.id) return
    if (cached.isLoading || cached.data || runningRef.current) return
    const key = jobKey(user.id, documentId)
    const existing = localStorage.getItem(key)
    if (!existing) return
    runningRef.current = true
    void drive(existing, key)
  }, [documentId, user?.id, cached.isLoading, cached.data, drive])

  return {
    synthesis: cached.data ?? null,
    isLoadingCached: cached.isLoading,
    isGenerating,
    progress,
    message,
    error,
    generate: () => generate(false),
    regenerate: () => generate(true),
  }
}
