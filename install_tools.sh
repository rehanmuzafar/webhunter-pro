#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║     WebHunter Pro v2.0 — Tool Installer                         ║
# ║     Parrot OS 7.1 ARM64                                         ║
# ╚══════════════════════════════════════════════════════════════════╝

RED='\033[91m'; GREEN='\033[92m'; YELLOW='\033[93m'
CYAN='\033[96m'; ORANGE='\033[38;5;208m'; BOLD='\033[1m'; RESET='\033[0m'

ok()    { echo -e "${GREEN}[+]${RESET} $1"; }
info()  { echo -e "${CYAN}[*]${RESET} $1"; }
warn()  { echo -e "${YELLOW}[!]${RESET} $1"; }
err()   { echo -e "${RED}[-]${RESET} $1"; }
phase() { echo -e "\n${ORANGE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
          echo -e "${ORANGE}${BOLD}  ★  $1${RESET}"
          echo -e "${ORANGE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"; }

TOOLS_DIR="$HOME/tools"
mkdir -p "$TOOLS_DIR"

echo -e "${RED}${BOLD}"
cat << 'EOF'
 ██╗    ██╗███████╗██████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗
 ██║    ██║██╔════╝██╔══██╗██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
 ██║ █╗ ██║█████╗  ██████╔╝███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
 ██║███╗██║██╔══╝  ██╔══██╗██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
 ╚███╔███╔╝███████╗██████╔╝██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
  ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
EOF
echo -e "${RESET}${CYAN}              Tool Installer — Parrot OS 7.1 ARM64${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"

# ── Check root ─────────────────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    err "Please run as root: sudo bash install_tools.sh"
    exit 1
fi

ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(eval echo "~$ACTUAL_USER")
TOOLS_DIR="$ACTUAL_HOME/tools"
mkdir -p "$TOOLS_DIR"

# ── PHASE 1: System Update & Base Deps ────────────────────────────────────────
phase "PHASE 1: SYSTEM UPDATE & BASE DEPENDENCIES"

info "Updating package lists..."
apt-get update -qq

info "Installing base dependencies..."
apt-get install -y -qq \
    git curl wget python3 python3-pip python3-venv \
    golang-go ruby ruby-dev build-essential \
    libssl-dev libffi-dev libxml2-dev libxslt1-dev \
    zlib1g-dev libjpeg-dev libpng-dev \
    nmap nikto wfuzz sqlmap \
    jq unzip tar net-tools dnsutils whois \
    chromium chromium-driver 2>/dev/null

ok "Base dependencies installed"

# ── Setup Go PATH ──────────────────────────────────────────────────────────────
export GOPATH="$ACTUAL_HOME/go"
export PATH="$PATH:$GOPATH/bin:/usr/local/go/bin"

# Add to .bashrc & .zshrc permanently
for rc in "$ACTUAL_HOME/.bashrc" "$ACTUAL_HOME/.zshrc"; do
    if [ -f "$rc" ]; then
        grep -q 'GOPATH' "$rc" || echo -e '\nexport GOPATH=$HOME/go\nexport PATH=$PATH:$GOPATH/bin:/usr/local/go/bin' >> "$rc"
    fi
done

# Check Go version
GO_VERSION=$(go version 2>/dev/null | awk '{print $3}')
if [ -z "$GO_VERSION" ]; then
    warn "Go not found — installing latest Go for ARM64..."
    wget -q https://go.dev/dl/go1.22.0.linux-arm64.tar.gz -O /tmp/go.tar.gz
    rm -rf /usr/local/go
    tar -C /usr/local -xzf /tmp/go.tar.gz
    export PATH=$PATH:/usr/local/go/bin
    ok "Go installed: $(go version)"
else
    ok "Go found: $GO_VERSION"
fi

mkdir -p "$ACTUAL_HOME/go/bin"

# ── Helper: run as actual user ─────────────────────────────────────────────────
run_as_user() {
    sudo -u "$ACTUAL_USER" env PATH="$PATH" GOPATH="$GOPATH" HOME="$ACTUAL_HOME" bash -c "$1"
}

