export function DocumentIllustration() {
  return (
    <svg
      viewBox="0 0 520 430"
      role="img"
      aria-labelledby="document-art-title"
      className="document-art"
    >
      <title id="document-art-title">
        Minh họa việc sắp xếp giấy tờ thành một checklist rõ ràng
      </title>
      <defs>
        <pattern id="paper-grid" width="26" height="26" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="1" fill="#B9CEC9" />
        </pattern>
      </defs>
      <rect x="12" y="12" width="496" height="406" rx="28" fill="#E8F1EE" />
      <rect x="12" y="12" width="496" height="406" rx="28" fill="url(#paper-grid)" />
      <path
        d="M71 274C119 274 107 149 170 149M351 280C400 280 386 164 445 164"
        stroke="#83ADA3"
        strokeWidth="2"
        strokeDasharray="5 7"
        fill="none"
      />
      <g transform="translate(103 75) rotate(-10 120 150)">
        <rect width="239" height="295" rx="13" fill="#CADDD7" stroke="#A3BEB4" />
        <rect x="21" y="30" width="135" height="9" rx="4" fill="#A1BCB1" />
        <rect x="21" y="54" width="177" height="6" rx="3" fill="#ACC5BC" />
      </g>
      <g transform="translate(174 58) rotate(5 120 150)">
        <rect y="8" width="240" height="306" rx="13" fill="#173F3C" opacity=".09" />
        <rect width="240" height="306" rx="13" fill="white" stroke="#D3E0DA" />
        <rect x="25" y="29" width="34" height="34" rx="9" fill="#E7F2EE" />
        <path
          d="m34 45 6 6 11-13"
          stroke="#18786B"
          strokeWidth="2.5"
          fill="none"
          strokeLinecap="round"
        />
        <rect x="72" y="33" width="117" height="8" rx="4" fill="#244A47" />
        <rect x="72" y="49" width="78" height="5" rx="2.5" fill="#A2B4AD" />
        {[96, 151, 206].map((y, i) => (
          <g key={y}>
            <rect
              x="25"
              y={y}
              width="23"
              height="23"
              rx="6"
              fill={i === 2 ? '#F4F7F5' : '#18786B'}
              stroke={i === 2 ? '#A3BEB4' : 'none'}
            />
            {i !== 2 && (
              <path
                d={`m32 ${y + 11} 4 4 7-9`}
                fill="none"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
              />
            )}
            <rect x="63" y={y + 3} width="139" height="6" rx="3" fill="#657D74" />
            <rect x="63" y={y + 17} width="98" height="5" rx="2.5" fill="#D1DDD6" />
          </g>
        ))}
        <rect x="25" y="268" width="190" height="4" rx="2" fill="#E2EBE5" />
      </g>
      <circle cx="114" cy="326" r="32" fill="#18786B" />
      <path
        d="m101 326 9 9 17-19"
        stroke="white"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}
