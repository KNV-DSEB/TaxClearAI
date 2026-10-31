// Hình minh họa trang trí: tài liệu thuế đã được đánh dấu từng mục, có khiên xác nhận
export function HeroIllustration() {
  return (
    <svg
      className="hero-art"
      viewBox="0 0 420 360"
      role="img"
      aria-label="Minh họa tờ khai thuế với các mục đã đánh dấu"
    >
      <defs>
        <linearGradient id="hero-glow" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#dff1e9" />
          <stop offset="1" stopColor="#f4faf7" />
        </linearGradient>
        <linearGradient id="hero-shield" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#2f9a7f" />
          <stop offset="1" stopColor="#0f5a4c" />
        </linearGradient>
      </defs>
      <ellipse cx="220" cy="190" rx="190" ry="150" fill="url(#hero-glow)" />
      <path
        d="M52 300c40-30 80-20 110 4"
        stroke="#cfe6dc"
        strokeWidth="10"
        fill="none"
        strokeLinecap="round"
      />
      <g transform="rotate(-8 210 170)">
        <rect x="118" y="58" width="180" height="236" rx="14" fill="#e9f3ef" />
        <rect x="136" y="44" width="180" height="236" rx="14" fill="#ffffff" stroke="#d7e7e0" />
        <path d="M286 44h16l14 14v16h-30z" fill="#e3efe9" />
        <text x="158" y="92" fontSize="30" fontWeight="700" fill="#173f3b" letterSpacing="2">
          TAX
        </text>
        {[124, 164, 204].map((y) => (
          <g key={y}>
            <circle cx="168" cy={y} r="11" fill="#17705f" />
            <path
              d={`M162 ${y}l4 4 8-8`}
              stroke="#fff"
              strokeWidth="2.6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <rect x="190" y={y - 7} width="96" height="6" rx="3" fill="#c9ddd5" />
            <rect x="190" y={y + 3} width="62" height="5" rx="2.5" fill="#e1ece7" />
          </g>
        ))}
        <rect x="158" y="236" width="128" height="6" rx="3" fill="#e1ece7" />
      </g>
      <path d="M340 170c-30-8-48 16-44 44 26 2 46-14 44-44z" fill="#bfe1d3" />
      <path d="M306 212c10-14 20-26 34-42" stroke="#8cc7b0" strokeWidth="3" fill="none" />
      <g transform="translate(262 186)">
        <path d="M52 0l52 18v38c0 34-22 58-52 70C22 114 0 90 0 56V18z" fill="url(#hero-shield)" />
        <path
          d="M30 60l16 16 30-32"
          stroke="#fff"
          strokeWidth="9"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </g>
    </svg>
  );
}
