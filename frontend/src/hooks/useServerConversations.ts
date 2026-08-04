import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  deleteConversationApi,
  listConversations,
} from '@/services/conversations'

const CONVERSATIONS_KEY = ['chat-conversations'] as const

/** History sidebar: real conversations persisted in PostgreSQL. */
export function useConversationList() {
  return useQuery({
    queryKey: CONVERSATIONS_KEY,
    queryFn: listConversations,
    staleTime: 10_000,
  })
}

export function useDeleteConversation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteConversationApi,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: CONVERSATIONS_KEY })
    },
  })
}

export { CONVERSATIONS_KEY }
