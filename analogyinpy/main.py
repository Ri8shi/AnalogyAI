import streamlit as st
import google.generativeai as genai
import requests
import zipfile
import tempfile
import re
import time
from pathlib import Path
from io import BytesIO
from collections import Counter

API_KEY = "enter your api key"

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".next", ".nuxt", "vendor", "bower_components", ".idea",
    ".vscode", ".gradle", "target", "bin", "obj", ".svn",
    "coverage", ".nyc_output", ".cache", ".parcel-cache",
}

SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "Pipfile.lock", "poetry.lock", "composer.lock",
    "Gemfile.lock", ".DS_Store", "Thumbs.db",
}

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp",
}

PRIORITY_FILES = {
    "README.md", "readme.md", "README.rst", "README.txt", "README",
    "setup.py", "setup.cfg", "pyproject.toml", "requirements.txt",
    "package.json", "Cargo.toml", "go.mod",
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
}

MAX_FILE_CHARS = 600         
MAX_TOTAL_CHARS = 8000      
MAX_FILES = 20               

EXT_TO_LANG = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".jsx": "React JSX", ".tsx": "React TSX", ".java": "Java",
    ".c": "C", ".cpp": "C++",
}

@st.cache_resource
def get_model():
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config=genai.GenerationConfig(
            max_output_tokens=800,        
            temperature=0.2,
        ),
        system_instruction="Senior engineer. Explain repos concisely. Markdown, bullets.",
    )

def parse_github_url(url: str):
    url = url.strip().rstrip("/")
    url_path = re.sub(r"^https?://", "", url)
    url_path = re.sub(r"^github\.com/", "", url_path)

    parts = url_path.split("/")
    if len(parts) < 2:
        return None, None, None

    owner, repo = parts[0], parts[1]
    branch = None
    if len(parts) >= 4 and parts[2] == "tree":
        branch = "/".join(parts[3:])

    return owner, repo, branch

@st.cache_data(show_spinner=False)
def download_repo_zip(owner: str, repo: str, branch: str = None) -> bytes:
    if branch:
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    else:
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"

    resp = requests.get(zip_url, stream=True, timeout=60)

    if resp.status_code == 404 and not branch:
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
        resp = requests.get(zip_url, stream=True, timeout=60)

    resp.raise_for_status()

    buf = BytesIO()
    for chunk in resp.iter_content(chunk_size=8192):
        buf.write(chunk)
    return buf.getvalue() 

def extract_zip(zip_bytes: bytes, dest: str):
    with zipfile.ZipFile(BytesIO(zip_bytes), "r") as zf:
        zf.extractall(dest)

