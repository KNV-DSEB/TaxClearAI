'use client';

import { ChangeEvent, useRef, useState } from 'react';
import NextImage from 'next/image';
import { Loader2, Trash2, Upload } from 'lucide-react';

import { cn } from '@/utils/cn';

import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { Popconfirm } from '@/components/common/Popconfirm';

const DEFAULT_FALLBACK = '/images/image-placeholder.svg';

type ImgStatus = 'loading' | 'loaded' | 'error';

type ImageProps = {
  src?: string | null;
  alt: string;
  fallback?: string;
  width?: number | string;
  height?: number | string;
  className?: string;
  preview?: boolean;
  disabled?: boolean;
  onUpload?: (file: File) => void | Promise<void>;
  onRemove?: () => void | Promise<void>;
};

// Reusable UI ONLY — no business logic, no API calls. See AGENTS.md
// "Frontend specifics". `onUpload`/`onRemove` are caller-supplied handlers
// (backed by a services/*.service.ts) — this component never calls an API.
//
// `src` is runtime/user-provided (upload result), so its domain is unknown
// at build time — the consuming app must allow it in next.config's
// `images.remotePatterns` (or pass `unoptimized` on next/image if the
// domain set can't be known ahead of time).
export function Image({
  src,
  alt,
  fallback = DEFAULT_FALLBACK,
  width,
  height,
  className,
  preview = true,
  disabled = false,
  onUpload,
  onRemove,
}: ImageProps) {
  const [status, setStatus] = useState<ImgStatus>(src ? 'loading' : 'error');
  const [previewOpen, setPreviewOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [removing, setRemoving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Đặt lại trạng thái khi src đổi, làm ngay lúc render để tránh render dư
  const [prevSrc, setPrevSrc] = useState(src);
  if (prevSrc !== src) {
    setPrevSrc(src);
    setStatus(src ? 'loading' : 'error');
  }

  const displaySrc = status === 'error' || !src ? fallback : src;
  const busy = uploading || removing;
  const canPreview = preview && !disabled && status !== 'error';

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file || !onUpload) return;

    try {
      setUploading(true);
      await onUpload(file);
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = async () => {
    if (!onRemove) return;
    try {
      setRemoving(true);
      await onRemove();
    } finally {
      setRemoving(false);
    }
  };

  const thumb = (
    <NextImage
      src={displaySrc}
      alt={alt}
      fill
      sizes="(max-width: 768px) 100vw, 320px"
      className={cn('object-cover', status === 'loading' && 'opacity-0')}
      onLoad={() => setStatus('loaded')}
      onError={() => setStatus('error')}
    />
  );

  return (
    <div
      className={cn('group relative overflow-hidden rounded-md border border-border bg-muted', className)}
      style={{ width, height }}
    >
      {status === 'loading' && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" aria-hidden />
        </div>
      )}

      {canPreview ? (
        <button
          type="button"
          className="block h-full w-full cursor-pointer p-0"
          aria-label={`Preview ${alt}`}
          onClick={() => setPreviewOpen(true)}
        >
          {thumb}
        </button>
      ) : (
        thumb
      )}

      {busy && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/40">
          <Loader2 className="h-5 w-5 animate-spin text-white" aria-hidden />
        </div>
      )}

      {!disabled && (onUpload || onRemove) && !busy && (
        <div className="absolute inset-x-0 bottom-0 flex items-center justify-center gap-2 bg-black/50 py-1.5 opacity-0 transition-opacity group-hover:opacity-100">
          {onUpload && (
            <>
              <Button
                type="text"
                size="sm"
                className="h-7 w-7 p-0 text-white hover:bg-white/20 hover:text-white"
                icon={<Upload className="h-4 w-4" aria-hidden />}
                aria-label="Upload image"
                onClick={() => fileInputRef.current?.click()}
              />
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleFileChange}
              />
            </>
          )}
          {onRemove && (
            <Popconfirm title="Remove this image?" danger okText="Remove" onConfirm={handleRemove}>
              <Button
                type="text"
                size="sm"
                danger
                className="h-7 w-7 p-0 text-white hover:bg-white/20 hover:text-white"
                icon={<Trash2 className="h-4 w-4" aria-hidden />}
                aria-label="Remove image"
              />
            </Popconfirm>
          )}
        </div>
      )}

      {canPreview && (
        <Modal open={previewOpen} onOpenChange={setPreviewOpen} footer={null} width="auto">
          {/* Plain <img>, not next/image: this is a natural-size lightbox
             (max-h/max-w cap, no fixed box) — next/image's `fill` mode needs
             a definitely-sized ancestor, which would force the box open even
             for small images instead of shrinking to the image's own size. */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={displaySrc} alt={alt} className="max-h-[80vh] max-w-[80vw] object-contain" />
        </Modal>
      )}
    </div>
  );
}
