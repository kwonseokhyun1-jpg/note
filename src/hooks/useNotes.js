import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  createNote,
  loadNotes,
  saveNotes,
  sortNotes,
  collectTags,
} from '../utils/notes'

export function useNotes() {
  const [notes, setNotes] = useState(loadNotes)
  const [activeId, setActiveId] = useState(() => notes[0]?.id ?? null)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const [activeTag, setActiveTag] = useState(null)

  useEffect(() => {
    saveNotes(notes)
  }, [notes])

  const tags = useMemo(() => collectTags(notes.filter((n) => !n.archived)), [notes])

  const filtered = useMemo(() => {
    let list = notes

    if (filter === 'pinned') list = list.filter((n) => n.pinned && !n.archived)
    else if (filter === 'archived') list = list.filter((n) => n.archived)
    else list = list.filter((n) => !n.archived)

    if (activeTag) {
      list = list.filter((n) =>
        n.tags?.some((t) => t.toLowerCase() === activeTag),
      )
    }

    const q = search.trim().toLowerCase()
    if (q) {
      list = list.filter(
        (n) =>
          n.title?.toLowerCase().includes(q) ||
          n.body?.toLowerCase().includes(q) ||
          n.tags?.some((t) => t.toLowerCase().includes(q)),
      )
    }

    return sortNotes(list)
  }, [notes, search, filter, activeTag])

  const activeNote = useMemo(
    () => notes.find((n) => n.id === activeId) ?? null,
    [notes, activeId],
  )

  const updateNote = useCallback((id, patch) => {
    setNotes((prev) =>
      prev.map((n) =>
        n.id === id ? { ...n, ...patch, updatedAt: Date.now() } : n,
      ),
    )
  }, [])

  const addNote = useCallback(() => {
    const note = createNote()
    setNotes((prev) => [note, ...prev])
    setActiveId(note.id)
    setFilter('all')
    setActiveTag(null)
    return note.id
  }, [])

  const deleteNote = useCallback(
    (id) => {
      setNotes((prev) => {
        const next = prev.filter((n) => n.id !== id)
        if (activeId === id) {
          const remaining = sortNotes(next.filter((n) => !n.archived))
          setActiveId(remaining[0]?.id ?? null)
        }
        return next
      })
    },
    [activeId],
  )

  const duplicateNote = useCallback((id) => {
    const source = notes.find((n) => n.id === id)
    if (!source) return
    const copy = createNote({
      title: source.title ? `${source.title} (copy)` : '',
      body: source.body,
      tags: [...(source.tags || [])],
      color: source.color,
      checklist: source.checklist,
      items: source.items?.map((i) => ({ ...i, id: crypto.randomUUID() })),
    })
    setNotes((prev) => [copy, ...prev])
    setActiveId(copy.id)
  }, [notes])

  return {
    notes,
    filtered,
    activeNote,
    activeId,
    setActiveId,
    search,
    setSearch,
    filter,
    setFilter,
    activeTag,
    setActiveTag,
    tags,
    updateNote,
    addNote,
    deleteNote,
    duplicateNote,
  }
}
