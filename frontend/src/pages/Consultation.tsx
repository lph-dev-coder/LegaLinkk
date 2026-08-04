import { useEffect, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import {
  ChevronDown,
  Coins,
  Download,
  FileOutput,
  FileText,
  Gavel,
  Layers,
  Library,
  Loader2,
  MessageSquare,
  Paperclip,
  Plus,
  Printer,
  Send,
  ShieldCheck,
  Sparkles,
  Square,
  Trash2,
  User,
  type LucideIcon,
} from 'lucide-react'
import { Logo } from '@/components/Logo'
import { MarkdownText } from '@/components/MarkdownText'
import { UploadZone } from '@/components/UploadZone'
import { IngestionProgress } from '@/components/IngestionProgress'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader } from '@/components/ui/Card'
import { suggestions } from '@/data/mock'
import { useDocuments, useUploadDocument } from '@/hooks/useDocuments'
import {
  cancelBackgroundChatJob,
  createBackgroundChatJob,
  downloadDocumentPdf,
  fetchBackgroundChatJobStatus,
  streamBackgroundChatJob,
  wantsDocument,
} from '@/services/chat'
import { fetchDocumentBlob } from '@/services/documents'
import { fetchGeneratedDocumentBlob } from '@/services/generatedDocuments'
import {
  createConversation,
  getConversation,
} from '@/services/conversations'
import {
  CONVERSATIONS_KEY,
  useConversationList,
  useDeleteConversation,
} from '@/hooks/useServerConversations'
import { useAuth } from '@/context/AuthContext'
import { cn } from '@/lib/cn'
import type {
  AgentDomain,
  ChatAgentAnalysis,
  ChatMessage,
  ChatMessageSource,
  ChatSourceRef,
} from '@/types'

/** Open a source document's PDF in a new tab (authenticated blob fetch). */
async function openDocument(documentId: string): Promise<void> {
  const blob = await fetchDocumentBlob(documentId)
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank', 'noopener,noreferrer')
  window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
}

/** Dedupe API source refs (by filename) into clickable message sources. */
function toMessageSources(refs: ChatSourceRef[]): ChatMessageSource[] {
  const seen = new Set<string>()
  const out: ChatMessageSource[] = []
  for (const ref of refs) {
    const filename = ref.filename
    if (!filename || seen.has(filename)) continue
    seen.add(filename)
    out.push({ filename, documentId: ref.document_id })
  }
  return out
}

/** Per-domain presentation (label + icon + soft badge colors). */
const DOMAIN_STYLE: Record<
  AgentDomain,
  { label: string; icon: LucideIcon; badge: string }
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

interface SlashCommand {
  key: string
  command: string
  label: string
  desc: string
  icon: LucideIcon
}

/** The four slash options shown when the user types "/" in the composer. */
const SLASH_COMMANDS: SlashCommand[] = [
  {
    key: 'legal',
    command: '/legal',
    label: 'Agent Juridique',
    desc: 'Clauses, obligations et risques contractuels',
    icon: Gavel,
  },
  {
    key: 'finance',
    command: '/finance',
    label: 'Agent Financier',
    desc: 'Paiements, pénalités, coûts et exposition',
    icon: Coins,
  },
  {
    key: 'compliance',
    command: '/compliance',
    label: 'Agent Conformité',
    desc: 'RGPD, réglementation, audit et conformité',
    icon: ShieldCheck,
  },
  {
    key: 'synthese',
    command: '/synthese',
    label: 'Synthèse des 3 agents',
    desc: 'Analyse croisée et recommandation globale',
    icon: Layers,
  },
]

type AgentCommand =
  | { mode: 'single'; domain: AgentDomain; label: string; toSend: string }
  | { mode: 'multi'; label: string; toSend: string }

/**
 * Parse a leading slash command from the composer text.
 * - `/legal|/finance|/compliance …` → single agent (prefix kept so the backend
 *   routes it).
 * - `/synthese|/synth|/tous|/all …` → multi-agent synthesis (prefix stripped so
 *   the backend runs all three + synthesis).
 * Returns `null` for a normal message (handled by the streaming chat).
 */
/** Alias → canonical single-agent domain (mirrors the backend router). */
const SINGLE_AGENT_ALIASES: Record<string, AgentDomain> = {
  legal: 'legal',
  juridique: 'legal',
  finance: 'finance',
  financier: 'finance',
  compliance: 'compliance',
  conformite: 'compliance',
  conformité: 'compliance',
}
const SYNTHESIS_ALIASES = ['synthese', 'synthèse', 'synth', 'tous', 'all']

function parseAgentCommand(text: string): AgentCommand | null {
  const match = /^\/([\p{L}]+)\b([\s\S]*)$/u.exec(text.trim())
  if (!match) return null
  const cmd = match[1].toLowerCase()
  const rest = match[2].trim()
  const domain = SINGLE_AGENT_ALIASES[cmd]
  if (domain) {
    return {
      mode: 'single',
      domain,
      label: DOMAIN_STYLE[domain].label,
      // Always emit the canonical /domain token so the backend routes it.
      toSend: rest ? `/${domain} ${rest}` : `/${domain}`,
    }
  }
  if (SYNTHESIS_ALIASES.includes(cmd)) {
    return {
      mode: 'multi',
      label: 'Synthèse des 3 agents',
      toSend: rest || 'Analyse ce contrat en détail.',
    }
  }
  return null
}

/** Remove a leading "/command" token so a report title shows the real request. */
function stripLeadingSlashCommand(text: string): string {
  return text.replace(/^\s*\/[\p{L}]+\b[ \t]*/u, '').trim()
}

/** Open the generated HTML in a new tab and trigger the browser print → PDF. */
function printDocument(html: string): void {
  const win = window.open('', '_blank', 'noopener,noreferrer')
  if (!win) return
  win.document.open()
  win.document.write(html)
  win.document.close()
  win.focus()
  // Give the new document a moment to lay out before printing.
  win.setTimeout(() => win.print(), 400)
}

