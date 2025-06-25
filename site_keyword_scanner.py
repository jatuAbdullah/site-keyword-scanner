#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
import os
import csv
import argparse
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import mimetypes
from datetime import datetime

visited_urls = set()

def normalize_url(url):
    try:
        url, _ = urldefrag(url)
        parsed = urlparse(url)
        scheme = parsed.scheme or "http"
        netloc = parsed.netloc
        path = parsed.path.rstrip('/')
        if path == '':
            path = '/'
        return f"{scheme}://{netloc}{path}"
    except:
        return url

def fetch_html(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"[!] Failed to fetch HTML: {url} - {e}")
        return None

def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text(separator=' ', strip=True).lower()

def extract_text_from_pdf(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        reader = PdfReader(BytesIO(resp.content))
        parts = []
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                parts.append(txt)
        return ' '.join(parts).lower()
    except Exception as e:
        print(f"[!] Failed to read PDF: {url} - {e}")
        return ''

def extract_text_from_docx(url):
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        tmp = 'temp_scan.docx'
        with open(tmp, 'wb') as f:
            f.write(resp.content)
        doc = Document(tmp)
        texts = [p.text for p in doc.paragraphs]
        os.remove(tmp)
        return ' '.join(texts).lower()
    except Exception as e:
        print(f"[!] Failed to read DOCX: {url} - {e}")
        return ''

def extract_text_from_txt(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text.lower()
    except Exception as e:
        print(f"[!] Failed to read TXT: {url} - {e}")
        return ''

def get_file_type(url):
    mime, _ = mimetypes.guess_type(url)
    if mime:
        if 'pdf' in mime:
            return 'pdf'
        elif 'word' in mime:
            return 'docx'
        elif 'text' in mime:
            return 'txt'
    return 'html'

def count_keywords(text, keywords):
    return {kw: text.count(kw) for kw in keywords}

def get_csv_filename(base_url):
    domain = urlparse(base_url).netloc.replace("www.", "").replace(".", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{domain}_results_{ts}.csv"

def write_row(filename, row):
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['URL', 'Type', 'Keyword', 'Occurrences'])
        writer.writerow(row)

def process_and_enqueue(start_url, keywords, max_depth, max_pages):
    parsed_base = urlparse(start_url).netloc
    queue = [(start_url, 0)]
    total_pages = 0

    while queue:
        url, depth = queue.pop(0)
        norm = normalize_url(url)
        if norm in visited_urls:
            continue
        visited_urls.add(norm)
        total_pages += 1
        print(f"[+] Processing (depth {depth}): {norm}")

        ftype = get_file_type(norm)
        text = ''
        if ftype == 'pdf':
            text = extract_text_from_pdf(norm)
        elif ftype == 'docx':
            text = extract_text_from_docx(norm)
        elif ftype == 'txt':
            text = extract_text_from_txt(norm)
        else:
            html = fetch_html(norm)
            if html:
                text = extract_text_from_html(html)

        if text:
            counts = count_keywords(text, keywords)
            any_found = False
            for kw, cnt in counts.items():
                if cnt > 0:
                    print(f"[✓] Found '{kw}' {cnt} time(s) in: {norm}")
                    yield [norm, ftype.upper(), kw, cnt]
                    any_found = True
            if not any_found:
                print(f"[–] No keyword found in: {norm}")
        else:
            print(f"[!] No text extracted from: {norm}")

        if ftype == 'html' and depth < max_depth and total_pages < max_pages:
            html = fetch_html(norm)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                for tag in soup.find_all('a', href=True):
                    link = urljoin(norm, tag['href'])
                    link_norm = normalize_url(link)
                    parsed_link = urlparse(link_norm).netloc
                    if parsed_link and parsed_link != parsed_base:
                        continue
                    if link_norm in visited_urls:
                        continue
                    if link_norm.lower().endswith(('.pdf', '.docx', '.txt')):
                        queue.insert(0, (link_norm, depth+1))
                    else:
                        queue.append((link_norm, depth+1))
                    if len(visited_urls) + len(queue) >= max_pages:
                        break
        if total_pages >= max_pages:
            break

def main():
    parser = argparse.ArgumentParser(description="Search keywords across site content.")
    parser.add_argument("url", help="Start URL or single page")
    parser.add_argument("keywords", nargs="+", help="Keywords to search (case-insensitive)")
    parser.add_argument("--single", action="store_true", help="Only scan this page/file, no crawling")
    parser.add_argument("--max-depth", type=int, default=2, help="Max crawl depth (default 2)")
    parser.add_argument("--max-pages", type=int, default=100, help="Max total pages/files to process (default 100)")
    args = parser.parse_args()

    keywords = [kw.lower() for kw in args.keywords]

    # Ensure 'csv' folder exists
    csv_folder = "csv"
    os.makedirs(csv_folder, exist_ok=True)

    base_filename = get_csv_filename(args.url)
    csv_file = os.path.join(csv_folder, base_filename)

    total_matches = 0

    try:
        if args.single:
            norm = normalize_url(args.url)
            print(f"[→] Single mode processing: {norm}")
            ftype = get_file_type(norm)
            text = ''
            if ftype == 'pdf':
                text = extract_text_from_pdf(norm)
            elif ftype == 'docx':
                text = extract_text_from_docx(norm)
            elif ftype == 'txt':
                text = extract_text_from_txt(norm)
            else:
                html = fetch_html(norm)
                if html:
                    text = extract_text_from_html(html)
            if text:
                counts = count_keywords(text, keywords)
                matches = []
                for kw, cnt in counts.items():
                    if cnt > 0:
                        print(f"[✓] Found '{kw}' {cnt} time(s) in: {norm}")
                        matches.append([norm, ftype.upper(), kw, cnt])
                if matches:
                    print(f"[✔] Saving {len(matches)} match(es) for: {norm}")
                    for row in matches:
                        write_row(csv_file, row)
                    total_matches += len(matches)
                else:
                    print(f"[–] No matches for: {norm}")
            else:
                print(f"[!] No text extracted from: {norm}")
        else:
            for match in process_and_enqueue(args.url, keywords, args.max_depth, args.max_pages):
                write_row(csv_file, match)
                total_matches += 1
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting...")

    if total_matches > 0:
        print(f"[✔] Total {total_matches} match(es) saved to: {csv_file}")
    else:
        print("[!] No keyword matches saved.")

if __name__ == "__main__":
    main()
