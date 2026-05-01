"use client";

import { useState } from "react";
import { JobMatch, AnalysisMatch } from "@/types";

interface EnrichedMatch extends JobMatch {
  analysisData?: AnalysisMatch;
}

interface Props {
  match: EnrichedMatch;
  index: number;
}

function scoreColor(rrf: number): string {
  if (rrf >= 0.75) return "#CCFF00";
  if (rrf >= 0.5) return "#FFB800";
  return "#888882";
}

function scoreBg(rrf: number): string {
  if (rrf >= 0.75) return "rgba(204,255,0,0.07)";
  if (rrf >= 0.5) return "rgba(255,184,0,0.07)";
  return "transparent";
}

function scoreLabel(rrf: number): string {
  if (rrf >= 0.75) return "Strong";
  if (rrf >= 0.5) return "Good";
  return "Fair";
}

export default function JobCard({ match, index }: Props) {
  const [expanded, setExpanded] = useState(false);
  const { metadata, rrf_score, skill_overlap, description, analysisData } = match;

  const pct = Math.round(rrf_score * 100);
  const overlap = Math.round(skill_overlap * 100);
  const color = scoreColor(rrf_score);

  return (
    <article
      className="job-card"
      style={{
        background: "#0D0D0D",
        borderRadius: "14px",
        padding: "26px",
        display: "flex",
        flexDirection: "column",
        gap: "18px",
        animationDelay: `${index * 0.05}s`,
      }}
    >
      {/* Header row */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: "16px",
        }}
      >
        {/* Job info */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              fontSize: "0.65rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "#484844",
              marginBottom: "5px",
            }}
          >
            {metadata.company}
          </div>
          <h3
            style={{
              fontSize: "1.05rem",
              fontWeight: 600,
              color: "#F0EDE5",
              lineHeight: 1.3,
              marginBottom: "4px",
            }}
          >
            {metadata.title}
          </h3>
          <div style={{ fontSize: "0.76rem", color: "#484844" }}>
            {metadata.location}
          </div>
        </div>

        {/* Score badge */}
        <div
          style={{
            flexShrink: 0,
            textAlign: "right",
            background: scoreBg(rrf_score),
            borderRadius: "10px",
            padding: "10px 14px",
          }}
        >
          <div
            style={{
              fontFamily: "var(--font-bebas)",
              fontSize: "2.8rem",
              lineHeight: 1,
              color,
            }}
          >
            {pct}
            <span style={{ fontSize: "1.1rem" }}>%</span>
          </div>
          <div
            style={{
              fontSize: "0.58rem",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              color,
              opacity: 0.7,
              marginTop: "1px",
            }}
          >
            {scoreLabel(rrf_score)} Match
          </div>
        </div>
      </div>

      {/* Score bars */}
      <div style={{ display: "flex", gap: "14px" }}>
        {[
          { label: "Relevance", val: pct, color, idx: index * 2 },
          { label: "Skill Overlap", val: overlap, color: "#9B8FFF", idx: index * 2 + 1 },
        ].map(({ label, val, color: c, idx }) => (
          <div key={label} style={{ flex: 1 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: "0.6rem",
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                color: "#484844",
                marginBottom: "5px",
              }}
            >
              <span>{label}</span>
              <span>{val}%</span>
            </div>
            <div
              style={{
                height: "3px",
                background: "#1A1A1A",
                borderRadius: "2px",
                overflow: "hidden",
              }}
            >
              <div
                className="bar-fill"
                style={
                  {
                    "--w": `${val}%`,
                    "--i": idx,
                    height: "100%",
                    background: c,
                    borderRadius: "2px",
                  } as React.CSSProperties
                }
              />
            </div>
          </div>
        ))}
      </div>

      {/* Match reasoning */}
      {analysisData?.match_reasoning && (
        <p
          style={{
            fontSize: "0.845rem",
            color: "#888882",
            lineHeight: 1.7,
          }}
        >
          {analysisData.match_reasoning}
        </p>
      )}

      {/* Evidence citations */}
      {analysisData?.evidence?.job && analysisData.evidence.job.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "7px" }}>
          {analysisData.evidence.job.slice(0, 2).map((ev, i) => (
            <blockquote
              key={i}
              style={{
                paddingLeft: "12px",
                borderLeft: "2px solid rgba(155,143,255,0.45)",
                fontSize: "0.78rem",
                color: "#555550",
                fontStyle: "italic",
                lineHeight: 1.6,
                margin: 0,
              }}
            >
              "{ev}"
            </blockquote>
          ))}
        </div>
      )}

      {/* Missing alignment */}
      {analysisData?.missing_alignment && analysisData.missing_alignment.length > 0 && (
        <div>
          <div
            style={{
              fontSize: "0.58rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "#484844",
              marginBottom: "7px",
            }}
          >
            Gaps
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
            {analysisData.missing_alignment.slice(0, 5).map((m, i) => (
              <span
                key={i}
                style={{
                  padding: "3px 10px",
                  background: "rgba(255,77,15,0.07)",
                  border: "1px solid rgba(255,77,15,0.18)",
                  borderRadius: "999px",
                  fontSize: "0.7rem",
                  color: "#FF6A40",
                }}
              >
                {m.job_requirement}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Description expander */}
      {description && (
        <div>
          <button
            className="expander-btn"
            onClick={() => setExpanded((v) => !v)}
            style={{
              background: "none",
              borderRadius: "6px",
              padding: "7px 12px",
              color: "#555550",
              fontSize: "0.74rem",
              cursor: "pointer",
              fontFamily: "inherit",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <span
              style={{
                display: "inline-block",
                transition: "transform 0.2s",
                transform: expanded ? "rotate(90deg)" : "none",
                fontSize: "0.55rem",
              }}
            >
              ▶
            </span>
            {expanded ? "Collapse description" : "View full description"}
          </button>
          {expanded && (
            <div
              style={{
                marginTop: "10px",
                padding: "14px",
                background: "#080808",
                borderRadius: "8px",
                fontSize: "0.77rem",
                color: "#555550",
                lineHeight: 1.75,
                maxHeight: "280px",
                overflowY: "auto",
                whiteSpace: "pre-wrap",
              }}
            >
              {description}
            </div>
          )}
        </div>
      )}
    </article>
  );
}
