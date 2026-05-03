"""Generate 15 synthetic resume PDFs for evaluation."""
import os

try:
    from fpdf import FPDF
except ImportError:
    import subprocess
    subprocess.run(["pip3", "install", "fpdf2", "-q"])
    from fpdf import FPDF

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "evaluation", "test_resumes")

RESUMES = [
    {"name": "senior_swe", "title": "Senior Software Engineer", "summary": "8 years of experience building scalable distributed systems. Led teams of 5-10 engineers.", "skills": "Python, Java, Go, Kubernetes, Docker, AWS, PostgreSQL, Redis, Kafka, gRPC, Terraform, CI/CD, System Design, Microservices", "experience": [
        ("Senior Software Engineer", "Google", "2021-Present", "Designed and maintained distributed data processing pipelines serving 50M+ daily requests. Led migration from monolith to microservices architecture. Mentored 4 junior engineers."),
        ("Software Engineer", "Amazon", "2018-2021", "Built real-time inventory management system using Java and DynamoDB. Implemented CI/CD pipelines with Jenkins and Docker. Reduced API latency by 40%."),
        ("Junior Developer", "Startup Inc", "2016-2018", "Full-stack development with Python/Django and React. Built REST APIs and integrated third-party payment systems."),
    ], "education": "B.S. Computer Science, Stanford University, 2016"},

    {"name": "ml_engineer", "title": "Machine Learning Engineer", "summary": "5 years specializing in NLP and computer vision. Published 3 papers at top venues.", "skills": "Python, PyTorch, TensorFlow, Hugging Face, scikit-learn, NumPy, Pandas, AWS SageMaker, Docker, MLflow, SQL, Spark, CUDA, Transformers", "experience": [
        ("ML Engineer", "Meta", "2022-Present", "Fine-tuned large language models for content moderation. Built training pipelines processing 1TB+ daily data. Deployed models serving 100K+ QPS."),
        ("Research Engineer", "OpenAI", "2020-2022", "Developed evaluation frameworks for language models. Implemented RLHF training loops. Co-authored 2 papers on instruction tuning."),
        ("Data Scientist", "Uber", "2019-2020", "Built demand forecasting models using gradient boosting and neural networks. Improved prediction accuracy by 15%."),
    ], "education": "M.S. Computer Science (ML focus), CMU, 2019\nB.S. Mathematics, MIT, 2017"},

    {"name": "frontend_dev", "title": "Frontend Developer", "summary": "4 years building responsive web applications with modern JavaScript frameworks.", "skills": "JavaScript, TypeScript, React, Next.js, Vue.js, HTML, CSS, Tailwind CSS, Node.js, GraphQL, Webpack, Jest, Cypress, Figma", "experience": [
        ("Senior Frontend Engineer", "Stripe", "2022-Present", "Built payment dashboard used by 100K+ merchants. Implemented design system with 50+ reusable components. Led accessibility audit achieving WCAG 2.1 AA compliance."),
        ("Frontend Developer", "Airbnb", "2020-2022", "Developed listing search interface with React and GraphQL. Optimized Core Web Vitals improving LCP by 35%. Built A/B testing framework."),
    ], "education": "B.S. Computer Science, UC Berkeley, 2020"},

    {"name": "data_scientist", "title": "Data Scientist", "summary": "6 years of experience in statistical modeling and machine learning for business analytics.", "skills": "Python, R, SQL, Pandas, NumPy, scikit-learn, XGBoost, Tableau, Power BI, A/B Testing, Statistics, Spark, Airflow, dbt", "experience": [
        ("Senior Data Scientist", "Netflix", "2021-Present", "Built recommendation algorithms improving user engagement by 12%. Designed A/B testing framework for content personalization. Led analytics for 3 product launches."),
        ("Data Scientist", "LinkedIn", "2019-2021", "Developed churn prediction models with 89% accuracy. Built automated reporting pipelines with Airflow and dbt. Conducted causal inference studies."),
        ("Data Analyst", "Deloitte", "2018-2019", "Created dashboards and reports for Fortune 500 clients. Performed statistical analysis on customer segmentation."),
    ], "education": "M.S. Statistics, Columbia University, 2018\nB.A. Economics, NYU, 2016"},

    {"name": "devops_engineer", "title": "DevOps Engineer", "summary": "5 years building and managing cloud infrastructure and CI/CD pipelines.", "skills": "AWS, GCP, Kubernetes, Docker, Terraform, Ansible, Jenkins, GitHub Actions, Linux, Bash, Python, Prometheus, Grafana, Datadog", "experience": [
        ("Senior DevOps Engineer", "Shopify", "2022-Present", "Managed Kubernetes clusters serving 1M+ requests/second. Implemented infrastructure as code with Terraform across 3 cloud regions. Reduced deployment time from 45min to 5min."),
        ("DevOps Engineer", "Twilio", "2020-2022", "Built CI/CD pipelines for 50+ microservices. Implemented monitoring and alerting with Prometheus and Grafana. Managed AWS infrastructure spending $2M+/month."),
    ], "education": "B.S. Computer Engineering, Georgia Tech, 2020"},

    {"name": "new_grad_cs", "title": "Software Engineer (New Graduate)", "summary": "Recent CS graduate with internship experience and strong academic background.", "skills": "Python, Java, C++, React, Node.js, SQL, Git, Docker, AWS, Data Structures, Algorithms", "experience": [
        ("Software Engineering Intern", "Microsoft", "Summer 2024", "Built internal tool for team productivity tracking using React and C#. Wrote unit tests achieving 90% code coverage."),
        ("Research Assistant", "University Lab", "2023-2024", "Implemented graph neural network models for protein structure prediction. Published poster at undergraduate research symposium."),
    ], "education": "B.S. Computer Science, University of Michigan, 2024\nGPA: 3.8/4.0, Dean's List"},

    {"name": "backend_engineer", "title": "Backend Engineer", "summary": "6 years building high-performance APIs and data processing systems.", "skills": "Python, Go, Java, PostgreSQL, MongoDB, Redis, Kafka, RabbitMQ, Docker, Kubernetes, REST, gRPC, FastAPI, Spring Boot", "experience": [
        ("Staff Backend Engineer", "Cloudflare", "2022-Present", "Architected edge computing platform handling 25M+ requests/second. Designed event-driven architecture with Kafka. Led API design reviews."),
        ("Backend Engineer", "Palantir", "2020-2022", "Built data integration pipelines processing petabyte-scale datasets. Implemented access control system for sensitive data. Optimized database queries reducing P99 latency by 60%."),
        ("Software Engineer", "Capital One", "2018-2020", "Developed RESTful APIs for banking services using Java and Spring Boot. Built fraud detection data pipeline."),
    ], "education": "M.S. Computer Science, Cornell University, 2018\nB.S. Computer Science, Virginia Tech, 2016"},

    {"name": "mobile_dev", "title": "Mobile Developer", "summary": "5 years building iOS and Android applications with millions of downloads.", "skills": "Swift, Kotlin, React Native, iOS, Android, Xcode, Firebase, REST APIs, GraphQL, Git, Agile, UI/UX, Core Data, Jetpack Compose", "experience": [
        ("Senior iOS Engineer", "Spotify", "2022-Present", "Led development of podcast player features used by 100M+ users. Implemented offline playback with Core Data. Reduced app crash rate by 70%."),
        ("Mobile Developer", "DoorDash", "2020-2022", "Built driver-side Android app features with Kotlin and Jetpack Compose. Implemented real-time location tracking and route optimization."),
    ], "education": "B.S. Computer Science, University of Washington, 2020"},

    {"name": "data_engineer", "title": "Data Engineer", "summary": "4 years building data pipelines and analytics infrastructure.", "skills": "Python, SQL, Spark, Airflow, dbt, Snowflake, BigQuery, Kafka, AWS, Terraform, Docker, Pandas, Databricks, ETL", "experience": [
        ("Senior Data Engineer", "Lyft", "2022-Present", "Built real-time data pipeline processing 500K events/second with Kafka and Spark. Migrated data warehouse to Snowflake reducing query costs by 40%."),
        ("Data Engineer", "Pinterest", "2020-2022", "Developed ETL pipelines with Airflow and dbt. Built data quality monitoring framework. Managed 50TB+ data warehouse."),
    ], "education": "M.S. Data Science, UC San Diego, 2020\nB.S. Computer Science, UT Austin, 2018"},

    {"name": "security_engineer", "title": "Security Engineer", "summary": "5 years in application and infrastructure security.", "skills": "Python, Go, Bash, Linux, AWS, Docker, Kubernetes, Burp Suite, OWASP, Terraform, CI/CD, Threat Modeling, Penetration Testing, SIEM", "experience": [
        ("Senior Security Engineer", "CrowdStrike", "2022-Present", "Led threat detection team building ML-based malware classification. Conducted security reviews for 30+ microservices. Implemented zero-trust architecture."),
        ("Security Engineer", "Datadog", "2020-2022", "Built automated vulnerability scanning pipeline integrated with CI/CD. Performed penetration testing and code reviews. Managed bug bounty program."),
    ], "education": "M.S. Cybersecurity, Johns Hopkins, 2020\nB.S. Computer Science, Purdue, 2018"},

    {"name": "fullstack_dev", "title": "Full Stack Developer", "summary": "4 years building end-to-end web applications.", "skills": "JavaScript, TypeScript, Python, React, Next.js, Node.js, Express, PostgreSQL, MongoDB, Docker, AWS, REST, GraphQL, Agile", "experience": [
        ("Full Stack Engineer", "Notion", "2022-Present", "Built collaborative editing features with real-time sync. Implemented server-side rendering improving page load by 50%. Developed internal admin tools."),
        ("Software Engineer", "HubSpot", "2020-2022", "Built CRM dashboard features with React and Node.js. Designed RESTful APIs serving 10K+ daily active users. Led migration from JavaScript to TypeScript."),
    ], "education": "B.S. Computer Science, Boston University, 2020"},

    {"name": "ai_researcher", "title": "AI Research Scientist", "summary": "PhD with 3 years industry experience in NLP and generative AI.", "skills": "Python, PyTorch, JAX, Transformers, Hugging Face, CUDA, LaTeX, NumPy, Pandas, scikit-learn, Weights & Biases, Docker, Linux, NLP", "experience": [
        ("Research Scientist", "DeepMind", "2022-Present", "Developed novel attention mechanisms for long-context language models. Published 5 papers at NeurIPS, ICML, and ACL. Led team of 3 research engineers."),
        ("Research Intern", "Google Brain", "Summer 2021", "Investigated chain-of-thought prompting strategies. Built evaluation benchmarks for reasoning capabilities."),
    ], "education": "Ph.D. Computer Science (NLP), University of Washington, 2022\nB.S. Computer Science, Caltech, 2017"},

    {"name": "product_manager_tech", "title": "Technical Product Manager", "summary": "5 years bridging engineering and business with technical background.", "skills": "Product Management, Agile, Scrum, Jira, SQL, Python, Data Analysis, A/B Testing, Technical Writing, Stakeholder Management, Figma, Roadmapping", "experience": [
        ("Senior PM", "Slack", "2022-Present", "Led development of enterprise features generating $20M ARR. Managed roadmap for team of 12 engineers. Ran 50+ A/B tests driving 15% engagement increase."),
        ("Product Manager", "Atlassian", "2020-2022", "Owned Jira workflow automation features. Conducted user research with 200+ customers. Defined API specifications for third-party integrations."),
    ], "education": "MBA, Wharton, 2020\nB.S. Computer Science, Penn State, 2016"},

    {"name": "career_changer", "title": "Software Engineer (Career Changer)", "summary": "Former mechanical engineer transitioning to software. Completed bootcamp and self-taught programming.", "skills": "Python, JavaScript, React, Node.js, SQL, Git, HTML, CSS, REST APIs, Agile", "experience": [
        ("Junior Software Developer", "Tech Startup", "2024-Present", "Building web application features with React and Node.js. Writing unit and integration tests. Participating in code reviews."),
        ("Mechanical Engineer", "Boeing", "2018-2023", "Designed aircraft structural components using CAD software. Led cross-functional team of 8 engineers. Managed project budgets of $5M+."),
    ], "education": "Software Engineering Bootcamp, Hack Reactor, 2024\nB.S. Mechanical Engineering, Purdue, 2018"},

    {"name": "cloud_architect", "title": "Cloud Solutions Architect", "summary": "7 years designing and implementing enterprise cloud architectures.", "skills": "AWS, Azure, GCP, Kubernetes, Docker, Terraform, Python, Go, System Design, Microservices, Serverless, Lambda, EC2, S3, CloudFormation", "experience": [
        ("Principal Cloud Architect", "Snowflake", "2022-Present", "Designed multi-cloud deployment strategy across AWS, GCP, and Azure. Led migration of 200+ services to Kubernetes. Reduced infrastructure costs by 35%."),
        ("Cloud Engineer", "Salesforce", "2019-2022", "Built serverless architectures with AWS Lambda and API Gateway. Implemented disaster recovery across 3 regions. Managed infrastructure for 99.99% uptime SLA."),
        ("Systems Engineer", "IBM", "2017-2019", "Administered Linux servers and VMware clusters. Automated provisioning with Ansible and Terraform."),
    ], "education": "B.S. Computer Science, RPI, 2017\nAWS Solutions Architect Professional Certified"},
]


def make_pdf(resume: dict, path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Name / Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, resume["title"], ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"email: {resume['name']}@example.com | Location: United States", ln=True)
    pdf.ln(4)

    # Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, resume["summary"])
    pdf.ln(3)

    # Skills
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Technical Skills", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, resume["skills"])
    pdf.ln(3)

    # Experience
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Experience", ln=True)
    for title, company, dates, desc in resume["experience"]:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"{title} - {company} ({dates})", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(2)

    # Education
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "Education", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, resume["education"])

    pdf.output(path)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for r in RESUMES:
        path = os.path.join(OUTPUT_DIR, f"{r['name']}.pdf")
        make_pdf(r, path)
        print(f"Created {path}")
    print(f"\nDone — {len(RESUMES)} resumes generated.")


if __name__ == "__main__":
    main()
