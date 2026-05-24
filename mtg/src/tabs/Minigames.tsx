import { useState } from 'react'
import { ArtGuessGame } from './ArtGuessGame'
import { UnscrambleGame } from './UnscrambleGame'

type MinigameId = 'menu' | 'art-guess' | 'unscramble'

const GAMES = [
  {
    id: 'art-guess' as const,
    title: 'Art Guess',
    description: 'Name the card from a zoomed-in art crop.',
  },
  {
    id: 'unscramble' as const,
    title: 'Unscramble',
    description: 'Unscramble the letters of a card name.',
  },
]

export function Minigames() {
  const [active, setActive] = useState<MinigameId>('menu')

  if (active === 'art-guess') {
    return (
      <div>
        <button
          type="button"
          onClick={() => setActive('menu')}
          className="mb-4 text-sm text-[var(--color-mtg-muted)] transition hover:text-[var(--color-mtg-gold)]"
        >
          ← Back to minigames
        </button>
        <ArtGuessGame />
      </div>
    )
  }

  if (active === 'unscramble') {
    return (
      <div>
        <button
          type="button"
          onClick={() => setActive('menu')}
          className="mb-4 text-sm text-[var(--color-mtg-muted)] transition hover:text-[var(--color-mtg-gold)]"
        >
          ← Back to minigames
        </button>
        <UnscrambleGame />
      </div>
    )
  }

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-6">
      <div className="text-center">
        <h2 className="font-[family-name:var(--font-display)] text-2xl font-bold text-[var(--color-mtg-gold)]">
          Minigames
        </h2>
        <p className="mt-1 text-sm text-[var(--color-mtg-muted)]">
          Quick Commander card challenges. Easy mode uses EDHREC staples; hard mode uses the full database.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {GAMES.map((game) => (
          <button
            key={game.id}
            type="button"
            onClick={() => setActive(game.id)}
            className="rounded-xl border border-[var(--color-mtg-border)] bg-[var(--color-mtg-panel)] p-5 text-left transition hover:border-[var(--color-mtg-gold-dim)] hover:bg-[var(--color-mtg-panel)]/80"
          >
            <h3 className="font-[family-name:var(--font-display)] text-lg font-semibold text-white">
              {game.title}
            </h3>
            <p className="mt-2 text-sm text-[var(--color-mtg-muted)]">{game.description}</p>
          </button>
        ))}
      </div>
    </div>
  )
}
