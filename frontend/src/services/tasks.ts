import type { UserTask } from '@/types'
import { api } from './api'

interface BackendTask {
  id: string
  type: UserTask['type']
  title: string
  status: UserTask['status']
  progress: number
  message: string
  document_id: string | null
  destination: string
  created_at: string
  updated_at: string
  error: string | null
}

export async function cancelTask(
  id: string,
  type: UserTask['type'],
): Promise<void> {
  await api.post(`/tasks/${id}/cancel`, { type })
}

export async function fetchTasks(): Promise<UserTask[]> {
  const { data } = await api.get<{ items: BackendTask[] }>('/tasks')
  return data.items.map((item) => ({
    id: item.id,
    type: item.type,
    title: item.title,
    status: item.status,
    progress: item.progress,
    message: item.message,
    documentId: item.document_id,
    destination: item.destination,
    createdAt: item.created_at,
    updatedAt: item.updated_at,
    error: item.error,
  }))
}
