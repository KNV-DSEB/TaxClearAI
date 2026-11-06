import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Tax Clear',
    short_name: 'Tax Clear',
    description: 'Trợ lý chuẩn bị hồ sơ giải thể cho doanh nghiệp.',
    start_url: '/',
    display: 'standalone',
    background_color: '#eef7f3',
    theme_color: '#0f5a4c',
    icons: [
      { src: '/brand/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/brand/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
  };
}