def should_skip(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    for part in rel.parts:
        if part in SKIP_DIRS:
            return True
    if path.is_file() and path.name in SKIP_FILES:
        return True
    return False

def collect_files(root: Path):
    tree = []
    files = []
    all_file_stats = []
    total_chars = 0
    children = list(root.iterdir())
    if len(children) == 1 and children[0].is_dir():
        root = children[0]

    for item in sorted(root.rglob("*")):
        if should_skip(item, root):
            continue

        rel = str(item.relative_to(root)).replace("\\", "/")

        if item.is_dir():
            tree.append(f"[DIR] {rel}/")
            continue

        tree.append(f"      {rel}")

        ext = item.suffix.lower()
        try:
            fsize = item.stat().st_size
            if fsize <= 200_000:
                raw = item.read_text(encoding="utf-8", errors="ignore")
                all_file_stats.append((rel, ext, raw.count("\n") + 1, len(raw)))
            else:
                all_file_stats.append((rel, ext, 0, fsize))
        except Exception:
            all_file_stats.append((rel, ext, 0, 0))

        if len(files) >= MAX_FILES or total_chars >= MAX_TOTAL_CHARS:
            continue

        name = item.name
        is_priority = name in PRIORITY_FILES
        is_code = ext in CODE_EXTENSIONS

        if not (is_priority or is_code):
            continue

        try:
            size = item.stat().st_size
            if size > 100_000:
                continue
            content = item.read_text(encoding="utf-8", errors="ignore")
            if len(content) > MAX_FILE_CHARS:
                content = content[:MAX_FILE_CHARS] + "\n..."
            total_chars += len(content)
            files.append((rel, content))
        except Exception:
            pass

    return tree, files, all_file_stats

def build_repo_prompt(repo_name: str, tree: list, files: list) -> str:
    dir_entries = [t for t in tree if t.startswith("[DIR]")]
    tree_str = "\n".join(dir_entries[:50])

    file_sections = []
    for path, content in files:
        file_sections.append(f"### {path}\n```\n{content}\n```")
    files_str = "\n".join(file_sections)

    return f"""Analyze **{repo_name}**:
1. Overview (1-2 sentences)
2. Tech Stack
3. Structure
4. Key Components
5. How It Works
6. Setup
Concise markdown.
## Dirs
```
{tree_str}
```

## Files
{files_str}
"""

def compute_local_stats(all_file_stats):
    lang_counter = Counter()
    total_loc = 0
    total_size = 0

    for rel, ext, lines, chars in all_file_stats:
        lang = EXT_TO_LANG.get(ext)
        if lang:
            lang_counter[lang] += 1
        total_loc += lines
        total_size += chars

    file_count = len(all_file_stats)
    return {
        "languages": lang_counter,
        "total_loc": total_loc,
        "total_size": total_size,
        "avg_file_size": total_size // file_count if file_count else 0,
        "file_count": file_count,
    }

def setup_page():
    st.set_page_config(
        page_title="Anlogy AI",
        layout="wide",
    )

def render_header():
    st.title("Anlogy AI")
    st.caption("Drop a GitHub link or ZIP file get an AI powered explanation in seconds")

def render_metrics(tree, files, all_file_stats, prompt_len):
    dir_count = sum(1 for t in tree if t.startswith("[DIR]"))
    file_count = len(tree) - dir_count
    read_count = len(files)
    stats = compute_local_stats(all_file_stats)
    est_tokens = prompt_len // 4

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Directories", dir_count)
    col2.metric("Total Files", file_count)
    col3.metric("Files Sent to AI", read_count)
    col4.metric("Total LOC", f"{stats['total_loc']:,}")
    col5.metric("Languages", len(stats["languages"]))
    col6.metric("Est. Tokens", f"~{est_tokens:,}")

def render_local_insights(all_file_stats):
    stats = compute_local_stats(all_file_stats)

    if stats["languages"]:
        with st.expander("Language Breakdown", expanded=False):
            sorted_langs = stats["languages"].most_common(15)
            for lang, count in sorted_langs:
                pct = count / stats["file_count"] * 100 if stats["file_count"] else 0
                st.text(f"  {lang:<20} {count:>4} files  ({pct:.1f}%)")

    sized_files = [(r, c) for r, e, l, c in all_file_stats if c > 0]
    if sized_files:
        sized_files.sort(key=lambda x: x[1], reverse=True)
        with st.expander("Largest Files (top 10)", expanded=False):
            for rel, chars in sized_files[:10]:
                st.text(f"  {rel:<50} {chars/1024:>8.1f} KB")

def process_repo(zip_bytes: bytes, repo_name: str):
    with tempfile.TemporaryDirectory() as tmp_dir:
        with st.spinner("Extracting repository..."):
            extract_zip(zip_bytes, tmp_dir)

        with st.spinner("Scanning files..."):
            tree, files, all_file_stats = collect_files(Path(tmp_dir))

        if not tree:
            st.error("No files found in the repository.")
            return

        prompt = build_repo_prompt(repo_name, tree, files)
        prompt_len = len(prompt)

        render_metrics(tree, files, all_file_stats, prompt_len)

        render_local_insights(all_file_stats)

        with st.expander("File Tree", expanded=False):
            st.code("\n".join(tree[:200]), language="text")

        with st.expander(f"Files Analyzed ({len(files)})", expanded=False):
            for path, content in files:
                st.markdown(f"**`{path}`**")
                ext = Path(path).suffix.lstrip(".")
                lang_map = {
                    "py": "python", "js": "javascript", "ts": "typescript",
                    "jsx": "javascript", "tsx": "typescript", "java": "java",
                    "cpp": "cpp", "c": "c",
                    "json": "json", "md": "markdown", "yaml": "yaml",
                    "yml": "yaml", "toml": "toml",
                }
                st.code(content, language=lang_map.get(ext, "text"))

        with st.spinner("Generating AI explanation..."):
            try:
                t0 = time.time()
                model = get_model()
                response = model.generate_content(prompt)
                elapsed = time.time() - t0
                explanation = response.text
            except Exception as e:
                st.error(f"Gemini API error: {e}")
                return

    st.markdown("---")
    st.subheader("Repository Explanation")
    st.markdown(explanation)
    st.download_button(
        label="Download Explanation",
        data=explanation,
        file_name=f"{repo_name.replace('/', '_')}_explanation.md",
        mime="text/markdown",
    )
    st.caption(f"Prompt: ~{prompt_len:,} chars / ~{prompt_len // 4:,} tokens | Response: {elapsed:.1f}s")

def main():
    setup_page()
    render_header()

    tab_url, tab_zip = st.tabs(["GitHub URL", "Upload ZIP"])

    with tab_url:
        url = st.text_input(
            "Paste a GitHub repository URL",
            value="https://github.com/Ri8shi/pngtojpgconverter",
            key="repo_url",
        )
        analyze_url = st.button("Analyze Repository", key="btn_url")

        if analyze_url:
            if not url or not url.strip():
                st.warning("Please enter a GitHub URL.")
            else:
                owner, repo, branch = parse_github_url(url)
                if not owner or not repo:
                    st.error("Invalid GitHub URL. Use format: https://github.com/owner/repo")
                else:
                    with st.spinner(f"Downloading {owner}/{repo}..."):
                        try:
                            zip_bytes = download_repo_zip(owner, repo, branch)
                        except requests.exceptions.HTTPError as e:
                            st.error(f"Failed to download repository: {e}")
                            st.info("Make sure the repository is public and the URL is correct.")
                            return
                        except Exception as e:
                            st.error(f"Download error: {e}")
                            return

                    process_repo(zip_bytes, f"{owner}/{repo}")

    with tab_zip:
        uploaded = st.file_uploader(
            "Upload a repository ZIP file",
            type=["zip"],
            key="repo_zip",
        )
        analyze_zip = st.button("Analyze ZIP", key="btn_zip")

        if analyze_zip:
            if uploaded is None:
                st.warning("Please upload a ZIP file first.")
            else:
                zip_bytes = uploaded.read()
                repo_name = uploaded.name.replace(".zip", "")
                process_repo(zip_bytes, repo_name)

if __name__ == "__main__":
    main()