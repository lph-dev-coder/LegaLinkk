import { useQuery } from '@tanstack/react-query'
import { fetchTasks } from '@/services/tasks'

export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: fetchTasks,
    refetchInterval: (query) =>
      query.state.data?.some((task) =>
        ['queued', 'processing'].includes(task.status),
      )
        ? 1500
        : 10_000,
    staleTime: 0,
  })
}
