import os
import sys

def verify_explanation():
    explanation_path = "EXPLANATION.md"
    if not os.path.exists(explanation_path):
        print(f"Error: {explanation_path} not found.")
        sys.exit(1)

    with open(explanation_path, "r", encoding="utf-8") as f:
        content = f.read()

    exclude_dirs = {
        ".git", ".venv", "node_modules", ".next", "__pycache__",
        ".pytest_cache", "dist", "build", ".ruff_cache", "data"
    }
    exclude_extensions = {".pyc", ".db", ".sqlite3", ".bin"}

    all_files = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.endswith(".egg-info")]
        for f in files:
            if any(f.endswith(ext) for ext in exclude_extensions):
                continue
            if f in {".env", "twinos.db", "verify_explanation.py"}:
                continue
            rel = os.path.relpath(os.path.join(root, f), ".").replace("\\", "/")
            all_files.append(rel)

    missing = []
    for f in all_files:
        basename = os.path.basename(f)
        if f not in content and basename not in content:
            missing.append(f)

    print(f"==================================================")
    print(f"TwinOS EXPLANATION.md Coverage Verification Report")
    print(f"==================================================")
    print(f"Total source/config files tracked: {len(all_files)}")
    print(f"Files verified in EXPLANATION.md:  {len(all_files) - len(missing)}")
    coverage = ((len(all_files) - len(missing)) / len(all_files)) * 100
    print(f"Coverage:                          {coverage:.2f}%")

    if missing:
        print("\nMissing files not found in EXPLANATION.md:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    else:
        print("\n>>> SUCCESS: 100% of repository files are documented in EXPLANATION.md!")
        sys.exit(0)

if __name__ == "__main__":
    verify_explanation()
