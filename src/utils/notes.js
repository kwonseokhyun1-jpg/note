export const STORAGE_KEY = 'memo-notes-v1'

export const NOTE_COLORS = [
  { id: 'default', label: 'Default', bg: 'var(--note-default)', border: 'var(--border)' },
  { id: 'yellow', label: 'Yellow', bg: '#fef9c3', border: '#fde047' },
  { id: 'green', label: 'Green', bg: '#dcfce7', border: '#86efac' },
  { id: 'blue', label: 'Blue', bg: '#dbeafe', border: '#93c5fd' },
  { id: 'pink', label: 'Pink', bg: '#fce7f3', border: '#f9a8d4' },
  { id: 'purple', label: 'Purple', bg: '#ede9fe', border: '#c4b5fd' },
]

export function createNote(overrides = {}) {
  const now = Date.now()
  return {
    id: crypto.randomUUID(),
    title: '',
    body: '',
    tags: [],
    color: 'default',
    pinned: false,
    archived: false,
    checklist: false,
    items: [],
    createdAt: now,
    updatedAt: now,
    ...overrides,
  }
}

export function parseChecklistItems(text) {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((text, i) => ({
      id: `item-${i}-${text.slice(0, 8)}`,
      text: text.replace(/^[-*]\s*\[[ xX]?\]\s*/, '').replace(/^[-*]\s+/, ''),
      done: /^\s*[-*]\s*\[[xX]\]/.test(line),
    }))
}

export function sortNotes(notes) {
  return [...notes].sort((a, b) => {
    if (a.pinned !== b.pinned) return a.pinned ? -1 : 1
    return b.updatedAt - a.updatedAt
  })
}

export function loadNotes() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return [createNote({ title: 'Welcome to Memo', body: 'Your notes are saved automatically in this browser.\n\nTry pinning, tagging, or switching to checklist mode!' })]
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function saveNotes(notes) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(notes))
}

export function formatDate(ts) {
  const d = new Date(ts)
  const now = new Date()
  const sameDay =
    d.getDate() === now.getDate() &&
    d.getMonth() === now.getMonth() &&
    d.getFullYear() === now.getFullYear()

  if (sameDay) {
    return d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
  }
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export function getPreview(note) {
  if (note.checklist && note.items?.length) {
    const done = note.items.filter((i) => i.done).length
    return `${done}/${note.items.length} tasks`
  }
  const text = note.body?.trim() || 'No content'
  return text.length > 80 ? text.slice(0, 80) + '…' : text
}

export function collectTags(notes) {
  const set = new Set()
  notes.forEach((n) => n.tags?.forEach((t) => set.add(t.toLowerCase())))
  return [...set].sort()
}
