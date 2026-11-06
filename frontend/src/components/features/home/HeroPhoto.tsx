import { ShieldCheck } from 'lucide-react';
import Image from 'next/image';

// Ảnh stock (Pexels License) chỉ để minh họa bối cảnh làm hồ sơ, không phải khách hàng của dự án
export function HeroPhoto() {
  return (
    <figure className="hero-photo">
      <Image
        alt="Hai bàn tay cùng xem và điền một biểu mẫu giấy trên bàn làm việc"
        className="hero-photo-img"
        height={1300}
        priority
        sizes="(max-width: 960px) 90vw, 480px"
        src="/images/hero-ky-ho-so.jpg"
        width={1040}
      />
      <span className="hero-photo-chip">
        <ShieldCheck aria-hidden="true" size={16} />
        Chuẩn bị hồ sơ trước khi gặp chuyên viên
      </span>
      <figcaption className="hero-photo-caption">Ảnh minh họa</figcaption>
    </figure>
  );
}
