import { useNotes } from './hooks/useNotes'
import Sidebar from './components/Sidebar'
import Editor from './components/Editor'
import './App.css'

export default function App() {
  const {
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
  } = useNotes()

  return (
    <div className="app">
      <Sidebar
        filtered={filtered}
        activeId={activeId}
        onSelect={setActiveId}
        search={search}
        onSearchChange={setSearch}
        filter={filter}
        onFilterChange={(f) => {
          setFilter(f)
          if (f === 'archived') setActiveTag(null)
        }}
        tags={tags}
        activeTag={activeTag}
        onTagChange={setActiveTag}
        onNewNote={addNote}
      />
      <Editor
        note={activeNote}
        onUpdate={updateNote}
        onDelete={deleteNote}
        onDuplicate={duplicateNote}
      />
    </div>
  )
}