/** Download the generated HTML document as a standalone .html file. */
function downloadDocument(html: string): void {
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `document-legallink-${Date.now()}.html`
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

function DocumentCard({
  html,
  sourceDocumentId,
  question,
  generatedDocumentId,
}: {
  /** Absent when reloading a persisted conversation (only the PDF is kept). */
  html?: string
  sourceDocumentId?: string
  question?: string
  generatedDocumentId?: string
}) {
  const [pdfLoading, setPdfLoading] = useState(false)
  const [pdfError, setPdfError] = useState<string | null>(null)
  // For a persisted report (no inline HTML) we preview the stored PDF itself.
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState<string | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)

  useEffect(() => {
    if (html || !generatedDocumentId) return
    let revoked = false
    let objectUrl: string | null = null
    setPreviewLoading(true)
    fetchGeneratedDocumentBlob(generatedDocumentId)
      .then((blob) => {
        if (revoked) return
        objectUrl = URL.createObjectURL(blob)
        setPdfPreviewUrl(objectUrl)
      })
      .catch(() => {
        /* Preview is best-effort; the download button still works. */
      })
      .finally(() => {
        if (!revoked) setPreviewLoading(false)
      })
    return () => {
      revoked = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [html, generatedDocumentId])

  const handleDownloadPdf = async () => {
    setPdfError(null)
    setPdfLoading(true)
    try {
      const title = question
        ? `Rapport — ${question.slice(0, 100)}`
        : 'Document généré dans une consultation'
      const filename = `document-legallink-${Date.now()}.pdf`
      const blob = generatedDocumentId
        ? await fetchGeneratedDocumentBlob(generatedDocumentId)
        : await downloadDocumentPdf(html ?? '', {
            filename,
            title,
            sourceDocumentId,
            kind: 'chat_report',
            question,
          })
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = filename
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      URL.revokeObjectURL(url)
    } catch {
      setPdfError('Le téléchargement du PDF a échoué. Veuillez réessayer.')
    } finally {
      setPdfLoading(false)
    }
  }

  return (
    <div className="mt-3 overflow-hidden rounded-xl border border-border bg-slate-50">
      <div className="flex items-center justify-between gap-2 border-b border-border bg-white px-3 py-2">
        <span className="flex items-center gap-1.5 text-xs font-medium text-slate-600">
          <FileText className="size-3.5 text-brand" />
          Document généré
        </span>
        <div className="flex gap-1.5">
          <button
            type="button"
            onClick={handleDownloadPdf}
            disabled={pdfLoading}
            className="inline-flex items-center gap-1 rounded-lg bg-brand px-2.5 py-1 text-[11px] font-medium text-white transition hover:bg-brand-dark disabled:opacity-60"
          >
            {pdfLoading ? (
              <Loader2 className="size-3 animate-spin" />
            ) : (
              <Download className="size-3" />
            )}
            {pdfLoading ? 'Génération…' : 'Télécharger PDF'}
          </button>
          {html ? (
            <>
              <button
                type="button"
                onClick={() => printDocument(html)}
                className="inline-flex items-center gap-1 rounded-lg border border-border bg-white px-2.5 py-1 text-[11px] font-medium text-slate-600 transition hover:border-brand/40 hover:text-brand"
              >
                <Printer className="size-3" /> Imprimer
              </button>
              <button
                type="button"
                onClick={() => downloadDocument(html)}
                className="inline-flex items-center gap-1 rounded-lg border border-border bg-white px-2.5 py-1 text-[11px] font-medium text-slate-600 transition hover:border-brand/40 hover:text-brand"
              >
                <FileText className="size-3" /> HTML
              </button>
            </>
          ) : null}
        </div>
      </div>
      {pdfError ? (
        <p className="border-b border-border bg-danger/5 px-3 py-1.5 text-[11px] text-danger">
          {pdfError}
        </p>
      ) : null}
      {html ? (
        <iframe
          // Sandbox with no allowances: renders styled HTML but blocks scripts.
          sandbox=""
          srcDoc={html}
          title="Aperçu du document généré"
          className="h-80 w-full bg-white"
        />
      ) : pdfPreviewUrl ? (
        <iframe
          src={pdfPreviewUrl}
          title="Aperçu du rapport (PDF)"
          className="h-80 w-full bg-white"
        />
      ) : previewLoading ? (
        <p className="flex items-center gap-2 px-3 py-3 text-xs text-slate-500">
          <Loader2 className="size-3.5 animate-spin text-brand" />
          Chargement de l’aperçu…
        </p>
      ) : (
        <p className="px-3 py-3 text-xs text-slate-500">
          Aperçu indisponible pour ce rapport enregistré — téléchargez le PDF
          pour le consulter.
        </p>
      )}
    </div>
  )
}

const THINKING_STEPS = [
  'Recherche dans vos documents…',
  'Analyse des clauses pertinentes…',
  'Vérification des références…',
  'Rédaction de la réponse…',
]
const ACTIVE_CONVERSATION_PREFIX = 'legallink.active-conversation.v1'
const PENDING_JOB_PREFIX = 'legallink.pending-chat-job.v1'

function pendingJobKey(userId: string, conversationId: string): string {
  return `${PENDING_JOB_PREFIX}.${userId}.${conversationId}`
}

function setPendingJob(userId: string, conversationId: string, jobId: string): void {
  localStorage.setItem(pendingJobKey(userId, conversationId), jobId)
}

function clearPendingJob(userId: string, conversationId: string): void {
  localStorage.removeItem(pendingJobKey(userId, conversationId))
}

function getPendingJob(userId: string, conversationId: string): string | null {
  return localStorage.getItem(pendingJobKey(userId, conversationId))
}

function nowLabel(): string {
  return new Date().toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatElapsed(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return ''
  if (seconds < 60) return `${seconds.toFixed(1).replace('.', ',')} s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return `${m} min ${s.toString().padStart(2, '0')} s`
}

function todayHeader(): string {
  const label = new Date().toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
  return label.charAt(0).toUpperCase() + label.slice(1)
}

/** A fresh assistant greeting for a brand-new conversation. */
function welcomeMessage(): ChatMessage {
  return {
    id: 'welcome',
    role: 'assistant',
    content:
      'Bonjour. Déposez un contrat ou posez une question juridique — je peux résumer, détecter les risques et citer les références applicables.',
    timestamp: nowLabel(),
  }
}

/** Short, human relative time for the history list (e.g. "il y a 3 min"). */
function relativeTime(timestamp: number): string {
  const diff = Date.now() - timestamp
  const min = Math.floor(diff / 60_000)
  if (min < 1) return "à l'instant"
  if (min < 60) return `il y a ${min} min`
  const hours = Math.floor(min / 60)
  if (hours < 24) return `il y a ${hours} h`
  const days = Math.floor(hours / 24)
  if (days < 7) return `il y a ${days} j`
  return new Date(timestamp).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
  })
}

function Avatar({ role }: { role: ChatMessage['role'] }) {
  if (role === 'user') {
    return (
      <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-600">
        <User className="size-4" />
      </div>
    )
  }
  return (
    <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand to-brand-dark text-white shadow-sm">
      <Logo className="size-5" />
    </div>
  )
}

function SourceChips({
  sources,
  isUser = false,
}: {
  sources: ChatMessageSource[]
  isUser?: boolean
}) {
  const [openingId, setOpeningId] = useState<string | null>(null)
  const [openError, setOpenError] = useState(false)

  const handleOpenSource = async (documentId: string) => {
    setOpenError(false)
    setOpeningId(documentId)
    try {
      await openDocument(documentId)
    } catch {
      setOpenError(true)
    } finally {
      setOpeningId(null)
    }
  }

  if (!sources.length) return null

  return (
    <>
      <div
        className={cn(
          'mt-2.5 flex flex-wrap gap-1.5 border-t pt-2',
          isUser ? 'border-white/20' : 'border-black/10',
        )}
      >
        {sources.map((src) => (
          <button
            key={src.filename}
            type="button"
            onClick={() => src.documentId && handleOpenSource(src.documentId)}
            disabled={!src.documentId || openingId === src.documentId}
            title={
              src.documentId
                ? 'Ouvrir le document (PDF)'
                : 'Document indisponible'
            }
            className={cn(
              'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium transition',
              isUser
                ? 'bg-white/15 text-white hover:bg-white/25'
                : 'bg-primary-soft text-primary hover:bg-primary/15',
              src.documentId ? 'cursor-pointer' : 'cursor-default opacity-70',
            )}
          >
            {openingId === src.documentId ? (
              <Loader2 className="size-3 animate-spin" />
            ) : (
              <FileText className="size-3" />
            )}
            {src.filename}
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

/** Collapsible per-agent analyses shown under a multi-agent synthesis. */
function AgentAnalysisList({ analyses }: { analyses: ChatAgentAnalysis[] }) {
  if (!analyses.length) return null
  return (
    <div className="mt-3 space-y-2 border-t border-black/10 pt-3">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
        Analyses détaillées des agents
      </p>
      {analyses.map((analysis) => {
        const style = DOMAIN_STYLE[analysis.domain as AgentDomain]
        const Icon = style?.icon ?? Sparkles
        return (
          <details
            key={analysis.domain || analysis.label}
            className="group rounded-xl border border-border bg-slate-50/70"
          >
            <summary className="flex cursor-pointer list-none items-center gap-2 px-3 py-2">
              <span
                className={cn(
                  'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold',
                  style?.badge ?? 'bg-slate-200 text-slate-600',
                )}
              >
                <Icon className="size-3" />
                {analysis.label}
              </span>
              {analysis.status !== 'ok' ? (
                <span className="text-[10px] font-medium text-danger">
                  indisponible
                </span>
              ) : null}
              <ChevronDown className="ml-auto size-4 text-slate-400 transition group-open:rotate-180" />
            </summary>
            <div className="border-t border-border px-3 py-2.5 text-sm text-slate-700">
              <MarkdownText content={analysis.answer} />
              <SourceChips sources={analysis.sources ?? []} />
            </div>
          </details>
        )
      })}
    </div>
  )
}

function MessageRow({
  message,
  streaming = false,
  liveSeconds,
}: {
  message: ChatMessage
  streaming?: boolean
  liveSeconds?: number
}) {
  const isUser = message.role === 'user'

  return (
    <div
      className={cn(
        'flex animate-message-in items-end gap-2.5',
        isUser ? 'flex-row-reverse' : 'flex-row',
      )}
    >
      <Avatar role={message.role} />
      <div className={cn('flex max-w-[80%] flex-col', isUser && 'items-end')}>
        <div
          className={cn(
            'rounded-2xl px-4 py-3 text-sm shadow-sm',
            isUser
              ? 'rounded-br-md bg-brand text-white'
              : 'rounded-bl-md bg-white ring-1 ring-border text-slate-800',
          )}
        >
          {isUser ? (
            <p className="leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          ) : (
            <div className="text-sm">
              {message.agentLabel ? (
                <div className="mb-1.5 inline-flex items-center gap-1 rounded-full bg-primary-soft px-2 py-0.5 text-[11px] font-semibold text-primary">
                  <Sparkles className="size-3" />
                  {message.agentLabel}
                </div>
              ) : null}
              <MarkdownText content={message.content} />
              {streaming ? (
                <span className="ml-0.5 inline-block h-3.5 w-[3px] translate-y-0.5 animate-pulse rounded-sm bg-brand align-middle" />
              ) : null}
            </div>
          )}
          {message.document || message.generatedDocumentId ? (
            <DocumentCard
              html={message.document}
              sourceDocumentId={message.generatedReportSourceDocumentId}
              question={message.generatedReportQuestion}
              generatedDocumentId={message.generatedDocumentId}
            />
          ) : null}
          {message.agentAnalyses?.length ? (
            <AgentAnalysisList analyses={message.agentAnalyses} />
          ) : null}
          <SourceChips sources={message.sources ?? []} isUser={isUser} />
        </div>
        <span className="mt-1 px-1 text-[10px] text-slate-400">
          {message.timestamp}
          {streaming && liveSeconds != null ? (
            <span className="text-brand">
              {' · '}
              {message.resumed ? 'Reprise en cours · ' : ''}
              {formatElapsed(liveSeconds)}
            </span>
          ) : message.role === 'assistant' && message.elapsed != null ? (
            <span> · Généré en {formatElapsed(message.elapsed)}</span>
          ) : null}
        </span>
      </div>
    </div>
  )
}

function ThinkingBubble({
  step,
  seconds,
}: {
  step: number
  seconds?: number
}) {
  return (
    <div className="flex animate-message-in items-end gap-2.5">
      <Avatar role="assistant" />
      <div className="flex flex-col">
        <div className="flex items-center gap-2 rounded-2xl rounded-bl-md bg-white px-4 py-3 shadow-sm ring-1 ring-border">
          <span className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="size-1.5 rounded-full bg-brand"
                style={{
                  animation: 'typing-bounce 1.2s infinite ease-in-out',
                  animationDelay: `${i * 0.18}s`,
                }}
              />
            ))}
          </span>
          <span className="text-xs font-medium text-slate-500">
            {THINKING_STEPS[step]}
          </span>
          {seconds != null && seconds >= 0.3 ? (
            <span className="text-[11px] font-medium tabular-nums text-brand">
              {formatElapsed(seconds)}
            </span>
          ) : null}
        </div>
      </div>
    </div>
  )
}

export function ConsultationPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    welcomeMessage(),
  ])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [draft, setDraft] = useState('')
  const [selectedDocId, setSelectedDocId] = useState('')
  const [chatMode, setChatMode] = useState<'conversation' | 'generation'>(
    'conversation',
  )
  const [sending, setSending] = useState(false)
  const [cancelling, setCancelling] = useState(false)
  const [streamingId, setStreamingId] = useState<string | null>(null)
  const [thinkingStep, setThinkingStep] = useState(0)
  const [elapsedMs, setElapsedMs] = useState(0)
  const [activeUpload, setActiveUpload] = useState<{
    documentId: string
    filename: string
  } | null>(null)
  const [attachError, setAttachError] = useState<string | null>(null)
  // Slash-command menu (agent picker) state.
  const [slashIndex, setSlashIndex] = useState(0)
  const [slashClosed, setSlashClosed] = useState(false)
  const [switchingConversation, setSwitchingConversation] = useState(false)
  const upload = useUploadDocument()
  const { data: documents } = useDocuments()
  const { user } = useAuth()
  const { data: serverConversations } = useConversationList()
  const conversations = serverConversations ?? []
  const deleteConversationMutation = useDeleteConversation()
  const queryClient = useQueryClient()
  const scrollRef = useRef<HTMLDivElement>(null)
  const startRef = useRef<number>(0)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const resumingJobsRef = useRef(new Set<string>())
  const restoredForUserRef = useRef<string | null>(null)
  // Aborts only the LOCAL SSE reader of the current stream (never the durable
  // Celery/Redis job) so the user can switch conversations mid-generation.
  const streamAbortRef = useRef<AbortController | null>(null)
  // Mirrors `activeId` so async callbacks (e.g. a resume that ends minutes
  // later) can tell whether the user is still on the same conversation before
  // reconciling its messages.
  const activeIdRef = useRef<string | null>(null)
  // Whether we already auto-scoped the chat to the current attachment.
  const autoScopedRef = useRef(false)

  // Only indexed documents can be searched; the empty value means "all".
  const searchableDocs = (documents ?? []).filter((d) => d.indexed)
  const selectedDoc = searchableDocs.find((d) => d.id === selectedDocId)
  const scopeLabel = selectedDoc
    ? selectedDoc.filename
    : 'Toute la bibliothèque'
  const uploadReady =
    !!activeUpload &&
    searchableDocs.some((d) => d.id === activeUpload.documentId)

  const markMessageCancelled = (assistantId: string, notice: string) => {
    setMessages((prev) =>
      prev.map((message) => {
        if (message.id !== assistantId) return message
        const partial = message.content.trim()
        return {
          ...message,
          content:
            partial && !/en cours…?$/i.test(partial)
              ? `${partial}\n\n_${notice}_`
              : notice,
          backgroundJobStatus: 'cancelled',
        }
      }),
    )
  }

  const recordBackgroundEvent = (assistantId: string, eventCount: number) => {
    setMessages((prev) =>
      prev.map((message) =>
        message.id === assistantId
          ? { ...message, backgroundJobEventCount: eventCount }
          : message,
      ),
    )
  }

  const MAX_UPLOAD_BYTES = 25 * 1024 * 1024

  const attachFile = (file: File | undefined) => {
    if (!file || sending || upload.isPending) return
    setAttachError(null)
    const isPdf =
      file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
    if (!isPdf) {
      setAttachError('Format non pris en charge : seuls les PDF sont acceptés.')
      return
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      setAttachError('Fichier trop volumineux (25 Mo maximum).')
      return
    }
    autoScopedRef.current = false
    upload.mutate(file, {
      onSuccess: (result) => {
        setActiveUpload({
          documentId: result.documentId,
          filename: result.filename,
        })
      },
      onError: (err) => {
        setAttachError(
          err instanceof Error
            ? err.message
            : "L'envoi du fichier a échoué. Veuillez réessayer.",
        )
      },
    })
  }

  const handleAttachClick = () => {
    if (sending || upload.isPending) return
    fileInputRef.current?.click()
  }

  useEffect(() => {
    activeIdRef.current = activeId
  }, [activeId])

  // Once the freshly attached file is indexed, scope the chat to it so the
  // next questions target that document by default.
  useEffect(() => {
    if (!activeUpload || autoScopedRef.current) return
    if (searchableDocs.some((d) => d.id === activeUpload.documentId)) {
      setSelectedDocId(activeUpload.documentId)
      autoScopedRef.current = true
    }
  }, [searchableDocs, activeUpload])

  // Restore the last-open conversation for this browser once per login. The
  // conversation's messages (and any still-running job) come from PostgreSQL.
  useEffect(() => {
    if (!user || restoredForUserRef.current === user.id) return
    restoredForUserRef.current = user.id
    const savedId = localStorage.getItem(`${ACTIVE_CONVERSATION_PREFIX}.${user.id}`)
    if (!savedId) return
    void loadConversation(savedId)
    // `loadConversation` is a stable closure for the lifetime of this mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  /**
   * Detach the LOCAL live stream so the user can switch conversations while a
   * reply is still generating. The Celery/Redis job keeps running and its reply
   * is persisted; the pending-job marker is intentionally kept so returning to
   * that conversation resumes/reconciles it.
   */
  const detachActiveStream = () => {
    streamAbortRef.current?.abort()
    streamAbortRef.current = null
    setStreamingId(null)
    setSending(false)
    setCancelling(false)
  }

  const startNewConversation = () => {
    if (switchingConversation) return
    detachActiveStream()
    if (user) {
      localStorage.removeItem(`${ACTIVE_CONVERSATION_PREFIX}.${user.id}`)
    }
    activeIdRef.current = null
    setActiveId(null)
    setMessages([welcomeMessage()])
    setDraft('')
  }

  /**
   * Resume an unfinished Redis-backed background job for `conversationId`
   * (e.g. the user navigated away or refreshed mid-generation). The reply
   * itself is durably persisted by the Celery task once it completes, so
   * this only needs to catch up the live UI.
   */
  const maybeResumePendingJob = async (conversationId: string) => {
    if (!user) return
    const jobId = getPendingJob(user.id, conversationId)
    if (!jobId || resumingJobsRef.current.has(jobId)) return

    let status
    try {
      status = await fetchBackgroundChatJobStatus(jobId)
    } catch {
      clearPendingJob(user.id, conversationId)
      return
    }
    if (status.status !== 'queued' && status.status !== 'processing') {
      // The job finished while we were away. Its reply is durably persisted, so
      // reload the conversation from PostgreSQL to show the completed answer
      // (loadConversation may have run before the reply landed in the DB).
      clearPendingJob(user.id, conversationId)
      try {
        const { messages: loaded } = await getConversation(conversationId)
        if (loaded.length) setMessages(loaded)
      } catch {
        /* Keep whatever is on screen if the reload fails. */
      }
      return
    }

    resumingJobsRef.current.add(jobId)
    // Resume the elapsed timer from the job's real queue time, not from zero.
    const startedAt = status.createdAt ? Date.parse(status.createdAt) : NaN
    startRef.current = Number.isNaN(startedAt) ? Date.now() : startedAt
    const assistantId = crypto.randomUUID()
    setMessages((prev) => [
      ...prev,
      {
        id: assistantId,
        role: 'assistant',
        // Reports emit no fragments until the PDF is ready, so show an explicit
        // "still running in the background" note instead of an empty bubble.
        content:
          status.mode === 'report'
            ? 'Le rapport est toujours en cours de génération en arrière-plan…'
            : '',
        timestamp: nowLabel(),
        resumed: true,
        backgroundJobId: jobId,
        backgroundJobMode: status.mode,
        backgroundJobStatus: 'processing',
        backgroundJobEventCount: 0,
      },
    ])
    setSending(true)
    setStreamingId(assistantId)

    const controller = new AbortController()
    streamAbortRef.current = controller
    let restoredSources: ChatMessageSource[] = []
    await streamBackgroundChatJob(
      jobId,
      {
        onEvent: (eventCount) => {
          recordBackgroundEvent(assistantId, eventCount)
        },
        onAgent: ({ domain, label }) => {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? {
                    ...message,
                    agentLabel:
                      DOMAIN_STYLE[domain as AgentDomain]?.label ??
                      label ??
                      message.agentLabel,
                  }
                : message,
            ),
          )
        },
        onSources: (incoming) => {
          restoredSources = toMessageSources(incoming)
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? { ...message, sources: restoredSources }
                : message,
            ),
          )
        },
        onAnalyses: (list) => {
          const analyses: ChatAgentAnalysis[] = list.map((analysis) => ({
            domain: analysis.domain ?? '',
            label:
              DOMAIN_STYLE[analysis.domain as AgentDomain]?.label ??
              analysis.label,
            status: analysis.status,
            answer:
              analysis.answer || analysis.message || 'Analyse indisponible.',
            sources: toMessageSources(analysis.sources ?? []),
          }))
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? { ...message, agentAnalyses: analyses }
                : message,
            ),
          )
        },
        onDocument: ({
          html,
          generatedDocumentId,
          sources: incoming,
          metadata,
        }) => {
          restoredSources = toMessageSources(incoming)
          const sourceIds = Array.from(
            new Set(
              incoming.map((source) => source.document_id).filter(Boolean),
            ),
          )
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? {
                    ...message,
                    content:
                      'Le rapport est prêt. Vous pouvez le consulter ou le télécharger.',
                    document: html,
                    generatedDocumentId,
                    generatedReportSourceDocumentId:
                      message.generatedReportSourceDocumentId ||
                      (sourceIds.length === 1 ? sourceIds[0] : undefined),
                    sources: restoredSources,
                    elapsed:
                      typeof metadata.generation_time === 'number'
                        ? metadata.generation_time
                        : message.elapsed,
                  }
                : message,
            ),
          )
        },
        onDelta: (text) => {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? { ...message, content: message.content + text }
                : message,
            ),
          )
        },
        onDone: ({ answer, metadata }) => {
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantId
                ? {
                    ...message,
                    content: message.content || answer || '',
                    sources: restoredSources.length
                      ? restoredSources
                      : message.sources,
                    elapsed:
                      typeof metadata.generation_time === 'number'
                        ? metadata.generation_time
                        : message.elapsed,
                    backgroundJobStatus: 'completed',
                  }
                : message,
            ),
          )
        },
        onCancelled: (notice) => {
          markMessageCancelled(assistantId, notice)
        },
        onError: (message) => {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantId
                ? {
                    ...item,
                    content:
                      item.content ||
                      `Désolé, la génération a échoué : ${message}`,
                    backgroundJobStatus: 'failed',
                  }
                : item,
            ),
          )
        },
      },
      { after: 0, signal: controller.signal },
    )

    resumingJobsRef.current.delete(jobId)
    // The user switched conversations mid-resume: leave the durable job (and its
    // pending marker) untouched so it can be resumed again later.
    if (controller.signal.aborted || activeIdRef.current !== conversationId)
      return
    if (streamAbortRef.current === controller) streamAbortRef.current = null
    setStreamingId(null)
    setSending(false)

    // The stream ended: either the job finished, or the connection dropped
    // during a long, event-less report. Re-check the durable status.
    let stillRunning = false
    try {
      const latest = await fetchBackgroundChatJobStatus(jobId)
      stillRunning =
        latest.status === 'queued' || latest.status === 'processing'
    } catch {
      stillRunning = false
    }
    if (stillRunning) {
      // Keep the pending marker so a later refresh resumes it again, and leave
      // the "still generating in background" note visible.
      return
    }
    // Terminal: forget the job and reconcile with the durably-persisted reply
    // so the final message (incl. any generated PDF) is authoritative even if
    // the live stream ended partial. Skip if the user switched conversations.
    clearPendingJob(user.id, conversationId)
    if (activeIdRef.current === conversationId) {
      try {
        const { messages: loaded } = await getConversation(conversationId)
        if (loaded.length) setMessages(loaded)
      } catch {
        /* Keep whatever is on screen if the reload fails. */
      }
    }
  }

  /** Fetch a persisted conversation's messages from PostgreSQL and open it. */
  const loadConversation = async (id: string) => {
    if (!user) return
    setSwitchingConversation(true)
    try {
      const { messages: loaded } = await getConversation(id)
      activeIdRef.current = id
      setActiveId(id)
      setMessages(loaded.length ? loaded : [welcomeMessage()])
      localStorage.setItem(`${ACTIVE_CONVERSATION_PREFIX}.${user.id}`, id)
      setDraft('')
    } catch {
      // Deleted or inaccessible remotely — fall back to a fresh chat.
      localStorage.removeItem(`${ACTIVE_CONVERSATION_PREFIX}.${user.id}`)
      setActiveId(null)
      setMessages([welcomeMessage()])
      setSwitchingConversation(false)
      return
    }
    setSwitchingConversation(false)
    void maybeResumePendingJob(id)
  }

  /** Refetch the sidebar so a freshly-titled/updated conversation appears. */
  const refreshConversations = () =>
    void queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY })

  /** First message of a fresh chat → create the persisted conversation lazily. */
  const ensureConversationId = async (): Promise<string | null> => {
    if (activeId) return activeId
    try {
      const created = await createConversation()
      activeIdRef.current = created.id
      setActiveId(created.id)
      if (user) {
        localStorage.setItem(
          `${ACTIVE_CONVERSATION_PREFIX}.${user.id}`,
          created.id,
        )
      }
      void queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY })
      return created.id
    } catch {
      return null
    }
  }

  const openConversation = (id: string) => {
    if (switchingConversation || id === activeId) return
    detachActiveStream()
    void loadConversation(id)
  }

  const deleteConversation = (id: string) => {
    if (user) clearPendingJob(user.id, id)
    void deleteConversationMutation.mutateAsync(id)
    if (id === activeId) startNewConversation()
  }

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    })
  }, [messages, sending, thinkingStep])

  useEffect(() => {
    if (!sending) {
      setThinkingStep(0)
      return
    }
    const id = setInterval(() => {
      setThinkingStep((s) => Math.min(s + 1, THINKING_STEPS.length - 1))
    }, 3500)
    return () => clearInterval(id)
  }, [sending])

  // Live elapsed timer while the assistant is thinking / streaming. It counts
  // from `startRef` (an epoch ms), which a fresh send sets to `Date.now()` and
  // a resume seeds with the job's real queue time — so refreshing the page mid
  // generation never restarts the chrono at zero.
  useEffect(() => {
    if (!sending) return
    const tick = () => setElapsedMs(Math.max(0, Date.now() - startRef.current))
    tick()
    const id = setInterval(tick, 100)
    return () => clearInterval(id)
  }, [sending])

  const send = async (content: string) => {
    const trimmed = content.trim()
    if (!trimmed || sending) return

    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: 'user',
        content: trimmed,
        timestamp: nowLabel(),
      },
    ])
    setDraft('')
    startRef.current = Date.now()
    setSending(true)

    const assistantId = crypto.randomUUID()
    let started = false
    let sources: ChatMessageSource[] = []

    const measuredElapsed = () =>
      Math.round(((Date.now() - startRef.current) / 1000) * 10) / 10

    // Conversation mode never creates files implicitly. If the user asks for
    // one, guide them to the explicit generation mode instead.
    if (chatMode === 'conversation' && wantsDocument(trimmed)) {
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: 'assistant',
          content:
            'Cette demande nécessite le mode **Génération PDF**. Sélectionnez ce mode au-dessus de la zone de saisie, puis renvoyez votre demande. Aucun document n’a été créé.',
          timestamp: nowLabel(),
        },
      ])
      setSending(false)
      return
    }

    // Agent mode (Conversation only): the message starts with a slash command
    // (/legal, /finance, /compliance → one agent; /synthese → all three +
    // streamed synthesis). Streamed (fragmented) exactly like the normal chat.
    // In Génération PDF mode the SAME commands fall through to the report path
    // below, which produces a domain-specialised PDF instead of a text answer.
    const agentCmd = parseAgentCommand(trimmed)
    if (agentCmd && chatMode === 'conversation') {
      let agentLabel: string | undefined =
        agentCmd.mode === 'single' ? agentCmd.label : undefined
      let agentAnalyses: ChatAgentAnalysis[] | undefined
      let agentSources: ChatMessageSource[] = []

      // Create-or-update the single assistant message for this run.
      const upsertAssistant = (patch: Partial<ChatMessage>) => {
        setMessages((prev) => {
          if (prev.some((m) => m.id === assistantId)) {
            return prev.map((m) =>
              m.id === assistantId ? { ...m, ...patch } : m,
            )
          }
          return [
            ...prev,
            {
              id: assistantId,
              role: 'assistant',
              content: '',
              timestamp: nowLabel(),
              agentLabel,
              agentAnalyses,
              sources: agentSources,
              ...patch,
            },
          ]
        })
      }

      const conversationId = await ensureConversationId()
      if (!conversationId) {
        upsertAssistant({
          content:
            'Désolé, impossible de démarrer une conversation. Veuillez réessayer.',
        })
        setSending(false)
        return
      }

      let job
      try {
        job = await createBackgroundChatJob(agentCmd.toSend, {
          mode: 'agent',
          topK: 15,
          finalK: 5,
          documentId: selectedDocId || null,
          conversationId,
        })
      } catch (error) {
        upsertAssistant({
          content: `Désolé, la réponse n’a pas pu être démarrée : ${
            error instanceof Error ? error.message : 'service indisponible'
          }`,
        })
        setSending(false)
        return
      }
      started = true
      setStreamingId(assistantId)
      if (user) setPendingJob(user.id, conversationId, job.jobId)
      refreshConversations()
      // The user switched conversations during setup: the durable job keeps
      // running (resumable later), so don't stream into a foreign conversation.
      if (activeIdRef.current !== conversationId) return
      upsertAssistant({
        backgroundJobId: job.jobId,
        backgroundJobMode: 'agent',
        backgroundJobStatus: 'processing',
        backgroundJobEventCount: 0,
      })

      const controller = new AbortController()
      streamAbortRef.current = controller
      await streamBackgroundChatJob(
        job.jobId,
        {
          onEvent: (eventCount) => {
            recordBackgroundEvent(assistantId, eventCount)
          },
          onAgent: ({ mode, domain, label }) => {
            if (mode === 'single') {
              agentLabel =
                DOMAIN_STYLE[domain as AgentDomain]?.label ??
                label ??
                agentCmd.label
            }
          },
          onSources: (incoming) => {
            agentSources = toMessageSources(incoming)
            if (started) upsertAssistant({ sources: agentSources })
          },
          onAnalyses: (list) => {
            agentAnalyses = list.map((a) => ({
              domain: a.domain ?? '',
              label: DOMAIN_STYLE[a.domain as AgentDomain]?.label ?? a.label,
              status: a.status,
              answer: a.answer || a.message || 'Analyse indisponible.',
              sources: toMessageSources(a.sources ?? []),
            }))
            started = true
            setStreamingId(assistantId)
            upsertAssistant({ agentAnalyses })
          },
          onDelta: (text) => {
            if (!started) {
              started = true
              setStreamingId(assistantId)
              upsertAssistant({ content: text })
            } else {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: m.content + text }
                    : m,
                ),
              )
            }
          },
          onDone: ({ answer, metadata }) => {
            const elapsed =
              typeof metadata.generation_time === 'number'
                ? (metadata.generation_time as number)
                : measuredElapsed()
            if (!started && answer) {
              started = true
              upsertAssistant({ content: answer, elapsed })
              return
            }
            upsertAssistant({
              elapsed,
              sources: agentSources,
              agentAnalyses,
              backgroundJobStatus: 'completed',
            })
          },
          onCancelled: (notice) => {
            markMessageCancelled(assistantId, notice)
          },
          onError: (msg) => {
            if (!started) {
              setMessages((prev) => [
                ...prev,
                {
                  id: assistantId,
                  role: 'assistant',
                  content: `Désolé, l’interrogation des agents a échoué : ${msg}`,
                  timestamp: nowLabel(),
                },
              ])
            } else {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? {
                        ...m,
                        content: `${m.content}\n\n[Interrompu : ${msg}]`,
                        backgroundJobStatus: 'failed',
                      }
                    : m,
                ),
              )
            }
          },
        },
        { signal: controller.signal },
      )

      // Aborted by a conversation switch: keep the durable job + pending marker.
      if (controller.signal.aborted || activeIdRef.current !== conversationId)
        return
      if (streamAbortRef.current === controller) streamAbortRef.current = null
      if (user) clearPendingJob(user.id, conversationId)
      setStreamingId(null)
      setSending(false)
      return
    }

    // Generation mode: every request becomes a persisted, branded PDF. A
    // leading slash command (/legal, /finance, /compliance, /synthese) makes
    // the backend produce a domain-specialised report; the token is stripped
    // from the on-screen title but kept in the request the backend parses.
    if (chatMode === 'generation') {
      const reportQuestion = stripLeadingSlashCommand(trimmed) || trimmed
      const conversationId = await ensureConversationId()
      if (!conversationId) {
        setMessages((prev) => [
          ...prev,
          {
            id: assistantId,
            role: 'assistant',
            content:
              'Désolé, impossible de démarrer une conversation. Veuillez réessayer.',
            timestamp: nowLabel(),
          },
        ])
        setSending(false)
        return
      }
      let controller: AbortController | null = null
      try {
        const reportJob = await createBackgroundChatJob(trimmed, {
          mode: 'report',
          topK: 15,
          finalK: 5,
          documentId: selectedDocId || null,
          conversationId,
        })
        if (user) setPendingJob(user.id, conversationId, reportJob.jobId)
        refreshConversations()
        // Switched conversations during setup: leave the durable job to resume.
        if (activeIdRef.current !== conversationId) return
        setMessages((prev) => [
          ...prev,
          {
            id: assistantId,
            role: 'assistant',
            content: 'Création du rapport en cours…',
            generatedReportSourceDocumentId: selectedDocId || undefined,
            generatedReportQuestion: reportQuestion,
            timestamp: nowLabel(),
            backgroundJobId: reportJob.jobId,
            backgroundJobMode: 'report',
            backgroundJobStatus: 'processing',
            backgroundJobEventCount: 0,
          },
        ])
        setStreamingId(assistantId)
        controller = new AbortController()
        streamAbortRef.current = controller
        await streamBackgroundChatJob(reportJob.jobId, {
          onEvent: (eventCount) => {
            recordBackgroundEvent(assistantId, eventCount)
          },
          onDocument: ({
            html,
            generatedDocumentId,
            sources: incoming,
            metadata,
          }) => {
            const sourceIds = Array.from(
              new Set(incoming.map((source) => source.document_id).filter(Boolean)),
            )
            const sourceDocumentId =
              selectedDocId ||
              (sourceIds.length === 1 ? sourceIds[0] : undefined)
            setMessages((prev) =>
              prev.map((message) =>
                message.id === assistantId
                  ? {
                      ...message,
                      content:
                        'Le rapport est prêt. Vous pouvez le consulter ou le télécharger.',
                      document: html,
                      generatedDocumentId,
                      generatedReportSourceDocumentId: sourceDocumentId,
                      sources: toMessageSources(incoming),
                      elapsed:
                        typeof metadata.generation_time === 'number'
                          ? metadata.generation_time
                          : measuredElapsed(),
                    }
                  : message,
              ),
            )
          },
          onDone: ({ answer }) => {
            // Normally the PDF arrived via onDocument; if not (e.g. an
            // out-of-domain slash command was refused), show the message.
            setMessages((prev) =>
              prev.map((message) =>
                message.id === assistantId
                  ? {
                      ...message,
                      content: message.document
                        ? message.content
                        : answer || message.content,
                      backgroundJobStatus: 'completed',
                    }
                  : message,
              ),
            )
          },
          onCancelled: (notice) => {
            markMessageCancelled(assistantId, notice)
          },
          onError: (message) => {
            setMessages((prev) =>
              prev.map((item) =>
                item.id === assistantId
                  ? {
                      ...item,
                      content: `La génération du rapport a échoué : ${message}`,
                      backgroundJobStatus: 'failed',
                    }
                  : item,
              ),
            )
          },
        }, { signal: controller.signal })
      } catch (err) {
        const msg =
          err instanceof Error ? err.message : 'La génération a échoué.'
        setMessages((prev) => {
          const exists = prev.some((message) => message.id === assistantId)
          if (exists) {
            return prev.map((message) =>
              message.id === assistantId
                ? {
                    ...message,
                    content: `La génération du rapport a échoué : ${msg}`,
                    backgroundJobStatus: 'failed',
                  }
                : message,
            )
          }
          return [
            ...prev,
            {
              id: assistantId,
              role: 'assistant',
              content: `La génération du rapport a échoué : ${msg}`,
              timestamp: nowLabel(),
            },
          ]
        })
      } finally {
        // If the user switched conversations mid-generation the stream was
        // aborted locally; keep the durable job + pending marker so it can be
        // resumed later instead of clearing it here.
        const aborted =
          controller?.signal.aborted || activeIdRef.current !== conversationId
        if (!aborted) {
          if (streamAbortRef.current === controller)
            streamAbortRef.current = null
          if (user) clearPendingJob(user.id, conversationId)
          setStreamingId(null)
          setSending(false)
        }
      }
      return
    }

    const conversationId = await ensureConversationId()
    if (!conversationId) {
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: 'assistant',
          content:
            'Désolé, impossible de démarrer une conversation. Veuillez réessayer.',
          timestamp: nowLabel(),
        },
      ])
      setSending(false)
      return
    }

    let job
    try {
      job = await createBackgroundChatJob(trimmed, {
        mode: 'chat',
        topK: 15,
        finalK: 5,
        documentId: selectedDocId || null,
        conversationId,
      })
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: 'assistant',
          content: `Désolé, la réponse n’a pas pu être démarrée : ${
            error instanceof Error ? error.message : 'service indisponible'
          }`,
          timestamp: nowLabel(),
        },
      ])
      setSending(false)
      return
    }
    started = true
    setStreamingId(assistantId)
    if (user) setPendingJob(user.id, conversationId, job.jobId)
    refreshConversations()
    // Switched conversations during setup: keep the durable job for later resume.
    if (activeIdRef.current !== conversationId) return
    setMessages((prev) => [
      ...prev,
      {
        id: assistantId,
        role: 'assistant',
        content: '',
        sources,
        timestamp: nowLabel(),
        backgroundJobId: job.jobId,
        backgroundJobMode: 'chat',
        backgroundJobStatus: 'processing',
        backgroundJobEventCount: 0,
      },
    ])

    const controller = new AbortController()
    streamAbortRef.current = controller
    await streamBackgroundChatJob(
      job.jobId,
      {
        onEvent: (eventCount) => {
          recordBackgroundEvent(assistantId, eventCount)
        },
        onSources: (incoming) => {
          sources = toMessageSources(incoming)
        },
        onDelta: (text) => {
          if (!started) {
            started = true
            setStreamingId(assistantId)
            setMessages((prev) => [
              ...prev,
              {
                id: assistantId,
                role: 'assistant',
                content: text,
                sources,
                timestamp: nowLabel(),
              },
            ])
          } else {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: m.content + text } : m,
              ),
            )
          }
        },
        onDone: ({ answer, metadata }) => {
          const elapsed =
            typeof metadata.generation_time === 'number'
              ? metadata.generation_time
              : measuredElapsed()
          // Fallback: if nothing streamed but the server returned a final
          // answer, render it so the user never sees an empty reply.
          if (!started && answer) {
            started = true
            setMessages((prev) => [
              ...prev,
              {
                id: assistantId,
                role: 'assistant',
                content: answer,
                sources,
                timestamp: nowLabel(),
                elapsed,
              },
            ])
            return
          }
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? {
                    ...m,
                    sources,
                    elapsed,
                    backgroundJobStatus: 'completed',
                  }
                : m,
            ),
          )
        },
        onCancelled: (notice) => {
          markMessageCancelled(assistantId, notice)
        },
        onError: (msg) => {
          if (!started) {
            setMessages((prev) => [
              ...prev,
              {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: `Désolé, une erreur est survenue : ${msg}`,
                timestamp: nowLabel(),
              },
            ])
          } else {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? {
                      ...m,
                      content: `${m.content}\n\n[Interrompu : ${msg}]`,
                      backgroundJobStatus: 'failed',
                    }
                  : m,
              ),
            )
          }
        },
      },
      { signal: controller.signal },
    )

    // Aborted by a conversation switch: keep the durable job + pending marker.
    if (controller.signal.aborted || activeIdRef.current !== conversationId)
      return
    if (streamAbortRef.current === controller) streamAbortRef.current = null
    if (user) clearPendingJob(user.id, conversationId)
    setStreamingId(null)
    setSending(false)
  }

  const activeJobMessage = messages.find(
    (message) =>
      message.id === streamingId &&
      message.backgroundJobId &&
      message.backgroundJobStatus === 'processing',
  )

  const stopGeneration = async () => {
    if (!activeJobMessage?.backgroundJobId || cancelling) return
    setCancelling(true)
    setAttachError(null)
    try {
      await cancelBackgroundChatJob(activeJobMessage.backgroundJobId)
      resumingJobsRef.current.delete(activeJobMessage.backgroundJobId)
      markMessageCancelled(
        activeJobMessage.id,
        'Génération arrêtée à votre demande.',
      )
      setStreamingId(null)
      setSending(false)
    } catch (error) {
      setAttachError(
        error instanceof Error
          ? error.message
          : "La génération n'a pas pu être arrêtée. Veuillez réessayer.",
      )
    } finally {
      setCancelling(false)
    }
  }

  // Slash-command (agent picker) menu: shown while the composer holds only a
  // partial "/command" token (no space yet), filtered by what's typed.
  const slashToken = (() => {
    const trimmedStart = draft.replace(/^\s+/, '')
    if (!trimmedStart.startsWith('/')) return null
    const m = /^\/([\p{L}]*)$/u.exec(trimmedStart)
    return m ? m[1].toLowerCase() : null
  })()
  const slashMatches =
    slashToken === null
      ? []
      : SLASH_COMMANDS.filter((c) => c.key.startsWith(slashToken))
  // The agent picker is available in both modes: in Conversation it streams a
  // text answer, in Génération PDF it produces a domain-specialised report.
  const slashMenuOpen = !slashClosed && !sending && slashMatches.length > 0
  const activeSlash = Math.min(slashIndex, Math.max(0, slashMatches.length - 1))

  const applySlash = (cmd: SlashCommand) => {
    setDraft(`${cmd.command} `)
    setSlashClosed(true)
    setSlashIndex(0)
    requestAnimationFrame(() => textareaRef.current?.focus())
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Card
        className="flex h-[calc(100dvh-7.5rem)] min-h-[420px] flex-col overflow-hidden lg:col-span-2"
        padding="none"
      >
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-border bg-gradient-to-r from-brand to-brand-dark px-5 py-4 text-white">
          <div className="flex size-10 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
            <Logo className="size-6" />
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-sm font-semibold">Assistant LegalLink</h2>
            <p className="flex items-center gap-1.5 text-xs text-blue-100">
              <span className="size-1.5 rounded-full bg-emerald-300 animate-pulse" />
              <span className="truncate">Portée : {scopeLabel}</span>
            </p>
          </div>
          <button
            type="button"
            onClick={startNewConversation}
            disabled={switchingConversation}
            title="Démarrer une nouvelle conversation (la génération en cours continue en arrière-plan)"
            className="inline-flex items-center gap-1.5 rounded-lg bg-white/15 px-3 py-1.5 text-xs font-medium text-white backdrop-blur transition hover:bg-white/25 disabled:opacity-50"
          >
            <Plus className="size-3.5" />
            <span className="hidden sm:inline">Nouvelle</span>
          </button>
        </div>

        {/* Messages */}
        <div
          ref={scrollRef}
          className="flex-1 space-y-4 overflow-y-auto bg-canvas/60 p-5 scrollbar-thin"
        >
          <div className="flex justify-center">
            <span className="rounded-full bg-white px-3 py-1 text-[11px] font-medium text-slate-500 shadow-sm ring-1 ring-border">
              {todayHeader()}
            </span>
          </div>

          {messages.map((message) => (
            <MessageRow
              key={message.id}
              message={message}
              streaming={message.id === streamingId}
              liveSeconds={
                message.id === streamingId ? elapsedMs / 1000 : undefined
              }
            />
          ))}

          {sending && !streamingId ? (
            <ThinkingBubble step={thinkingStep} seconds={elapsedMs / 1000} />
          ) : null}
        </div>

        {/* Composer */}
        <div className="border-t border-border bg-white p-4">
          <div className="mb-2 flex w-full rounded-xl border border-border bg-slate-50 p-1">
            <button
              type="button"
              disabled={sending}
              onClick={() => {
                setChatMode('conversation')
                setSlashClosed(false)
              }}
              className={cn(
                'flex flex-1 items-center justify-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition disabled:opacity-50',
                chatMode === 'conversation'
                  ? 'bg-white text-brand shadow-sm ring-1 ring-border'
                  : 'text-slate-500 hover:text-slate-700',
              )}
            >
              <MessageSquare className="size-3.5" />
              Conversation
            </button>
            <button
              type="button"
              disabled={sending}
              onClick={() => {
                setChatMode('generation')
                setSlashClosed(false)
              }}
              className={cn(
                'flex flex-1 items-center justify-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition disabled:opacity-50',
                chatMode === 'generation'
                  ? 'bg-brand text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-700',
              )}
            >
              <FileOutput className="size-3.5" />
              Génération PDF
            </button>
          </div>
          <div className="mb-2 flex items-center gap-2 text-xs">
            <span className="flex shrink-0 items-center gap-1.5 font-medium text-slate-500">
              <Library className="size-3.5 text-brand" />
              Interroger
            </span>
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              disabled={sending}
              className="min-w-0 flex-1 truncate rounded-lg border border-border bg-slate-50 px-2.5 py-1.5 text-slate-700 outline-none transition focus:border-brand focus:bg-white focus:ring-2 focus:ring-brand/15 disabled:opacity-60"
            >
              <option value="">
                Tous les documents ({searchableDocs.length})
              </option>
              {searchableDocs.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
          </div>
          {upload.isPending || activeUpload ? (
            <div className="mb-2 flex items-center gap-2 rounded-lg border border-border bg-slate-50 px-2.5 py-1.5 text-xs">
              {!upload.isPending && uploadReady ? (
                <FileText className="size-3.5 shrink-0 text-success" />
              ) : (
                <Loader2 className="size-3.5 shrink-0 animate-spin text-brand" />
              )}
              <span className="min-w-0 flex-1 truncate text-slate-600">
                {upload.isPending
                  ? 'Envoi du fichier…'
                  : `${activeUpload?.filename} · ${uploadReady ? 'prêt à être interrogé' : 'préparation en cours…'}`}
              </span>
              {activeUpload && !upload.isPending ? (
                <button
                  type="button"
                  onClick={() => setActiveUpload(null)}
                  className="shrink-0 rounded-md px-1.5 py-0.5 text-[11px] font-medium text-slate-400 transition hover:text-slate-600"
                >
                  Fermer
                </button>
              ) : null}
            </div>
          ) : null}
          {attachError ? (
            <p className="mb-2 text-xs text-danger">{attachError}</p>
          ) : null}
          <div className="relative">
            {slashMenuOpen ? (
              <div className="absolute bottom-full left-0 z-20 mb-2 w-full max-w-md overflow-hidden rounded-xl border border-border bg-white shadow-lg">
                <p className="border-b border-border px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">
                  {chatMode === 'generation'
                    ? 'Générer un rapport PDF spécialisé'
                    : 'Interroger un agent'}
                </p>
                {slashMatches.map((cmd, i) => {
                  const Icon = cmd.icon
                  return (
                    <button
                      key={cmd.key}
                      type="button"
                      // onMouseDown (not onClick) so the textarea keeps focus.
                      onMouseDown={(e) => {
                        e.preventDefault()
                        applySlash(cmd)
                      }}
                      onMouseEnter={() => setSlashIndex(i)}
                      className={cn(
                        'flex w-full items-center gap-2.5 px-3 py-2 text-left transition',
                        i === activeSlash ? 'bg-brand-soft' : 'hover:bg-slate-50',
                      )}
                    >
                      <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-primary-soft text-primary">
                        <Icon className="size-4" />
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="flex items-center gap-1.5">
                          <span className="text-sm font-medium text-slate-800">
                            {cmd.label}
                          </span>
                          <code className="rounded bg-slate-100 px-1 text-[10px] text-slate-500">
                            {cmd.command}
                          </code>
                        </span>
                        <span className="block truncate text-[11px] text-slate-400">
                          {cmd.desc}
                        </span>
                      </span>
                    </button>
                  )
                })}
              </div>
            ) : null}
            <div className="flex items-end gap-2 rounded-2xl border border-border bg-slate-50 p-2 shadow-sm transition-all focus-within:border-brand focus-within:bg-white focus-within:ring-2 focus-within:ring-brand/15">
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf,.pdf"
                className="hidden"
                onChange={(e) => {
                  attachFile(e.target.files?.[0])
                  // Allow re-selecting the same file later.
                  e.target.value = ''
                }}
              />
              <button
                type="button"
                onClick={handleAttachClick}
                disabled={sending || upload.isPending}
                className="rounded-xl p-2.5 text-muted transition hover:bg-white hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                aria-label="Joindre un fichier PDF"
                title="Joindre un PDF"
              >
                {upload.isPending ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  <Paperclip className="size-4" />
                )}
              </button>
              <textarea
                ref={textareaRef}
                value={draft}
                onChange={(e) => {
                  setDraft(e.target.value)
                  setSlashClosed(false)
                  setSlashIndex(0)
                }}
                onKeyDown={(e) => {
                  if (slashMenuOpen) {
                    if (e.key === 'ArrowDown') {
                      e.preventDefault()
                      setSlashIndex((i) => (i + 1) % slashMatches.length)
                      return
                    }
                    if (e.key === 'ArrowUp') {
                      e.preventDefault()
                      setSlashIndex(
                        (i) =>
                          (i - 1 + slashMatches.length) % slashMatches.length,
                      )
                      return
                    }
                    if (e.key === 'Enter' || e.key === 'Tab') {
                      e.preventDefault()
                      applySlash(slashMatches[activeSlash])
                      return
                    }
                    if (e.key === 'Escape') {
                      e.preventDefault()
                      setSlashClosed(true)
                      return
                    }
                  }
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    send(draft)
                  }
                }}
                rows={1}
                placeholder={
                  chatMode === 'generation'
                    ? 'Décrivez le rapport PDF… (ou / pour un rapport d’agent)'
                    : 'Écrivez votre message… (tapez / pour choisir un agent)'
                }
                disabled={sending || switchingConversation}
                className="max-h-32 min-h-[44px] flex-1 resize-none bg-transparent py-2.5 text-sm outline-none placeholder:text-slate-400 disabled:opacity-60"
              />
              {sending && activeJobMessage ? (
                <Button
                  size="sm"
                  variant="secondary"
                  className="rounded-xl"
                  onClick={stopGeneration}
                  disabled={cancelling}
                  leftIcon={
                    cancelling ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Square className="size-3.5 fill-current" />
                    )
                  }
                >
                  {cancelling ? 'Arrêt…' : 'Arrêter'}
                </Button>
              ) : (
                <Button
                  size="sm"
                  className="rounded-xl"
                  onClick={() => send(draft)}
                  disabled={sending || switchingConversation || !draft.trim()}
                  leftIcon={
                    sending ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Send className="size-4" />
                    )
                  }
                >
                  {sending ? 'Analyse…' : 'Envoyer'}
                </Button>
              )}
            </div>
          </div>
          <p className="mt-2 px-1 text-[11px] text-slate-400">
            {chatMode === 'generation' ? (
              <>
                Chaque demande crée et enregistre automatiquement un PDF · Tapez{' '}
                <code className="rounded bg-slate-100 px-1">/</code> pour un
                rapport spécialisé (juridique, financier, conformité) · Entrée
                pour envoyer
              </>
            ) : (
              <>
                Entrée pour envoyer · Maj + Entrée pour un retour à la ligne ·
                Tapez <code className="rounded bg-slate-100 px-1">/</code> pour
                interroger un agent
              </>
            )}
          </p>
        </div>
      </Card>

      <div className="space-y-4">
        <Card padding="lg">
          <CardHeader
            title="Conversations"
            subtitle={
              conversations.length
                ? `${conversations.length} enregistrée${conversations.length > 1 ? 's' : ''}`
                : 'Votre historique'
            }
            action={
              <button
                type="button"
                onClick={startNewConversation}
                disabled={switchingConversation}
                title="Nouvelle conversation (la génération en cours continue en arrière-plan)"
                className="inline-flex items-center gap-1 rounded-lg border border-border px-2 py-1 text-xs font-medium text-slate-600 transition hover:border-brand/40 hover:text-brand disabled:opacity-50"
              >
                <Plus className="size-3.5" />
                Nouvelle
              </button>
            }
          />
          {conversations.length ? (
            <div className="mt-1 max-h-64 space-y-1 overflow-y-auto scrollbar-thin">
              {conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={cn(
                    'group flex items-center gap-2 rounded-lg border px-2.5 py-2 transition',
                    conv.id === activeId
                      ? 'border-brand/40 bg-brand-soft'
                      : 'border-transparent hover:border-border hover:bg-slate-50',
                  )}
                >
                  <button
                    type="button"
                    onClick={() => openConversation(conv.id)}
                    disabled={switchingConversation}
                    className="flex min-w-0 flex-1 items-start gap-2 text-left disabled:cursor-not-allowed"
                  >
                    <MessageSquare
                      className={cn(
                        'mt-0.5 size-3.5 shrink-0',
                        conv.id === activeId ? 'text-brand' : 'text-slate-400',
                      )}
                    />
                    <span className="min-w-0">
                      <span
                        className={cn(
                          'block truncate text-xs font-medium',
                          conv.id === activeId
                            ? 'text-brand'
                            : 'text-slate-700',
                        )}
                      >
                        {conv.title || 'Nouvelle conversation'}
                      </span>
                      <span className="block text-[10px] text-slate-400">
                        {relativeTime(new Date(conv.updatedAt).getTime())}
                      </span>
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteConversation(conv.id)}
                    title="Supprimer la conversation"
                    aria-label="Supprimer la conversation"
                    className="shrink-0 rounded-md p-1 text-slate-300 opacity-0 transition hover:bg-danger-soft hover:text-danger group-hover:opacity-100"
                  >
                    <Trash2 className="size-3.5" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-2 text-xs text-slate-400">
              Vos conversations apparaîtront ici, enregistrées et accessibles
              depuis n’importe quelle session.
            </p>
          )}
        </Card>

        <Card padding="lg">
          <CardHeader title="Document" subtitle="PDF uniquement · max 25 Mo" />
          <UploadZone onFiles={(files) => attachFile(files[0])} />
          {upload.isPending ? (
            <p className="mt-3 text-xs text-brand">Envoi du document…</p>
          ) : null}
          {activeUpload ? (
            <IngestionProgress
              documentId={activeUpload.documentId}
              filename={activeUpload.filename}
            />
          ) : null}
        </Card>

        <Card padding="lg">
          <CardHeader
            title="Suggestions"
            subtitle="Actions rapides"
            action={<Sparkles className="size-4 text-brand" />}
          />
          <div className="flex flex-col gap-2">
            {suggestions.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => send(item.label)}
                disabled={sending || switchingConversation}
                className="rounded-lg border border-border bg-white px-3 py-2.5 text-left text-sm text-slate-700 transition hover:border-brand/40 hover:bg-brand-soft hover:text-brand disabled:cursor-not-allowed disabled:opacity-60"
              >
                {item.label}
              </button>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
