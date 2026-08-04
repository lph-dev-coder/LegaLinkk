import type { ChatAgentAnalysis, ChatMessage, ChatMessageSource } from '@/types'
import { api } from './api'

export interface ServerConversationSummary {
  id: string
  title: string | null
  createdAt: string
  updatedAt: string
}

interface ServerMessageDto {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  metadata: Record<string, unknown>
}

interface ConversationResponseDto {
  id: string
  title: string | null
  created_at: string
  updated_at: string
  messages: ServerMessageDto[]
}

interface ConversationListResponseDto {
  items: ConversationResponseDto[]
  total: number
}

function mapSummary(dto: ConversationResponseDto): ServerConversationSummary {
  return {
    id: dto.id,
    title: dto.title,
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
  }
}

function formatTimestamp(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

/** Domain -> business-friendly agent label (mirrors Consultation's DOMAIN_STYLE). */
const AGENT_DOMAIN_LABELS: Record<string, string> = {
  legal: 'Agent Juridique',
  finance: 'Agent Financier',
  compliance: 'Agent Conformité',
}

function toMessageSources(raw: unknown): ChatMessageSource[] {
  if (!Array.isArray(raw)) return []
  const seen = new Set<string>()
  const out: ChatMessageSource[] = []
  for (const item of raw) {
    if (!item || typeof item !== 'object') continue
    const rec = item as Record<string, unknown>
    const filename = typeof rec.filename === 'string' ? rec.filename : null
    if (!filename || seen.has(filename)) continue
    seen.add(filename)
    out.push({
      filename,
      documentId:
        typeof rec.document_id === 'string' ? rec.document_id : undefined,
    })
  }
  return out
}

function mapAnalyses(raw: unknown): ChatAgentAnalysis[] | undefined {
  if (!Array.isArray(raw) || !raw.length) return undefined
  return raw.map((entry) => {
    const rec = (entry ?? {}) as Record<string, unknown>
    const domain = typeof rec.domain === 'string' ? rec.domain : ''
    const rawLabel = typeof rec.label === 'string' ? rec.label : ''
    return {
      domain,
      label: AGENT_DOMAIN_LABELS[domain] ?? rawLabel,
      status: typeof rec.status === 'string' ? rec.status : 'ok',
      answer: typeof rec.answer === 'string' ? rec.answer : '',
      sources: toMessageSources(rec.sources),
    }
  })
}

function mapMessage(dto: ServerMessageDto): ChatMessage {
  const base: ChatMessage = {
    id: dto.id,
    role: dto.role,
    content: dto.content,
    timestamp: formatTimestamp(dto.timestamp),
  }
  if (dto.role !== 'assistant') return base

  const metadata = (dto.metadata ?? {}) as Record<string, unknown>
  const generation = (metadata.generation ?? {}) as Record<string, unknown>
  const sources = toMessageSources(metadata.sources)
  const elapsed =
    typeof generation.generation_time === 'number'
      ? generation.generation_time
      : undefined
  const rawAgentLabel =
    typeof metadata.agent_label === 'string' ? metadata.agent_label : undefined
  const agentDomain =
    typeof metadata.agent_domain === 'string' ? metadata.agent_domain : undefined
  const agentLabel = agentDomain
    ? (AGENT_DOMAIN_LABELS[agentDomain] ?? rawAgentLabel)
    : rawAgentLabel
  const generatedDocumentId =
    typeof metadata.generated_document_id === 'string'
      ? metadata.generated_document_id
      : undefined

  return {
    ...base,
    sources: sources.length ? sources : undefined,
    elapsed,
    agentLabel,
    agentAnalyses: mapAnalyses(metadata.agent_analyses),
    generatedDocumentId,
  }
}

export async function createConversation(
  title?: string,
): Promise<ServerConversationSummary> {
  const { data } = await api.post<ConversationResponseDto>(
    '/chat/conversations',
    title ? { title } : {},
  )
  return mapSummary(data)
}

export async function listConversations(): Promise<
  ServerConversationSummary[]
> {
  const { data } = await api.get<ConversationListResponseDto>(
    '/chat/conversations',
  )
  return data.items.map(mapSummary)
}

export async function getConversation(
  id: string,
): Promise<{ id: string; messages: ChatMessage[] }> {
  const { data } = await api.get<ConversationResponseDto>(
    `/chat/conversations/${id}`,
  )
  return { id: data.id, messages: data.messages.map(mapMessage) }
}

export async function deleteConversationApi(id: string): Promise<void> {
  await api.delete(`/chat/conversations/${id}`)
}
