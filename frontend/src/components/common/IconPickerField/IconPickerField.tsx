'use client';

import { useMemo, useState } from 'react';
import { ChevronDown, Search } from 'lucide-react';

import { AppIcon } from '@/components/common/AppIcon';
import { Input } from '@/components/common/Input';
import { Popover } from '@/components/common/Popover';
import { cn } from '@/utils/cn';
import { DEFAULT_ICON_NAME, ICON_KEYS, SUGGESTED_ICON_NAMES } from '@/utils/icon-registry';

type IconPickerFieldProps = {
  value?: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
};

// Shared by both AdminAppCategories and AdminApps forms.
export function IconPickerField({ value, onChange, disabled }: IconPickerFieldProps) {
  const current = value && ICON_KEYS.includes(value) ? value : DEFAULT_ICON_NAME;
  const [query, setQuery] = useState('');

  // Static curated list (~160 icons) — filtering is instant, no
  // network/lazy-load involved, so no debounce needed.
  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return SUGGESTED_ICON_NAMES;
    return ICON_KEYS.filter((name) => name.includes(q));
  }, [query]);

  return (
    <Popover
      trigger={
        <button
          type="button"
          disabled={disabled}
          className={cn(
            'flex h-10 w-full items-center gap-2 rounded-md border border-input bg-background px-3 text-sm text-foreground',
            'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
          )}
        >
          <AppIcon name={current} className="h-4 w-4 shrink-0 text-muted-foreground" />
          <span className="flex-1 text-left">{current}</span>
          <ChevronDown className="h-4 w-4 shrink-0 opacity-50" aria-hidden />
        </button>
      }
      content={
        <div className="flex flex-col gap-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tìm icon (vd: chart, ship, factory...)"
            prefix={<Search className="h-4 w-4" aria-hidden />}
          />
          <div className="grid max-h-56 grid-cols-6 gap-1 overflow-y-auto">
            {results.map((name) => (
              <button
                key={name}
                type="button"
                title={name}
                aria-label={name}
                onClick={() => onChange?.(name)}
                className={cn(
                  'flex h-9 w-9 items-center justify-center rounded-md border transition-colors',
                  name === current ? 'border-primary bg-primary/5 text-primary' : 'border-border text-muted-foreground hover:bg-accent'
                )}
              >
                <AppIcon name={name} className="h-4 w-4" />
              </button>
            ))}
            {results.length === 0 && (
              <p className="col-span-6 py-4 text-center text-xs text-muted-foreground">Không tìm thấy icon phù hợp.</p>
            )}
          </div>
        </div>
      }
      className="w-72"
    />
  );
}
