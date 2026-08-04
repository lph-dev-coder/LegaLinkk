import { useMemo } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ClipboardCheck,
  FileText,
  ListChecks,
  ShieldCheck,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { DocumentCard } from '@/components/DocumentCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Card, CardHeader } from '@/components/ui/Card'
import { useDocuments, useRecentActivity } from '@/hooks/useDocuments'
import { useTasks } from '@/hooks/useTasks'
import { cn } from '@/lib/cn'

const RISK_BANDS = [
  {
    key: 'high',
    label: 'Risque élevé',
    range: 'Score inférieur à 50',
    bar: 'bg-danger',
    dot: 'bg-danger',
    text: 'text-danger',
    soft: 'bg-danger-soft',
  },
  {
    key: 'medium',
    label: 'Risque modéré',
    range: 'Score de 50 à 79',
    bar: 'bg-warning',
    dot: 'bg-warning',
    text: 'text-amber-700',
    soft: 'bg-warning-soft',
  },
  {
    key: 'low',
    label: 'Risque faible',
    range: 'Score de 80 à 100',
    bar: 'bg-success',
    dot: 'bg-success',
    text: 'text-success',
    soft: 'bg-success-soft',
  },
] as const

export function DashboardPage() {
  const { data: documents, isLoading: documentsLoading } = useDocuments()
  const { data: activity, isLoading } = useRecentActivity()
  const { data: tasks = [], isLoading: tasksLoading } = useTasks()

  const stats = useMemo(() => {
    const list = documents ?? []
    const analyzed = list.filter((document) => document.score != null)
    const high = analyzed.filter((document) => (document.score ?? 100) < 50).length
    const medium = analyzed.filter((document) => {
      const score = document.score ?? 100
      return score >= 50 && score < 80
    }).length
    const low = analyzed.filter((document) => (document.score ?? 0) >= 80).length
    const activeTasks = tasks.filter((task) =>
      ['queued', 'processing'].includes(task.status),
    )
    return {
      total: list.length,
      analyzed: analyzed.length,
      notAnalyzed: list.length - analyzed.length,
      high,
      medium,
      low,
      activeTasks,
    }
  }, [documents, tasks])

  const cards = [
    {
      label: 'Contrats déposés',
      value: stats.total,
      icon: FileText,
      color: 'text-primary',
      bg: 'bg-primary-soft',
      detail: 'Portefeuille complet',
      to: '/documents',
    },
    {
      label: 'Contrats analysés',
      value: stats.analyzed,
      icon: ClipboardCheck,
      color: 'text-success',
      bg: 'bg-success-soft',
      detail:
        stats.total > 0
          ? `${Math.round((stats.analyzed / stats.total) * 100)} % du portefeuille`
          : 'Aucun contrat déposé',
      to: '/history',
    },
    {
      label: 'Risque élevé',
      value: stats.high,
      icon: AlertTriangle,
      color: 'text-danger',
      bg: 'bg-danger-soft',
      detail: stats.high ? 'À examiner en priorité' : 'Aucune alerte critique',
      to: '/history',
    },
    {
      label: 'Tâches actives',
      value: stats.activeTasks.length,
      icon: ListChecks,
      color: 'text-brand',
      bg: 'bg-brand-soft',
      detail: stats.activeTasks.length ? 'Traitements en arrière-plan' : 'Tout est à jour',
      to: '/tasks',
    },
  ]

  const analyzedTotal = Math.max(stats.analyzed, 1)

  return (
    <div className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((stat) => (
          <Link
            key={stat.label}
            to={stat.to}
            className="group block"
          >
            <Card className="h-full transition-all duration-300 group-hover:-translate-y-0.5 group-hover:border-brand/20 group-hover:shadow-md">
              <div className="flex items-start justify-between gap-4">
                <div
                  className={`flex size-11 shrink-0 items-center justify-center rounded-xl ${stat.bg} ${stat.color}`}
                >
                  <stat.icon className="size-5" />
                </div>
                <ArrowRight className="size-4 text-slate-300 transition group-hover:translate-x-0.5 group-hover:text-brand" />
              </div>
              <div className="mt-4">
                <p className="text-3xl font-bold tracking-tight text-slate-900">
                  {documentsLoading || tasksLoading ? '—' : stat.value}
                </p>
                <p className="mt-1 text-xs font-semibold text-slate-700">
                  {stat.label}
                </p>
                <p className="mt-1 text-[11px] text-muted">{stat.detail}</p>
              </div>
            </Card>
          </Link>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.6fr)_minmax(300px,0.8fr)]">
        <Card padding="lg" className="overflow-hidden">
          <CardHeader
            title="Répartition des risques"
            subtitle="Niveau de risque des contrats dont l’analyse est disponible"
            action={
              <Link
                to="/history"
                className="inline-flex items-center gap-1 text-xs font-semibold text-brand hover:text-brand-dark"
              >
                Voir les analyses
                <ArrowRight className="size-3.5" />
              </Link>
            }
          />

          {documentsLoading ? (
            <LoadingSpinner label="Calcul des niveaux de risque…" />
          ) : stats.analyzed > 0 ? (
            <div className="space-y-6">
              <div className="rounded-xl border border-border bg-slate-50/70 p-4">
                <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
                  <div>
                    <p className="text-2xl font-bold text-slate-900">
                      {stats.analyzed}
                      <span className="ml-1 text-sm font-medium text-muted">
                        sur {stats.total}
                      </span>
                    </p>
                    <p className="text-xs text-muted">
                      contrats disposent d’un score
                    </p>
                  </div>
                  <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-brand ring-1 ring-border">
                    {Math.round((stats.analyzed / Math.max(stats.total, 1)) * 100)} %
                    analysés
                  </span>
                </div>

                <div
                  className="flex h-3 overflow-hidden rounded-full bg-slate-200"
                  aria-label="Répartition des niveaux de risque"
                >
                  {RISK_BANDS.map((band) => {
                    const value = stats[band.key]
                    return value > 0 ? (
                      <div
                        key={band.key}
                        className={cn('h-full transition-all', band.bar)}
                        style={{ width: `${(value / analyzedTotal) * 100}%` }}
                        title={`${band.label} : ${value}`}
                      />
                    ) : null
                  })}
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                {RISK_BANDS.map((band) => {
                  const value = stats[band.key]
                  const percentage = Math.round((value / analyzedTotal) * 100)
                  return (
                    <div
                      key={band.key}
                      className="rounded-xl border border-border bg-white p-4"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span
                          className={cn(
                            'flex size-8 items-center justify-center rounded-lg',
                            band.soft,
                            band.text,
                          )}
                        >
                          {band.key === 'low' ? (
                            <ShieldCheck className="size-4" />
                          ) : band.key === 'medium' ? (
                            <AlertTriangle className="size-4" />
                          ) : (
                            <AlertTriangle className="size-4" />
                          )}
                        </span>
                        <span className={cn('text-xs font-bold', band.text)}>
                          {percentage} %
                        </span>
                      </div>
                      <p className="mt-3 text-xl font-bold text-slate-900">{value}</p>
                      <p className="text-xs font-semibold text-slate-700">
                        {band.label}
                      </p>
                      <p className="mt-1 text-[10px] text-muted">{band.range}</p>
                    </div>
                  )
                })}
              </div>

              {stats.notAnalyzed > 0 ? (
                <div className="flex items-center justify-between gap-3 rounded-xl border border-dashed border-border bg-canvas/60 px-4 py-3">
                  <div className="flex items-center gap-2.5">
                    <span className="flex size-8 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
                      <FileText className="size-4" />
                    </span>
                    <div>
                      <p className="text-xs font-semibold text-slate-700">
                        {stats.notAnalyzed} contrat
                        {stats.notAnalyzed > 1 ? 's' : ''} sans analyse
                      </p>
                      <p className="text-[11px] text-muted">
                        Aucun niveau de risque n’est encore disponible.
                      </p>
                    </div>
                  </div>
                  <Link
                    to="/documents"
                    className="shrink-0 text-xs font-semibold text-brand hover:text-brand-dark"
                  >
                    Consulter
                  </Link>
                </div>
              ) : null}
            </div>
          ) : (
            <div className="flex min-h-64 flex-col items-center justify-center rounded-xl border border-dashed border-border bg-canvas/50 px-6 text-center">
              <span className="flex size-12 items-center justify-center rounded-2xl bg-brand-soft text-brand">
                <ShieldCheck className="size-6" />
              </span>
              <p className="mt-4 text-sm font-semibold text-slate-800">
                Aucun score de risque disponible
              </p>
              <p className="mt-1 max-w-sm text-xs leading-5 text-muted">
                Lancez l’analyse d’un contrat pour obtenir une vue consolidée de
                votre portefeuille.
              </p>
              <Link
                to="/documents"
                className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-brand hover:text-brand-dark"
              >
                Choisir un contrat
                <ArrowRight className="size-3.5" />
              </Link>
            </div>
          )}
        </Card>

        <Card padding="lg">
          <CardHeader
            title="Tâches en cours"
            subtitle="Traitements exécutés en arrière-plan"
            action={
              <Link
                to="/tasks"
                className="text-xs font-semibold text-brand hover:text-brand-dark"
              >
                Tout voir
              </Link>
            }
          />
          {tasksLoading ? (
            <LoadingSpinner label="Chargement des tâches…" />
          ) : stats.activeTasks.length ? (
            <div className="space-y-3">
              {stats.activeTasks.slice(0, 4).map((task) => (
                <Link
                  key={task.id}
                  to={task.destination}
                  className="group block rounded-xl border border-border p-3 transition hover:border-brand/25 hover:bg-brand-soft/30"
                >
                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-brand-soft text-brand">
                      <ListChecks className="size-4" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <p className="truncate text-xs font-semibold text-slate-800 group-hover:text-brand">
                          {task.title}
                        </p>
                        <span className="shrink-0 text-[10px] font-bold text-brand">
                          {task.progress} %
                        </span>
                      </div>
                      <p className="mt-1 truncate text-[11px] text-muted">
                        {task.message}
                      </p>
                      <div className="mt-2 h-1 overflow-hidden rounded-full bg-slate-100">
                        <div
                          className="h-full rounded-full bg-brand transition-all"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="flex min-h-56 flex-col items-center justify-center text-center">
              <span className="flex size-11 items-center justify-center rounded-2xl bg-success-soft text-success">
                <CheckCircle2 className="size-5" />
              </span>
              <p className="mt-3 text-sm font-semibold text-slate-800">
                Tout est à jour
              </p>
              <p className="mt-1 text-xs text-muted">
                Aucune tâche n’est en attente ou en cours.
              </p>
            </div>
          )}
        </Card>
      </section>

      <section>
        <Card padding="lg">
          <CardHeader
            title="Activité récente"
            subtitle="Vos derniers contrats et leur état de préparation"
            action={
              <Link
                to="/documents"
                className="inline-flex items-center gap-1 text-xs font-semibold text-brand hover:text-brand-dark"
              >
                Tous les contrats
                <ArrowRight className="size-3.5" />
              </Link>
            }
          />
          {isLoading ? (
            <LoadingSpinner label="Chargement de l’activité…" />
          ) : activity && activity.length ? (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {activity.map((item) => (
                <DocumentCard key={item.id} item={item} />
              ))}
            </div>
          ) : (
            <div className="py-10 text-center">
              <p className="text-sm font-semibold text-slate-800">
                Aucun contrat pour le moment
              </p>
              <p className="mt-1 text-xs text-muted">
                Déposez votre premier contrat pour démarrer.
              </p>
            </div>
          )}
        </Card>
      </section>
    </div>
  )
}
