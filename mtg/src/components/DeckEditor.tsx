import { useEffect, useState } from 'react'
import type { DeckAnalysis } from '../types/mtg'
import type { CardRecord, UpgradeRecommendation } from '../types/card'
import { cardImage } from '../api/scryfall'
import { UpgradeSuggestions } from './UpgradeSuggestions'
import { PlaytestBoard, type PlaytestState } from './PlaytestBoard'
import { useCardDetail } from '../context/CardDetailContext'
import { deckStrengthsWeaknesses } from '../lib/advice'
import { cardToDetail } from '../lib/card-insight'
import {
  generateDeckReview,
  renderDeckReviewMarkdown,
} from '../lib/deck-review'
import { loadCardDatabase } from '../lib/card-db'
import { analyzeDecklist } from '../lib/decklist'
import { fetchCommanderEdhrecPage } from '../lib/edhrec-api'
import {
  suggestComboUpgrades,
  suggestLandUpgrades,
} from '../lib/edhrec-upgrades'
import { findGameChangersInDeck } from '../lib/game-changers'
import { ensureMinimumUpgrades, suggestUpgradesLocal } from '../lib/upgrade-match'

type SectionId = 'overview' | 'playtest' | 'upgrades' | 'beat'

type Props = {
  deckName: string
  onDeckNameChange: (name: string) => void
  initialText?: string
  onTextChange?: (text: string) => void
  onBack?: () => void
  saveStatus?: string
  showNameField?: boolean
}

