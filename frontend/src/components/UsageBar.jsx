function UsageBar({
  label,
  used,
  limit
}) {
  const pct = limit ? Math.min(100, Math.round(used / limit * 100)) : 0;
  return <div><div className="mb-1 flex justify-between text-sm"><span className="font-medium text-ink-700 dark:text-slate-200">{label}</span><span className="text-ink-700/60 dark:text-slate-400">{used} / {limit ?? "\u221E"}</span></div>{limit !== null && <div className="h-2 overflow-hidden rounded-full bg-ink-200 dark:bg-slate-700"><div className={`h-full rounded-full ${pct >= 90 ? "bg-red-500" : "bg-brand-600"}`} style={{
        width: `${pct}%`
      }} role="progressbar" aria-valuenow={used} aria-valuemin={0} aria-valuemax={limit} /></div>}</div>;
}
export { UsageBar };