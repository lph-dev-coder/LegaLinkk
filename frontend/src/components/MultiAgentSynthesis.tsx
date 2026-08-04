import { useState, type ComponentType } from 'react'
import {
  ChevronDown,
  Coins,
  FileText,
  Gavel,
  Loader2,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'
import { MarkdownText } from '@/components/MarkdownText'
import { cn } from '@/lib/cn'
import { fetchDocumentBlob } from '@/services/documents'
import type { AgentAnswer, AgentSynthesisResult, ChatSourceRef } from '@/types'

type IconType = ComponentType<{ className?: string }>

const DOMAIN_STYLE: Record<
  string,
  { label: string; icon: IconType; badge: string }
> = {
  legal: {
    label: 'Agent Juridique',
    icon: Gavel,
    badge: 'bg-primary-soft text-primary',
  },
  finance: {
    label: 'Agent Financier',
    icon: Coins,
    badge: 'bg-warning-soft text-warning',
  },
  compliance: {
    label: 'Agent Conformité',
    icon: ShieldCheck,
    badge: 'bg-success-soft text-success',
  },
}

async function openSourceDocument(documentId: string): Promise<void> {
  const blob = await fetchDocumentBlob(documentId)
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank', 'noopener,noreferrer')
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
}

function SourceChips({ sources }: { sources: ChatSourceRef[] }) {
  const [openingId, setOpeningId] = useState<string | null>(null)
  const [openError, setOpenError] = useState(false)

  const seen = new Set<string>()
  const unique = sources.filter((source) => {
    const key = source.filename ?? source.document_id
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
  if (!unique.length) return null

  const handleOpen = async (documentId: string) => {
    setOpenError(false)
    setOpeningId(documentId)
    try {
      await openSourceDocument(documentId)
    } catch {
      setOpenError(true)
    } finally {
      setOpeningId(null)
    }
  }

  return (
    <>
      <div className="mt-2.5 flex flex-wrap gap-1.5 border-t border-black/10 pt-2">
        {unique.map((src) => (
          <button
            key={src.filename ?? src.document_id}
            type="button"
            onClick={() => src.document_id && handleOpen(src.document_id)}
            disabled={!src.document_id || openingId === src.document_id}
            title={src.document_id ? 'Ouvrir le document (PDF)' : 'Document indisponible'}
            className={cn(
              'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium transition',
              'bg-primary-soft text-primary hover:bg-primary/15',
              src.document_id ? 'cursor-pointer' : 'cursor-default opacity-70',
            )}
          >
            {openingId === src.document_id ? (
              <Loader2 className="size-3 animate-spin" />
            ) : (
              <FileText className="size-3" />
            )}
            {src.filename ?? 'Document'}
          </button>
        ))}
      </div>
      {openError ? (
        <p className="mt-1.5 text-[11px] text-danger">
          Impossible d’ouvrir le document.
        </p>
      ) : null}
    </>
  )
}

function AgentDetail({ domain, answer }: { domain: string; answer: AgentAnswer }) {
  const style = DOMAIN_STYLE[domain]
  const Icon = style?.icon ?? Sparkles
  const text =
    answer.answer || answer.message || 'Analyse indisponible pour cet agent.'
  return (
    <details className="group rounded-xl border border-border bg-slate-50/70">
      <summary className="flex cursor-pointer list-none items-center gap-2 px-3 py-2">
        <span
          className={cn(
            'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold',
            style?.badge ?? 'bg-slate-200 text-slate-600',
          )}
        >
          <Icon className="size-3" />
          {style?.label ?? domain}
        </span>
        {answer.status !== 'ok' ? (
          <span className="text-[10px] font-medium text-danger">
            hors périmètre / indisponible
          </span>
        ) : null}
        <ChevronDown className="ml-auto size-4 text-slate-400 transition group-open:rotate-180" />
      </summary>
      <div className="border-t border-border px-3 py-2.5 text-sm text-slate-700">
        <MarkdownText content={text} />
        <SourceChips sources={answer.sources ?? []} />
      </div>
    </details>
  )
}

/**
 * Render a persisted multi-agent synthesis exactly like the chat: the synthesis
 * agent's recommendation on top, then the three individual agent analyses as
 * collapsible detail sections.
 */
export function MultiAgentSynthesis({
  synthesis,
}: {
  synthesis: AgentSynthesisResult
}) {
  const agents: Array<{ domain: string; answer: AgentAnswer | null | undefined }> =
    [
      { domain: 'legal', answer: synthesis.legal },
      { domain: 'finance', answer: synthesis.finance },
      { domain: 'compliance', answer: synthesis.compliance },
    ]
  const available = agents.filter((a) => a.answer)

  return (
    <div className="space-y-4">
      <div>
        <div className="mb-1.5 inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-2.5 py-1 text-[11px] font-semibold text-primary">
          <Sparkles className="size-3.5" />
          Recommandation de synthèse
        </div>
        {synthesis.recommendation ? (
          <MarkdownText
            content={synthesis.recommendation}
            className="text-sm text-slate-700"
          />
        ) : (
          <p className="text-sm text-muted">
            La recommandation de synthèse n’est pas disponible.
          </p>
        )}
      </div>

      {available.length ? (
        <div className="space-y-2 border-t border-border pt-3">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            Analyses détaillées des agents
          </p>
          {available.map(({ domain, answer }) => (
            <AgentDetail key={domain} domain={domain} answer={answer as AgentAnswer} />
          ))}
        </div>
      ) : null}
    </div>
  )
}
