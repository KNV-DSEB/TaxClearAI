import { FACETS, FACETS_ON_DARK, FACETS_SMALL, type Facet } from './brand-geometry';

export function Facets({ facets, className }: { facets: Facet[]; className?: string }) {
  return (
    <>
      {facets.map((facet, index) => (
        <path
          key={facet.d}
          d={facet.d}
          fill={facet.fill}
          className={className}
          style={className ? { animationDelay: `${index * 45}ms` } : undefined}
          data-warm={facet.warm || undefined}
        />
      ))}
    </>
  );
}

// Biểu tượng "C pha lê"; dưới 32 px dùng bản 7 mặt để không nhòe
export function BrandMark({
  size = 40,
  onDark = false,
  title,
}: {
  size?: number;
  onDark?: boolean;
  title?: string;
}) {
  const facets = size <= 32 ? FACETS_SMALL : onDark ? FACETS_ON_DARK : FACETS;
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role={title ? 'img' : undefined}
      aria-label={title}
      aria-hidden={title ? undefined : true}
    >
      <Facets facets={facets} />
    </svg>
  );
}
