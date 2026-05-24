import { ARCHETYPES, archetypeById, resolveThemeArchetypes } from './archetypes'
import { detectTribesInText, parseCreatureTypes, singularizeTribe } from './commander-tribes'
import { normalizeWithTypos } from './fuzzy-text'
import { detectKeywordsInText } from './mtg-keywords'
import { getSlangArchetypeIds } from './mtg-slang'

/** Multi-word playstyle phrases → archetype ids */
const THEME_PHRASES: Array<{ pattern: RegExp; archetypes: string[] }> = [
  { pattern: /\blands?\s+matter\b/, archetypes: ['lands'] },
  { pattern: /\bgroup\s+hug\b/, archetypes: ['group-hug'] },
  { pattern: /\bwheels?\b|\bwheel effect\b|\bdraw punish(?:er)?\b/, archetypes: ['wheel'] },
  { pattern: /\bgo[\s-]?wide\b/, archetypes: ['tokens'] },
  { pattern: /\bstax\b|\btaxes\b|\bresource\s+denial\b/, archetypes: ['stax'] },
  { pattern: /\baristocrats?\b|\bsacrifice\s+(?:outlet|synerg)/, archetypes: ['aristocrats'] },
  { pattern: /\bspellslinger\b|\binstants?\s+(?:and|&)\s+sorcer/, archetypes: ['spellslinger'] },
  { pattern: /\b\+?1\/\+?1\s+counters?\b|\bproliferate\b/, archetypes: ['counters'] },
  { pattern: /\bvoltron\b|\bequipment\b|\bauras?\s+matter\b/, archetypes: ['voltron'] },
  { pattern: /\bblink\b|\bflicker\b|\betb\b|\benter(?:s)?\s+the\s+battlefield\b/, archetypes: ['blink'] },
  { pattern: /\breanimator?\b|\breanimate\b|\brecursion\b/, archetypes: ['graveyard'] },
  { pattern: /\bgraveyard\b|\bgy\b/, archetypes: ['graveyard'] },
  { pattern: /\baggro\b|\bbeatdown\b|\bcombat\b/, archetypes: ['combat'] },
  { pattern: /\bcontrol\b|\bcounterspells?\b|\bpermission\b/, archetypes: ['control'] },
  { pattern: /\bcombo\b|\binfinite\b/, archetypes: ['combo'] },
  { pattern: /\bartifacts?\b|\btreasure\b/, archetypes: ['artifacts', 'treasure'] },
  { pattern: /\benchantments?\b|\bconstellation\b|\bshrines?\b/, archetypes: ['enchantments'] },
  { pattern: /\benchantress\b|\benchantrix\b/, archetypes: ['enchantments'] },
  { pattern: /\btheft\b|\bsteal(?:s|ing)?\b|\bthieves?\b/, archetypes: ['theft'] },
  { pattern: /\bsuperfriends\b|\bplaneswalkers?\b/, archetypes: ['superfriends'] },
  { pattern: /\bburn\b|\bdirect damage\b/, archetypes: ['burn'] },
  { pattern: /\bmill(?:ing)?\b/, archetypes: ['mill'] },
  { pattern: /\blifegain\b|\bextort\b/, archetypes: ['lifegain'] },
  { pattern: /\blandfall\b/, archetypes: ['lands'] },
  { pattern: /\bpillowfort\b|\bpillow[\s-]?fort\b/, archetypes: ['stax'] },
  { pattern: /\bblue farm\b|\btymna[\s/]+kraum\b/, archetypes: ['spellslinger', 'control'] },
  { pattern: /\bcedh\b|\bcompetitive edh\b/, archetypes: ['combo', 'control'] },
  { pattern: /\bramp\b|\bmana\s+rocks?\b/, archetypes: ['treasure'] },
]

export type CommanderIntent = {
  normalizedTheme: string
  archetypes: string[]
  keywords: ReturnType<typeof detectKeywordsInText>
  tribalTypes: string[]
  phrases: string[]
}

