# WebHunter Pro v2.0

> Full-stack automated web exploitation framework built for professional bug bounty hunters and penetration testers.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Platform-Parrot%20OS%20%7C%20Kali%20%7C%20Ubuntu-orange?style=for-the-badge&logo=linux&logoColor=white"/>
  <img src="https://img.shields.io/badge/Architecture-ARM64%20%7C%20x86__64-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge"/>
</p>

---

## What is WebHunter Pro?

WebHunter Pro automates the entire bug bounty pipeline in a single command — from subdomain discovery all the way to exploitation and report generation. Instead of manually chaining 20+ tools together, WebHunter Pro does it automatically, intelligently selecting the right tool for each vulnerability type it discovers.

---

## Attack Pipeline

```
Target Domain
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE 1  │  Subdomain Enumeration                       │
│           │  subfinder · amass · assetfinder · crt.sh    │
├─────────────────────────────────────────────────────────┤
│  PHASE 2  │  Alive Host Detection                        │
│           │  httpx · whatweb (tech fingerprinting)       │
├─────────────────────────────────────────────────────────┤
│  PHASE 3  │  Crawling & Param Discovery                  │
│           │  katana · hakrawler · gospider               │
│           │  waybackurls · gau · arjun · paramspider     │
│           │  LinkFinder (JS endpoint extraction)         │
├─────────────────────────────────────────────────────────┤
│  PHASE 4  │  Nuclei Scanning                             │
│           │  Full default template library               │
│           │  CVEs · Misconfigs · Exposures · RCE         │
├─────────────────────────────────────────────────────────┤
│  PHASE 5  │  Secret & JS Analysis                        │
│           │  SecretFinder · Custom regex engine          │
│           │  AWS · GitHub · Slack · JWT · API Keys       │
├─────────────────────────────────────────────────────────┤
│  PHASE 6  │  Full Arsenal Exploitation                   │
│           │  SQLi   → sqlmap                             │
│           │  XSS    → dalfox · XSStrike                  │
│           │  SSRF   → SSRFmap · custom prober            │
│           │  LFI    → LFISuite · custom payloads         │
│           │  CMDi   → commix · time-based detection      │
│           │  SSTI   → tplmap · polyglot payloads         │
│           │  CORS   → Corsy · custom checker             │
│           │  XXE    → custom XML injection               │
│           │  IDOR   → numeric param detector             │
│           │  JWT    → jwt_tool · alg:none check          │
│           │  Redirect → custom payload tester            │
│           │  Nikto  → web server scanner                 │
├─────────────────────────────────────────────────────────┤
│  PHASE 7  │  Directory & File Fuzzing                    │
│           │  ffuf · gobuster · feroxbuster               │
├─────────────────────────────────────────────────────────┤
│  PHASE 8  │  Report Generation                           │
│           │  HTML (dark themed) · JSON · Markdown        │
└─────────────────────────────────────────────────────────┘
```

---

## Installation

### Requirements
- Parrot OS 7.1 / Kali Linux / Ubuntu 22+
- ARM64 or x86_64
- Python 3.8+
- Go 1.20+
- Root access for installer

### One-Command Install

```bash
git clone https://github.com/YOUR_USERNAME/webhunter-pro.git
cd webhunter-pro
chmod +x install_tools.sh
sudo bash install_tools.sh
```

The installer automatically handles everything:
- System dependencies via `apt`
- All Go-based tools via `go install`
- All Python tools via `pip` and `git clone`
- Nuclei template updates
- SecLists wordlists
- Symlinks for all tools
- Permission fixes

After install:
```bash
source ~/.bashrc
```

---

## Usage

```bash
# Basic scan
python3 WebHunter.py -d target.com

# Skip specific phases
python3 WebHunter.py -d target.com --skip-fuzz
python3 WebHunter.py -d target.com --skip-nuclei --skip-exploit

# Custom output directory
python3 WebHunter.py -d target.com --output my_results

# High thread count
python3 WebHunter.py -d target.com --threads 100
```

### All Flags

| Flag | Description |
|------|-------------|
| `-d DOMAIN` | Target domain **(required)** |
| `--threads N` | Thread count (default: 50) |
| `--output DIR` | Custom output directory |
| `--skip-enum` | Skip subdomain enumeration |
| `--skip-alive` | Skip alive host detection |
| `--skip-crawl` | Skip URL crawling |
| `--skip-nuclei` | Skip nuclei scanning |
| `--skip-secrets` | Skip JS/secret scanning |
| `--skip-exploit` | Skip exploitation phase |
| `--skip-fuzz` | Skip directory fuzzing |

