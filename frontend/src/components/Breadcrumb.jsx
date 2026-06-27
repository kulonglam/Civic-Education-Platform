import { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from './Icons';

export function Breadcrumb({ items }) {
  return (
    <nav
      aria-label="Breadcrumb"
      className="mb-4 flex items-center gap-1 text-sm text-gray-500 dark:text-slate-400"
    >
      {items.map((item, idx) => (
        <Fragment key={idx}>
          {idx > 0 && <ChevronRight className="h-3.5 w-3.5 flex-shrink-0 text-gray-400 dark:text-slate-600" />}
          {item.to ? (
            <Link
              to={item.to}
              className="truncate max-w-[160px] transition-colors hover:text-brand-600 dark:hover:text-brand-400"
            >
              {item.label}
            </Link>
          ) : (
            <span className="truncate max-w-[220px] font-medium text-gray-800 dark:text-slate-200">
              {item.label}
            </span>
          )}
        </Fragment>
      ))}
    </nav>
  );
}
