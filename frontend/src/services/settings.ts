import { api } from './api'

export type AgentPromptKey = 'legal' | 'finance' | 'compliance' | 'synthesis'

export interface AgentPromptField {
  label: string
  value: string
  default: string
  customized: boolean
  uses_no_answer: boolean
}

export type AgentPrompts = Record<AgentPromptKey, AgentPromptField>

export async function fetchAgentPrompts(): Promise<AgentPrompts> {
  const { data } = await api.get<AgentPrompts>('/settings/prompts')
  return data
}

export async function saveAgentPrompts(
  payload: Partial<Record<AgentPromptKey, string>>,
): Promise<AgentPrompts> {
  const { data } = await api.put<AgentPrompts>('/settings/prompts', payload)
  return data
}
