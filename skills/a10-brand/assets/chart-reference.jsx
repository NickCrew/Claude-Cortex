import { useState } from "react";

// A10 Brand Color System
const colors = {
  // Primary
  blue: "#0057B7",
  navy: "#001E62",
  white: "#FFFFFF",
  // Secondary
  sky: "#529EEC",
  magenta: "#D62598",
  // Accents
  green: "#00B140",
  orange: "#E35205",
  red: "#EF3340",
  purple: "#440099",
  cloudBlue: "#5E8AB4",
  // UI
  cardDark: "#0A1A3A",
  grayLight: "#F0F4F8",
  grayMedium: "#DFE8F0",
  grayDark: "#404040",
  grayMid: "#7F7F7F",
  // Tints
  blueDark: "#004189",
  blueLight: "#7CBAFF",
  skyLight: "#BEDDFF",
  navyDark: "#00174A",
};

// Chart data series color assignments (ordered by usage priority)
const seriesColors = {
  primary: colors.blue,
  secondary: colors.sky,
  success: colors.green,
  warning: colors.orange,
  danger: colors.red,
  accent: colors.magenta,
  info: colors.cloudBlue,
  highlight: colors.purple,
};

// SVG gradient definitions for depth
const GradientDefs = ({ id, baseColor, darkMode = true }) => {
  const lighten = (hex, amt) => {
    const num = parseInt(hex.replace("#", ""), 16);
    const r = Math.min(255, ((num >> 16) & 0xff) + amt);
    const g = Math.min(255, ((num >> 8) & 0xff) + amt);
    const b = Math.min(255, (num & 0xff) + amt);
    return `rgb(${r},${g},${b})`;
  };
  const darken = (hex, amt) => lighten(hex, -amt);

  return (
    <>
      <linearGradient id={`${id}-v`} x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stopColor={lighten(baseColor, 30)} />
        <stop offset="100%" stopColor={darken(baseColor, 20)} />
      </linearGradient>
      <linearGradient id={`${id}-h`} x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stopColor={darken(baseColor, 20)} />
        <stop offset="100%" stopColor={lighten(baseColor, 30)} />
      </linearGradient>
    </>
  );
};

