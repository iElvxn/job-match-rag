"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";

interface Props {
  onAnalyze: (file: File) => void;
  error: string | null;
}

const TAGS = [
  "Hybrid BM25 + Dense Retrieval",
  "GPT-4 Powered Analysis",
  "Real LinkedIn Job Data",
  "Skill Gap Identification",
  "Market Intelligence",
  "Evidence-Grounded Matches",
];

export default function HeroSection({ onAnalyze, error }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [over, setOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setOver(false);
    const f = e.dataTransfer.files[0];
    if (f?.name.toLowerCase().endsWith(".pdf")) setFile(f);
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) setFile(f);
  };

  return (
    <div
      style={{
        minHeight: "100dvh",
        display: "flex",
        flexDirection: "column",
        background: "#0A0A0A",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Dot grid background */}
      <div
        aria-hidden
        style={{
          position: "fixed",
          inset: 0,
          backgroundImage:
            "radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* Ambient glow */}
      <div
        aria-hidden
        style={{
          position: "fixed",
          top: "-20%",
          left: "-10%",
          width: "60vw",
          height: "60vw",
          background:
            "radial-gradient(circle, rgba(204,255,0,0.04) 0%, transparent 70%)",
          pointerEvents: "none",
          zIndex: 0,
        }}
      />

      {/* Nav */}
      <nav
        style={{
          position: "relative",
          zIndex: 10,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "24px 48px",
          borderBottom: "1px solid #1A1A1A",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 9,
              height: 9,
              background: "#CCFF00",
              borderRadius: "50%",
              animation: "glow 2s ease-in-out infinite",
            }}
          />
          <span
            style={{
              fontFamily: "var(--font-bebas)",
              fontSize: "1.05rem",
              letterSpacing: "0.14em",
              color: "#F0EDE5",
            }}
          >
            JOBMATCH
          </span>
        </div>
        <span
          style={{
            fontSize: "0.68rem",
            letterSpacing: "0.14em",
            color: "#484844",
            textTransform: "uppercase",
          }}
        >
          RAG-Powered Career Intelligence
        </span>
      </nav>

      {/* Hero body */}
      <div
        style={{
          position: "relative",
          zIndex: 10,
          flex: 1,
          display: "grid",
          gridTemplateColumns: "1.1fr 0.9fr",
          gap: "48px",
          padding: "72px 48px 60px",
          maxWidth: "1440px",
          margin: "0 auto",
          width: "100%",
          alignItems: "center",
        }}
      >
        {/* Left: display text */}
        <div className="fade-up" style={{ "--d": "0" } as React.CSSProperties}>
          <p
            style={{
              fontSize: "0.7rem",
              letterSpacing: "0.2em",
              color: "#CCFF00",
              textTransform: "uppercase",
              marginBottom: "24px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <span
              style={{
                display: "inline-block",
                width: "24px",
                height: "1px",
                background: "#CCFF00",
              }}
            />
            Career Intelligence Platform
          </p>

          <h1 style={{ lineHeight: 0.88, marginBottom: "36px" }}>
            <span
              style={{
                display: "block",
                fontFamily: "var(--font-bebas)",
                fontSize: "clamp(5.5rem, 13vw, 15rem)",
                color: "#CCFF00",
                letterSpacing: "-0.01em",
              }}
            >
              CAREER
            </span>
            <span
              style={{
                display: "block",
                fontFamily: "var(--font-bebas)",
                fontSize: "clamp(5.5rem, 13vw, 15rem)",
                color: "#F0EDE5",
                letterSpacing: "-0.01em",
              }}
            >
              INTEL
            </span>
          </h1>

          <p
            style={{
              fontSize: "1rem",
              color: "#888882",
              lineHeight: 1.7,
              maxWidth: "400px",
            }}
          >
            Upload your resume. We match it against thousands of real job
            listings using hybrid RAG retrieval, then surface exactly where you
            fit — and where you don't.
          </p>
        </div>

        {/* Right: upload card */}
        <div
          className="fade-up"
          style={
            {
              "--d": "2",
              display: "flex",
              flexDirection: "column",
              gap: "14px",
            } as React.CSSProperties
          }
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            style={{ display: "none" }}
            onChange={handleChange}
          />

          <div
            className={`upload-zone${over ? " over" : ""}`}
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setOver(true);
            }}
            onDragLeave={() => setOver(false)}
            onDrop={handleDrop}
            style={{
              padding: "56px 40px",
              textAlign: "center",
              background: "#0D0D0D",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "14px",
            }}
          >
            {/* Icon */}
            <div
              style={{
                width: "52px",
                height: "52px",
                borderRadius: "50%",
                border: `1.5px solid ${file ? "#CCFF00" : "#2E2E2E"}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "1.3rem",
                color: file ? "#CCFF00" : "#484844",
                transition: "all 0.2s",
              }}
            >
              {file ? "✓" : "↑"}
            </div>

            <div>
              <div
                style={{
                  fontFamily: "var(--font-bebas)",
                  fontSize: "1.15rem",
                  letterSpacing: "0.09em",
                  color: file ? "#F0EDE5" : "#888882",
                  marginBottom: "4px",
                }}
              >
                {file ? file.name : "DROP YOUR RESUME"}
              </div>
              <div
                style={{
                  fontSize: "0.72rem",
                  color: "#484844",
                  letterSpacing: "0.06em",
                }}
              >
                {file
                  ? `${(file.size / 1024).toFixed(0)} KB · Click to change`
                  : "PDF ONLY · DRAG & DROP OR CLICK TO BROWSE"}
              </div>
            </div>
          </div>

          {error && (
            <div
              style={{
                padding: "12px 16px",
                background: "rgba(255,77,15,0.08)",
                border: "1px solid rgba(255,77,15,0.25)",
                borderRadius: "10px",
                color: "#FF6A40",
                fontSize: "0.84rem",
                lineHeight: 1.5,
              }}
            >
              {error}
            </div>
          )}

          <button
            onClick={() => file && onAnalyze(file)}
            disabled={!file}
            style={{
              padding: "18px 32px",
              background: file ? "#CCFF00" : "#141414",
              color: file ? "#0A0A0A" : "#484844",
              border: "none",
              borderRadius: "12px",
              fontFamily: "var(--font-bebas)",
              fontSize: "1.25rem",
              letterSpacing: "0.08em",
              cursor: file ? "pointer" : "not-allowed",
              transition: "background 0.2s, color 0.2s, transform 0.15s",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "10px",
            }}
            onMouseEnter={(e) => {
              if (file)
                (e.currentTarget as HTMLButtonElement).style.transform =
                  "scale(1.015)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.transform = "scale(1)";
            }}
          >
            ANALYZE MY RESUME
            <span style={{ fontSize: "0.9rem", opacity: 0.7 }}>↗</span>
          </button>

          <p
            style={{
              fontSize: "0.7rem",
              color: "#484844",
              textAlign: "center",
              letterSpacing: "0.05em",
            }}
          >
            Analysis takes ~15 seconds · Rate limited to 3 requests/min
          </p>
        </div>
      </div>

      {/* Bottom strip */}
      <div
        style={{
          position: "relative",
          zIndex: 10,
          borderTop: "1px solid #151515",
          padding: "14px 48px",
          display: "flex",
          gap: "0",
          flexWrap: "wrap",
        }}
      >
        {TAGS.map((tag, i) => (
          <span
            key={tag}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              fontSize: "0.67rem",
              letterSpacing: "0.12em",
              color: "#383834",
              textTransform: "uppercase",
              padding: "2px 20px 2px 0",
              whiteSpace: "nowrap",
            }}
          >
            {i > 0 && (
              <span
                style={{
                  color: "#CCFF00",
                  fontSize: "0.4rem",
                  marginRight: "12px",
                }}
              >
                ◆
              </span>
            )}
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}
