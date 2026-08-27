/**
 * Horizontal tab list for dense admin / org pages.
 */
export function TabList({ tabs, active, onChange }) {
  return (
    <div
      role="tablist"
      aria-label="Sections"
      className="mb-8 flex gap-1 overflow-x-auto rounded-2xl border border-ink-100/70 bg-white/70 p-1.5 shadow-soft backdrop-blur-sm dark:border-slate-700 dark:bg-slate-900/60"
    >
      {tabs.map((tab) => {
        const selected = tab.id === active;
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={selected}
            id={`tab-${tab.id}`}
            className={`shrink-0 rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors ${
              selected
                ? 'bg-brand-700 text-white shadow-sm dark:bg-brand-600'
                : 'text-ink-700 hover:bg-white/80 dark:text-slate-300 dark:hover:bg-slate-800'
            }`}
            onClick={() => onChange(tab.id)}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}

export function TabPanel({ id, active, children }) {
  if (id !== active) return null;
  return (
    <div role="tabpanel" aria-labelledby={`tab-${id}`} className="animate-fade-in">
      {children}
    </div>
  );
}
