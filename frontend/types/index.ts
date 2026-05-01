export interface JobMatch {
  chunk_id: string;
  score: number;
  metadata: {
    job_id: string;
    title: string;
    company: string;
    location: string;
    chunk_type: string;
  };
  rrf_score: number;
  skill_overlap: number;
  description?: string;
}

export interface SkillFrequencyEntry {
  count: number;
  job_ids: string[];
}

export interface MarketIntelData {
  skill_frequency: Record<string, SkillFrequencyEntry>;
  job_skills_map: Record<string, string[]>;
  total_jobs: number;
  market_summary: string[];
}

export interface SkillData {
  resume_skills: string[];
  job_skills: string[];
  gaps: string[];
}

export interface AnalysisMatch {
  job_id: string;
  title: string;
  company: string;
  match_reasoning: string;
  evidence: {
    resume: string[];
    job: string[];
  };
  missing_alignment: Array<{
    job_requirement: string;
    reason: string;
  }>;
  rrf_score?: number;
  skill_overlap?: number;
  description?: string;
}

export interface SkillGapItem {
  skill: string;
  evidence: string[];
  frequency: string;
}

export interface RecommendationItem {
  skill: string;
  frequency: string;
  reason: string;
  action: string;
}

export interface AnalysisData {
  matches: AnalysisMatch[];
  skill_gaps: SkillGapItem[];
  recommendations: RecommendationItem[];
}

export interface AnalysisResult {
  matches: JobMatch[];
  skill_data: SkillData;
  market_intel: MarketIntelData;
  analysis: AnalysisData;
}
