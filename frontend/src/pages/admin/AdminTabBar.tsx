type AdminTab = {
  id: string;
  label: string;
};

type AdminTabBarProps = {
  tabs: AdminTab[];
  value: string;
  onChange: (id: string) => void;
  label: string;
};

export function AdminTabBar({ tabs, value, onChange, label }: AdminTabBarProps) {
  return (
    <div
      role="tablist"
      aria-label={label}
      className="flex flex-wrap gap-2 border-b border-ink-100 pb-4 dark:border-slate-700"
    >
      {tabs.map((tab) => {
        const selected = value === tab.id;
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={selected}
            className={selected ? 'btn-primary text-sm' : 'btn-secondary text-sm'}
            onClick={() => onChange(tab.id)}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
