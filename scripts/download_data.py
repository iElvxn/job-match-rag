import subprocess
import sys


def main():
    result = subprocess.run(
        [
            "kaggle", "datasets", "download",
            "arshkon/linkedin-job-postings",
            "--unzip",
            "-p", "data/linkedin_jobs",
        ]
    )
    if result.returncode != 0:
        print("Download failed. Make sure ~/.kaggle/kaggle.json is set up.")
        print("Get your API token at: kaggle.com → Settings → API → Create New Token")
        sys.exit(1)

    print("Dataset downloaded to data/linkedin_jobs/")


if __name__ == "__main__":
    main()
