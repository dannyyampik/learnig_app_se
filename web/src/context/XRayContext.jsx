import { createContext, useContext, useEffect, useState } from 'react'
import { onTrace } from '../api.js'

// X-Ray state: the collected traces and whether the panel is showing.
// Traces arrive via api.js's pub/sub (see onTrace there) — newest first,
// capped so a long session doesn't grow forever.

const XRayContext = createContext(null)
const MAX_ENTRIES = 50

let nextId = 1

export function XRayProvider({ children }) {
  const [entries, setEntries] = useState([])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    // Subscribe on mount, unsubscribe on unmount — onTrace returns the
    // cleanup function, which is exactly what useEffect wants back.
    return onTrace((traceData) => {
      setEntries((prev) =>
        [{ ...traceData, id: nextId++ }, ...prev].slice(0, MAX_ENTRIES),
      )
    })
  }, [])

  useEffect(() => {
    // The ` (backtick) key toggles the panel — unless you're typing.
    function onKey(event) {
      if (event.key !== '`') return
      if (event.target.closest('input, textarea')) return
      setOpen((wasOpen) => !wasOpen)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const value = {
    entries,
    open,
    toggle: () => setOpen((wasOpen) => !wasOpen),
    clear: () => setEntries([]),
  }
  return <XRayContext.Provider value={value}>{children}</XRayContext.Provider>
}

export function useXRay() {
  return useContext(XRayContext)
}
