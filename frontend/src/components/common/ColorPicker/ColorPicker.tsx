'use client';

import { useRef, useState } from 'react';
import { ChevronDown } from 'lucide-react';

import { Input } from '@/components/common/Input';
import { Popover } from '@/components/common/Popover';
import { hexToHsv, hsvToHex, hueToHex, isValidHex, type HSV } from '@/utils/color';
import { cn } from '@/utils/cn';

export type ColorPickerProps = {
  value?: string;
  onChange?: (value: string) => void;
  presets?: string[];
  disabled?: boolean;
  className?: string;
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics". Mirrors antd's ColorPicker: a swatch trigger opens
// a popover with a full saturation/value panel + hue slider (any color, not
// a fixed preset list) plus an optional preset row and a hex input.
export function ColorPicker({ value, onChange, presets, disabled, className }: ColorPickerProps) {
  const current = value && isValidHex(value) ? value : '#257BF4';
  const [hsv, setHsv] = useState<HSV>(() => hexToHsv(current));
  const [hexDraft, setHexDraft] = useState(current);

  // Đồng bộ lại khi giá trị từ ngoài đổi, làm ngay lúc render để tránh render dư
  const [prevCurrent, setPrevCurrent] = useState(current);
  if (prevCurrent !== current) {
    setPrevCurrent(current);
    setHsv(hexToHsv(current));
    setHexDraft(current);
  }

  const commitHsv = (next: HSV) => {
    setHsv(next);
    const hex = hsvToHex(next);
    setHexDraft(hex);
    onChange?.(hex);
  };

  const commitHex = (next: string) => {
    setHexDraft(next);
    if (isValidHex(next)) {
      setHsv(hexToHsv(next));
      onChange?.(next);
    }
  };

  const svRef = useRef<HTMLDivElement>(null);
  const hueRef = useRef<HTMLDivElement>(null);

  const dragSv = (event: React.PointerEvent) => {
    const el = svRef.current;
    if (!el) return;
    el.setPointerCapture(event.pointerId);
    const move = (e: PointerEvent | React.PointerEvent) => {
      const rect = el.getBoundingClientRect();
      const s = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
      const v = 1 - Math.min(1, Math.max(0, (e.clientY - rect.top) / rect.height));
      commitHsv({ ...hsv, s, v });
    };
    move(event);
    const up = () => window.removeEventListener('pointermove', move as (e: PointerEvent) => void);
    window.addEventListener('pointermove', move as (e: PointerEvent) => void);
    window.addEventListener('pointerup', up, { once: true });
  };

  const dragHue = (event: React.PointerEvent) => {
    const el = hueRef.current;
    if (!el) return;
    el.setPointerCapture(event.pointerId);
    const move = (e: PointerEvent | React.PointerEvent) => {
      const rect = el.getBoundingClientRect();
      const h = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width)) * 360;
      commitHsv({ ...hsv, h });
    };
    move(event);
    const up = () => window.removeEventListener('pointermove', move as (e: PointerEvent) => void);
    window.addEventListener('pointermove', move as (e: PointerEvent) => void);
    window.addEventListener('pointerup', up, { once: true });
  };

  return (
    <Popover
      trigger={
        <button
          type="button"
          disabled={disabled}
          className={cn(
            'flex h-10 w-full items-center gap-2 rounded-md border border-input bg-background px-3 text-sm text-foreground',
            'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            className
          )}
        >
          <span className="h-5 w-5 shrink-0 rounded-full border border-border" style={{ backgroundColor: current }} aria-hidden />
          <span className="flex-1 text-left font-mono uppercase">{current}</span>
          <ChevronDown className="h-4 w-4 shrink-0 opacity-50" aria-hidden />
        </button>
      }
      content={
        <div className="flex flex-col gap-3">
          {/* Saturation/Value panel */}
          <div
            ref={svRef}
            onPointerDown={dragSv}
            className="relative h-32 w-full cursor-crosshair touch-none rounded-md"
            style={{
              backgroundColor: hueToHex(hsv.h),
              backgroundImage: 'linear-gradient(to top, #000, transparent), linear-gradient(to right, #fff, transparent)',
            }}
          >
            <span
              className="absolute h-3 w-3 -translate-x-1/2 translate-y-1/2 rounded-full border-2 border-white shadow"
              style={{ left: `${hsv.s * 100}%`, bottom: `${hsv.v * 100}%`, backgroundColor: current }}
            />
          </div>

          {/* Hue slider */}
          <div
            ref={hueRef}
            onPointerDown={dragHue}
            className="relative h-3 w-full cursor-pointer touch-none rounded-full"
            style={{
              background: 'linear-gradient(to right, #f00, #ff0, #0f0, #0ff, #00f, #f0f, #f00)',
            }}
          >
            <span
              className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white shadow"
              style={{ left: `${(hsv.h / 360) * 100}%`, backgroundColor: hueToHex(hsv.h) }}
            />
          </div>

          <Input
            value={hexDraft}
            onChange={(e) => commitHex(e.target.value)}
            prefix={<span className="h-4 w-4 rounded-full border border-border" style={{ backgroundColor: isValidHex(hexDraft) ? hexDraft : 'transparent' }} />}
            placeholder="#RRGGBB"
            className="font-mono uppercase"
          />

          {presets && presets.length > 0 && (
            <div className="flex flex-wrap gap-2 border-t border-border pt-3">
              {presets.map((preset) => (
                <button
                  key={preset}
                  type="button"
                  aria-label={preset}
                  onClick={() => commitHex(preset)}
                  className={cn(
                    'h-6 w-6 shrink-0 rounded-full border transition-shadow',
                    preset.toLowerCase() === current.toLowerCase()
                      ? 'border-foreground ring-2 ring-ring ring-offset-2'
                      : 'border-border hover:scale-110'
                  )}
                  style={{ backgroundColor: preset }}
                />
              ))}
            </div>
          )}
        </div>
      }
      className="w-64"
    />
  );
}
