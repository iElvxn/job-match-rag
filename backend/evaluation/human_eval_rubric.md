# Human Evaluation Rubric

## Overview

Evaluate system outputs **blindly** — you should NOT know which retrieval/prompting condition produced each output. Each evaluator rates the same set of outputs independently.

## Rating Scale: 1–5

| Score | Meaning |
|-------|---------|
| 1 | Very poor — unusable, mostly wrong or irrelevant |
| 2 | Poor — significant issues, only partially relevant |
| 3 | Acceptable — some useful information, some issues |
| 4 | Good — mostly accurate and useful, minor issues |
| 5 | Excellent — highly accurate, well-grounded, actionable |

## Evaluation Criteria

### 1. Job Relevance
> Are the matched jobs actually relevant to the candidate's resume?

- 5: All matched jobs are highly relevant to the resume's skills and experience
- 3: Some jobs are relevant, others are questionable
- 1: Most matched jobs are irrelevant to the resume

### 2. Skill Match Accuracy
> Are the identified skill matches between resume and jobs correct?

- 5: All skill matches are accurate, no false matches
- 3: Most matches are correct, a few errors
- 1: Many incorrect or fabricated skill matches

### 3. Skill Gap Accuracy
> Are the identified skill gaps real and meaningful?

- 5: All gaps are genuine (skills actually required by jobs, genuinely missing from resume)
- 3: Some gaps are valid, others are wrong or trivial
- 1: Most gaps are incorrect or hallucinated

### 4. Evidence Quality
> Are the quoted evidence spans accurate and verifiable?

- 5: All quotes are exact, traceable to the source text
- 3: Some quotes are accurate, others seem paraphrased or questionable
- 1: Evidence appears fabricated or unverifiable

### 5. Usefulness
> Would this output be genuinely useful to a job seeker?

- 5: Highly actionable — I would use this to guide my job search
- 3: Somewhat useful — provides some direction but needs verification
- 1: Not useful — too vague, wrong, or unhelpful

### 6. Trustworthiness
> Do you trust the analysis and insights provided?

- 5: Fully trust — claims are well-grounded with clear evidence
- 3: Partial trust — some claims seem grounded, others unsupported
- 1: No trust — output seems unreliable or hallucinated

## Procedure

1. **Sample size:** Rate at least 15 system outputs per evaluator
2. **Blind evaluation:** Each output is labeled with a random ID only
3. **Independent scoring:** Do NOT discuss scores with other evaluators until all ratings are submitted
4. **Record in spreadsheet:** One row per output, columns for each criterion (1–5)

## Inter-Annotator Agreement

After all ratings are collected, compute **Cohen's Kappa** between each pair of evaluators to measure agreement. Report the average Kappa score.

| Kappa Range | Interpretation |
|-------------|----------------|
| 0.81–1.00 | Almost perfect agreement |
| 0.61–0.80 | Substantial agreement |
| 0.41–0.60 | Moderate agreement |
| 0.21–0.40 | Fair agreement |
| 0.00–0.20 | Slight agreement |

## Output Format

Save results as a CSV with columns:

```
output_id, evaluator, job_relevance, skill_match, skill_gap, evidence_quality, usefulness, trustworthiness
```