// ─── VERTICAL BAR CHART ────────────────────────────
const VerticalBarChart = ({ data, title, subtitle, height = 300, showValues = true }) => {
  const [hovered, setHovered] = useState(null);
  const maxVal = Math.max(...data.map((d) => d.value));
  const yTicks = 5;
  const padding = { top: 20, right: 20, bottom: 60, left: 60 };
  const chartW = 560;
  const chartH = height;
  const innerW = chartW - padding.left - padding.right;
  const innerH = chartH - padding.top - padding.bottom;
  const barGap = 0.3;
  const barW = (innerW / data.length) * (1 - barGap);
  const barSpacing = innerW / data.length;

  const niceMax = Math.ceil(maxVal / Math.pow(10, Math.floor(Math.log10(maxVal)))) * Math.pow(10, Math.floor(Math.log10(maxVal)));

  return (
    <div style={{ background: colors.cardDark, padding: "24px", marginBottom: 24 }}>
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ color: colors.grayLight, fontSize: 20, fontWeight: 300, margin: 0, fontFamily: "'Rubik', sans-serif" }}>{title}</h3>
        {subtitle && <p style={{ color: colors.grayMid, fontSize: 14, margin: "4px 0 0", fontFamily: "'Rubik', sans-serif", fontWeight: 400 }}>{subtitle}</p>}
      </div>
      <svg width={chartW} height={chartH} style={{ overflow: "visible" }}>
        <defs>
          {data.map((d, i) => (
            <GradientDefs key={i} id={`vbar-${i}`} baseColor={d.color || colors.blue} />
          ))}
        </defs>

        {/* Grid lines */}
        {Array.from({ length: yTicks + 1 }).map((_, i) => {
          const y = padding.top + innerH - (i / yTicks) * innerH;
          const val = Math.round((i / yTicks) * niceMax);
          return (
            <g key={i}>
              <line x1={padding.left} y1={y} x2={padding.left + innerW} y2={y} stroke={colors.navy} strokeWidth={1} strokeDasharray={i === 0 ? "none" : "4,4"} opacity={i === 0 ? 0.8 : 0.3} />
              <text x={padding.left - 10} y={y + 4} textAnchor="end" fill={colors.grayMid} fontSize={12} fontFamily="'Rubik', sans-serif" fontWeight={400}>
                {val >= 1000 ? `${(val / 1000).toFixed(val >= 10000 ? 0 : 1)}k` : val}
              </text>
            </g>
          );
        })}

        {/* Bars */}
        {data.map((d, i) => {
          const barH = (d.value / niceMax) * innerH;
          const x = padding.left + i * barSpacing + (barSpacing - barW) / 2;
          const y = padding.top + innerH - barH;
          const isHovered = hovered === i;

          return (
            <g key={i} onMouseEnter={() => setHovered(i)} onMouseLeave={() => setHovered(null)} style={{ cursor: "default" }}>
              {/* Bar */}
              <rect x={x} y={y} width={barW} height={barH} fill={`url(#vbar-${i}-v)`} opacity={isHovered ? 1 : 0.9} style={{ transition: "opacity 0.15s ease" }} />

              {/* Highlight edge (left) */}
              <rect x={x} y={y} width={2} height={barH} fill="rgba(255,255,255,0.15)" />

              {/* Value label */}
              {showValues && (
                <text x={x + barW / 2} y={y - 8} textAnchor="middle" fill={isHovered ? colors.white : colors.grayLight} fontSize={13} fontFamily="'Rubik', sans-serif" fontWeight={500} opacity={isHovered ? 1 : 0.85}>
                  {d.value >= 1000 ? `${(d.value / 1000).toFixed(1)}k` : d.value}
                </text>
              )}

              {/* X-axis label */}
              <text x={x + barW / 2} y={padding.top + innerH + 20} textAnchor="middle" fill={colors.grayMid} fontSize={12} fontFamily="'Rubik', sans-serif" fontWeight={400}>
                {d.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

// ─── HORIZONTAL BAR CHART ──────────────────────────
const HorizontalBarChart = ({ data, title, subtitle, barHeight = 28, showValues = true }) => {
  const [hovered, setHovered] = useState(null);
  const maxVal = Math.max(...data.map((d) => d.value));
  const padding = { top: 10, right: 70, bottom: 10, left: 100 };
  const chartW = 560;
  const rowH = barHeight + 16;
  const chartH = padding.top + data.length * rowH + padding.bottom;
  const innerW = chartW - padding.left - padding.right;

  const niceMax = Math.ceil(maxVal / Math.pow(10, Math.floor(Math.log10(maxVal)))) * Math.pow(10, Math.floor(Math.log10(maxVal)));

  return (
    <div style={{ background: colors.cardDark, padding: "24px", marginBottom: 24 }}>
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ color: colors.grayLight, fontSize: 20, fontWeight: 300, margin: 0, fontFamily: "'Rubik', sans-serif" }}>{title}</h3>
        {subtitle && <p style={{ color: colors.grayMid, fontSize: 14, margin: "4px 0 0", fontFamily: "'Rubik', sans-serif", fontWeight: 400 }}>{subtitle}</p>}
      </div>
      <svg width={chartW} height={chartH} style={{ overflow: "visible" }}>
        <defs>
          {data.map((d, i) => (
            <GradientDefs key={i} id={`hbar-${i}`} baseColor={d.color || colors.blue} />
          ))}
        </defs>

        {/* Vertical grid lines */}
        {Array.from({ length: 5 }).map((_, i) => {
          const x = padding.left + ((i + 1) / 5) * innerW;
          return <line key={i} x1={x} y1={padding.top} x2={x} y2={chartH - padding.bottom} stroke={colors.navy} strokeWidth={1} strokeDasharray="4,4" opacity={0.3} />;
        })}

        {/* Bars */}
        {data.map((d, i) => {
          const barW = (d.value / niceMax) * innerW;
          const y = padding.top + i * rowH + (rowH - barHeight) / 2;
          const isHovered = hovered === i;

          return (
            <g key={i} onMouseEnter={() => setHovered(i)} onMouseLeave={() => setHovered(null)} style={{ cursor: "default" }}>
              {/* Label */}
              <text x={padding.left - 12} y={y + barHeight / 2 + 4} textAnchor="end" fill={colors.grayLight} fontSize={13} fontFamily="'Rubik', sans-serif" fontWeight={400}>
                {d.label}
              </text>

              {/* Bar */}
              <rect x={padding.left} y={y} width={barW} height={barHeight} fill={`url(#hbar-${i}-h)`} opacity={isHovered ? 1 : 0.9} style={{ transition: "opacity 0.15s ease" }} />

              {/* Top highlight edge */}
              <rect x={padding.left} y={y} width={barW} height={2} fill="rgba(255,255,255,0.12)" />

              {/* Value */}
              {showValues && (
                <text x={padding.left + barW + 10} y={y + barHeight / 2 + 5} textAnchor="start" fill={isHovered ? colors.white : colors.grayLight} fontSize={13} fontFamily="'Rubik', sans-serif" fontWeight={500}>
                  {d.value >= 1000 ? `${(d.value / 1000).toFixed(1)}k` : d.value}
                </text>
              )}
            </g>
          );
        })}

        {/* Baseline */}
        <line x1={padding.left} y1={padding.top} x2={padding.left} y2={chartH - padding.bottom} stroke={colors.navy} strokeWidth={1} opacity={0.6} />
      </svg>
    </div>
  );
};

// ─── STACKED HORIZONTAL BAR ────────────────────────
const StackedHorizontalBar = ({ data, title, subtitle, series, barHeight = 28 }) => {
  const [hovered, setHovered] = useState(null);
  const maxTotal = Math.max(...data.map((d) => series.reduce((sum, s) => sum + (d[s.key] || 0), 0)));
  const padding = { top: 10, right: 20, bottom: 40, left: 100 };
  const chartW = 560;
  const rowH = barHeight + 16;
  const chartH = padding.top + data.length * rowH + padding.bottom;
  const innerW = chartW - padding.left - padding.right;

  return (
    <div style={{ background: colors.cardDark, padding: "24px", marginBottom: 24 }}>
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ color: colors.grayLight, fontSize: 20, fontWeight: 300, margin: 0, fontFamily: "'Rubik', sans-serif" }}>{title}</h3>
        {subtitle && <p style={{ color: colors.grayMid, fontSize: 14, margin: "4px 0 0", fontFamily: "'Rubik', sans-serif", fontWeight: 400 }}>{subtitle}</p>}
      </div>
      <svg width={chartW} height={chartH} style={{ overflow: "visible" }}>
        <defs>
          {series.map((s, si) => (
            <GradientDefs key={si} id={`sbar-${si}`} baseColor={s.color} />
          ))}
        </defs>

        {data.map((d, i) => {
          const y = padding.top + i * rowH + (rowH - barHeight) / 2;
          const total = series.reduce((sum, s) => sum + (d[s.key] || 0), 0);
          let xOffset = padding.left;
          const isHovered = hovered === i;

          return (
            <g key={i} onMouseEnter={() => setHovered(i)} onMouseLeave={() => setHovered(null)}>
              <text x={padding.left - 12} y={y + barHeight / 2 + 4} textAnchor="end" fill={colors.grayLight} fontSize={13} fontFamily="'Rubik', sans-serif" fontWeight={400}>
                {d.label}
              </text>

              {series.map((s, si) => {
                const val = d[s.key] || 0;
                const segW = (val / maxTotal) * innerW;
                const segX = xOffset;
                xOffset += segW;

                return (
                  <g key={si}>
                    <rect x={segX} y={y} width={Math.max(segW, 0)} height={barHeight} fill={`url(#sbar-${si}-h)`} opacity={isHovered ? 1 : 0.9} style={{ transition: "opacity 0.15s ease" }} />
                    {segW > 40 && (
                      <text x={segX + segW / 2} y={y + barHeight / 2 + 4} textAnchor="middle" fill="rgba(255,255,255,0.9)" fontSize={11} fontFamily="'Rubik', sans-serif" fontWeight={500}>
                        {val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val}
                      </text>
                    )}
                    {/* Top highlight */}
                    <rect x={segX} y={y} width={Math.max(segW, 0)} height={1.5} fill="rgba(255,255,255,0.1)" />
                  </g>
                );
              })}

              {/* Total label */}
              <text x={xOffset + 10} y={y + barHeight / 2 + 4} textAnchor="start" fill={colors.grayMid} fontSize={12} fontFamily="'Rubik', sans-serif" fontWeight={400}>
                {total >= 1000 ? `${(total / 1000).toFixed(1)}k` : total}
              </text>
            </g>
          );
        })}

        {/* Baseline */}
        <line x1={padding.left} y1={padding.top} x2={padding.left} y2={chartH - padding.bottom} stroke={colors.navy} strokeWidth={1} opacity={0.6} />

        {/* Legend */}
        {series.map((s, i) => {
          const legendX = padding.left + i * 140;
          const legendY = chartH - 10;
          return (
            <g key={i}>
              <rect x={legendX} y={legendY - 8} width={12} height={12} fill={s.color} />
              <text x={legendX + 18} y={legendY + 3} fill={colors.grayMid} fontSize={12} fontFamily="'Rubik', sans-serif" fontWeight={400}>
                {s.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

// ─── GROUPED VERTICAL BAR ──────────────────────────
const GroupedVerticalBar = ({ data, title, subtitle, series, height = 300 }) => {
  const [hovered, setHovered] = useState(null);
  const allVals = data.flatMap((d) => series.map((s) => d[s.key] || 0));
  const maxVal = Math.max(...allVals);
  const yTicks = 5;
  const padding = { top: 20, right: 20, bottom: 70, left: 60 };
  const chartW = 560;
  const chartH = height;
  const innerW = chartW - padding.left - padding.right;
  const innerH = chartH - padding.top - padding.bottom;
  const groupW = innerW / data.length;
  const groupPad = 0.25;
  const subBarW = (groupW * (1 - groupPad)) / series.length;

  const niceMax = Math.ceil(maxVal / Math.pow(10, Math.floor(Math.log10(maxVal)))) * Math.pow(10, Math.floor(Math.log10(maxVal)));

  return (
    <div style={{ background: colors.cardDark, padding: "24px", marginBottom: 24 }}>
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ color: colors.grayLight, fontSize: 20, fontWeight: 300, margin: 0, fontFamily: "'Rubik', sans-serif" }}>{title}</h3>
        {subtitle && <p style={{ color: colors.grayMid, fontSize: 14, margin: "4px 0 0", fontFamily: "'Rubik', sans-serif", fontWeight: 400 }}>{subtitle}</p>}
      </div>
      <svg width={chartW} height={chartH} style={{ overflow: "visible" }}>
        <defs>
          {series.map((s, si) => (
            <GradientDefs key={si} id={`gbar-${si}`} baseColor={s.color} />
          ))}
        </defs>

        {/* Grid */}
        {Array.from({ length: yTicks + 1 }).map((_, i) => {
          const y = padding.top + innerH - (i / yTicks) * innerH;
          const val = Math.round((i / yTicks) * niceMax);
          return (
            <g key={i}>
              <line x1={padding.left} y1={y} x2={padding.left + innerW} y2={y} stroke={colors.navy} strokeWidth={1} strokeDasharray={i === 0 ? "none" : "4,4"} opacity={i === 0 ? 0.8 : 0.3} />
              <text x={padding.left - 10} y={y + 4} textAnchor="end" fill={colors.grayMid} fontSize={12} fontFamily="'Rubik', sans-serif" fontWeight={400}>
                {val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}
              </text>
            </g>
          );
        })}

        {/* Grouped bars */}
        {data.map((d, di) => {
          const groupX = padding.left + di * groupW + (groupW * groupPad) / 2;
          return (
            <g key={di}>
              {series.map((s, si) => {
                const val = d[s.key] || 0;
                const barH = (val / niceMax) * innerH;
                const x = groupX + si * subBarW;
                const y = padding.top + innerH - barH;
                const isHov = hovered === `${di}-${si}`;

                return (
                  <g key={si} onMouseEnter={() => setHovered(`${di}-${si}`)} onMouseLeave={() => setHovered(null)}>
                    <rect x={x} y={y} width={subBarW - 2} height={barH} fill={`url(#gbar-${si}-v)`} opacity={isHov ? 1 : 0.9} />
                    <rect x={x} y={y} width={1.5} height={barH} fill="rgba(255,255,255,0.12)" />
                    {barH > 25 && (
                      <text x={x + (subBarW - 2) / 2} y={y - 6} textAnchor="middle" fill={colors.grayLight} fontSize={11} fontFamily="'Rubik', sans-serif" fontWeight={500} opacity={0.85}>
                        {val >= 1000 ? `${(val / 1000).toFixed(1)}k` : val}
                      </text>
                    )}
                  </g>
                );
              })}
              <text x={padding.left + di * groupW + groupW / 2} y={padding.top + innerH + 20} textAnchor="middle" fill={colors.grayMid} fontSize={12} fontFamily="'Rubik', sans-serif" fontWeight={400}>
                {d.label}
              </text>
            </g>
          );
        })}

        {/* Legend */}
        {series.map((s, i) => {
          const legendX = padding.left + i * 140;
          const legendY = chartH - 8;
          return (
            <g key={i}>
              <rect x={legendX} y={legendY - 8} width={12} height={12} fill={s.color} />
              <text x={legendX + 18} y={legendY + 3} fill={colors.grayMid} fontSize={12} fontFamily="'Rubik', sans-serif" fontWeight={400}>
                {s.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

// ─── GUIDELINES PANEL ──────────────────────────────
const GuidelinePanel = () => (
  <div style={{ background: colors.navy, padding: "24px", marginBottom: 24, borderLeft: `3px solid ${colors.blue}` }}>
    <h3 style={{ color: colors.blueLight, fontSize: 16, fontWeight: 300, margin: "0 0 16px", fontFamily: "'Rubik', sans-serif", letterSpacing: "0.05em", textTransform: "uppercase" }}>
      Chart Standards
    </h3>
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
      {[
        { title: "Always include", items: ["Value labels on every bar", "Dashed grid lines (opacity 0.3)", "Rubik font, Light 300 headings", "Subtitle with context", "Hover states for interactivity"] },
        { title: "Never do", items: ["Flat solid fills (use subtle gradient)", "Missing value labels", "Overlapping axis text", "Rounded corners on bars", "Colors outside brand palette"] },
        { title: "Gradient formula", items: ["Vertical: lighten +30 top → darken -20 bottom", "Horizontal: darken -20 left → lighten +30 right", "Left/top highlight edge: rgba(255,255,255,0.12)", "Base opacity: 0.9, hover: 1.0"] },
        { title: "Color priority", items: ["1. A10 Blue #0057B7 (primary)", "2. Sky Blue #529EEC (secondary)", "3. Green #00B140 (success)", "4. Orange #E35205 (warning)", "5. Red #EF3340 (danger/error)"] },
      ].map((section, i) => (
        <div key={i}>
          <h4 style={{ color: colors.grayLight, fontSize: 13, fontWeight: 500, margin: "0 0 8px", fontFamily: "'Rubik', sans-serif" }}>{section.title}</h4>
          {section.items.map((item, j) => (
            <div key={j} style={{ color: colors.grayMid, fontSize: 12, fontFamily: "'Rubik', sans-serif", fontWeight: 400, padding: "2px 0", lineHeight: 1.5 }}>
              {item}
            </div>
          ))}
        </div>
      ))}
    </div>
  </div>
);

// ─── MAIN COMPONENT ────────────────────────────────
export default function A10ChartReference() {
  return (
    <div style={{ background: colors.navyDark, minHeight: "100vh", padding: "32px", fontFamily: "'Rubik', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
          <div style={{ width: 4, height: 32, background: colors.blue }} />
          <h1 style={{ color: colors.white, fontSize: 28, fontWeight: 300, margin: 0, fontFamily: "'Rubik', sans-serif" }}>
            Chart Style Reference
          </h1>
        </div>
        <p style={{ color: colors.grayMid, fontSize: 14, margin: "8px 0 0 16px", fontFamily: "'Rubik', sans-serif", fontWeight: 400 }}>
          A10 Networks — Signal Horizon / Edge Protection Platform
        </p>
      </div>

      <GuidelinePanel />

      {/* Vertical Bar */}
      <VerticalBarChart
        title="Response Time Distribution"
        subtitle="Request latency percentile buckets (last 24h)"
        data={[
          { label: "0-50ms", value: 42500, color: colors.green },
          { label: "50-100ms", value: 28300, color: colors.blue },
          { label: "100-200ms", value: 8200, color: colors.sky },
          { label: "200-500ms", value: 3100, color: colors.orange },
          { label: "500ms-1s", value: 890, color: colors.orange },
          { label: "1s+", value: 210, color: colors.red },
        ]}
      />

      {/* Horizontal Bar */}
      <HorizontalBarChart
        title="Request Methods"
        subtitle="HTTP method distribution across all endpoints"
        data={[
          { label: "GET", value: 45200, color: colors.blue },
          { label: "POST", value: 18900, color: colors.green },
          { label: "PUT", value: 4300, color: colors.sky },
          { label: "DELETE", value: 1800, color: colors.red },
          { label: "PATCH", value: 920, color: colors.orange },
          { label: "OPTIONS", value: 3400, color: colors.cloudBlue },
        ]}
      />

      {/* Stacked Horizontal - Service Health */}
      <StackedHorizontalBar
        title="Service Health"
        subtitle="Response codes breakdown by service"
        data={[
          { label: "Auth", success: 8200, client: 1200, error: 45 },
          { label: "Users", success: 12500, client: 340, error: 12 },
          { label: "Products", success: 9800, client: 560, error: 8 },
          { label: "Orders", success: 7600, client: 890, error: 23 },
          { label: "Search", success: 5400, client: 1100, error: 67 },
          { label: "Payments", success: 3200, client: 180, error: 5 },
        ]}
        series={[
          { key: "success", label: "2xx Success", color: colors.blue },
          { key: "client", label: "4xx Client Error", color: colors.orange },
          { key: "error", label: "5xx Server Error", color: colors.red },
        ]}
      />

      {/* Grouped Vertical */}
      <GroupedVerticalBar
        title="Traffic Comparison"
        subtitle="Allowed vs blocked requests by hour"
        data={[
          { label: "00:00", allowed: 2800, blocked: 120 },
          { label: "04:00", allowed: 1200, blocked: 45 },
          { label: "08:00", allowed: 4500, blocked: 230 },
          { label: "12:00", allowed: 5200, blocked: 310 },
          { label: "16:00", allowed: 4800, blocked: 280 },
          { label: "20:00", allowed: 3600, blocked: 190 },
        ]}
        series={[
          { key: "allowed", label: "Allowed", color: colors.blue },
          { key: "blocked", label: "Blocked", color: colors.red },
        ]}
      />

      {/* Color Swatch Reference */}
      <div style={{ background: colors.cardDark, padding: "24px" }}>
        <h3 style={{ color: colors.grayLight, fontSize: 20, fontWeight: 300, margin: "0 0 16px", fontFamily: "'Rubik', sans-serif" }}>Data Series Palette</h3>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          {Object.entries(seriesColors).map(([name, color]) => (
            <div key={name} style={{ display: "flex", alignItems: "center", gap: 8, background: colors.navy, padding: "8px 14px" }}>
              <div style={{ width: 16, height: 16, background: color }} />
              <div>
                <div style={{ color: colors.grayLight, fontSize: 12, fontFamily: "'Rubik', sans-serif", fontWeight: 500, textTransform: "capitalize" }}>{name}</div>
                <div style={{ color: colors.grayMid, fontSize: 11, fontFamily: "'Rubik', sans-serif", fontWeight: 400 }}>{color}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
