'use client';

import { type ChangeEvent, type DragEvent, useRef, useState } from 'react';
import { Upload as UploadIcon } from 'lucide-react';

import { cn } from '@/utils/cn';

type DraggerProps = {
  accept?: string;
  disabled?: boolean;
  onFileSelect: (file: File) => void;
  title?: string;
  hint?: string;
  className?: string;
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics". Single-file drag-and-drop zone (click-to-browse
// fallback included) — caller owns what happens with the selected file.
export function Dragger({
  accept,
  disabled = false,
  onFileSelect,
  title = 'Kéo thả file vào đây, hoặc bấm để chọn',
  hint,
  className,
}: DraggerProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const openBrowser = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
    e.target.value = '';
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (disabled) return;
    const file = e.dataTransfer.files?.[0];
    if (file) onFileSelect(file);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (!disabled) setIsDragOver(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  return (
    <div
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-disabled={disabled}
      onClick={openBrowser}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openBrowser();
        }
      }}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={cn(
        'flex cursor-pointer flex-col items-center gap-2 rounded-md border-2 border-dashed border-border p-8 text-center transition-colors',
        'hover:border-primary/50 hover:bg-accent/50',
        isDragOver && 'border-primary bg-accent/50',
        disabled && 'cursor-not-allowed opacity-50 hover:border-border hover:bg-transparent',
        className
      )}
    >
      <UploadIcon className="h-8 w-8 text-muted-foreground" aria-hidden />
      <p className="text-sm font-medium text-foreground">{title}</p>
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        disabled={disabled}
        className="hidden"
        onChange={handleInputChange}
      />
    </div>
  );
}
