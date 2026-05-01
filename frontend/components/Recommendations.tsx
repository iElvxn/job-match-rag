"use client";

import { RecommendationItem } from "@/types";

interface Props {
  items: RecommendationItem[];
}

export default function Recommendations({ items }: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
      {items.map((rec, i) => (
        <div
          key={rec.skill}
          className="job-card"
          style={{
            background: "#0D0D0D",
            borderRadius: "14px",
            padding: "26px 28px",
            display: "grid",
            gridTemplateColumns: "72px 1fr",
            gap: "24px",
            alignItems: "flex-start",
          }}
        >
          {/* Index number */}
          <div
            style={{
              fontFamily: "var(--font-bebas)",
              fontSize: "4rem",
              lineHeight: 1,
              color: "#1C1C1C",
              userSelect: "none",
              textAlign: "center",
              paddingTop: "4px",
            }}
          >
            {String(i + 1).padStart(2, "0")}
          </div>

          {/* Content */}
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {/* Skill name + frequency badge */}
            <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
              <span
                style={{
                  fontFamily: "var(--font-bebas)",
                  fontSize: "1.45rem",
                  letterSpacing: "0.06em",
                  color: "#F0EDE5",
                  textTransform: "uppercase",
                }}
              >
                {rec.skill}
              </span>
              <span
                style={{
                  padding: "3px 10px",
                  background: "rgba(255,184,0,0.1)",
                  border: "1px solid rgba(255,184,0,0.22)",
                  borderRadius: "999px",
                  fontSize: "0.66rem",
                  color: "#FFB800",
                  letterSpacing: "0.06em",
                }}
              >
                {rec.frequency}
              </span>
            </div>

            {/* Reason */}
            <p
              style={{
                fontSize: "0.845rem",
                color: "#555550",
                lineHeight: 1.7,
              }}
            >
              {rec.reason}
            </p>

            {/* Action step */}
            <div
              style={{
                padding: "12px 16px",
                background: "rgba(204,255,0,0.04)",
                borderRadius: "8px",
                borderLeft: "2.5px solid #CCFF00",
                fontSize: "0.82rem",
                color: "#CCFF00",
                lineHeight: 1.55,
              }}
            >
              → {rec.action}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
