"use client";

import { useState } from "react";
import { AnalysisResult } from "@/types";
import HeroSection from "@/components/HeroSection";
import LoadingState from "@/components/LoadingState";
import ResultsSection from "@/components/ResultsSection";

type AppState = "idle" | "loading" | "results";

export default function Home() {
  const [appState, setAppState] = useState<AppState>("idle");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (file: File) => {
    setAppState("loading");
    setError(null);

    const body = new FormData();
    body.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { detail?: string }).detail ?? `Request failed (${res.status})`);
      }

      const data: AnalysisResult = await res.json();
      setResult(data);
      setAppState("results");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed. Please try again.");
      setAppState("idle");
    }
  };

  const handleReset = () => {
    setAppState("idle");
    setResult(null);
    setError(null);
  };

  return (
    <main style={{ minHeight: "100dvh", background: "#0A0A0A" }}>
      {appState === "idle" && (
        <HeroSection onAnalyze={handleAnalyze} error={error} />
      )}
      {appState === "loading" && <LoadingState />}
      {appState === "results" && result && (
        <ResultsSection result={result} onReset={handleReset} />
      )}
    </main>
  );
}
