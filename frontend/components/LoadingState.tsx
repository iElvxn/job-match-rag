"use client";

import { useEffect, useState } from "react";

const STEPS = [
  { label: "Parsing resume text", detail: "Extracting and cleaning PDF content" },
  { label: "Running hybrid retrieval", detail: "BM25 + dense vector search via Pinecone" },
  { label: "Computing skill overlap", detail: "Matching skills with fuzzy detection" },
  { label: "Generating AI analysis", detail: "GPT-4 grounding evidence and reasoning" },
  { label: "Preparing your results", detail: "Ranking and enriching job matches" },
];

export default function LoadingState() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const id = setInterval(
      () => setStep((s) => Math.min(s + 1, STEPS.length - 1)),
      2400,
    );
    return () => clearInterval(id);
  }, []);

  return (
    <div
      style={{
        minHeight: "100dvh",
        background: "#0A0A0A",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "56px",
        padding: "40px",
        position: "relative",
      }}
    >
      {/* Ambient glow */}
      <div
        aria-hidden
        style={{
          position: "fixed",
          top: "20%",
          left: "50%",
          transform: "translateX(-50%)",
          width: "500px",
          height: "500px",
          background:
            "radial-gradient(circle, rgba(204,255,0,0.05) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      {/* Spinner + wordmark */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "20px" }}>
        <div style={{ position: "relative", width: "56px", height: "56px" }}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              border: "1.5px solid #1C1C1C",
              borderTop: "1.5px solid #CCFF00",
              borderRadius: "50%",
              animation: "spin 0.9s linear infinite",
            }}
          />
          <div
            style={{
              position: "absolute",
              inset: "8px",
              border: "1px solid #181818",
              borderBottom: "1px solid rgba(204,255,0,0.3)",
              borderRadius: "50%",
              animation: "spin 1.4s linear infinite reverse",
            }}
          />
        </div>

        <div
          style={{
            fontFamily: "var(--font-bebas)",
            fontSize: "0.85rem",
            letterSpacing: "0.2em",
            color: "#484844",
          }}
        >
          JOBMATCH
        </div>
      </div>

      {/* Step list */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          minWidth: "340px",
          maxWidth: "420px",
          width: "100%",
        }}
      >
        {STEPS.map((s, i) => {
          const done = i < step;
          const active = i === step;
          return (
            <div
              key={s.label}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "14px",
                opacity: i > step ? 0.18 : 1,
                transition: "opacity 0.4s ease",
              }}
            >
              {/* Dot */}
              <div style={{ paddingTop: "3px", flexShrink: 0 }}>
                {done ? (
                  <div
                    style={{
                      width: "16px",
                      height: "16px",
                      borderRadius: "50%",
                      background: "rgba(204,255,0,0.15)",
                      border: "1px solid rgba(204,255,0,0.4)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "0.6rem",
                      color: "#CCFF00",
                    }}
                  >
                    ✓
                  </div>
                ) : active ? (
                  <div
                    style={{
                      width: "16px",
                      height: "16px",
                      borderRadius: "50%",
                      background: "#CCFF00",
                      boxShadow: "0 0 12px rgba(204,255,0,0.6)",
                      animation: "blink 1.2s ease-in-out infinite",
                    }}
                  />
                ) : (
                  <div
                    style={{
                      width: "16px",
                      height: "16px",
                      borderRadius: "50%",
                      border: "1px solid #242424",
                    }}
                  />
                )}
              </div>

              {/* Text */}
              <div>
                <div
                  style={{
                    fontSize: "0.9rem",
                    color: done ? "#888882" : active ? "#F0EDE5" : "#888882",
                    fontWeight: active ? 500 : 400,
                    transition: "color 0.3s",
                    marginBottom: "2px",
                  }}
                >
                  {s.label}
                </div>
                {active && (
                  <div
                    style={{
                      fontSize: "0.72rem",
                      color: "#484844",
                      letterSpacing: "0.02em",
                    }}
                  >
                    {s.detail}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Progress bar */}
      <div
        style={{
          width: "280px",
          height: "2px",
          background: "#1A1A1A",
          borderRadius: "1px",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            background: "#CCFF00",
            borderRadius: "1px",
            width: `${((step + 1) / STEPS.length) * 100}%`,
            transition: "width 0.6s cubic-bezier(0.4, 0, 0.2, 1)",
            boxShadow: "0 0 8px rgba(204,255,0,0.5)",
          }}
        />
      </div>
    </div>
  );
}
