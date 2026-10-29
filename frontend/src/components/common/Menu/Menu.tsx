'use client';

import { ReactNode, useState } from 'react';
import { ChevronDown } from 'lucide-react';

import { cn } from '@/utils/cn';

export type MenuItem = {
  key: string;
  label: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
  children?: MenuItem[];
};

type MenuProps = {
  items: MenuItem[];
  mode?: 'vertical' | 'horizontal';
  selectedKeys?: string[];
  defaultOpenKeys?: string[];
  onSelect?: (key: string) => void;
  className?: string;
};

function MenuNode({
  item,
  depth,
  mode,
  selectedKeys,
  openKeys,
  toggleOpen,
  onSelect,
}: {
  item: MenuItem;
  depth: number;
  mode: 'vertical' | 'horizontal';
  selectedKeys: string[];
  openKeys: string[];
  toggleOpen: (key: string) => void;
  onSelect?: (key: string) => void;
}) {
  const hasChildren = !!item.children?.length;
  const isSelected = selectedKeys.includes(item.key);
  const isOpen = openKeys.includes(item.key);

  return (
    <li>
      <button
        type="button"
        disabled={item.disabled}
        onClick={() => {
          if (hasChildren) {
            toggleOpen(item.key);
            return;
          }
          onSelect?.(item.key);
        }}
        style={mode === 'vertical' ? { paddingLeft: 12 + depth * 16 } : undefined}
        className={cn(
          'flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm text-foreground transition-colors',
          'hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-50',
          isSelected && !hasChildren && 'bg-primary/10 font-medium text-primary'
        )}
      >
        {item.icon}
        <span className="flex-1">{item.label}</span>
        {hasChildren && (
          <ChevronDown className={cn('h-4 w-4 transition-transform', isOpen && 'rotate-180')} aria-hidden />
        )}
      </button>
      {hasChildren && isOpen && (
        <ul className={mode === 'vertical' ? undefined : 'absolute mt-1 min-w-[10rem] rounded-md border border-border bg-popover p-1 shadow-md'}>
          {item.children!.map((child) => (
            <MenuNode
              key={child.key}
              item={child}
              depth={depth + 1}
              mode={mode}
              selectedKeys={selectedKeys}
              openKeys={openKeys}
              toggleOpen={toggleOpen}
              onSelect={onSelect}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics".
export function Menu({
  items,
  mode = 'vertical',
  selectedKeys = [],
  defaultOpenKeys = [],
  onSelect,
  className,
}: MenuProps) {
  const [openKeys, setOpenKeys] = useState<string[]>(defaultOpenKeys);

  const toggleOpen = (key: string) => {
    setOpenKeys((prev) => (prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]));
  };

  return (
    <ul
      className={cn(
        mode === 'vertical' ? 'flex flex-col gap-0.5' : 'relative flex items-center gap-1',
        className
      )}
    >
      {items.map((item) => (
        <MenuNode
          key={item.key}
          item={item}
          depth={0}
          mode={mode}
          selectedKeys={selectedKeys}
          openKeys={openKeys}
          toggleOpen={toggleOpen}
          onSelect={onSelect}
        />
      ))}
    </ul>
  );
}
