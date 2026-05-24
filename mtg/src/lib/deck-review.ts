import type { CardRecord } from '../types/card'
import type { DeckAnalysis } from '../types/mtg'
import { getCardByNameLocal } from './card-db'
import { chatCompletion } from './groq-chat'

export type DeckReviewResult = {
  review: string
  source: 'ai' | 'local'
}

const DECK_REVIEW_SYSTEM = `You are an expert Magic: The Gathering Commander deck analyst.

Write a genuine, honest deck review in 3–5 short paragraphs as a cohesive narrative. Be specific to the list provided — do not give generic Commander advice.

Cover: what the deck is trying to do, how cohesive the strategy feels, power level signals, and one or two actionable tuning suggestions (not a full upgrade list).

Do NOT use separate "Strengths" and "Weaknesses" headings — weave pros and cons naturally into your review.

Tone: direct, helpful, like a knowledgeable friend at the LGS. No fluff. Do not invent cards that are not in the list. If game changers are listed, comment on how they shape the deck's power level.`

function buildDeckSummary(
  analysis: DeckAnalysis,
  gameChangers: CardRecord[],
): string {
  const cardLines = analysis.cards
    .map((c) => `${c.quantity}x ${c.name}`)
    .join('\n')

  const roleCounts = countRoles(analysis)

  return [
    `Commander: ${analysis.commander?.name ?? 'Unknown'}`,
    `Colors: ${analysis.colorIdentity.join('') || 'Colorless'}`,
    `Cards: ${analysis.totalCards} (avg CMC ${analysis.avgCmc.toFixed(2)}, est. $${analysis.totalUsd.toFixed(0)})`,
    '',
    'Role counts in deck:',
    ...Object.entries(roleCounts).map(([k, v]) => `- ${k}: ${v}`),
    '',
    gameChangers.length > 0
      ? `Game Changers (Scryfall): ${gameChangers.map((c) => c.name).join(', ')}`
      : 'Game Changers: none detected',
    '',
    'Decklist:',
    cardLines,
  ].join('\n')
}

function countRoles(analysis: DeckAnalysis): Record<string, number> {
  const counts: Record<string, number> = {
    ramp: 0,
    draw: 0,
    removal: 0,
    wipe: 0,
    tutor: 0,
    protection: 0,
    recursion: 0,
  }

  for (const entry of analysis.cards) {
    const local = getCardByNameLocal(entry.name)
    if (!local) continue
    for (const role of local.roles) {
      if (role in counts) counts[role] += entry.quantity
    }
  }

  return counts
}

function localDeckReview(
  analysis: DeckAnalysis,
  gameChangers: CardRecord[],
): string {
  const commander = analysis.commander?.name ?? 'your commander'
  const colors = analysis.colorIdentity.join('') || 'colorless'

  const parts = [
    `This ${colors} list led by **${commander}** runs ${analysis.totalCards} cards at an average mana value of ${analysis.avgCmc.toFixed(2)} (estimated value $${analysis.totalUsd.toFixed(0)}).`,
  ]

  if (gameChangers.length > 0) {
    parts.push(
      `It includes ${gameChangers.length} Commander Game Changer${gameChangers.length === 1 ? '' : 's'} (${gameChangers.map((c) => c.name).join(', ')}), which will draw table attention and raise the overall power floor.`,
    )
  }

  parts.push(
    `The list reads as a focused Commander deck — check the **Strengths and Weaknesses** tab for a structural breakdown, and **Upgrades** for card suggestions.`,
  )

  if (analysis.warnings.length > 0) {
    parts.push('', '**Notes:**', ...analysis.warnings.map((w) => `• ${w}`))
  }

  parts.push(
    '',
    '_AI deck review uses Groq when the API proxy is available (Vercel or local dev with GROQ_API_KEY)._',
  )

  return parts.join('\n\n')
}

async function callGroqReview(summary: string): Promise<string> {
  return chatCompletion({
    temperature: 0.5,
    max_tokens: 1200,
    messages: [
      { role: 'system', content: DECK_REVIEW_SYSTEM },
      { role: 'user', content: summary },
    ],
  })
}

export async function generateDeckReview(
  analysis: DeckAnalysis,
  gameChangers: CardRecord[],
): Promise<DeckReviewResult> {
  const summary = buildDeckSummary(analysis, gameChangers)

  try {
    const review = await callGroqReview(summary)
    return { review, source: 'ai' }
  } catch {
    /* fall through to local */
  }

  return {
    review: localDeckReview(analysis, gameChangers),
    source: 'local',
  }
}

export function renderDeckReviewMarkdown(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    .replace(/\n/g, '<br />')
}