---

## Output Structure

```
target_com_scan/
├── subdomains.txt                  # All discovered subdomains
├── alive_hosts.txt                 # Live HTTP(S) hosts
├── all_urls.txt                    # All crawled URLs
├── endpoints_with_params.txt       # Parameter endpoints
├── js_files.txt                    # JavaScript files
├── katana_urls.txt                 # Katana spider output
├── nuclei_results.json             # Nuclei findings (raw)
├── nuclei_endpoints.json           # Nuclei on params
├── sqli_confirmed.txt              # Confirmed SQLi
├── xss_dalfox.txt                  # XSS findings
├── lfi_confirmed.txt               # Confirmed LFI
├── secrets_found.txt               # Exposed secrets/keys
├── idor_candidates.txt             # IDOR candidates
├── ffuf_*.json                     # Directory fuzzing
├── report.html                     # Professional HTML report
├── report.json                     # Machine-readable report
├── report.md                       # Markdown report
└── webhunter.log                   # Full scan log
```

---

## Tool Arsenal

| Category | Tool | Purpose |
|----------|------|---------|
| Recon | subfinder | Subdomain enumeration |
| Recon | amass | Passive subdomain enum |
| Recon | assetfinder | Fast subdomain discovery |
| Recon | dnsx | DNS resolution & validation |
| Alive | httpx | HTTP probing + fingerprinting |
| Crawl | katana | JS-aware web spider |
| Crawl | hakrawler | Fast URL harvester |
| Crawl | gospider | Deep web spider |
| Crawl | waybackurls | Historical URL discovery |
| Crawl | gau | Fetch all known URLs |
| Params | arjun | Hidden parameter discovery |
| Params | paramspider | Parameter URL miner |
| Params | LinkFinder | JS endpoint extractor |
| Scan | nuclei | Multi-template vuln scanner |
| Secrets | SecretFinder | JS secret scanner |
| SQLi | sqlmap | SQL injection exploitation |
| XSS | dalfox | Fast XSS scanner |
| XSS | XSStrike | Advanced XSS framework |
| SSRF | SSRFmap | SSRF exploitation |
| CMDi | commix | Command injection |
| SSTI | tplmap | Template injection |
| CORS | Corsy | CORS misconfiguration |
| JWT | jwt_tool | JWT attack toolkit |
| LFI | LFISuite | Local file inclusion |
| Fuzz | ffuf | Directory/file fuzzing |
| Fuzz | gobuster | Directory brute-forcer |
| Misc | nikto | Web server scanner |
| Misc | nmap | Port/service scanner |
| Misc | gf | Pattern grep for URLs |

---

## Smart Exploitation Logic

WebHunter Pro doesn't just scan — it thinks. Based on nuclei findings and endpoint parameter analysis, it automatically decides which exploitation tool to run:

- Parameter named `id=1` → IDOR candidate flagged
- Parameter named `file=` or `path=` → LFI payloads fired
- Parameter named `url=` or `redirect=` → SSRF + open redirect tested
- Parameter named `cmd=` or `exec=` → commix launched
- Parameter named `template=` or `view=` → SSTI polyglot tested
- JWT in response headers/cookies → jwt_tool alg:none check
- JS files discovered → SecretFinder + custom regex (AWS, GitHub, Slack keys)
- XML content-type endpoint → XXE payload injected

---

## Reports

Every scan generates three report formats simultaneously:

**HTML Report** — Dark-themed professional report with vulnerability table, severity badges, subdomain list, stats dashboard. Ready for submission.

**JSON Report** — Machine-readable structured output. Integrates with other tools, pipelines, or custom dashboards.

**Markdown Report** — Clean documentation-ready format. Perfect for writeups, GitHub, or Notion.

---

## Legal Disclaimer

**This tool is for authorized penetration testing and bug bounty programs only.**

Only use WebHunter Pro on targets you have explicit written permission to test. The author is not responsible for any misuse, damage, or illegal activity caused by this tool. Unauthorized testing is a criminal offense in most jurisdictions.

---

## Author
Rehan Muzafar
Offensive Security Researcher | Web App Pentester | CTF Player
