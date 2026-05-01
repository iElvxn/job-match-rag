"use client";

import { AnalysisResult } from "@/types";
import JobCard from "./JobCard";
import MarketIntel from "./MarketIntel";
import SkillGap from "./SkillGap";
import Recommendations from "./Recommendations";

interface Props {
  result: AnalysisResult;
  onReset: () => void;
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h2
      style={{
        fontFamily: "var(--font-bebas)",
        fontSize: "clamp(2.8rem, 5vw, 5.5rem)",
        color: "#F0EDE5",
        lineHeight: 0.9,
        letterSpacing: "-0.01em",
        marginBottom: "28px",
      }}
    >
      {children}
    </h2>
  );
}

export default function ResultsSection({ result, onReset }: Props) {
  const { matches, skill_data, market_intel, analysis } = result;
  // Drive cards from LLM-validated matches only — raw retrieval chunks may include
  // jobs the LLM excluded as irrelevant, producing empty cards with 0% overlap.
  const rawEnriched = analysis.matches
    .map((analysisData) => {
      const retrieval = matches.find((m) => m.metadata.job_id === analysisData.job_id);
      if (!retrieval) return null;
      return {
        ...retrieval,
        rrf_score: analysisData.rrf_score ?? retrieval.score,
        skill_overlap: analysisData.skill_overlap ?? 0,
        description: analysisData.description,
        analysisData,
      };
    })
    .filter((m): m is NonNullable<typeof m> => m !== null);

  const rrfScores = rawEnriched.map((m) => m.rrf_score);
  const maxRrf = Math.max(...rrfScores);
  const minRrf = Math.min(...rrfScores);
  const rrfRange = maxRrf - minRrf || 1;

  // Normalize to [0.30, 0.95] so scores are meaningful relative to each other
  const enriched = rawEnriched.map((m) => ({
    ...m,
    rrf_score: 0.30 + 0.65 * ((m.rrf_score - minRrf) / rrfRange),
  }));

  const topMatches = enriched;

  const tickerSkills = [...skill_data.resume_skills, ...skill_data.resume_skills];

  const stats = [
    { label: "Matches", value: topMatches.length },
    { label: "Skills", value: skill_data.resume_skills.length },
    { label: "Gaps", value: skill_data.gaps.length },
    { label: "Jobs Indexed", value: market_intel.total_jobs },
  ];

  return (
    <div style={{ minHeight: "100dvh", background: "#0A0A0A" }}>
      {/* Sticky header */}
      <header
        style={{
          position: "sticky",
          top: 0,
          zIndex: 50,
          background: "rgba(10,10,10,0.9)",
          backdropFilter: "blur(16px)",
          WebkitBackdropFilter: "blur(16px)",
          borderBottom: "1px solid #191919",
          padding: "14px 48px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "24px",
        }}
      >
        <button
          className="reset-btn"
          onClick={onReset}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "7px",
            background: "none",
            borderRadius: "8px",
            padding: "8px 14px",
            color: "#888882",
            fontSize: "0.82rem",
            cursor: "pointer",
            fontFamily: "inherit",
            flexShrink: 0,
          }}
        >
          ← New Analysis
        </button>

        {/* Stats */}
        <div style={{ display: "flex", gap: "32px", alignItems: "center" }}>
          {stats.map(({ label, value }) => (
            <div key={label} style={{ textAlign: "center" }}>
              <div
                style={{
                  fontFamily: "var(--font-bebas)",
                  fontSize: "1.9rem",
                  color: "#CCFF00",
                  lineHeight: 1,
                }}
              >
                {value}
              </div>
              <div
                style={{
                  fontSize: "0.6rem",
                  color: "#484844",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  marginTop: "1px",
                }}
              >
                {label}
              </div>
            </div>
          ))}
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            flexShrink: 0,
          }}
        >
          <div
            style={{
              width: 7,
              height: 7,
              background: "#CCFF00",
              borderRadius: "50%",
              boxShadow: "0 0 8px #CCFF00",
              animation: "glow 2s ease-in-out infinite",
            }}
          />
          <span
            style={{
              fontFamily: "var(--font-bebas)",
              fontSize: "0.9rem",
              letterSpacing: "0.14em",
              color: "#484844",
            }}
          >
            JOBMATCH
          </span>
        </div>
      </header>

      {/* Skill ticker */}
      {skill_data.resume_skills.length > 0 && (
        <div
          style={{
            background: "#CCFF00",
            overflow: "hidden",
            padding: "11px 0",
          }}
        >
          <div className="ticker-track" style={{ gap: "0" }}>
            {tickerSkills.map((skill, i) => (
              <span
                key={i}
                style={{
                  fontFamily: "var(--font-bebas)",
                  fontSize: "0.95rem",
                  letterSpacing: "0.11em",
                  color: "#0A0A0A",
                  whiteSpace: "nowrap",
                  padding: "0 28px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "28px",
                }}
              >
                {skill.toUpperCase()}
                <span style={{ fontSize: "0.45rem", opacity: 0.35 }}>◆</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Main content */}
      <div
        style={{
          maxWidth: "1440px",
          margin: "0 auto",
          padding: "72px 48px 96px",
        }}
      >
        {/* Top Matches */}
        <section style={{ marginBottom: "88px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "space-between",
              marginBottom: "28px",
            }}
          >
            <SectionLabel>TOP MATCHES</SectionLabel>
            <span
              style={{
                fontSize: "0.7rem",
                color: "#484844",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                marginBottom: "8px",
              }}
            >
              {topMatches.length} jobs · ranked by relevance
            </span>
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(560px, 1fr))",
              gap: "14px",
            }}
          >
            {enriched.map((m, i) => (
              <JobCard key={m.chunk_id} match={m} index={i} />
            ))}
          </div>
        </section>

        {/* Market Intelligence */}
        <section style={{ marginBottom: "88px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "flex-end",
              justifyContent: "space-between",
              marginBottom: "28px",
            }}
          >
            <SectionLabel>MARKET INTEL</SectionLabel>
            <span
              style={{
                fontSize: "0.7rem",
                color: "#484844",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                marginBottom: "8px",
              }}
            >
              Top skills across {market_intel.total_jobs} matched jobs
            </span>
          </div>
          <MarketIntel data={market_intel} />
        </section>

        {/* Skill Analysis */}
        <section style={{ marginBottom: "88px" }}>
          <SectionLabel>SKILL ANALYSIS</SectionLabel>
          <SkillGap
            skillData={skill_data}
            skillGaps={analysis.skill_gaps}
          />
        </section>

        {/* Recommendations */}
        {analysis.recommendations.length > 0 && (
          <section>
            <div
              style={{
                display: "flex",
                alignItems: "flex-end",
                justifyContent: "space-between",
                marginBottom: "28px",
              }}
            >
              <SectionLabel>RECOMMENDATIONS</SectionLabel>
              <span
                style={{
                  fontSize: "0.7rem",
                  color: "#484844",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  marginBottom: "8px",
                }}
              >
                Prioritized by market demand
              </span>
            </div>
            <Recommendations items={analysis.recommendations} />
          </section>
        )}
      </div>
    </div>
  );
}