# ── PHASE 2: Go-based Tools (ProjectDiscovery) ────────────────────────────────
phase "PHASE 2: GO TOOLS — PROJECTDISCOVERY SUITE"

GO_TOOLS=(
    "subfinder:go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    "httpx:go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"
    "katana:go install github.com/projectdiscovery/katana/cmd/katana@latest"
    "nuclei:go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
    "dnsx:go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
    "naabu:go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
    "notify:go install -v github.com/projectdiscovery/notify/cmd/notify@latest"
    "interactsh-client:go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest"
)

for entry in "${GO_TOOLS[@]}"; do
    name="${entry%%:*}"
    cmd="${entry#*:}"
    if command -v "$name" &>/dev/null; then
        ok "$name already installed"
    else
        info "Installing $name..."
        run_as_user "$cmd" && ok "$name installed" || err "$name failed"
    fi
done

phase "PHASE 3: MORE GO TOOLS"

MORE_GO_TOOLS=(
    "waybackurls:go install github.com/tomnomnom/waybackurls@latest"
    "gau:go install github.com/lc/gau/v2/cmd/gau@latest"
    "assetfinder:go install github.com/tomnomnom/assetfinder@latest"
    "ffuf:go install github.com/ffufproject/ffuf/v2@latest"
    "gobuster:go install github.com/OJ/gobuster/v3@latest"
    "dalfox:go install github.com/hahwul/dalfox/v2@latest"
    "hakrawler:go install github.com/hakluke/hakrawler@latest"
    "gospider:go install github.com/jaeles-project/gospider@latest"
    "anew:go install github.com/tomnomnom/anew@latest"
    "qsreplace:go install github.com/tomnomnom/qsreplace@latest"
    "gf:go install github.com/tomnomnom/gf@latest"
    "httprobe:go install github.com/tomnomnom/httprobe@latest"
    "meg:go install github.com/tomnomnom/meg@latest"
)

for entry in "${MORE_GO_TOOLS[@]}"; do
    name="${entry%%:*}"
    cmd="${entry#*:}"
    if command -v "$name" &>/dev/null; then
        ok "$name already installed"
    else
        info "Installing $name..."
        run_as_user "$cmd" && ok "$name installed" || err "$name failed"
    fi
done

# ── PHASE 4: Python Tools ─────────────────────────────────────────────────────
phase "PHASE 4: PYTHON TOOLS"

info "Installing Python packages globally..."
pip3 install --break-system-packages -q \
    sqlmap arjun paramspider \
    requests beautifulsoup4 lxml \
    urllib3 colorama tqdm \
    jwt pycryptodome 2>/dev/null
ok "Python packages installed"

# XSStrike
if [ ! -d "$TOOLS_DIR/XSStrike" ]; then
    info "Cloning XSStrike..."
    run_as_user "git clone -q https://github.com/s0md3v/XSStrike.git $TOOLS_DIR/XSStrike"
    pip3 install --break-system-packages -q -r "$TOOLS_DIR/XSStrike/requirements.txt" 2>/dev/null
    # Create symlink
    ln -sf "$TOOLS_DIR/XSStrike/xsstrike.py" /usr/local/bin/xsstrike
    ok "XSStrike installed → $TOOLS_DIR/XSStrike"
else
    ok "XSStrike already exists"
fi

# SSRFmap
if [ ! -d "$TOOLS_DIR/SSRFmap" ]; then
    info "Cloning SSRFmap..."
    run_as_user "git clone -q https://github.com/swisskyrepo/SSRFmap.git $TOOLS_DIR/SSRFmap"
    pip3 install --break-system-packages -q -r "$TOOLS_DIR/SSRFmap/requirements.txt" 2>/dev/null
    ln -sf "$TOOLS_DIR/SSRFmap/ssrfmap.py" /usr/local/bin/ssrfmap
    ok "SSRFmap installed → $TOOLS_DIR/SSRFmap"
else
    ok "SSRFmap already exists"
fi

