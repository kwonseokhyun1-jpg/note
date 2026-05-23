import { formatDate, getPreview, NOTE_COLORS } from '../utils/notes'

function NoteCard({ note, active, onSelect }) {
  const color = NOTE_COLORS.find((c) => c.id === note.color) ?? NOTE_COLORS[0]

  return (
    <button
      type="button"
      className={`note-card ${active ? 'note-card--active' : ''}`}
      onClick={() => onSelect(note.id)}
      style={{
        '--card-bg': color.bg,
        '--card-border': color.border,
      }}
    >
      <div className="note-card__top">
        <span className="note-card__title">
          {note.pinned && <span className="note-card__pin" aria-hidden>📌</span>}
          {note.title?.trim() || 'Untitled'}
        </span>
        <time className="note-card__time">{formatDate(note.updatedAt)}</time>
      </div>
      <p className="note-card__preview">{getPreview(note)}</p>
      {note.tags?.length > 0 && (
        <div className="note-card__tags">
          {note.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="tag tag--sm">
              {tag}
            </span>
          ))}
        </div>
      )}
    </button>
  )
}

export default function Sidebar({
  filtered,
  activeId,
  onSelect,
  search,
  onSearchChange,
  filter,
  onFilterChange,
  tags,
  activeTag,
  onTagChange,
  onNewNote,
}) {
  const filters = [
    { id: 'all', label: 'All notes' },
    { id: 'pinned', label: 'Pinned' },
    { id: 'archived', label: 'Archive' },
  ]

  return (
    <aside className="sidebar">
      <header className="sidebar__header">
        <h1 className="logo">
          <span className="logo__icon" aria-hidden>✦</span>
          Memo
        </h1>
        <button type="button" className="btn btn--primary" onClick={onNewNote}>
          + New note
        </button>
      </header>

      <div className="search-box">
        <span className="search-box__icon" aria-hidden>⌕</span>
        <input
          type="search"
          placeholder="Search notes…"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          aria-label="Search notes"
        />
      </div>

      <nav className="filter-nav" aria-label="Note filters">
        {filters.map((f) => (
          <button
            key={f.id}
            type="button"
            className={`filter-btn ${filter === f.id ? 'filter-btn--active' : ''}`}
            onClick={() => onFilterChange(f.id)}
          >
            {f.label}
          </button>
        ))}
      </nav>

      {tags.length > 0 && filter !== 'archived' && (
        <div className="tag-filter">
          <span className="tag-filter__label">Tags</span>
          <div className="tag-filter__list">
            <button
              type="button"
              className={`tag ${!activeTag ? 'tag--active' : ''}`}
              onClick={() => onTagChange(null)}
            >
              all
            </button>
            {tags.map((tag) => (
              <button
                key={tag}
                type="button"
                className={`tag ${activeTag === tag ? 'tag--active' : ''}`}
                onClick={() => onTagChange(tag)}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="note-list" role="list">
        {filtered.length === 0 ? (
          <p className="empty-state">
            {filter === 'archived'
              ? 'No archived notes.'
              : 'No notes match. Create one!'}
          </p>
        ) : (
          filtered.map((note) => (
            <NoteCard
              key={note.id}
              note={note}
              active={note.id === activeId}
              onSelect={onSelect}
            />
          ))
        )}
      </div>
    </aside>
  )
}
