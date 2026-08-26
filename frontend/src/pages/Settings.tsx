import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { LogOut, RotateCcw, Save } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/context/AuthContext'
import {
  fetchAgentPrompts,
  saveAgentPrompts,
  type AgentPromptKey,
  type AgentPrompts,
} from '@/services/settings'

const PROMPT_ORDER: AgentPromptKey[] = [
  'legal',
  'finance',
  'compliance',
  'synthesis',
]

export function SettingsPage() {
  const { user, logout } = useAuth()
  const queryClient = useQueryClient()
  const prompts = useQuery({
    queryKey: ['agent-prompts'],
    queryFn: fetchAgentPrompts,
  })
  const [drafts, setDrafts] = useState<Partial<Record<AgentPromptKey, string>>>(
    {},
  )
  const [notice, setNotice] = useState<string | null>(null)

  const save = useMutation({
    mutationFn: saveAgentPrompts,
    onSuccess: (data) => {
      queryClient.setQueryData(['agent-prompts'], data)
      setDrafts({})
      setNotice('Prompts enregistrés. Ils s’appliquent aux prochaines analyses.')
    },
    onError: (error) => {
      setNotice(
        error instanceof Error
          ? error.message
          : 'L’enregistrement a échoué.',
      )
    },
  })

  const valueOf = (key: AgentPromptKey, data: AgentPrompts) =>
    drafts[key] ?? data[key].value

  const dirty =
    prompts.data != null &&
    PROMPT_ORDER.some((key) => valueOf(key, prompts.data) !== prompts.data[key].value)

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Card padding="lg">
        <CardHeader title="Profil" subtitle="Informations de votre compte" />
        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Nom"
            defaultValue={user?.full_name ?? ''}
            key={user?.full_name}
            readOnly
          />
          <Input
            label="E-mail"
            defaultValue={user?.email ?? ''}
            key={user?.email}
            readOnly
          />
          <div className="sm:col-span-2">
            <Input
              label="Rôle"
              defaultValue={user?.role ?? ''}
              key={user?.role}
              readOnly
            />
          </div>
        </div>
      </Card>

      <Card padding="lg">
        <CardHeader
          title="Prompts des agents"
          subtitle="Ces consignes système s’appliquent à /legal, /finance, /compliance et à la synthèse. Un champ vide à l’enregistrement restaure le défaut."
        />
        {prompts.isLoading ? (
          <p className="text-sm text-muted">Chargement des prompts…</p>
        ) : prompts.isError ? (
          <p className="text-sm text-danger">
            Impossible de charger les prompts. Réessayez.
          </p>
        ) : prompts.data ? (
          <div className="space-y-6">
            {PROMPT_ORDER.map((key) => {
              const field = prompts.data[key]
              const value = valueOf(key, prompts.data)
              return (
                <label key={key} className="block">
                  <span className="mb-1.5 flex items-center justify-between gap-3 text-sm font-medium text-slate-700">
                    <span>{field.label}</span>
                    {field.customized ? (
                      <span className="text-xs font-normal text-brand">
                        Personnalisé
                      </span>
                    ) : (
                      <span className="text-xs font-normal text-muted">
                        Défaut
                      </span>
                    )}
                  </span>
                  <textarea
                    value={value}
                    onChange={(event) =>
                      setDrafts((current) => ({
                        ...current,
                        [key]: event.target.value,
                      }))
                    }
                    rows={10}
                    className="w-full rounded-lg border border-border bg-white px-3 py-2 font-mono text-xs leading-5 text-slate-800 outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                  />
                  <span className="mt-1.5 flex flex-wrap items-center justify-between gap-2 text-xs text-muted">
                    <span>
                      {field.uses_no_answer
                        ? 'Conservez {no_answer} pour le message « information indisponible ». Échappez les autres accolades avec {{ }}.'
                        : 'Prompt de synthèse : accolades libres (pas de {no_answer}).'}
                    </span>
                    <button
                      type="button"
                      className="inline-flex items-center gap-1 font-medium text-primary hover:underline"
                      onClick={() =>
                        setDrafts((current) => ({
                          ...current,
                          [key]: field.default,
                        }))
                      }
                    >
                      <RotateCcw className="size-3.5" />
                      Restaurer le défaut
                    </button>
                  </span>
                </label>
              )
            })}
            {notice ? (
              <p className="text-sm text-slate-600">{notice}</p>
            ) : null}
            <div className="flex flex-wrap gap-2">
              <Button
                disabled={save.isPending || !dirty}
                onClick={() => {
                  if (!prompts.data) return
                  setNotice(null)
                  save.mutate({
                    legal: valueOf('legal', prompts.data),
                    finance: valueOf('finance', prompts.data),
                    compliance: valueOf('compliance', prompts.data),
                    synthesis: valueOf('synthesis', prompts.data),
                  })
                }}
              >
                <Save className="size-4" />
                {save.isPending ? 'Enregistrement…' : 'Enregistrer'}
              </Button>
            </div>
          </div>
        ) : null}
      </Card>

      <Card padding="lg">
        <CardHeader title="Session" subtitle="Gérer votre connexion" />
        <Button
          variant="secondary"
          leftIcon={<LogOut className="size-4" />}
          onClick={logout}
        >
          Se déconnecter
        </Button>
      </Card>
    </div>
  )
}
