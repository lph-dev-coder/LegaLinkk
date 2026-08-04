import { useEffect, useMemo, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import {
  AlertTriangle,
  ArrowRightLeft,
  CheckCircle2,
  Loader2,
  RefreshCw,
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader } from '@/components/ui/Card'
import { IngestionProgress } from '@/components/IngestionProgress'
import { UploadZone } from '@/components/UploadZone'
import { useContractComparison } from '@/hooks/useComparison'
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments'
import { cn } from '@/lib/cn'
import type { ComparisonChangeType, RiskLevel } from '@/types'

const CHANGE_LABEL: Record<ComparisonChangeType, string> = {
  added: 'Ajout',
  removed: 'Suppression',
  modified: 'Modification',
  unchanged: 'Inchangée',
}

const CHANGE_STYLE: Record<ComparisonChangeType, string> = {
  added: 'bg-emerald-50 text-emerald-700',
  removed: 'bg-red-50 text-red-700',
  modified: 'bg-amber-50 text-amber-700',
  unchanged: 'bg-slate-100 text-slate-500',
}

const RISK_STYLE: Record<RiskLevel, string> = {
  low: 'bg-emerald-50 text-emerald-700',
  medium: 'bg-amber-50 text-amber-700',
  high: 'bg-red-50 text-red-700',
}

const RISK_LABEL: Record<RiskLevel, string> = {
  low: 'Faible',
  medium: 'Moyen',
  high: 'Élevé',
}

export function ComparisonsPage() {
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const { data: documents = [], isLoading } = useDocuments()
  const baseUpload = useUploadDocument()
  const targetUpload = useUploadDocument()
  const available = useMemo(
    () => documents.filter((item) => item.indexed || item.status === 'completed'),
    [documents],
  )
  const [baseId, setBaseId] = useState(() => searchParams.get('base') ?? '')
  const [targetId, setTargetId] = useState(
    () => searchParams.get('target') ?? '',
  )
  const [pendingBase, setPendingBase] = useState<{
    documentId: string
    filename: string
  } | null>(null)
  const [pendingTarget, setPendingTarget] = useState<{
    documentId: string
    filename: string
  } | null>(null)
  const comparison = useContractComparison(
    baseId || undefined,
    targetId || undefined,
  )
  const canCompare = Boolean(baseId && targetId && baseId !== targetId)

  useEffect(() => {
    const next = new URLSearchParams()
    if (baseId) next.set('base', baseId)
    if (targetId) next.set('target', targetId)
    setSearchParams(next, { replace: true })
  }, [baseId, targetId, setSearchParams])

  return (
    <div className="space-y-6">
      <Card padding="lg">
        <CardHeader
          title="Comparer deux contrats"
          subtitle="Analyse sémantique clause par clause entre une version de référence et une nouvelle version"
        />
        <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr] md:items-end">
          <div className="space-y-3">
            <DocumentSelect
              label="Version A — Référence"
              value={baseId}
              onChange={setBaseId}
              documents={available}
              disabledId={targetId}
            />
            <UploadSlot
              label="Ou uploader la version A"
              pending={pendingBase}
              busy={baseUpload.isPending}
              onFiles={(files) => {
                const file = files[0]
                if (!file) return
                baseUpload.mutate(file, {
                  onSuccess: (result) =>
                    setPendingBase({
                      documentId: result.documentId,
                      filename: result.filename,
                    }),
                })
              }}
              onCompleted={() => {
                if (!pendingBase) return
                setBaseId(pendingBase.documentId)
                setPendingBase(null)
                void queryClient.invalidateQueries({ queryKey: ['documents'] })
              }}
            />
          </div>
          <ArrowRightLeft className="mb-3 hidden size-5 text-brand md:block" />
          <div className="space-y-3">
            <DocumentSelect
              label="Version B — Nouvelle version"
              value={targetId}
              onChange={setTargetId}
              documents={available}
              disabledId={baseId}
            />
            <UploadSlot
              label="Ou uploader la version B"
              pending={pendingTarget}
              busy={targetUpload.isPending}
              onFiles={(files) => {
                const file = files[0]
                if (!file) return
                targetUpload.mutate(file, {
                  onSuccess: (result) =>
                    setPendingTarget({
                      documentId: result.documentId,
                      filename: result.filename,
                    }),
                })
              }}
              onCompleted={() => {
                if (!pendingTarget) return
                setTargetId(pendingTarget.documentId)
                setPendingTarget(null)
                void queryClient.invalidateQueries({ queryKey: ['documents'] })
              }}
            />
          </div>
        </div>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <Button
            disabled={!canCompare || comparison.isGenerating || isLoading}
            onClick={comparison.generate}
          >
            {comparison.isGenerating ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <ArrowRightLeft className="size-4" />
            )}
            {comparison.isGenerating ? 'Comparaison en cours…' : 'Comparer'}
          </Button>
          {comparison.comparison ? (
            <Button
              variant="outline"
              disabled={comparison.isGenerating}
              onClick={comparison.regenerate}
            >
              <RefreshCw className="size-4" />
              Recalculer
            </Button>
          ) : null}
          {comparison.isGenerating ? (
            <div className="min-w-64 flex-1">
              <div className="mb-1 flex justify-between text-xs text-muted">
                <span>{comparison.message}</span>
                <span>{comparison.progress}%</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-brand transition-all"
                  style={{ width: `${comparison.progress}%` }}
                />
              </div>
            </div>
          ) : null}
        </div>
        {comparison.error ? (
          <p className="mt-4 flex items-center gap-2 text-sm text-danger">
            <AlertTriangle className="size-4" />
            {comparison.error}
          </p>
        ) : null}
      </Card>

      {comparison.comparison ? (
        <>
          <Card padding="lg">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-brand">
                  Synthèse comparative
                </p>
                <p className="mt-2 max-w-4xl whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {comparison.comparison.summary}
                </p>
              </div>
              <span
                className={cn(
                  'rounded-full px-3 py-1 text-xs font-bold',
                  RISK_STYLE[comparison.comparison.overall_risk_impact],
                )}
              >
                Impact {RISK_LABEL[comparison.comparison.overall_risk_impact]}
              </span>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Metric label="Ajouts" value={comparison.comparison.added_count} />
              <Metric
                label="Suppressions"
                value={comparison.comparison.removed_count}
              />
              <Metric
                label="Modifications"
                value={comparison.comparison.modified_count}
              />
              <Metric
                label="Inchangées"
                value={comparison.comparison.unchanged_count}
              />
            </div>
          </Card>

          <Card padding="none">
            <div className="border-b border-border px-5 py-4">
              <h2 className="font-semibold text-slate-900">
                Tableau clause par clause
              </h2>
              <p className="text-xs text-muted">
                {comparison.comparison.base_filename} →{' '}
                {comparison.comparison.target_filename}
              </p>
            </div>
            <div className="max-h-[38rem] overflow-auto">
              <table className="min-w-[1050px] w-full text-left text-sm">
                <thead className="sticky top-0 z-10 bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-4 py-3">Clause</th>
                    <th className="px-4 py-3">Changement</th>
                    <th className="px-4 py-3">Version A</th>
                    <th className="px-4 py-3">Version B</th>
                    <th className="px-4 py-3">Impact</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {comparison.comparison.changes.map((change, index) => (
                    <tr key={`${change.clause}-${index}`} className="align-top">
                      <td className="max-w-48 px-4 py-3 font-semibold text-slate-900">
                        {change.clause}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={cn(
                            'rounded-full px-2 py-1 text-xs font-semibold',
                            CHANGE_STYLE[change.change_type],
                          )}
                        >
                          {CHANGE_LABEL[change.change_type]}
                        </span>
                      </td>
                      <td className="max-w-72 whitespace-pre-wrap px-4 py-3 text-slate-600">
                        {change.base_text || '—'}
                      </td>
                      <td className="max-w-72 whitespace-pre-wrap px-4 py-3 text-slate-600">
                        {change.target_text || '—'}
                      </td>
                      <td className="max-w-64 px-4 py-3">
                        <span
                          className={cn(
                            'rounded-full px-2 py-1 text-xs font-semibold',
                            RISK_STYLE[change.risk_impact],
                          )}
                        >
                          {RISK_LABEL[change.risk_impact]}
                        </span>
                        <p className="mt-2 text-xs leading-5 text-slate-500">
                          {change.risk_reason}
                        </p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="flex items-center gap-2 font-semibold text-slate-900">
              <CheckCircle2 className="size-5 text-brand" />
              Recommandations
            </h2>
            <ul className="mt-3 space-y-2 text-sm text-slate-700">
              {comparison.comparison.recommendations.map((item, index) => (
                <li key={index} className="flex gap-2">
                  <span className="text-brand">•</span>
                  {item}
                </li>
              ))}
            </ul>
          </Card>
        </>
      ) : null}
    </div>
  )
}

function DocumentSelect({
  label,
  value,
  onChange,
  documents,
  disabledId,
}: {
  label: string
  value: string
  onChange: (value: string) => void
  documents: Array<{ id: string; filename: string }>
  disabledId: string
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-semibold text-slate-600">
        {label}
      </span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-11 w-full rounded-xl border border-border bg-white px-3 text-sm text-slate-800 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/10"
      >
        <option value="">Sélectionner un contrat…</option>
        {documents.map((document) => (
          <option
            key={document.id}
            value={document.id}
            disabled={document.id === disabledId}
          >
            {document.filename}
          </option>
        ))}
      </select>
    </label>
  )
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-border bg-slate-50 px-4 py-3">
      <p className="text-2xl font-bold text-slate-900">{value}</p>
      <p className="text-xs text-muted">{label}</p>
    </div>
  )
}

function UploadSlot({
  label,
  pending,
  busy,
  onFiles,
  onCompleted,
}: {
  label: string
  pending: { documentId: string; filename: string } | null
  busy: boolean
  onFiles: (files: File[]) => void
  onCompleted: () => void
}) {
  return (
    <div>
      <p className="mb-2 text-xs text-muted">{label}</p>
      {pending ? (
        <IngestionProgress
          documentId={pending.documentId}
          filename={pending.filename}
          onCompleted={onCompleted}
        />
      ) : busy ? (
        <div className="flex min-h-28 items-center justify-center rounded-xl border border-border bg-slate-50 text-sm text-muted">
          <Loader2 className="mr-2 size-4 animate-spin" />
          Envoi du PDF…
        </div>
      ) : (
        <UploadZone onFiles={onFiles} className="min-h-28 py-4" />
      )}
    </div>
  )
}
