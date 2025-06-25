

---

````markdown
# 🔍 Site Keyword Scanner

A command-line Python tool to **scan an entire website or a single page** (including PDFs, DOCX, TXT, and HTML) for **specific keywords**.

Matches are saved to a timestamped CSV file in a `csv/` folder.

---

## 📦 Features

- ✅ Scan **single pages** or **entire websites** (depth-controlled)
- ✅ Case-insensitive keyword detection
- ✅ Supports:
  - HTML pages
  - PDF files
  - DOCX files
  - TXT files
- ✅ Saves matching results with count and file type to CSV

---

## 🛠 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jatuAbdullah/site-keyword-scanner.git
   cd site-keyword-scanner
````

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   **Contents of `requirements.txt`:**

   ```text
   requests
   beautifulsoup4
   python-docx
   PyPDF2
   ```

---

## 🚀 Usage

### Basic Command

```bash
python3 site_keyword_scanner.py <URL> <keyword1> <keyword2> ...
```

---

### 🔹 Scan a **single page or file only**

```bash
python3 site_keyword_scanner.py https://example.com neosoft --single
```

* Only scans that page (or file)
* Supports `.html`, `.pdf`, `.docx`, and `.txt`
* Ignores all internal links

---

### 🔹 Scan a **full website**

```bash
python3 site_keyword_scanner.py https://example.com neosoft innovation
```

* Crawls links within the same domain
* Matches keywords across all pages and supported files

---

### 🔹 With depth limit and page count

```bash
python3 site_keyword_scanner.py https://example.com neosoft --max-depth 2 --max-pages 50
```

* `--max-depth` (default: 2): how deep to crawl links
* `--max-pages` (default: 100): limit number of pages/files to scan

---

## ⚙️ Command-Line Options

| Option          | Description                                            |
| --------------- | ------------------------------------------------------ |
| `--single`      | Only scan the specified page or file (no crawling)     |
| `--max-depth N` | Max link depth to crawl (only if not using `--single`) |
| `--max-pages N` | Max number of total pages/files to scan                |
| `<URL>`         | The website or file URL to start from                  |
| `<keywords>`    | One or more keywords to search for (case-insensitive)  |

---

## 🧾 Output

* Output saved in: `csv/<domain>_results_<timestamp>.csv`
* Columns:

  * **URL** – where keyword was found
  * **Type** – HTML / PDF / DOCX / TXT
  * **Keyword** – matched keyword
  * **Occurrences** – how many times it appeared

---

## 📂 Folder Structure

```
site-keyword-scanner/
├── site_keyword_scanner.py
├── requirements.txt
├── csv/
│   └── <domain>_results_<timestamp>.csv
└── README.md
```

---

## 📄 License

MIT License

```
MIT License

Copyright (c) 2025 Abdullah Jatu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

```