export function DeckEditor({
  deckName,
  onDeckNameChange,
  initialText = '',
  onTextChange,
  onBack,
  saveStatus,
  showNameField = true,
}: Props) {
  const { openDetail } = useCardDetail()
  const [text, setText] = useState(initialText)
  const [analysis, setAnalysis] = useState<DeckAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [budget, setBudget] = useState(150)
  const [playtest, setPlaytest] = useState<PlaytestState | null>(null)
  const [activeSection, setActiveSection] = useState<SectionId>('overview')
  const [cardDbReady, setCardDbReady] = useState(false)
  const [cardDbCount, setCardDbCount] = useState(0)
  const [upgradeList, setUpgradeList] = useState<UpgradeRecommendation[]>([])
  const [upgradesLoading, setUpgradesLoading] = useState(false)
  const [upgradeSource, setUpgradeSource] = useState('')
  const [gameChangers, setGameChangers] = useState<CardRecord[]>([])
  const [deckReview, setDeckReview] = useState<{
    review: string
    source: 'ai' | 'local'
  } | null>(null)
  const [reviewLoading, setReviewLoading] = useState(false)

  useEffect(() => {
    setText(initialText)
    setAnalysis(null)
    setPlaytest(null)
    setActiveSection('overview')
  }, [initialText])

  useEffect(() => {
    loadCardDatabase()
      .then((db) => {
        setCardDbCount(db.count)
        setCardDbReady(true)
      })
      .catch(() => setCardDbReady(false))
  }, [])

  useEffect(() => {
    if (!analysis) {
      setGameChangers([])
      setDeckReview(null)
      return
    }

    let cancelled = false
    setReviewLoading(true)

    findGameChangersInDeck(analysis)
      .then(async (found) => {
        if (cancelled) return
        setGameChangers(found)
        const review = await generateDeckReview(analysis, found)
        if (!cancelled) {
          setDeckReview(review)
          setReviewLoading(false)
        }
      })
      .catch(() => {
        if (!cancelled) setReviewLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [analysis])

  const updateText = (value: string) => {
    setText(value)
    onTextChange?.(value)
  }

  const analyze = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeDecklist(text)
      setAnalysis(result)
      setActiveSection('overview')
      setPlaytest(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to parse decklist')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!analysis || !cardDbReady) {
      setUpgradeList([])
      setUpgradeSource('')
      return
    }

    let cancelled = false
    setUpgradesLoading(true)

    loadCardDatabase().then(async (db) => {
      const budgetPerCard = Math.max(5, budget / 15)
      const commanderName = analysis.commander?.name
      const local = suggestUpgradesLocal(analysis, db.cards, 3, budgetPerCard)

      let combined = [...local]
      let source = 'Local role gaps'

      if (commanderName) {
        const edhrec = await fetchCommanderEdhrecPage(commanderName)
        if (edhrec && !cancelled) {
          const combo = suggestComboUpgrades(analysis, edhrec, db.cards, budgetPerCard)
          const lands = suggestLandUpgrades(analysis, edhrec, db.cards, budgetPerCard)
          combined = [...combo, ...lands, ...local]
          source = `EDHREC data for ${commanderName} + local staples`
        }
      }

      combined = ensureMinimumUpgrades(
        combined,
        analysis,
        db.cards,
        Math.max(budgetPerCard, 12),
        3,
      )

      if (!cancelled) {
        setUpgradeList(combined.slice(0, 8))
        setUpgradeSource(source)
        setUpgradesLoading(false)
      }
    })

    return () => {
      cancelled = true
    }
  }, [analysis, budget, cardDbReady])

  const strengthWeakness = analysis
    ? deckStrengthsWeaknesses(analysis, gameChangers)
    : null

  return (
    <div className="space-y-6">
      {(onBack || saveStatus) && (
        <div className="flex flex-wrap items-center justify-between gap-3">
          {onBack ? (
            <button
              type="button"
              onClick={onBack}
              className="rounded-lg border border-[var(--color-mtg-border)] px-3 py-1.5 text-sm text-[var(--color-mtg-muted)] hover:border-[var(--color-mtg-gold)] hover:text-white"
            >
              ← All decks
            </button>
          ) : (
            <span />
          )}
          {saveStatus && (
            <p className="text-xs text-[var(--color-mtg-muted)]">{saveStatus}</p>
          )}
        </div>
      )}

      <section className="rounded-xl border border-[var(--color-mtg-border)] bg-[var(--color-mtg-panel)] p-5">
        {showNameField && (
          <div className="mb-4">
            <label className="text-sm text-[var(--color-mtg-muted)]">Deck name</label>
            <input
              type="text"
              value={deckName}
              onChange={(e) => onDeckNameChange(e.target.value)}
              placeholder="My Sliver deck"
              className="mt-1 w-full max-w-md rounded-lg border border-[var(--color-mtg-border)] bg-[var(--color-mtg-bg)] px-3 py-2 text-sm"
            />
          </div>
        )}

        <p className="text-sm text-[var(--color-mtg-muted)]">
          Paste your 99-card maindeck, then put your commander as the last line.
        </p>
        {cardDbReady && (
          <p className="text-xs text-[var(--color-mtg-muted)]">
            {cardDbCount.toLocaleString()} cards loaded
          </p>
        )}

        <textarea
          value={text}
          onChange={(e) => updateText(e.target.value)}
          rows={14}
          placeholder={'1 Sol Ring\n1 Command Tower\n1 Arcane Signet\n...\n1 Atraxa, Praetors\' Voice'}
          className="mt-4 w-full rounded-lg border border-[var(--color-mtg-border)] bg-[var(--color-mtg-bg)] px-3 py-2 font-mono text-xs"
        />

        <div className="mt-4">
          <button
            type="button"
            onClick={analyze}
            disabled={loading || !text.trim()}
            className="rounded-lg bg-[var(--color-mtg-gold)] px-5 py-2 text-sm font-semibold text-black disabled:opacity-50"
          >
            {loading ? 'Analyzing…' : 'Analyze Deck'}
          </button>
        </div>
        {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      </section>

      {analysis && (
        <>
          <div className="flex flex-wrap gap-2">
            {(
              [
                ['overview', 'Overview'],
                ['playtest', 'Playtest'],
                ['upgrades', 'Upgrades'],
                ['beat', 'Strengths and Weaknesses'],
              ] as const
            ).map(([id, label]) => (
              <button
                key={id}
                type="button"
                onClick={() => setActiveSection(id)}
                className={`rounded-lg px-3 py-1.5 text-sm ${
                  activeSection === id
                    ? 'bg-[var(--color-mtg-gold)] text-black'
                    : 'border border-[var(--color-mtg-border)] text-[var(--color-mtg-muted)]'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {activeSection === 'overview' && (
            <section className="rounded-xl border border-[var(--color-mtg-border)] bg-[var(--color-mtg-panel)] p-5 space-y-5">
              <div className="flex flex-wrap gap-6">
                {analysis.commander?.card && (
                  <img
                    src={cardImage(analysis.commander.card)}
                    alt={analysis.commander.name}
                    className="w-36 rounded-lg shadow-lg"
                  />
                )}
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="text-[var(--color-mtg-muted)]">Commander:</span>{' '}
                    {analysis.commander?.name ?? '—'}
                  </p>
                  <p>
                    <span className="text-[var(--color-mtg-muted)]">Cards:</span> {analysis.totalCards}
                  </p>
                  <p>
                    <span className="text-[var(--color-mtg-muted)]">Identity:</span>{' '}
                    {analysis.colorIdentity.join('') || 'Colorless'}
                  </p>
                  <p>
                    <span className="text-[var(--color-mtg-muted)]">Avg CMC:</span>{' '}
                    {analysis.avgCmc.toFixed(2)}
                  </p>
                  <p>
                    <span className="text-[var(--color-mtg-muted)]">Est. value:</span> $
                    {analysis.totalUsd.toFixed(2)}
                  </p>
                </div>
              </div>

              {gameChangers.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-[var(--color-mtg-gold)]">
                    Game Changers ({gameChangers.length})
                  </h3>
                  <p className="mt-1 text-xs text-[var(--color-mtg-muted)]">
                    Cards on Scryfall&apos;s Commander Game Changer list in this deck.
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {gameChangers.map((card) => (
                      <button
                        key={card.id}
                        type="button"
                        onClick={() => openDetail(cardToDetail(card))}
                        className="rounded-full border border-amber-600/50 bg-amber-950/30 px-2.5 py-1 text-xs text-amber-300 hover:border-amber-400"
                      >
                        {card.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="text-sm font-semibold text-[var(--color-mtg-gold)]">Deck review</h3>
                {reviewLoading ? (
                  <p className="mt-2 text-sm text-[var(--color-mtg-muted)] animate-pulse">
                    Analyzing your list…
                  </p>
                ) : deckReview ? (
                  <>
                    {deckReview.source === 'ai' && (
                      <p className="mt-1 text-[10px] uppercase tracking-wide text-[var(--color-mtg-muted)]">
                        Groq AI review
                      </p>
                    )}
                    <div
                      className="mt-2 text-sm leading-relaxed text-[var(--color-mtg-muted)]"
                      dangerouslySetInnerHTML={{
                        __html: renderDeckReviewMarkdown(deckReview.review),
                      }}
                    />
                  </>
                ) : null}
              </div>

              {analysis.issues.length > 0 && (
                <ul className="space-y-1 text-sm text-red-400">
                  {analysis.issues.map((i) => (
                    <li key={i}>• {i}</li>
                  ))}
                </ul>
              )}
              {analysis.warnings.length > 0 && (
                <ul className="space-y-1 text-sm text-amber-400">
                  {analysis.warnings.map((w) => (
                    <li key={w}>• {w}</li>
                  ))}
                </ul>
              )}
            </section>
          )}

          {activeSection === 'playtest' && (
            <section className="rounded-xl border border-[var(--color-mtg-border)] bg-[var(--color-mtg-panel)] p-5">
              <PlaytestBoard
                analysis={analysis}
                playtest={playtest}
                onPlaytestChange={setPlaytest}
              />
            </section>
          )}

          {activeSection === 'upgrades' && (
            <section className="space-y-4 rounded-xl border border-[var(--color-mtg-border)] bg-[var(--color-mtg-panel)] p-5">
              <div>
                <label className="text-sm text-[var(--color-mtg-muted)]">Budget per card (USD)</label>
                <input
                  type="number"
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                  className="mt-1 block w-32 rounded border border-[var(--color-mtg-border)] bg-[var(--color-mtg-bg)] px-3 py-2 text-sm"
                />
              </div>
              {upgradeSource && (
                <p className="text-xs text-[var(--color-mtg-muted)]">Sources: {upgradeSource}</p>
              )}
              <UpgradeSuggestions
                upgrades={upgradeList}
                loading={upgradesLoading || !cardDbReady}
              />
            </section>
          )}

          {activeSection === 'beat' && strengthWeakness && (
            <section className="rounded-xl border border-[var(--color-mtg-border)] bg-[var(--color-mtg-panel)] p-5 space-y-5">
              <div>
                <h3 className="font-semibold text-[var(--color-mtg-gold)]">Strengths</h3>
                <ul className="mt-2 list-disc pl-5 text-sm text-[var(--color-mtg-muted)]">
                  {strengthWeakness.strengths.map((s) => (
                    <li key={s}>{s}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-[var(--color-mtg-gold)]">Weaknesses</h3>
                <ul className="mt-2 list-disc pl-5 text-sm text-[var(--color-mtg-muted)]">
                  {strengthWeakness.weaknesses.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              </div>
              {gameChangers.length > 0 && (
                <div>
                  <h3 className="font-semibold text-[var(--color-mtg-gold)]">Game Changers</h3>
                  <p className="mt-1 text-sm text-[var(--color-mtg-muted)]">
                    This deck runs {gameChangers.length} card
                    {gameChangers.length === 1 ? '' : 's'} on Scryfall&apos;s Game Changer list:{' '}
                    {gameChangers.map((c) => c.name).join(', ')}.
                  </p>
                </div>
              )}
            </section>
          )}
        </>
      )}
    </div>
  )
}
