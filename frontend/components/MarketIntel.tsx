"use client";

import { MarketIntelData } from "@/types";

interface Props {
  data: MarketIntelData;
}

const BAR_COLORS = ["#CCFF00", "#B8E800", "#9DD000", "#7EAA00", "#607F00"];
const BAR_DIM_COLOR = "#2A3A00";

export default function MarketIntel({ data }: Props) {
  const { skill_frequency, total_jobs } = data;

  const skills = Object.entries(skill_frequency)
    .sort(([, a], [, b]) => b.count - a.count)
    .slice(0, 15);

  const maxCount = skills[0]?.[1].count ?? 1;

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "2px",
        background: "#141414",
        borderRadius: "14px",
        overflow: "hidden",
        border: "1px solid #1A1A1A",
      }}
    >
      {/* Left: bar chart */}
      <div style={{ background: "#0D0D0D", padding: "32px" }}>
        <div
          style={{
            fontSize: "0.62rem",
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: "#484844",
            marginBottom: "24px",
          }}
        >
          Skill frequency across {total_jobs} jobs
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "13px" }}>
          {skills.slice(0, 10).map(([skill, { count }], i) => {
            const pct = (count / maxCount) * 100;
            const color = i < BAR_COLORS.length ? BAR_COLORS[Math.min(i, BAR_COLORS.length - 1)] : BAR_DIM_COLOR;
            return (
              <div key={skill} style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <div
                  style={{
                    width: "110px",
                    fontSize: "0.78rem",
                    color: "#888882",
                    textTransform: "capitalize",
                    flexShrink: 0,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {skill}
                </div>
                <div
                  style={{
                    flex: 1,
                    height: "5px",
                    background: "#1A1A1A",
                    borderRadius: "3px",
                    overflow: "hidden",
                  }}
                >
                  <div
                    className="bar-fill"
                    style={
                      {
                        "--w": `${pct}%`,
                        "--i": i,
                        height: "100%",
                        background: color,
                        borderRadius: "3px",
                      } as React.CSSProperties
                    }
                  />
                </div>
                <div
                  style={{
                    width: "32px",
                    textAlign: "right",
                    fontFamily: "var(--font-bebas)",
                    fontSize: "0.95rem",
                    color: i === 0 ? "#CCFF00" : "#484844",
                    flexShrink: 0,
                  }}
                >
                  {count}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right: top 5 callout + remainder list */}
      <div style={{ background: "#0A0A0A", padding: "32px" }}>
        <div
          style={{
            fontSize: "0.62rem",
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: "#484844",
            marginBottom: "24px",
          }}
        >
          Top demanded skills
        </div>

        {/* Top 3 big callouts */}
        <div style={{ display: "flex", flexDirection: "column", gap: "14px", marginBottom: "28px" }}>
          {skills.slice(0, 3).map(([skill, { count }], i) => (
            <div
              key={skill}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "14px 16px",
                background: i === 0 ? "rgba(204,255,0,0.06)" : "#111111",
                borderRadius: "10px",
                border: i === 0 ? "1px solid rgba(204,255,0,0.14)" : "1px solid #1A1A1A",
              }}
            >
              <div>
                <div
                  style={{
                    fontFamily: "var(--font-bebas)",
                    fontSize: "1.1rem",
                    letterSpacing: "0.07em",
                    color: i === 0 ? "#CCFF00" : "#888882",
                    textTransform: "capitalize",
                  }}
                >
                  {skill}
                </div>
                <div style={{ fontSize: "0.68rem", color: "#484844" }}>
                  {Math.round((count / total_jobs) * 100)}% of matched jobs
                </div>
              </div>
              <div
                style={{
                  fontFamily: "var(--font-bebas)",
                  fontSize: "2rem",
                  lineHeight: 1,
                  color: i === 0 ? "#CCFF00" : "#333330",
                }}
              >
                {count}
              </div>
            </div>
          ))}
        </div>

        {/* Remaining as chips */}
        <div
          style={{
            fontSize: "0.62rem",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "#484844",
            marginBottom: "10px",
          }}
        >
          Also in demand
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
          {skills.slice(3, 15).map(([skill, { count }]) => (
            <span
              key={skill}
              title={`${count} jobs`}
              style={{
                padding: "4px 10px",
                background: "#111",
                border: "1px solid #1E1E1E",
                borderRadius: "999px",
                fontSize: "0.72rem",
                color: "#888882",
                textTransform: "capitalize",
              }}
            >
              {skill}
              <span style={{ color: "#484844", marginLeft: "5px" }}>{count}</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
