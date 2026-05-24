import { useEffect, useState, type CSSProperties } from 'react'

type Player = {
  id: string
  name: string
  life: number
  poison: number
}

const FULLSCREEN_COLORS = ['#f5c542', '#e8a0bf', '#e53935', '#3b82f6', '#22c55e']

type FullscreenSlot = {
  player: Player | undefined
  color: string
  rotated: boolean
  className: string
}

function getFullscreenLayout(players: Player[]): {
  gridClass: string
  gridStyle?: CSSProperties
  slots: FullscreenSlot[]
} {
  const color = (i: number) => FULLSCREEN_COLORS[i % FULLSCREEN_COLORS.length]

  if (players.length === 2) {
    return {
      gridClass: 'grid-cols-2 grid-rows-1',
      slots: [
        { player: players[0], color: color(0), rotated: false, className: 'col-start-1 row-start-1' },
        { player: players[1], color: color(1), rotated: true, className: 'col-start-2 row-start-1' },
      ],
    }
  }

  if (players.length === 3) {
    return {
      gridClass: 'grid-cols-3 grid-rows-1',
      slots: players.map((player, i) => ({
        player,
        color: color(i),
        rotated: i === 2,
        className: `col-start-${i + 1} row-start-1`,
      })),
    }
  }

  if (players.length === 4) {
    return {
      gridClass: 'grid-cols-2 grid-rows-2',
      slots: [
        { player: players[2], color: color(2), rotated: true, className: 'col-start-1 row-start-1' },
        { player: players[3], color: color(3), rotated: true, className: 'col-start-2 row-start-1' },
        { player: players[0], color: color(0), rotated: false, className: 'col-start-1 row-start-2' },
        { player: players[1], color: color(1), rotated: false, className: 'col-start-2 row-start-2' },
      ],
    }
  }

  if (players.length === 5) {
    return {
      gridClass: 'grid-cols-3 grid-rows-2',
      slots: [
        { player: players[2], color: color(2), rotated: true, className: 'col-start-1 row-start-1' },
        { player: players[3], color: color(3), rotated: true, className: 'col-start-2 row-start-1' },
        { player: players[4], color: color(4), rotated: true, className: 'col-start-3 row-start-1' },
        { player: players[0], color: color(0), rotated: false, className: 'col-start-1 row-start-2' },
        { player: players[1], color: color(1), rotated: false, className: 'col-start-3 row-start-2' },
      ],
    }
  }

  const topCount = Math.ceil(players.length / 2)
  const top = players.slice(topCount)
  const bottom = players.slice(0, topCount)
  const cols = Math.max(top.length, bottom.length)

  return {
    gridClass: 'grid-rows-2',
    gridStyle: { gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` },
    slots: [
      ...top.map((player, i) => ({
        player,
        color: color(topCount + i),
        rotated: true,
        className: `col-start-${i + 1} row-start-1`,
      })),
      ...bottom.map((player, i) => ({
        player,
        color: color(i),
        rotated: false,
        className: `col-start-${i + 1} row-start-2`,
      })),
    ],
  }
}

function uid() {
  return Math.random().toString(36).slice(2, 9)
}

function useLandscapeMobile(): boolean {
  const [landscapeMobile, setLandscapeMobile] = useState(false)

  useEffect(() => {
    const mq = window.matchMedia('(orientation: landscape) and (max-height: 500px)')
    const update = () => setLandscapeMobile(mq.matches)
    update()
    mq.addEventListener('change', update)
    return () => mq.removeEventListener('change', update)
  }, [])

  return landscapeMobile
}

function isPlayerDead(
  player: Player,
  players: Player[],
  cmdDamage: Record<string, Record<string, number>>,
  commanderDamageLimit: number,
): boolean {
  const lethalCmd = players.some((from) => {
    const dmg = cmdDamage[from.id]?.[player.id] ?? 0
    return from.id !== player.id && dmg >= commanderDamageLimit
  })
  return player.life <= 0 || player.poison >= 10 || lethalCmd
}

export function LifeCounter() {
  const [startingLife, setStartingLife] = useState(40)
  const [commanderDamageLimit, setCommanderDamageLimit] = useState(21)
  const [players, setPlayers] = useState<Player[]>([
    { id: uid(), name: 'Player 1', life: 40, poison: 0 },
    { id: uid(), name: 'Player 2', life: 40, poison: 0 },
    { id: uid(), name: 'Player 3', life: 40, poison: 0 },
    { id: uid(), name: 'Player 4', life: 40, poison: 0 },
  ])
  const [cmdDamage, setCmdDamage] = useState<Record<string, Record<string, number>>>({})
  const [advancedOpen, setAdvancedOpen] = useState<Record<string, boolean>>({})
  const [fullscreenOpen, setFullscreenOpen] = useState(false)
  const landscapeMobile = useLandscapeMobile()

  useEffect(() => {
    if (!fullscreenOpen) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setFullscreenOpen(false)
    }
    window.addEventListener('keydown', onKey)
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', onKey)
      document.body.style.overflow = prevOverflow
    }
  }, [fullscreenOpen])

  useEffect(() => {
    const anyOpen = Object.values(advancedOpen).some(Boolean)
    if (!anyOpen) return

    const onPointerDown = (e: PointerEvent) => {
      const target = e.target
      if (target instanceof Element && target.closest('[data-life-advanced]')) return
      setAdvancedOpen({})
    }

    document.addEventListener('pointerdown', onPointerDown)
    return () => document.removeEventListener('pointerdown', onPointerDown)
  }, [advancedOpen])

  const toggleAdvanced = (id: string) => {
    setAdvancedOpen((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const addPlayer = () => {
    const n = players.length + 1
    setPlayers([
      ...players,
      { id: uid(), name: `Player ${n}`, life: startingLife, poison: 0 },
    ])
  }

  const removePlayer = (id: string) => {
    if (players.length <= 2) return
    setPlayers(players.filter((p) => p.id !== id))
    setCmdDamage((prev) => {
      const next = { ...prev }
      delete next[id]
      for (const from of Object.keys(next)) {
        delete next[from][id]
      }
      return next
    })
  }

  const adjustLife = (id: string, delta: number) => {
    setPlayers(
      players.map((p) =>
        p.id === id ? { ...p, life: Math.max(0, p.life + delta) } : p,
      ),
    )
  }

  const adjustPoison = (id: string, delta: number) => {
    setPlayers(
      players.map((p) =>
        p.id === id ? { ...p, poison: Math.max(0, Math.min(10, p.poison + delta)) } : p,
      ),
    )
  }

  const adjustCmdDamage = (fromId: string, toId: string, delta: number) => {
    if (fromId === toId) return
    setCmdDamage((prev) => {
      const row = { ...(prev[fromId] ?? {}) }
      const current = row[toId] ?? 0
      row[toId] = Math.max(0, current + delta)
      return { ...prev, [fromId]: row }
    })
    if (delta > 0) {
      setPlayers(
        players.map((p) =>
          p.id === toId ? { ...p, life: Math.max(0, p.life - delta) } : p,
        ),
      )
    } else if (delta < 0) {
      setPlayers(
        players.map((p) =>
          p.id === toId ? { ...p, life: p.life - delta } : p,
        ),
      )
    }
  }

  const resetAll = () => {
    setPlayers(
      players.map((p) => ({
        ...p,
        life: startingLife,
        poison: 0,
      })),
    )
    setCmdDamage({})
  }

  const applyStartingLife = () => {
    setPlayers(players.map((p) => ({ ...p, life: startingLife, poison: 0 })))
    setCmdDamage({})
  }

  const renderAdvanced = (player: Player, compact = false) => (
    <>
      <div className={`flex items-center justify-between ${compact ? 'text-xs' : 'text-xs md:text-sm'}`}>
        <span className={compact ? 'text-black/70' : 'text-[var(--color-mtg-muted)]'}>Poison</span>
        <div className="flex items-center gap-2">
          <button type="button" onClick={() => adjustPoison(player.id, -1)} className="px-2">−</button>
          <span className={player.poison >= 10 ? 'font-bold text-red-700' : ''}>
            {player.poison}
          </span>
          <button type="button" onClick={() => adjustPoison(player.id, 1)} className="px-2">+</button>
        </div>
      </div>

      <div className={compact ? 'mt-2' : 'mt-3 md:mt-4'}>
        <p className={compact ? 'text-[10px] text-black/70' : 'text-[10px] text-[var(--color-mtg-muted)] md:text-xs'}>
          Commander damage received
        </p>
        <ul className={`space-y-1 ${compact ? 'mt-1' : 'mt-1 md:mt-2'}`}>
          {players
            .filter((p) => p.id !== player.id)
            .map((from) => {
              const dmg = cmdDamage[from.id]?.[player.id] ?? 0
              const lethal = dmg >= commanderDamageLimit
              return (
                <li
                  key={from.id}
                  className={`flex items-center justify-between ${compact ? 'text-[10px]' : 'text-[10px] md:text-xs'}`}
                >
                  <span className={`truncate pr-1 ${lethal ? 'font-bold text-red-700' : ''}`}>
                    from {from.name}
                  </span>
                  <div className="flex shrink-0 items-center gap-1">
                    <button
                      type="button"
                      onClick={() => adjustCmdDamage(from.id, player.id, -1)}
                      className={`rounded border px-1.5 ${compact ? 'border-black/30' : 'border-[var(--color-mtg-border)]'}`}
                    >
                      −
                    </button>
                    <span className={`w-6 text-center ${lethal ? 'font-bold text-red-700' : ''}`}>
                      {dmg}
                    </span>
                    <button
                      type="button"
                      onClick={() => adjustCmdDamage(from.id, player.id, 1)}
                      className={`rounded border px-1.5 ${compact ? 'border-black/30' : 'border-[var(--color-mtg-border)]'}`}
                    >
                      +
                    </button>
                  </div>
                </li>
              )
            })}
        </ul>
      </div>
    </>
  )

  const renderPlayerCard = (player: Player) => {
    const dead = isPlayerDead(player, players, cmdDamage, commanderDamageLimit)

    return (
      <div
        key={player.id}
        className={`rounded-xl border p-3 md:p-4 ${
          dead
            ? 'border-red-500/60 bg-red-950/20'
            : 'border-[var(--color-mtg-border)] bg-[var(--color-mtg-panel)]'
        }`}
      >
        <div className="flex items-center justify-between gap-2">
          <input
            type="text"
            value={player.name}
            onChange={(e) =>
              setPlayers(
                players.map((p) =>
                  p.id === player.id ? { ...p, name: e.target.value } : p,
                ),
              )
            }
            className="min-w-0 flex-1 bg-transparent text-sm font-semibold outline-none md:text-base"
          />
          {players.length > 2 && (
            <button
              type="button"
              onClick={() => removePlayer(player.id)}
              className="shrink-0 text-xs text-[var(--color-mtg-muted)] hover:text-red-400"
            >
              Remove
            </button>
          )}
        </div>

        <div className="mt-3 flex items-center justify-center gap-2 md:mt-4 md:gap-3">
          <button
            type="button"
            onClick={() => adjustLife(player.id, -1)}
            className="flex h-10 w-10 items-center justify-center rounded-full border border-[var(--color-mtg-border)] text-lg hover:bg-white/5 md:h-12 md:w-12 md:text-xl"
          >
            −
          </button>
          <span
            className={`min-w-[3rem] text-center text-3xl font-bold md:min-w-[4rem] md:text-4xl ${
              player.life <= 0 ? 'text-red-400' : 'text-white'
            }`}
          >
            {player.life}
          </span>
          <button
            type="button"
            onClick={() => adjustLife(player.id, 1)}
            className="flex h-10 w-10 items-center justify-center rounded-full border border-[var(--color-mtg-border)] text-lg hover:bg-white/5 md:h-12 md:w-12 md:text-xl"
          >
            +
          </button>
        </div>

        <div className="mt-2 flex justify-center gap-1.5 md:mt-3 md:gap-2">
          {[-5, -10, 5, 10].map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => adjustLife(player.id, d)}
              className="rounded border border-[var(--color-mtg-border)] px-1.5 py-0.5 text-[10px] md:px-2 md:text-xs"
            >
              {d > 0 ? `+${d}` : d}
            </button>
          ))}
        </div>

        <button
          type="button"
          data-life-advanced
          onClick={() => toggleAdvanced(player.id)}
          className="mt-3 w-full rounded border border-[var(--color-mtg-border)] px-2 py-1 text-xs text-[var(--color-mtg-muted)] hover:border-[var(--color-mtg-gold-dim)] hover:text-white md:mt-4"
        >
          Advanced {advancedOpen[player.id] ? '▾' : '▸'}
        </button>

        {advancedOpen[player.id] && (
          <div className="mt-3" data-life-advanced>
            {renderAdvanced(player)}
          </div>
        )}
      </div>
    )
  }

  const renderFullscreenQuadrant = (
    player: Player | undefined,
    color: string,
    rotated: boolean,
    compactLandscape: boolean,
  ) => {
    if (!player) {
      return (
        <div
          className="h-full min-h-0 bg-neutral-900"
          style={rotated ? { transform: 'rotate(180deg)' } : undefined}
        />
      )
    }

    const dead = isPlayerDead(player, players, cmdDamage, commanderDamageLimit)
    const advanced = advancedOpen[player.id]

    return (
      <div
        className={`@container [container-type:size] relative flex h-full min-h-0 w-full flex-col overflow-hidden ${
          dead ? 'opacity-80' : ''
        }`}
        style={{
          backgroundColor: color,
          transform: rotated ? 'rotate(180deg)' : undefined,
        }}
      >
        <div
          className={
            compactLandscape
              ? 'flex shrink-0 justify-center px-[4cqmax] pt-[5cqmax]'
              : 'flex shrink-0 justify-center px-[4cqmin] pt-[5cqmin]'
          }
        >
          <p
            className={`max-w-full truncate text-center font-bold text-black/80 ${
              compactLandscape
                ? 'text-[clamp(0.875rem,7cqmax,2.25rem)]'
                : 'text-[clamp(0.875rem,6cqmin,2.5rem)]'
            }`}
          >
            {player.name}
          </p>
        </div>

        <div
          className={
            compactLandscape
              ? 'flex min-h-0 flex-1 items-center justify-center px-[3cqmax]'
              : 'flex min-h-0 flex-1 items-center justify-center px-[3cqmin]'
          }
        >
          <div
            className={`flex w-full max-w-full items-center justify-center ${
              compactLandscape
                ? 'gap-[clamp(0.5rem,5cqmax,2rem)]'
                : 'gap-[clamp(0.5rem,5cqmin,2.5rem)]'
            }`}
          >
            <button
              type="button"
              onClick={() => adjustLife(player.id, -1)}
              className={`flex aspect-square shrink-0 items-center justify-center bg-black/15 font-light text-black transition hover:bg-black/25 ${
                compactLandscape
                  ? 'rounded-[1.5cqmax] h-[clamp(2.75rem,18cqmax,8rem)] w-[clamp(2.75rem,18cqmax,8rem)] text-[clamp(1.75rem,13cqmax,4.5rem)]'
                  : 'rounded-[1.5cqmin] h-[clamp(2.75rem,20cqmin,10rem)] w-[clamp(2.75rem,20cqmin,10rem)] text-[clamp(1.75rem,14cqmin,6rem)]'
              }`}
              aria-label={`Decrease ${player.name} life`}
            >
              −
            </button>
            <span
              className={`shrink text-center font-bold leading-none text-black ${
                compactLandscape
                  ? 'text-[clamp(3rem,28cqmax,11rem)]'
                  : 'text-[clamp(3rem,32cqmin,16rem)]'
              } ${player.life <= 0 ? 'text-red-900' : ''}`}
            >
              {player.life}
            </span>
            <button
              type="button"
              onClick={() => adjustLife(player.id, 1)}
              className={`flex aspect-square shrink-0 items-center justify-center bg-black/15 font-light text-black transition hover:bg-black/25 ${
                compactLandscape
                  ? 'rounded-[1.5cqmax] h-[clamp(2.75rem,18cqmax,8rem)] w-[clamp(2.75rem,18cqmax,8rem)] text-[clamp(1.75rem,13cqmax,4.5rem)]'
                  : 'rounded-[1.5cqmin] h-[clamp(2.75rem,20cqmin,10rem)] w-[clamp(2.75rem,20cqmin,10rem)] text-[clamp(1.75rem,14cqmin,6rem)]'
              }`}
              aria-label={`Increase ${player.name} life`}
            >
              +
            </button>
          </div>
        </div>

        <div
          className={
            compactLandscape
              ? 'flex shrink-0 flex-col items-center gap-[clamp(0.25rem,3.5cqmax,1rem)] px-[3cqmax] pb-[5cqmax]'
              : 'flex shrink-0 flex-col items-center gap-[clamp(0.25rem,2.5cqmin,1rem)] px-[3cqmin] pb-[5cqmin]'
          }
        >
          <div
            className={`flex flex-wrap justify-center ${
              compactLandscape
                ? 'gap-[clamp(0.25rem,3cqmax,0.75rem)]'
                : 'gap-[clamp(0.25rem,2cqmin,0.75rem)]'
            }`}
          >
            {[-5, -10, 5, 10].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => adjustLife(player.id, d)}
                className={`bg-black/15 font-semibold text-black hover:bg-black/25 ${
                  compactLandscape
                    ? 'rounded-[1cqmax] px-[clamp(0.375rem,3cqmax,1rem)] py-[clamp(0.125rem,1.5cqmax,0.5rem)] text-[clamp(0.625rem,4.5cqmax,1.25rem)]'
                    : 'rounded-[1cqmin] px-[clamp(0.375rem,3cqmin,1.25rem)] py-[clamp(0.125rem,1.5cqmin,0.625rem)] text-[clamp(0.625rem,4.5cqmin,1.5rem)]'
                }`}
              >
                {d > 0 ? `+${d}` : d}
              </button>
            ))}
          </div>

          <button
            type="button"
            data-life-advanced
            onClick={() => toggleAdvanced(player.id)}
            className={`bg-black/15 font-semibold text-black hover:bg-black/25 ${
              compactLandscape
                ? 'rounded-[1cqmax] px-[clamp(0.5rem,4cqmax,1.25rem)] py-[clamp(0.125rem,2cqmax,0.625rem)] text-[clamp(0.625rem,4.5cqmax,1.25rem)]'
                : 'rounded-[1cqmin] px-[clamp(0.5rem,4cqmin,1.5rem)] py-[clamp(0.125rem,2cqmin,0.75rem)] text-[clamp(0.625rem,4.5cqmin,1.25rem)]'
            }`}
          >
            Advanced {advanced ? '▾' : '▸'}
          </button>
        </div>

        {advanced && (
          <div
            className={
              compactLandscape
                ? 'absolute inset-[3cqmax] z-10 overflow-y-auto rounded-[2cqmax] bg-white/95 p-[3cqmax] text-black shadow-lg'
                : 'absolute inset-[3cqmin] z-10 overflow-y-auto rounded-[2cqmin] bg-white/95 p-[3cqmin] text-black shadow-lg'
            }
            data-life-advanced
          >
            {renderAdvanced(player, true)}
          </div>
        )}
      </div>
    )
  }

  const fullscreenLayout = getFullscreenLayout(players)

  return (
    <>
      <div className="space-y-4 md:space-y-6">
        <section className="rounded-xl border border-[var(--color-mtg-border)] bg-[var(--color-mtg-panel)] p-4 md:p-5">
          <h2 className="font-[family-name:var(--font-display)] text-lg text-[var(--color-mtg-gold)]">
            Life Counter
          </h2>
          <p className="mt-1 text-sm text-[var(--color-mtg-muted)]">
            Commander damage tracked per opponent. Damage to a player also reduces their life.
          </p>

          <div className="mt-4 flex flex-wrap gap-4 text-sm">
            <div>
              <label className="text-[var(--color-mtg-muted)]">Starting life</label>
              <input
                type="number"
                value={startingLife}
                onChange={(e) => setStartingLife(Number(e.target.value))}
                className="mt-1 block w-24 rounded border border-[var(--color-mtg-border)] bg-[var(--color-mtg-bg)] px-2 py-1"
              />
            </div>
            <div>
              <label className="text-[var(--color-mtg-muted)]">CMD damage to lose</label>
              <input
                type="number"
                value={commanderDamageLimit}
                onChange={(e) => setCommanderDamageLimit(Number(e.target.value))}
                className="mt-1 block w-24 rounded border border-[var(--color-mtg-border)] bg-[var(--color-mtg-bg)] px-2 py-1"
              />
            </div>
            <div className="flex flex-wrap items-end gap-2">
              <button
                type="button"
                onClick={applyStartingLife}
                className="rounded border border-[var(--color-mtg-border)] px-3 py-1 hover:border-[var(--color-mtg-gold)]"
              >
                Apply to all
              </button>
              <button
                type="button"
                onClick={resetAll}
                className="rounded border border-[var(--color-mtg-border)] px-3 py-1 hover:border-[var(--color-mtg-gold)]"
              >
                Reset game
              </button>
              <button
                type="button"
                onClick={() => setFullscreenOpen(true)}
                className="rounded border border-[var(--color-mtg-gold-dim)] px-3 py-1 text-[var(--color-mtg-gold)] hover:border-[var(--color-mtg-gold)] hover:bg-[var(--color-mtg-gold)] hover:text-black"
              >
                Enter full screen
              </button>
              <button
                type="button"
                onClick={addPlayer}
                className="rounded bg-[var(--color-mtg-gold)] px-3 py-1 text-black"
              >
                + Player
              </button>
            </div>
          </div>
        </section>

        <div className="grid grid-cols-2 gap-2 md:gap-4">
          {players.map((player) => renderPlayerCard(player))}
        </div>
      </div>

      {fullscreenOpen && (
        <div className="fixed inset-0 z-[60] overscroll-none bg-black pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)] pt-[env(safe-area-inset-top)] pb-[env(safe-area-inset-bottom)]">
          <div
            className={`grid h-[100dvh] max-h-[100dvh] w-full min-h-0 ${fullscreenLayout.gridClass}`}
            style={fullscreenLayout.gridStyle}
          >
            {fullscreenLayout.slots.map((slot) => (
              <div
                key={slot.player?.id ?? slot.className}
                className={`h-full min-h-0 min-w-0 ${slot.className}`}
              >
                {renderFullscreenQuadrant(slot.player, slot.color, slot.rotated, landscapeMobile)}
              </div>
            ))}
            {players.length === 5 && (
              <div
                className="pointer-events-none col-start-2 row-start-2 h-full min-h-0"
                aria-hidden
              />
            )}
          </div>

          <button
            type="button"
            onClick={() => setFullscreenOpen(false)}
            className="absolute left-1/2 top-1/2 z-20 flex h-10 w-10 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full border-2 border-black/30 bg-white/90 text-base shadow-lg transition hover:bg-white sm:h-12 sm:w-12 sm:text-lg [@media(max-height:500px)]:h-8 [@media(max-height:500px)]:w-8 [@media(max-height:500px)]:text-sm"
            title="Exit full screen (Esc)"
            aria-label="Exit full screen"
          >
            ✕
          </button>
        </div>
      )}
    </>
  )
}
