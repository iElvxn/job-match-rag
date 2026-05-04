"""
Generate 8 stress-test resumes designed to expose retrieval failure modes.

Categories:
  1. Sparse resumes (< 80 words) — tests retrieval with thin signal
  2. Vocab-mismatched (k8s, ML, NLP, CV abbreviations) — tests semantic matching
  3. Cross-domain (bioinformatics, fintech) — tests domain ambiguity
  4. Niche stack (Rust/Solidity, embedded/Verilog) — tests dataset coverage
"""
import os
from fpdf import FPDF

OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "backend", "evaluation", "test_resumes"
)

STRESS_RESUMES = [
    # === Sparse resumes (< 80 words) ===
    {
        "name": "sparse_minimal",
        "title": "Software Developer",
        "summary": "Backend developer.",
        "skills": "Python, SQL, Git",
        "experience": [("Developer", "Tech Co", "2022-Present", "Built REST APIs.")],
        "education": "B.S. Computer Science, 2022",
    },
    {
        "name": "sparse_grad",
        "title": "Software Engineer",
        "summary": "Recent graduate.",
        "skills": "Java, Python",
        "experience": [("Intern", "Local Co", "Summer 2024", "Web development.")],
        "education": "B.S. Computer Science, 2024",
    },

    # === Vocab-mismatched resumes (uses abbreviations / informal terms) ===
    {
        "name": "vocab_abbreviated",
        "title": "ML/AI Engineer",
        "summary": "5 years building ML/AI systems. Strong in NLP and CV.",
        "skills": "Py, k8s, TF, PyTorch, HF, sklearn, GH Actions, IaC, AWS",
        "experience": [
            ("Sr. MLE", "AI Co", "2022-Present",
             "Trained LLMs with HF transformers. Deployed on k8s. Used MLOps with TF and CI/CD pipelines. Built CV pipelines with OpenCV."),
            ("MLE", "DataCo", "2020-2022",
             "Built RAG systems. NER and QA models. Worked with PyTorch and HF."),
        ],
        "education": "M.S. CS (ML), 2020",
    },
    {
        "name": "vocab_casual",
        "title": "DevOps",
        "summary": "Infra and SRE work for 4 years.",
        "skills": "K8s, TF, Helm, Argo, Prom, Graf, GH Actions, IaC",
        "experience": [
            ("SRE", "Cloud Co", "2022-Present",
             "Managed k8s clusters. IaC with TF. CI/CD with GH Actions. Observability with Prom + Graf."),
            ("DevOps", "Startup", "2020-2022",
             "Built CI/CD. Helm charts. Argo CD for GitOps."),
        ],
        "education": "B.S. CS, 2020",
    },

    # === Cross-domain resumes ===
    {
        "name": "cross_bioinformatics",
        "title": "Bioinformatics Scientist",
        "summary": "PhD bioinformatics with strong programming. Genomics + ML.",
        "skills": "Python, R, Bash, Linux, Pandas, NumPy, scikit-learn, BLAST, BWA, GATK, samtools, snakemake, AWS, Docker",
        "experience": [
            ("Sr. Bioinformatics Scientist", "BioPharma Inc", "2021-Present",
             "Built variant-calling pipelines processing whole-genome sequencing data on AWS. Trained ML classifiers for protein function prediction. Pipeline orchestration with Snakemake."),
            ("Postdoc", "Stanford", "2019-2021",
             "Single-cell RNA-seq analysis. Published 4 papers in Nature/Cell journals."),
        ],
        "education": "Ph.D. Bioinformatics, 2019\nB.S. Biology + CS, 2014",
    },
    {
        "name": "cross_fintech",
        "title": "Quantitative Developer",
        "summary": "5 years in fintech / quant trading. Low-latency systems.",
        "skills": "C++, Python, Rust, KDB+/Q, FIX protocol, multithreading, SIMD, Linux, FPGA basics, options pricing, time series",
        "experience": [
            ("Sr. Quant Dev", "Hedge Fund", "2022-Present",
             "Built low-latency trading systems in C++. Sub-microsecond order execution. Statistical arbitrage strategies."),
            ("Quant Dev", "Investment Bank", "2019-2022",
             "Pricing models for derivatives in Python and C++. Risk analytics platform."),
        ],
        "education": "M.S. Financial Engineering, 2019\nB.S. Math, 2017",
    },

    # === Niche tech stack ===
    {
        "name": "niche_rust_blockchain",
        "title": "Blockchain Engineer",
        "summary": "4 years blockchain + smart contract development.",
        "skills": "Rust, Solidity, TypeScript, Ethers.js, Hardhat, Foundry, Substrate, IPFS, zkSNARKs, EVM, Solana",
        "experience": [
            ("Sr. Blockchain Engineer", "Web3 Startup", "2022-Present",
             "Wrote smart contracts in Solidity. Built Substrate-based L1 chain in Rust. Audited DeFi protocols."),
            ("Blockchain Dev", "Crypto Exchange", "2020-2022",
             "Wallet integration. Custodial systems. Hot wallet security."),
        ],
        "education": "B.S. CS, 2020",
    },
    {
        "name": "niche_embedded",
        "title": "Embedded Systems Engineer",
        "summary": "6 years embedded firmware + hardware integration.",
        "skills": "C, C++, Verilog, VHDL, FPGA, ARM Cortex-M, RTOS, FreeRTOS, Zephyr, I2C, SPI, UART, CAN bus, Yocto",
        "experience": [
            ("Sr. Embedded Engineer", "Robotics Co", "2021-Present",
             "Firmware for ARM Cortex-M microcontrollers. RTOS-based motor control. FPGA designs in Verilog for high-speed sensor interfaces."),
            ("Embedded Engineer", "IoT Startup", "2018-2021",
             "Sensor fusion firmware. Yocto-based Linux for edge devices. CAN bus integration for automotive."),
        ],
        "education": "B.S. Computer Engineering, 2018",
    },
]


def make_pdf(resume: dict, path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, resume["title"], ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"email: {resume['name']}@example.com | Location: United States", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, resume["summary"])
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Technical Skills", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, resume["skills"])
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Experience", ln=True)
    for title, company, dates, desc in resume["experience"]:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"{title} - {company} ({dates})", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Education", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, resume["education"])

    pdf.output(path)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for r in STRESS_RESUMES:
        path = os.path.join(OUTPUT_DIR, f"{r['name']}.pdf")
        make_pdf(r, path)
        print(f"Created {path}")
    print(f"\nDone — {len(STRESS_RESUMES)} stress-test resumes generated.")


if __name__ == "__main__":
    main()
