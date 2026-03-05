import logging
import os
import time
import urllib.parse
from typing import Iterable, List

import requests
from tqdm import tqdm

logging.basicConfig(
    filename='pastpaper.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_API = "https://pastpapers.co/api/file"
BOARD = "caie"



def scrape_subject(
    subject_code: str,
    level: str,
    paper_type: str,
    session_code: str | List[str],
    year_code: str | List[str],
    out_dir: str,
    paper_numbers: Iterable[str] | None = None,
    retries: int = 3,
    timeout: int = 15,
):
    if isinstance(session_code, str):
        session_code = [session_code]
    if isinstance(year_code, str):
        year_code = [year_code]

    os.makedirs(out_dir, exist_ok=True)

    # Infer slugs if not provided (for backward compatibility of this helper)
    # This is a simplified fallback; for full control, use the CLI or direct build_download_tasks
    subject_slug = f"Subject-{subject_code}" 
    level_slug = level 
    
    tasks = build_download_tasks(
        subject_code,
        subject_slug,
        level_slug,
        paper_type,
        session_code if isinstance(session_code, list) else [session_code],
        [session_code] if isinstance(session_code, str) else session_code, # Fallback name
        year_code if isinstance(year_code, list) else [year_code],
        paper_numbers,
        out_dir,
    )

    if not tasks:
        print("no matching papers found")
        return

    with tqdm(tasks, desc="downloading", unit="file") as bar:
        for url, out_path in bar:
            if os.path.exists(out_path):
                bar.set_postfix_str("skipped")
                # Extract subject from URL for logging
                subject = 'unknown'
                try: parts = url.split('/'); subject = parts[5] if len(parts) > 5 else 'unknown'
                except: pass
                log_download_status(subject, url, out_path, "SKIPPED")
                continue

            success = download_with_retry(
                url,
                out_path,
                retries=retries,
                timeout=timeout,
            )

            bar.set_postfix_str("ok" if success else "failed")


def build_download_tasks(
    subject_code: str,
    subject_slug: str,
    level_slug: str,
    selected_type: str,
    session_codes: List[str],
    session_slugs: List[str],
    years: List[str],
    paper_numbers: Iterable[str] | None,
    out_dir: str,
):
    tasks = []
    
    # Map 'all' or specific types
    types_to_look_for = []
    if selected_type == "all":
        types_to_look_for = ["qp", "ms", "in", "er", "gt"]
    elif "both" in selected_type:
        types_to_look_for = ["qp", "ms"]
    elif " (insert)" in selected_type:
        types_to_look_for = ["in"]
    elif " (examiner report)" in selected_type:
        types_to_look_for = ["er"]
    elif " (grade threshold)" in selected_type:
        types_to_look_for = ["gt"]
    else:
        types_to_look_for = [selected_type]

    for year in years:
        for session_code, session_name in zip(session_codes, session_slugs):
            session_folder = f"20{year}-{session_name}"
            prefix = f"{subject_code}_{session_code}{year}"

            for kind in types_to_look_for:
                tasks += discover_files(
                    subject_slug,
                    level_slug,
                    session_folder,
                    prefix,
                    kind,
                    paper_numbers,
                    out_dir,
                )

    return tasks


def discover_files(
    subject_slug: str,
    level_name: str,
    session_folder: str,
    prefix: str,
    kind: str,
    paper_numbers: Iterable[str] | None,
    out_dir: str,
):
    results = []

    # URL‑encode the subject slug to handle spaces but keep parentheses literal as per website spec
    encoded_subject_slug = urllib.parse.quote(subject_slug, safe='()')

    for paper in paper_numbers or [
        "11",
        "12",
        "13",
        "21",
        "22",
        "23",
        "31",
        "32",
        "33",
    ]:
        filename = f"{prefix}_{kind}_{paper}.pdf"

        url = (
            f"{BASE_API}/"
            f"{BOARD}/"
            f"{level_name}/"
            f"{encoded_subject_slug}/"
            f"{session_folder}/"
            f"{filename}"
            "?download=true"
        )

        out_path = os.path.join(
            out_dir,
            session_folder,
            kind,
            filename,
        )

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        results.append((url, out_path))

    return results

def log_download_status(subject: str, url: str, out_path: str, status: str) -> None:
    """Append a log entry for each download attempt.
    Status can be SUCCESS, FAIL, or SKIPPED.
    The log is stored in ~/pastpaper_logs/download_status.log.
    If status is SUCCESS, we remove any previous FAIL entries for this same file.
    """
    log_dir = os.path.expanduser('~/pastpaper_logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, 'download_status.log')
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    # If success, clean up previous failures for this file to keep the log tidy
    if status == "SUCCESS" and os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                lines = f.readlines()
            
            # Filter out any FAIL lines that match this specific URL and path
            new_lines = [
                line for line in lines 
                if not (f" | FAIL | " in line and url in line and out_path in line)
            ]
            
            if len(new_lines) < len(lines):
                with open(log_path, 'w') as f:
                    f.writelines(new_lines)
        except Exception:
            pass # Silently fail if log cleanup issues occur

    with open(log_path, 'a') as f:
        f.write(f"{timestamp} | {subject} | {status} | {url} -> {out_path}\n")


def download_with_retry(url: str, out_path: str, retries: int = 3, timeout: int = 60) -> bool:
    """Download a file with retries and log the outcome.
    The subject is inferred from the URL for logging purposes.
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://pastpapers.co/",
        "Accept": "application/pdf,*/*",
    }
    # Attempt to extract subject slug from URL for logging
    subject = 'unknown'
    try:
        parts = url.split('/')
        # URL format: .../file/BOARD/level/subject_slug/...
        subject = parts[7] if len(parts) > 7 else 'unknown'
    except Exception:
        pass
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout, stream=True)
            if r.status_code == 200:
                with open(out_path, 'wb') as f:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                # sanity check
                with open(out_path, 'rb') as f:
                    if f.read(4) == b"%PDF":
                        log_download_status(subject, url, out_path, "SUCCESS")
                        return True
                os.remove(out_path)
                logging.error(f"Invalid PDF (sanity check failed): {url}")
                log_download_status(subject, url, out_path, "FAIL")
                return False
            elif r.status_code == 404:
                logging.error(f"File not found (404): {url}")
                log_download_status(subject, url, out_path, "FAIL")
                return False
            else:
                logging.error(f"Failed to download {url}: Status code {r.status_code}")
                log_download_status(subject, url, out_path, "FAIL")
        except requests.Timeout:
            logging.error(f"Timeout error for {url}")
        except requests.RequestException as e:
            logging.error(f"Request error for {url}: {e}")
        time.sleep(2 * attempt)
    log_download_status(subject, url, out_path, "FAIL")
    return False
