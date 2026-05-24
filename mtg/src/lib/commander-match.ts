import type { CommanderMatch, CommanderRecord } from '../types/commander'
import type { ColorFilter } from '../types/mtg'
import {
  archetypeById,
  describeCommanderIntent,
  parseCommanderIntent,
  resolveCommanderIntent,
  themeHasIntent,
} from './commander-intent'
import {
  containsWholeWord,
  hasCreatureType,
  isTribeLord,
  parseCreatureTypes,
  singularizeTribe,
} from './commander-tribes'
import { fitsColorIdentity } from './color-filter'
import { type CommanderSort, edhrecScoreBoost } from './edhrec'
import {
  cardHasKeyword,
  oracleReferencesKeyword,
  type KeywordDef,
} from './mtg-keywords'
import { detectSlang, describeSlangInPrompt } from './mtg-slang'
import {
  oracleMatchesGroupHug,
  oracleMatchesReanimator,
  oracleMatchesStax,
  oracleMatchesTheft,
  oracleMatchesWheel,
} from './archetype-patterns'

function oracleForMatching(oracle: string): string {
  return oracle.replace(/\([^)]*\)/g, ' ')
}

export const MIN_COMMANDER_MATCH_PERCENT = 35

const ORACLE_ONLY_ARCHETYPES = new Set(['graveyard', 'mill', 'theft', 'group-hug', 'wheel', 'stax'])

type Criterion = {
  id: string
  label: string
  weight: number
  test: (commander: CommanderRecord) => { hit: boolean; reason?: string }
}

function oracleMatchesSignals(oracle: string, signals: RegExp[]): boolean {
  const cleaned = oracleForMatching(oracle)
  const flat = cleaned.replace(/\n/g, ' ')
  return signals.some((re) => re.test(flat) || re.test(cleaned))
}

function archetypeOracleHit(
  archId: string,
  oracle: string,
  arch?: ReturnType<typeof archetypeById>,
): boolean {
  if (archId === 'graveyard') return oracleMatchesReanimator(oracle)
  if (archId === 'theft') return oracleMatchesTheft(oracle)
  if (archId === 'group-hug') return oracleMatchesGroupHug(oracle)
  if (archId === 'wheel') return oracleMatchesWheel(oracle)
  if (archId === 'stax') return oracleMatchesStax(oracle)
  if (!arch) return false
  const cleaned = oracleForMatching(oracle)
  const flat = cleaned.replace(/\n/g, ' ')
  if (arch.excludeSignals?.some((re) => re.test(flat) || re.test(cleaned))) return false
  return oracleMatchesSignals(oracle, arch.signals)
}

function commanderTypes(commander: CommanderRecord): string[] {
  return commander.creature_types?.length
    ? commander.creature_types
    : parseCreatureTypes(commander.type_line)
}