# commix
if [ ! -d "$TOOLS_DIR/commix" ]; then
    info "Cloning commix..."
    run_as_user "git clone -q https://github.com/commixproject/commix.git $TOOLS_DIR/commix"
    ln -sf "$TOOLS_DIR/commix/commix.py" /usr/local/bin/commix
    ok "commix installed → $TOOLS_DIR/commix"
else
    ok "commix already exists"
fi

# tplmap (SSTI)
if [ ! -d "$TOOLS_DIR/tplmap" ]; then
    info "Cloning tplmap (SSTI)..."
    run_as_user "git clone -q https://github.com/epinna/tplmap.git $TOOLS_DIR/tplmap"
    pip3 install --break-system-packages -q -r "$TOOLS_DIR/tplmap/requirements.txt" 2>/dev/null
    ln -sf "$TOOLS_DIR/tplmap/tplmap.py" /usr/local/bin/tplmap
    ok "tplmap installed → $TOOLS_DIR/tplmap"
else
    ok "tplmap already exists"
fi

# Corsy (CORS)
if [ ! -d "$TOOLS_DIR/Corsy" ]; then
    info "Cloning Corsy (CORS)..."
    run_as_user "git clone -q https://github.com/s0md3v/Corsy.git $TOOLS_DIR/Corsy"
    pip3 install --break-system-packages -q -r "$TOOLS_DIR/Corsy/requirements.txt" 2>/dev/null
    ln -sf "$TOOLS_DIR/Corsy/corsy.py" /usr/local/bin/corsy
    ok "Corsy installed → $TOOLS_DIR/Corsy"
else
    ok "Corsy already exists"
fi

# jwt_tool
if [ ! -d "$TOOLS_DIR/jwt_tool" ]; then
    info "Cloning jwt_tool..."
    run_as_user "git clone -q https://github.com/ticarpi/jwt_tool.git $TOOLS_DIR/jwt_tool"
    pip3 install --break-system-packages -q -r "$TOOLS_DIR/jwt_tool/requirements.txt" 2>/dev/null
    ln -sf "$TOOLS_DIR/jwt_tool/jwt_tool.py" /usr/local/bin/jwt_tool
    ok "jwt_tool installed → $TOOLS_DIR/jwt_tool"
else
    ok "jwt_tool already exists"
fi

# SecretFinder
if [ ! -d "$TOOLS_DIR/SecretFinder" ]; then
    info "Cloning SecretFinder..."
    run_as_user "git clone -q https://github.com/m4ll0k/SecretFinder.git $TOOLS_DIR/SecretFinder"
    pip3 install --break-system-packages -q -r "$TOOLS_DIR/SecretFinder/requirements.txt" 2>/dev/null
    ln -sf "$TOOLS_DIR/SecretFinder/SecretFinder.py" /usr/local/bin/secretfinder
    ok "SecretFinder installed → $TOOLS_DIR/SecretFinder"
else
    ok "SecretFinder already exists"
fi

# LinkFinder
if [ ! -d "$TOOLS_DIR/LinkFinder" ]; then
    info "Cloning LinkFinder..."
    run_as_user "git clone -q https://github.com/GerbenJavado/LinkFinder.git $TOOLS_DIR/LinkFinder"
    pip3 install --break-system-packages -q -r "$TOOLS_DIR/LinkFinder/requirements.txt" 2>/dev/null
    ln -sf "$TOOLS_DIR/LinkFinder/linkfinder.py" /usr/local/bin/linkfinder
    ok "LinkFinder installed → $TOOLS_DIR/LinkFinder"
else
    ok "LinkFinder already exists"
fi

# LFISuite
if [ ! -d "$TOOLS_DIR/LFISuite" ]; then
    info "Cloning LFISuite..."
    run_as_user "git clone -q https://github.com/D35m0nd142/LFISuite.git $TOOLS_DIR/LFISuite"
    ln -sf "$TOOLS_DIR/LFISuite/lfisuite.py" /usr/local/bin/lfisuite
    ok "LFISuite installed → $TOOLS_DIR/LFISuite"
else
    ok "LFISuite already exists"
fi

# ── PHASE 5: Nuclei Templates ─────────────────────────────────────────────────
phase "PHASE 5: NUCLEI TEMPLATES"