export function parseCommanderIntent(theme: string, raw = false): CommanderIntent {
  const normalizedTheme = raw
    ? theme.toLowerCase().replace(/[^\w\s+'/-]/g, ' ').replace(/\s+/g, ' ').trim()
    : normalizeWithTypos(theme).text

  const archetypes = new Set(resolveThemeArchetypes(normalizedTheme))
  const phrases: string[] = []

  for (const id of getSlangArchetypeIds(theme)) archetypes.add(id)

  for (const { pattern, archetypes: ids } of THEME_PHRASES) {
    if (pattern.test(normalizedTheme)) {
      for (const id of ids) archetypes.add(id)
      phrases.push(pattern.source.replace(/\\b/g, '').slice(0, 40))
    }
  }

  // Tribes only from what the user typed — not slang expansion (avoids false positives).
  const tribalTypes = detectTribesInText(normalizedTheme).map(singularizeTribe)
  const uniqueTribal = [...new Set(tribalTypes)]

  const explicitTribal = /\b(tribal|tribe)\b/.test(normalizedTheme)
  if (uniqueTribal.length > 0 || explicitTribal) archetypes.add('tribal')

  if (/\benchantments?\b|\benchantress\b|\benchantrix\b/.test(normalizedTheme)) {
    archetypes.delete('voltron')
    archetypes.add('enchantments')
  }
  if (/\bequipment\b|\bvoltron\b/.test(normalizedTheme)) {
    archetypes.delete('enchantments')
  }

  return {
    normalizedTheme,
    archetypes: [...archetypes],
    keywords: detectKeywordsInText(normalizedTheme),
    tribalTypes: uniqueTribal,
    phrases,
  }
}

export function describeCommanderIntent(intent: CommanderIntent): string {
  const parts: string[] = []
  if (intent.archetypes.length > 0) {
    const labels = intent.archetypes.map((id) => archetypeById(id)?.label ?? id)
    parts.push(`Archetypes: ${labels.join(', ')}`)
  }
  if (intent.tribalTypes.length > 0) {
    parts.push(`Tribal: ${intent.tribalTypes.join(', ')}`)
  }
  if (intent.keywords.length > 0) {
    parts.push(`Keywords: ${intent.keywords.map((k) => k.name).join(', ')}`)
  }
  return parts.join(' · ')
}

export function themeHasIntent(intent: CommanderIntent): boolean {
  return (
    intent.normalizedTheme.trim().length > 0 ||
    intent.archetypes.length > 0 ||
    intent.keywords.length > 0 ||
    intent.tribalTypes.length > 0
  )
}

/** All creature subtypes present in the loaded commander database. */
export function knownSubtypesFromCommanders(
  commanders: Array<{ creature_types?: string[]; type_line: string }>,
): Set<string> {
  const set = new Set<string>()
  for (const commander of commanders) {
    const types = commander.creature_types?.length
      ? commander.creature_types
      : parseCreatureTypes(commander.type_line)
    for (const type of types) set.add(singularizeTribe(type))
  }
  return set
}

/** Match tribe tokens from the query against the full subtype vocabulary (not just COMMON_TRIBES). */
export function enrichIntentWithSubtypes(
  intent: CommanderIntent,
  theme: string,
  knownSubtypes: Iterable<string>,
): CommanderIntent {
  const known = knownSubtypes instanceof Set ? knownSubtypes : new Set(knownSubtypes)
  const found = new Set(intent.tribalTypes.map(singularizeTribe))
  const tokens = theme.toLowerCase().match(/\b[a-z][a-z'-]{1,}\b/g) ?? []

  for (const token of tokens) {
    const singular = singularizeTribe(token)
    if (known.has(singular)) found.add(singular)
  }

  const tribalTypes = [...found]
  const archetypes = new Set(intent.archetypes)
  if (tribalTypes.length > 0) archetypes.add('tribal')

  return { ...intent, tribalTypes, archetypes: [...archetypes] }
}

export function resolveCommanderIntent(
  theme: string,
  commanders: Array<{ creature_types?: string[]; type_line: string }>,
  raw = false,
): CommanderIntent {
  const base = parseCommanderIntent(theme, raw)
  return enrichIntentWithSubtypes(base, theme, knownSubtypesFromCommanders(commanders))
}

/** Re-export for archetype signal checks in scoring */
export { ARCHETYPES, archetypeById }