function buildCriteria(
  intent: ReturnType<typeof parseCommanderIntent>,
  rawTheme: string,
): Criterion[] {
  const criteria: Criterion[] = []
  const seen = new Set<string>()
  const tribalIntent = [...new Set(intent.tribalTypes.map(singularizeTribe))]
  const slangEntries = detectSlang(rawTheme)
  const themeArchetypes = intent.archetypes.filter((id) => id !== 'tribal')

  for (const tribe of tribalIntent) {
    const id = `tribe:${tribe}`
    seen.add(id)
    const label = `${tribe.charAt(0).toUpperCase()}${tribe.slice(1)} tribal`
    criteria.push({
      id,
      label,
      weight: 50,
      test: (commander) => {
        const types = commanderTypes(commander)
        if (hasCreatureType(types, tribe)) {
          return { hit: true, reason: `${label} commander` }
        }
        if (isTribeLord(commander.oracle_text, commander.type_line, tribe)) {
          return { hit: true, reason: `${label} payoff in text` }
        }
        return { hit: false }
      },
    })
  }

  for (const archId of themeArchetypes) {
    if (seen.has(archId)) continue
    seen.add(archId)
    const arch = archetypeById(archId)
    criteria.push({
      id: archId,
      label: arch?.label ?? archId,
      weight: archId === 'graveyard' ? 50 : 42,
      test: (commander) => {
        const oracleHit = archetypeOracleHit(archId, commander.oracle_text, arch)
        if (ORACLE_ONLY_ARCHETYPES.has(archId)) {
          if (oracleHit) {
            return { hit: true, reason: `${arch?.label ?? archId} synergy in text` }
          }
          return { hit: false }
        }
        if (commander.tags.includes(archId)) {
          return { hit: true, reason: `Fits ${arch?.label.toLowerCase() ?? archId}` }
        }
        if (oracleHit) {
          return { hit: true, reason: `${arch?.label ?? archId} synergy in text` }
        }
        return { hit: false }
      },
    })
  }

  for (const kw of intent.keywords) {
    const id = `kw:${kw.id}`
    if (seen.has(id)) continue
    seen.add(id)
    criteria.push({
      id,
      label: kw.name,
      weight: 35,
      test: (commander) => testKeyword(commander, kw),
    })
  }

  for (const { entry } of slangEntries) {
    const id = `slang:${entry.id}`
    if (seen.has(id)) continue
    seen.add(id)
    const shortLabel = entry.label.split(' — ')[0] ?? entry.label
    criteria.push({
      id,
      label: shortLabel,
      weight: 45,
      test: (commander) => {
        const oracle = oracleForMatching(commander.oracle_text)
        const flatOracle = oracle.replace(/\n/g, ' ')
        const hay = `${commander.name} ${commander.type_line} ${flatOracle}`
        const nameHit = entry.commanders?.some(
          (n) => n.toLowerCase() === commander.name.toLowerCase(),
        )
        if (nameHit) return { hit: true, reason: shortLabel }
        if (entry.id === 'theft' && oracleMatchesTheft(commander.oracle_text)) {
          return { hit: true, reason: `${shortLabel} in text` }
        }
        if (entry.id === 'group-hug' && oracleMatchesGroupHug(commander.oracle_text)) {
          return { hit: true, reason: `${shortLabel} in text` }
        }
        if (entry.id === 'wheel' && oracleMatchesWheel(commander.oracle_text)) {
          return { hit: true, reason: `${shortLabel} in text` }
        }
        if (entry.id === 'reanimator' && oracleMatchesReanimator(commander.oracle_text)) {
          return { hit: true, reason: `${shortLabel} in text` }
        }
        if (entry.id === 'stax' && oracleMatchesStax(commander.oracle_text)) {
          return { hit: true, reason: `${shortLabel} in text` }
        }
        if (entry.commanderOracle?.some((re) => re.test(hay) || re.test(oracle))) {
          return { hit: true, reason: `${shortLabel} in text` }
        }
        return { hit: false }
      },
    })
  }

  return criteria
}

function testKeyword(
  commander: CommanderRecord,
  kw: KeywordDef,
): { hit: boolean; reason?: string } {
  if (cardHasKeyword(commander.keywords, kw)) {
    return { hit: true, reason: `Has ${kw.name}` }
  }
  if (oracleReferencesKeyword(oracleForMatching(commander.oracle_text), kw)) {
    return { hit: true, reason: `${kw.name} in text` }
  }
  return { hit: false }
}

function scoreNameQuery(name: string, query: string): number {
  const n = name.toLowerCase()
  const q = query.toLowerCase().trim()
  if (!q) return 0
  if (n === q) return 100
  if (containsWholeWord(n, q)) return 100
  const qTokens = q.split(/\s+/).filter((t) => t.length > 2)
  if (qTokens.length === 0) return 0
  const matched = qTokens.filter((t) => containsWholeWord(n, t)).length
  if (matched === 0) return 0
  return Math.round((matched / qTokens.length) * 100)
}