if command -v nuclei &>/dev/null; then
    info "Downloading/updating nuclei templates..."
    run_as_user "nuclei -update-templates -silent"
    ok "Nuclei templates updated"
else
    warn "nuclei not found — skipping template update"
fi

# GF Patterns (for gf tool)
if command -v gf &>/dev/null; then
    info "Installing gf patterns..."
    GF_DIR="$ACTUAL_HOME/.gf"
    mkdir -p "$GF_DIR"
    if [ ! -d "$TOOLS_DIR/Gf-Patterns" ]; then
        run_as_user "git clone -q https://github.com/1ndianl33t/Gf-Patterns.git $TOOLS_DIR/Gf-Patterns"
        cp "$TOOLS_DIR/Gf-Patterns/"*.json "$GF_DIR/" 2>/dev/null
    fi
    ok "GF patterns installed → $GF_DIR"
fi

# ── PHASE 6: Wordlists ────────────────────────────────────────────────────────
phase "PHASE 6: WORDLISTS"

WORDLIST_DIR="/usr/share/wordlists"
mkdir -p "$WORDLIST_DIR"

if [ ! -d "$WORDLIST_DIR/seclists" ]; then
    info "Installing SecLists (this may take a while)..."
    apt-get install -y -qq seclists 2>/dev/null || \
    run_as_user "git clone -q --depth 1 https://github.com/danielmiessler/SecLists.git $WORDLIST_DIR/seclists"
    ok "SecLists installed"
else
    ok "SecLists already exists"
fi

# Unzip rockyou if needed
if [ -f "$WORDLIST_DIR/rockyou.txt.gz" ] && [ ! -f "$WORDLIST_DIR/rockyou.txt" ]; then
    info "Extracting rockyou.txt..."
    gunzip "$WORDLIST_DIR/rockyou.txt.gz"
    ok "rockyou.txt extracted"
fi

# ── PHASE 7: Fix Permissions ──────────────────────────────────────────────────
phase "PHASE 7: FIXING PERMISSIONS"

chown -R "$ACTUAL_USER:$ACTUAL_USER" "$TOOLS_DIR" 2>/dev/null
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$ACTUAL_HOME/go" 2>/dev/null
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$ACTUAL_HOME/.gf" 2>/dev/null
chmod +x /usr/local/bin/xsstrike /usr/local/bin/ssrfmap /usr/local/bin/commix \
         /usr/local/bin/tplmap /usr/local/bin/corsy /usr/local/bin/jwt_tool \
         /usr/local/bin/secretfinder /usr/local/bin/linkfinder /usr/local/bin/lfisuite 2>/dev/null
ok "Permissions fixed"

# ── FINAL: Tool Status ────────────────────────────────────────────────────────
phase "INSTALLATION COMPLETE — TOOL STATUS"

TOOLS_CHECK=(
    subfinder httpx katana nuclei dnsx naabu
    waybackurls gau assetfinder ffuf gobuster
    dalfox hakrawler gospider anew gf
    sqlmap nikto nmap wfuzz
    xsstrike ssrfmap commix tplmap
    corsy jwt_tool secretfinder linkfinder lfisuite
)

FOUND=0; MISSING=0
echo ""
for tool in "${TOOLS_CHECK[@]}"; do
    if command -v "$tool" &>/dev/null; then
        echo -e "  ${GREEN}[✓]${RESET} $tool"
        ((FOUND++))
    else
        echo -e "  ${RED}[✗]${RESET} $tool"
        ((MISSING++))
    fi
done

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  ${GREEN}Installed : $FOUND tools${RESET}"
echo -e "  ${RED}Missing   : $MISSING tools${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "  ${YELLOW}Reload your shell:${RESET}"
echo -e "  ${BOLD}source ~/.bashrc${RESET}  or  ${BOLD}source ~/.zshrc${RESET}"
echo ""
echo -e "  ${GREEN}Then run WebHunter Pro:${RESET}"
echo -e "  ${BOLD}python3 WebHunter.py -d example.com${RESET}"
echo ""
