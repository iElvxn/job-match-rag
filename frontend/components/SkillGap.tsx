"use client";

import { SkillData, SkillGapItem } from "@/types";

interface Props {
  skillData: SkillData;
  skillGaps: SkillGapItem[];
}

function Chip({
  label,
  variant,
}: {
  label: string;
  variant: "matched" | "gap";
}) {
  const styles =
    variant === "matched"
      ? {
          background: "rgba(204,255,0,0.07)",
          border: "1px solid rgba(204,255,0,0.18)",
          color: "#CCFF00",
        }
      : {
          background: "rgba(255,77,15,0.07)",
          border: "1px solid rgba(255,77,15,0.18)",
          color: "#FF6A40",
        };

  return (
    <span
      style={{
        ...styles,
        padding: "4px 12px",
        borderRadius: "999px",
        fontSize: "0.75rem",
        textTransform: "capitalize",
        display: "inline-block",
      }}
    >
      {label}
    </span>
  );
}

export default function SkillGap({ skillData, skillGaps }: Props) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "14px",
      }}
    >
      {/* Your skills panel */}
      <div
        style={{
          background: "#0D0D0D",
          border: "1px solid #1A1A1A",
          borderRadius: "14px",
          padding: "28px",
        }}
      >
        <div style={{ marginBottom: "20px" }}>
          <div
            style={{
              fontFamily: "var(--font-bebas)",
              fontSize: "1.05rem",
              letterSpacing: "0.08em",
              color: "#CCFF00",
              marginBottom: "3px",
            }}
          >
            YOUR SKILLS
          </div>
          <div style={{ fontSize: "0.68rem", color: "#484844" }}>
            {skillData.resume_skills.length} skills detected in your resume
          </div>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "7px" }}>
          {skillData.resume_skills.map((s) => (
            <Chip key={s} label={s} variant="matched" />
          ))}
        </div>
      </div>

      {/* Skill gaps panel */}
      <div
        style={{
          background: "#0D0D0D",
          border: "1px solid #1A1A1A",
          borderRadius: "14px",
          padding: "28px",
        }}
      >
        <div style={{ marginBottom: "20px" }}>
          <div
            style={{
              fontFamily: "var(--font-bebas)",
              fontSize: "1.05rem",
              letterSpacing: "0.08em",
              color: "#FF4D0F",
              marginBottom: "3px",
            }}
          >
            SKILL GAPS
          </div>
          <div style={{ fontSize: "0.68rem", color: "#484844" }}>
            {skillData.gaps.length} skills missing from your resume
          </div>
        </div>

        {skillGaps.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {skillGaps.slice(0, 12).map((gap) => (
              <div
                key={gap.skill}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "10px",
                }}
              >
                <Chip label={gap.skill} variant="gap" />
                <span
                  style={{
                    fontSize: "0.68rem",
                    color: "#484844",
                    flexShrink: 0,
                    letterSpacing: "0.02em",
                  }}
                >
                  {gap.frequency}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "7px" }}>
            {skillData.gaps.slice(0, 12).map((s) => (
              <Chip key={s} label={s} variant="gap" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