export function scoreCommander(
  commander: CommanderRecord,
  intent: ReturnType<typeof parseCommanderIntent>,
  rawTheme = '',
): { score: number; matchPercent: number; matchedTags: string[]; reasons: string[] } {
  const criteria = buildCriteria(intent, rawTheme)
  const tribalIntent = [...new Set(intent.tribalTypes.map(singularizeTribe))]
  const matchedTags: string[] = []
  const reasons: string[] = []

  if (criteria.length === 0) {
    const namePct = scoreNameQuery(commander.name, intent.normalizedTheme)
    return {
      score: namePct + edhrecScoreBoost(commander.edhrec_rank, 4),
      matchPercent: namePct,
      matchedTags: namePct > 0 ? ['name'] : [],
      reasons: namePct > 0 ? ['Name matches your search'] : [],
    }
  }

  let earned = 0
  let possible = 0
  let tribalHit = false
  let textMatchBonus = 0
  let namedSlangBonus = 0

  for (const crit of criteria) {
    possible += crit.weight
    const result = crit.test(commander)
    if (result.hit) {
      earned += crit.weight
      matchedTags.push(crit.id)
      if (result.reason) {
        reasons.push(result.reason)
        if (result.reason.endsWith(' in text')) textMatchBonus += 3
        else if (crit.id.startsWith('slang:')) namedSlangBonus += 12
      }
      if (crit.id.startsWith('tribe:')) tribalHit = true
    }
  }

  if (tribalIntent.length > 0 && !tribalHit) {
    earned = Math.min(earned, Math.floor(possible * 0.12))
  }

  const matchPercent = possible > 0 ? Math.round((earned / possible) * 100) : 0
  const score =
    matchPercent * 10 +
    matchedTags.length * 5 +
    textMatchBonus +
    namedSlangBonus +
    edhrecScoreBoost(commander.edhrec_rank, 4)

  return {
    score,
    matchPercent,
    matchedTags,
    reasons: [...new Set(reasons)].slice(0, 5),
  }
}

function sortCommanderMatches(
  scored: Array<{
    commander: CommanderRecord
    score: number
    matchPercent: number
    matchedTags: string[]
    reasons: string[]
  }>,
  sort: CommanderSort,
): typeof scored {
  return [...scored].sort((a, b) => {
    if (sort === 'popularity') {
      const ra = a.commander.edhrec_rank ?? 999999
      const rb = b.commander.edhrec_rank ?? 999999
      if (ra !== rb) return ra - rb
      return b.matchPercent - a.matchPercent || b.score - a.score
    }
    if (b.matchPercent !== a.matchPercent) return b.matchPercent - a.matchPercent
    if (b.score !== a.score) return b.score - a.score
    return (a.commander.edhrec_rank ?? 999999) - (b.commander.edhrec_rank ?? 999999)
  })
}

export function matchCommanders(
  commanders: CommanderRecord[],
  theme: string,
  colorFilter: ColorFilter,
  limit = 60,
  sort: CommanderSort = 'match',
  options?: { raw?: boolean },
): CommanderMatch[] {
  const intent = resolveCommanderIntent(theme, commanders, options?.raw ?? false)
  const filtered = commanders.filter((c) =>
    fitsColorIdentity(c.color_identity, colorFilter),
  )

  const scored = filtered.map((commander) => {
    const result = scoreCommander(commander, intent, theme)
    return { commander, ...result }
  })

  const hasTheme = themeHasIntent(intent)

  return sortCommanderMatches(
    scored.filter((s) => (hasTheme ? s.matchPercent >= MIN_COMMANDER_MATCH_PERCENT : true)),
    sort,
  ).slice(0, limit)
}

export function suggestSimilarCommanders(
  commanders: CommanderRecord[],
  theme: string,
  colorFilter: ColorFilter,
  limit = 8,
  options?: { raw?: boolean },
): CommanderMatch[] {
  const intent = resolveCommanderIntent(theme, commanders, options?.raw ?? false)
  if (!themeHasIntent(intent)) return []

  const filtered = commanders.filter((c) =>
    fitsColorIdentity(c.color_identity, colorFilter),
  )

  return filtered
    .map((commander) => {
      const result = scoreCommander(commander, intent, theme)
      return { commander, ...result }
    })
    .filter(
      (s) =>
        s.matchPercent > 0 &&
        s.matchPercent < MIN_COMMANDER_MATCH_PERCENT,
    )
    .sort((a, b) => b.matchPercent - a.matchPercent || b.score - a.score)
    .slice(0, limit)
}

export function describeTheme(theme: string): string {
  const slang = describeSlangInPrompt(theme)
  const intent = describeCommanderIntent(parseCommanderIntent(theme))
  return [slang, intent].filter(Boolean).join(' · ')
}

export const MIN_COMMANDER_MATCH_SCORE = MIN_COMMANDER_MATCH_PERCENT
