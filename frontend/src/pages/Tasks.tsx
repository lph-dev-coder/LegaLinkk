import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Bot,
  CheckCircle2,
  Clock3,
  FileOutput,
  Gavel,
  GitCompareArrows,
  Loader2,
  MessageSquare,
  RefreshCw,
  Sparkles,
  StopCircle,
  UploadCloud,
  XCircle,
} from 'lucide-react'
import { EmptyState } from '@/components/EmptyState'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader } from '@/components/ui/Card'
import { useTasks } from '@/hooks/useTasks'
import { cancelTask } from '@/services/tasks'
import { cn } from '@/lib/cn'
import type { UserTask } from '@/types'

type Filter = 'active' | 'completed' | 'all'

const TYPE_META = {
  chat: { label: 'Conversation', icon: MessageSquare },
  agent: { label: 'Consultation spécialisée', icon: Bot },
  report: { label: 'Rapport PDF', icon: FileOutput },
  analysis: { label: 'Analyse de contrat', icon: Gavel },
  synthesis: { label: 'Synthèse multi-agents', icon: Sparkles },
  comparison: { label: 'Comparaison de contrats', icon: GitCompareArrows },
  ingestion: { label: 'Préparation du document', icon: UploadCloud },
} satisfies Record<UserTask['type'], { label: string; icon: typeof Clock3 }>

function formatDate(value: string) {
  return new Date(value).toLocaleString('fr-FR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function TasksPage() {
  const { data = [], isLoading, isError, refetch, isFetching } = useTasks()
  const [filter, setFilter] = useState<Filter>('active')
  const queryClient = useQueryClient()
  const cancelMutation = useMutation({
    mutationFn: ({ id, type }: { id: string; type: UserTask['type'] }) =>
      cancelTask(id, type),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  })
  const filtered = useMemo(
    () =>
      data.filter((task) => {
        if (filter === 'active')
          return task.status === 'queued' || task.status === 'processing'
        if (filter === 'completed')
          return ['completed', 'failed', 'cancelled'].includes(task.status)
        return true
      }),
    [data, filter],
  )
  const activeCount = data.filter((task) =>
    ['queued', 'processing'].includes(task.status),
  ).length

  return (
    <div className="space-y-6">
      <Card padding="lg">
        <CardHeader
          title="Centre des tâches"
          subtitle="Suivez vos rapports, analyses et réponses en arrière-plan"
          action={
            <Button
              size="sm"
              variant="outline"
              onClick={() => refetch()}
              disabled={isFetching}
            >
              <RefreshCw
                className={cn('size-4', isFetching && 'animate-spin')}
              />
              Actualiser
            </Button>
          }
        />

        <div className="mb-5 flex flex-wrap gap-2">
          {(
            [
              ['active', `En cours (${activeCount})`],
              ['completed', 'Terminées'],
              ['all', 'Toutes'],
            ] as Array<[Filter, string]>
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => setFilter(value)}
              className={cn(
                'rounded-full border px-3.5 py-1.5 text-xs font-semibold transition',
                filter === value
                  ? 'border-brand bg-brand text-white'
                  : 'border-border bg-white text-slate-500 hover:border-brand/30',
              )}
            >
              {label}
            </button>
          ))}
        </div>

        {isLoading ? (
          <LoadingSpinner label="Chargement de vos tâches…" />
        ) : isError ? (
          <EmptyState
            icon={<XCircle className="size-6 text-danger" />}
            title="Tâches indisponibles"
            description="Impossible de charger le centre des tâches pour le moment."
          />
        ) : !filtered.length ? (
          <EmptyState
            icon={<CheckCircle2 className="size-6 text-success" />}
            title={
              filter === 'active'
                ? 'Aucune tâche en cours'
                : 'Aucune tâche à afficher'
            }
            description="Les rapports et analyses lancés apparaîtront automatiquement ici."
          />
        ) : (
          <ul className="space-y-3">
            {filtered.map((task) => {
              const meta = TYPE_META[task.type]
              const Icon = meta.icon
              const active =
                task.status === 'queued' || task.status === 'processing'
              return (
                <li
                  key={task.id}
                  className="rounded-xl border border-border bg-white p-4 transition hover:border-brand/30 hover:shadow-sm"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="flex min-w-0 flex-1 items-start gap-3">
                      <span
                        className={cn(
                          'flex size-10 shrink-0 items-center justify-center rounded-xl',
                          active
                            ? 'bg-brand-soft text-brand'
                            : task.status === 'completed'
                              ? 'bg-emerald-50 text-success'
                              : task.status === 'cancelled'
                                ? 'bg-amber-50 text-amber-600'
                              : 'bg-red-50 text-danger',
                        )}
                      >
                        {active ? (
                          <Loader2 className="size-5 animate-spin" />
                        ) : (
                          <Icon className="size-5" />
                        )}
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="max-w-xl truncate text-sm font-semibold text-slate-900">
                            {task.title}
                          </p>
                          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-500">
                            {meta.label}
                          </span>
                        </div>
                        <p className="mt-1 text-xs text-muted">
                          {task.error || task.message} · {formatDate(task.createdAt)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {active && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-danger/30 text-danger hover:bg-red-50"
                          disabled={
                            cancelMutation.isPending &&
                            cancelMutation.variables?.id === task.id
                          }
                          onClick={() =>
                            cancelMutation.mutate({
                              id: task.id,
                              type: task.type,
                            })
                          }
                        >
                          {cancelMutation.isPending &&
                          cancelMutation.variables?.id === task.id ? (
                            <Loader2 className="size-4 animate-spin" />
                          ) : (
                            <StopCircle className="size-4" />
                          )}
                          Arrêter
                        </Button>
                      )}
                      <Link to={task.destination}>
                        <Button size="sm" variant="outline">
                          {active ? 'Voir le suivi' : 'Ouvrir'}
                        </Button>
                      </Link>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="mb-1 flex items-center justify-between text-[11px] text-slate-400">
                      <span>
                        {task.status === 'queued'
                          ? 'En attente'
                          : task.status === 'processing'
                            ? 'En cours'
                            : task.status === 'completed'
                              ? 'Terminée'
                              : task.status === 'cancelled'
                                ? 'Annulée'
                              : 'Échec'}
                      </span>
                      <span>{task.progress}%</span>
                    </div>
                    <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={cn(
                          'h-full rounded-full transition-all duration-500',
                          task.status === 'failed'
                            ? 'bg-danger'
                            : task.status === 'cancelled'
                              ? 'bg-amber-500'
                              : 'bg-brand',
                        )}
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                  </div>
                </li>
              )
            })}
          </ul>
        )}
      </Card>
    </div>
  )
}
