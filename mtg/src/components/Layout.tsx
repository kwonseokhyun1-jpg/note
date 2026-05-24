import { useEffect, useState, type ReactNode } from 'react'
import { Minigames } from '../tabs/Minigames'
import { LifeCounter } from '../tabs/LifeCounter'

export type TabId =
  | 'commander'
  | 'cards'
  | 'deck'
  | 'finance'
  | 'judge'

const TABS: { id: TabId; label: string }[] = [
  { id: 'commander', label: 'Find Commander' },
  { id: 'cards', label: 'Find Cards' },
  { id: 'deck', label: 'Decks' },
  { id: 'finance', label: 'Finance' },
  { id: 'judge', label: 'Assistant' },
]

type Props = {
  active: TabId
  onTabChange: (tab: TabId) => void
  children: ReactNode
}

export function Layout({ active, onTabChange, children }: Props) {
  const [playOpen, setPlayOpen] = useState(false)
  const [minigameOpen, setMinigameOpen] = useState(false)

  useEffect(() => {
    if (!playOpen && !minigameOpen) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setPlayOpen(false)
        setMinigameOpen(false)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [playOpen, minigameOpen])

  return (
    <>
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 pb-8 pt-6">
        <header className="mb-6 border-b border-[var(--color-mtg-border)] pb-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1
                className="font-[family-name:var(--font-display)] text-2xl font-bold tracking-wide text-[var(--color-mtg-gold)] sm:text-3xl"
              >
                Commander Helper
              </h1>
              <p className="mt-1 text-sm text-[var(--color-mtg-muted)]">
                Commander deck tools · Groq-powered AI
              </p>
            </div>
            <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
              <button
                type="button"
                onClick={() => setMinigameOpen(true)}
                className="rounded-lg border border-[var(--color-mtg-border)] px-2.5 py-1 text-xs font-medium text-[var(--color-mtg-muted)] transition hover:border-[var(--color-mtg-gold-dim)] hover:text-white sm:px-3 sm:py-1.5 sm:text-sm"
              >
                Minigames
              </button>
              <button
                type="button"
                onClick={() => setPlayOpen(true)}
                className="rounded-lg border border-[var(--color-mtg-gold-dim)] px-2.5 py-1 text-xs font-medium text-[var(--color-mtg-gold)] transition hover:border-[var(--color-mtg-gold)] hover:bg-[var(--color-mtg-gold)] hover:text-black sm:px-3 sm:py-1.5 sm:text-sm"
              >
                Play
              </button>
            </div>
          </div>
          <nav className="mt-4 flex flex-wrap gap-2">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => onTabChange(tab.id)}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                  active === tab.id
                    ? 'bg-[var(--color-mtg-gold)] text-black'
                    : 'border border-[var(--color-mtg-border)] text-[var(--color-mtg-muted)] hover:border-[var(--color-mtg-gold-dim)] hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </header>
        <main className="flex-1">{children}</main>
      </div>

      {playOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto overscroll-contain bg-[var(--color-mtg-bg)] pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)]">
          <div className="mx-auto max-w-7xl px-4 py-6">
            <div className="mb-4 flex justify-end">
              <button
                type="button"
                onClick={() => setPlayOpen(false)}
                className="rounded-lg border border-[var(--color-mtg-border)] px-3 py-1.5 text-sm text-[var(--color-mtg-muted)] transition hover:border-[var(--color-mtg-gold)] hover:text-white"
              >
                Close
              </button>
            </div>
            <LifeCounter />
          </div>
        </div>
      )}

      {minigameOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto overscroll-contain bg-[var(--color-mtg-bg)] pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)]">
          <div className="mx-auto max-w-7xl px-4 py-6">
            <div className="mb-4 flex justify-end">
              <button
                type="button"
                onClick={() => setMinigameOpen(false)}
                className="rounded-lg border border-[var(--color-mtg-border)] px-3 py-1.5 text-sm text-[var(--color-mtg-muted)] transition hover:border-[var(--color-mtg-gold)] hover:text-white"
              >
                Close
              </button>
            </div>
            <Minigames />
          </div>
        </div>
      )}
    </>
  )
}
