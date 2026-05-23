import { useState } from 'react'
import { NOTE_COLORS, parseChecklistItems } from '../utils/notes'

function ChecklistEditor({ items, onChange }) {
  const addItem = () => {
    onChange([
      ...items,
      { id: crypto.randomUUID(), text: '', done: false },
    ])
  }

  const updateItem = (id, patch) => {
    onChange(items.map((i) => (i.id === id ? { ...i, ...patch } : i)))
  }

  const removeItem = (id) => {
    onChange(items.filter((i) => i.id !== id))
  }

  return (
    <div className="checklist">
      {items.map((item, index) => (
        <div key={item.id} className="checklist__row">
          <input
            type="checkbox"
            checked={item.done}
            onChange={(e) => updateItem(item.id, { done: e.target.checked })}
            aria-label={`Mark item ${index + 1} done`}
          />
          <input
            type="text"
            className={`checklist__input ${item.done ? 'checklist__input--done' : ''}`}
            value={item.text}
            placeholder="List item…"
            onChange={(e) => updateItem(item.id, { text: e.target.value })}
          />
          <button
            type="button"
            className="icon-btn"
            onClick={() => removeItem(item.id)}
            aria-label="Remove item"
          >
            ×
          </button>
        </div>
      ))}
      <button type="button" className="btn btn--ghost checklist__add" onClick={addItem}>
        + Add item
      </button>
    </div>
  )
}

export default function Editor({
  note,
  onUpdate,
  onDelete,
  onDuplicate,
}) {
  const [tagInput, setTagInput] = useState('')

  if (!note) {
    return (
      <section className="editor editor--empty">
        <div className="editor__placeholder">
          <span className="editor__placeholder-icon" aria-hidden>📝</span>
          <h2>Select or create a note</h2>
          <p>Your memos, todos, and ideas — all in one place.</p>
        </div>
      </section>
    )
  }

  const addTag = () => {
    const tag = tagInput.trim().toLowerCase()
    if (!tag || note.tags?.includes(tag)) {
      setTagInput('')
      return
    }
    onUpdate(note.id, { tags: [...(note.tags || []), tag] })
    setTagInput('')
  }

  const removeTag = (tag) => {
    onUpdate(note.id, { tags: note.tags.filter((t) => t !== tag) })
  }

  const toggleChecklist = () => {
    if (note.checklist) {
      const body = note.items
        ?.map((i) => `${i.done ? '[x]' : '[ ]'} ${i.text}`)
        .join('\n')
      onUpdate(note.id, { checklist: false, body: body || note.body, items: [] })
    } else {
      const items = parseChecklistItems(note.body || '')
      onUpdate(note.id, {
        checklist: true,
        items: items.length ? items : [{ id: crypto.randomUUID(), text: '', done: false }],
      })
    }
  }

  const color = NOTE_COLORS.find((c) => c.id === note.color) ?? NOTE_COLORS[0]

  return (
    <section
      className="editor"
      style={{ '--editor-bg': color.bg }}
    >
      <header className="editor__toolbar">
        <div className="editor__actions">
          <button
            type="button"
            className={`icon-btn ${note.pinned ? 'icon-btn--active' : ''}`}
            onClick={() => onUpdate(note.id, { pinned: !note.pinned })}
            title={note.pinned ? 'Unpin' : 'Pin'}
            aria-label={note.pinned ? 'Unpin note' : 'Pin note'}
          >
            📌
          </button>
          <button
            type="button"
            className={`icon-btn ${note.checklist ? 'icon-btn--active' : ''}`}
            onClick={toggleChecklist}
            title="Toggle checklist"
            aria-label="Toggle checklist mode"
          >
            ☑
          </button>
          <button
            type="button"
            className="icon-btn"
            onClick={() => onDuplicate(note.id)}
            title="Duplicate"
            aria-label="Duplicate note"
          >
            ⧉
          </button>
          <button
            type="button"
            className="icon-btn"
            onClick={() => onUpdate(note.id, { archived: !note.archived })}
            title={note.archived ? 'Restore' : 'Archive'}
            aria-label={note.archived ? 'Restore note' : 'Archive note'}
          >
            {note.archived ? '↩' : '📦'}
          </button>
          <button
            type="button"
            className="icon-btn icon-btn--danger"
            onClick={() => {
              if (window.confirm('Delete this note permanently?')) onDelete(note.id)
            }}
            title="Delete"
            aria-label="Delete note"
          >
            🗑
          </button>
        </div>

        <div className="color-picker" role="group" aria-label="Note color">
          {NOTE_COLORS.map((c) => (
            <button
              key={c.id}
              type="button"
              className={`color-swatch ${note.color === c.id ? 'color-swatch--active' : ''}`}
              style={{ background: c.bg, borderColor: c.border }}
              onClick={() => onUpdate(note.id, { color: c.id })}
              title={c.label}
              aria-label={c.label}
              aria-pressed={note.color === c.id}
            />
          ))}
        </div>
      </header>

      <input
        type="text"
        className="editor__title"
        placeholder="Title"
        value={note.title}
        onChange={(e) => onUpdate(note.id, { title: e.target.value })}
        aria-label="Note title"
      />

      <div className="editor__tags-row">
        <div className="editor__tags">
          {note.tags?.map((tag) => (
            <span key={tag} className="tag">
              {tag}
              <button
                type="button"
                className="tag__remove"
                onClick={() => removeTag(tag)}
                aria-label={`Remove tag ${tag}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
        <div className="tag-input">
          <input
            type="text"
            placeholder="Add tag…"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                addTag()
              }
            }}
          />
          <button type="button" className="btn btn--ghost btn--sm" onClick={addTag}>
            Add
          </button>
        </div>
      </div>

      {note.checklist ? (
        <ChecklistEditor
          items={note.items || []}
          onChange={(items) => onUpdate(note.id, { items })}
        />
      ) : (
        <textarea
          className="editor__body"
          placeholder="Start writing…"
          value={note.body}
          onChange={(e) => onUpdate(note.id, { body: e.target.value })}
          aria-label="Note body"
        />
      )}
    </section>
  )
}
