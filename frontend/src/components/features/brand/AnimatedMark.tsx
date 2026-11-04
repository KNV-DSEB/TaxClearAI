'use client';

import { useMarkMarkup } from './BrandMark';

// Khiên hiện lên, chữ C xoay vào, rồi dấu tick tự vẽ; tắt khi người dùng chọn giảm chuyển động
export function AnimatedMark({ size = 72 }: { size?: number }) {
  const markup = useMarkMarkup();
  return (
    <svg
      viewBox="0 0 128 128"
      width={size}
      height={size}
      aria-hidden="true"
      className="animated-mark"
      dangerouslySetInnerHTML={{ __html: markup }}
    />
  );
}
