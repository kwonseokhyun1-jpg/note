import type { CommanderPairMatch, CommanderRecord } from '../types/commander'
import type { ColorFilter, ManaColor } from '../types/mtg'
import { MANA_COLORS } from '../types/mtg'
import { scoreCommander } from './commander-match'
import { resolveCommanderIntent, themeHasIntent } from './commander-intent'
import { fitsColorIdentity } from './color-filter'
import { type CommanderSort } from './edhrec'
import { getSlangPartnerPairs, pairMatchesSlang } from './mtg-slang'

export type PartnerKind =
  | 'partner'
  | 'partner-with'
  | 'partner-variant'
  | 'friends-forever'
  | 'background'
  | 'doctors-companion'

export type PartnerInfo = {
  kinds: PartnerKind[]
  /** Slug for Partner—Variant lines (e.g. friends-forever, character-select). */
  variant?: string
  partnerWithName?: string
}

function slugifyPartnerVariant(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

function getPartnerVariant(text: string): string | undefined {
  // Use \u escapes — literal em/en dashes can be stripped by minifiers.
  const match = text.match(/Partner\s*[\u2014\u2013-]\s*([^(]+?)\s*\(/i)
  return match ? slugifyPartnerVariant(match[1]) : undefined
}

function hasGenericPartner(text: string): boolean {
  return /\bPartner\s*\(\s*You can have two commanders if both have partner/i.test(text)
}

function hasPartnerVariantLine(text: string): boolean {
  return /Partner\s*[\u2014\u2013-]/i.test(text)
}

export function getPartnerInfo(commander: CommanderRecord): PartnerInfo {
  const text = commander.oracle_text
  const keywords = commander.keywords.map((k) => k.toLowerCase())
  const kinds: PartnerKind[] = []
  let partnerWithName: string | undefined
  let variant: string | undefined

  if (/partner with/i.test(text)) {
    kinds.push('partner-with')
    const pw = text.match(/Partner with ([^(.\n]+)/i)
    if (pw) partnerWithName = pw[1].trim().replace(/\.$/, '')
  } else {
    variant = getPartnerVariant(text)
    if (variant) {
      kinds.push('partner-variant')
      if (variant === 'friends-forever') kinds.push('friends-forever')
    } else if (hasPartnerVariantLine(text)) {
      kinds.push('partner-variant')
      variant = 'unknown'
    } else if (hasGenericPartner(text)) {
      kinds.push('partner')
    }
  }

  if (/choose a background/i.test(text)) kinds.push('background')
  if (/doctor's companion/i.test(text) || keywords.includes("doctor's companion")) {
    kinds.push('doctors-companion')
  }

  return { kinds: [...new Set(kinds)], variant, partnerWithName }
}

/** Canonical pairing bucket — commanders must share the same bucket to pair (except background / doctor rules). */
export function getPairGroup(commander: CommanderRecord): string | null {
  if (isBackgroundCommander(commander)) return 'background-enchantment'

  const text = commander.oracle_text
  const keywords = commander.keywords.map((k) => k.toLowerCase())

  if (/doctor's companion/i.test(text) || keywords.includes("doctor's companion")) {
    return 'doctors-companion'
  }

  const info = getPartnerInfo(commander)
  if (info.partnerWithName) return null
  if (info.variant) return `variant:${info.variant}`
  if (info.kinds.includes('partner')) return 'partner'
  if (info.kinds.includes('background')) return 'background'

  return null
}

export function isBackgroundCommander(c: CommanderRecord): boolean {
  return c.type_line.toLowerCase().includes('background')
}

export function isTimeLordDoctor(c: CommanderRecord): boolean {
  return /time lord doctor/i.test(`${c.type_line} ${c.oracle_text}`)
}

function namesMatch(a: string, b: string): boolean {
  return a.toLowerCase().trim() === b.toLowerCase().trim()
}

function combinedIdentity(a: CommanderRecord, b: CommanderRecord): ManaColor[] {
  const set = new Set<ManaColor>([...a.color_identity, ...b.color_identity])
  return MANA_COLORS.filter((c) => set.has(c))
}

function variantLabel(variant: string): string {
  return variant
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function pairTypeLabel(primary: PartnerInfo, partner: PartnerInfo, a: CommanderRecord, b: CommanderRecord): string {
  if (primary.partnerWithName || partner.partnerWithName) return 'Partner with'
  if (primary.kinds.includes('background') && isBackgroundCommander(b)) return 'Background'
  if (partner.kinds.includes('background') && isBackgroundCommander(a)) return 'Background'
  const sharedVariant = primary.variant && primary.variant === partner.variant ? primary.variant : undefined
  if (sharedVariant === 'friends-forever') return 'Friends forever'
  if (sharedVariant) return variantLabel(sharedVariant)
  if (
    (primary.kinds.includes('doctors-companion') && isTimeLordDoctor(b)) ||
    (partner.kinds.includes('doctors-companion') && isTimeLordDoctor(a))
  ) {
    return "Doctor's companion"
  }
  return 'Partner'
}

export function canCommandersPair(a: CommanderRecord, b: CommanderRecord): boolean {
  if (a.id === b.id) return false

  const infoA = getPartnerInfo(a)
  const infoB = getPartnerInfo(b)

  if (infoA.partnerWithName && namesMatch(infoA.partnerWithName, b.name)) return true
  if (infoB.partnerWithName && namesMatch(infoB.partnerWithName, a.name)) return true
  if (infoA.partnerWithName || infoB.partnerWithName) return false

  const groupA = getPairGroup(a)
  const groupB = getPairGroup(b)
  if (groupA && groupB && groupA === groupB) return true

  if (groupA === 'background' && groupB === 'background-enchantment') return true
  if (groupA === 'background-enchantment' && groupB === 'background') return true

  if (groupA === 'doctors-companion' && isTimeLordDoctor(b)) return true
  if (groupB === 'doctors-companion' && isTimeLordDoctor(a)) return true

  return false
}

function canBePrimaryCommander(c: CommanderRecord): boolean {
  const info = getPartnerInfo(c)
  return info.kinds.length > 0 && !isBackgroundCommander(c)
}

function buildNameIndex(commanders: CommanderRecord[]): Map<string, CommanderRecord> {
  const map = new Map<string, CommanderRecord>()
  for (const c of commanders) {
    map.set(c.name.toLowerCase(), c)
  }
  return map
}

function pushPair(
  pairs: CommanderPairMatch[],
  seen: Set<string>,
  primary: CommanderRecord,
  partner: CommanderRecord,
  score: number,
  matchedTags: string[],
  reasons: string[],
): void {
  if (!canCommandersPair(primary, partner)) return

  const key = [primary.id, partner.id].sort().join('|')
  if (seen.has(key)) return
  seen.add(key)

  pairs.push({
    primary,
    partner,
    score,
    matchPercent: 0,
    matchedTags,
    reasons,
    pairType: pairTypeLabel(getPartnerInfo(primary), getPartnerInfo(partner), primary, partner),
  })
}

export function matchCommanderPairs(
  commanders: CommanderRecord[],
  theme: string,
  colorFilter: ColorFilter,
  limit = 30,
  sort: CommanderSort = 'match',
  options?: { raw?: boolean },
): CommanderPairMatch[] {
  const intent = resolveCommanderIntent(theme, commanders, options?.raw ?? false)
  const hasTheme = themeHasIntent(intent)
  const byName = buildNameIndex(commanders)

  const primaries = commanders.filter((c) => canBePrimaryCommander(c))
  const backgrounds = commanders.filter(isBackgroundCommander)
  const pairable = [...primaries, ...backgrounds]

  const pairs: CommanderPairMatch[] = []
  const seen = new Set<string>()

  for (const [aName, bName] of getSlangPartnerPairs(theme)) {
    const a = byName.get(aName.toLowerCase())
    const b = byName.get(bName.toLowerCase())
    if (!a || !b) continue
    if (!fitsColorIdentity(combinedIdentity(a, b), colorFilter)) continue
    pushPair(pairs, seen, a, b, 200, ['combo'], ['Known partner pair from your search'])
  }

  for (const primary of primaries) {
    const info = getPartnerInfo(primary)
    const primaryScore = scoreCommander(primary, intent, theme)
    if (hasTheme && primaryScore.score <= 0) continue

    if (info.partnerWithName) {
      const named = byName.get(info.partnerWithName.toLowerCase())
      if (named && canCommandersPair(primary, named)) {
        if (fitsColorIdentity(combinedIdentity(primary, named), colorFilter)) {
          const partnerScore = scoreCommander(named, intent, theme)
          let combinedScore = hasTheme
            ? (primaryScore.score + partnerScore.score) / 2
            : ((primary.edhrec_rank ?? 999999) + (named.edhrec_rank ?? 999999)) / -200 + 50
          combinedScore += 40
          pushPair(
            pairs,
            seen,
            primary,
            named,
            combinedScore,
            [...new Set([...primaryScore.matchedTags, ...partnerScore.matchedTags])],
            [`Partner with ${named.name}`, ...primaryScore.reasons.slice(0, 1)],
          )
        }
      }
      continue
    }

    const candidates = pairable.filter(
      (p) =>
        p.id !== primary.id &&
        canCommandersPair(primary, p) &&
        fitsColorIdentity(combinedIdentity(primary, p), colorFilter),
    )

    for (const partner of candidates) {
      const partnerScore = scoreCommander(partner, intent, theme)
      let combinedScore = hasTheme
        ? (primaryScore.score + partnerScore.score) / 2
        : ((primary.edhrec_rank ?? 999999) + (partner.edhrec_rank ?? 999999)) / -200 + 50

      const pairSlang = pairMatchesSlang(primary.name, partner.name, theme)
      if (pairSlang) combinedScore += pairSlang.boost
      if (hasTheme && combinedScore <= 0) continue

      pushPair(
        pairs,
        seen,
        primary,
        partner,
        combinedScore,
        [...new Set([...primaryScore.matchedTags, ...partnerScore.matchedTags])],
        [
          ...(pairSlang ? [pairSlang.reason] : []),
          ...primaryScore.reasons.slice(0, 2),
          ...partnerScore.reasons.slice(0, 1),
        ],
      )
    }
  }

  const sorted = pairs
    .sort((a, b) => {
      if (sort === 'popularity') {
        const ar = (a.primary.edhrec_rank ?? 999999) + (a.partner.edhrec_rank ?? 999999)
        const br = (b.primary.edhrec_rank ?? 999999) + (b.partner.edhrec_rank ?? 999999)
        if (ar !== br) return ar - br
        return b.score - a.score
      }
      if (b.score !== a.score) return b.score - a.score
      const ar = (a.primary.edhrec_rank ?? 999999) + (a.partner.edhrec_rank ?? 999999)
      const br = (b.primary.edhrec_rank ?? 999999) + (b.partner.edhrec_rank ?? 999999)
      return ar - br
    })
    .slice(0, limit)

  const maxScore = Math.max(...sorted.map((p) => p.score), 1)

  return sorted.map((p) => ({
    ...p,
    matchPercent: hasTheme ? Math.round((p.score / maxScore) * 100) : 0,
  }))
}

export function canSearchPairs(commanders: CommanderRecord[]): boolean {
  return commanders.some((c) => getPartnerInfo(c).kinds.length > 0 || isBackgroundCommander(c))
}
