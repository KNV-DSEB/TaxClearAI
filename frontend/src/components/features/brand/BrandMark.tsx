'use client';

import { useId } from 'react';

import { MARK_SMALL_SVG, MARK_SVG } from './brand-geometry';

// Mã gradient riêng cho mỗi lần hiển thị để nhiều logo trên một trang không dùng chung id
export function useMarkMarkup(small = false): string {
  const id = `tc${useId().replace(/[^a-zA-Z0-9]/g, '')}`;
  return (small ? MARK_SMALL_SVG : MARK_SVG).replaceAll('__ID__', id);
}

// Khiên hồ sơ + chữ C vàng nghệ; từ 32 px trở xuống dùng bản bỏ đổ bóng, tick dày hơn
export function BrandMark({ size = 40, title }: { size?: number; title?: string }) {
  const markup = useMarkMarkup(size <= 32);
  return (
    <svg
      viewBox="0 0 128 128"
      width={size}
      height={size}
      role={title ? 'img' : undefined}
      aria-label={title}
      aria-hidden={title ? undefined : true}
      // Markup sinh sẵn từ build_brand.py, không có dữ liệu người dùng
      dangerouslySetInnerHTML={{ __html: markup }}
    />
  );
}
