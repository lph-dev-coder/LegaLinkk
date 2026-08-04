import { useCallback, useEffect, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuth } from '@/context/AuthContext'
import {
  fetchCachedComparison,
  fetchComparisonJob,
  startComparisonJob,
} from '@/services/comparisons'
import type { ContractComparisonResult } from '@/types'

const PREFIX = 'legallink.comparison-job.v1'

function key(userId: string, baseId: string, targetId: string) {
  return `${PREFIX}.${userId}.${baseId}.${targetId}`
}

const pause = (ms: number) =>
  new Promise<void>((resolve) => window.setTimeout(resolve, ms))

async function follow(
  jobId: string,
  onProgress: (progress: number, message: string) => void,
) {
  for (;;) {
    const job = await fetchComparisonJob(jobId)
    onProgress(job.progress, job.message)
    if (job.status === 'completed' && job.result) return job.result
    if (job.status === 'failed' || job.status === 'cancelled') {
      throw new Error(job.error ?? job.message)
    }
    await pause(1500)
  }
}

function comparisonKey(baseId?: string, targetId?: string) {
  return ['contract-comparison', baseId, targetId] as const
}

export function useContractComparison(baseId?: string, targetId?: string) {
  const { user } = useAuth()
  const client = useQueryClient()
  const running = useRef(false)
  const [isGenerating, setGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('')
  const [error, setError] = useState<string | null>(null)
  const valid = Boolean(baseId && targetId && baseId !== targetId && user?.id)

  const cached = useQuery({
    queryKey: comparisonKey(baseId, targetId),
    queryFn: () =>
      fetchCachedComparison(baseId as string, targetId as string),
    enabled: valid,
    retry: 0,
    staleTime: 30 * 60_000,
  })

  const setResult = useCallback(
    (result: ContractComparisonResult) => {
      client.setQueryData(comparisonKey(baseId, targetId), result)
    },
    [client, baseId, targetId],
  )

  const drive = useCallback(
    async (jobId: string, storageKey: string) => {
      setGenerating(true)
      setError(null)
      try {
        const result = await follow(jobId, (p, m) => {
          setProgress(p)
          setMessage(m)
        })
        localStorage.removeItem(storageKey)
        setResult(result)
      } catch (cause) {
        localStorage.removeItem(storageKey)
        setError(
          cause instanceof Error
            ? cause.message
            : 'La comparaison a échoué.',
        )
      } finally {
        running.current = false
        setGenerating(false)
      }
    },
    [setResult],
  )

  const generate = useCallback(
    async (forceRefresh = false) => {
      if (!valid || !user?.id || !baseId || !targetId || running.current) return
      running.current = true
      const storageKey = key(user.id, baseId, targetId)
      setGenerating(true)
      setProgress(5)
      setMessage('Démarrage de la comparaison…')
      setError(null)
      try {
        if (!forceRefresh) {
          const existing = localStorage.getItem(storageKey)
          if (existing) {
            await drive(existing, storageKey)
            return
          }
        }
        const job = await startComparisonJob({
          baseDocumentId: baseId,
          targetDocumentId: targetId,
          forceRefresh,
        })
        localStorage.setItem(storageKey, job.job_id)
        await drive(job.job_id, storageKey)
      } catch (cause) {
        running.current = false
        setGenerating(false)
        setError(
          cause instanceof Error
            ? cause.message
            : 'La comparaison n’a pas pu être démarrée.',
        )
      }
    },
    [valid, user?.id, baseId, targetId, drive],
  )

  useEffect(() => {
    if (!valid || !user?.id || !baseId || !targetId || running.current) return
    const existing = localStorage.getItem(key(user.id, baseId, targetId))
    if (!existing) return
    running.current = true
    void drive(existing, key(user.id, baseId, targetId))
  }, [valid, user?.id, baseId, targetId, drive])

  return {
    comparison: cached.data ?? null,
    isLoadingCached: cached.isLoading,
    isGenerating,
    progress,
    message,
    error,
    generate: () => generate(false),
    regenerate: () => generate(true),
  }
}
