#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
#  EIAMS Production Deploy Script
#  Run as root on the NixOS server:  sudo bash deploy.sh
#
#  This script:
#   1. Installs Nix with flakes support
#   2. Copies the EIAMS application to /var/lib/eiams/app
#   3. Creates /etc/eiams/secrets.env (if it doesn't exist)
#   4. Applies NixOS configuration
#   5. Starts all services
# ════════════════════════════════════════════════════════════════════

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()  { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN ]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Check root ────────────────────────────────────────────────────────
[[ $EUID -ne 0 ]] && err "Run as root: sudo bash deploy.sh"

APP_SRC="$(cd "$(dirname "$0")/.." && pwd)"   # Parent of nix/
APP_DEST="/var/lib/eiams/app"
NIX_CFG="/etc/nixos"

log "Starting EIAMS deployment from: $APP_SRC"

# ── Step 1: Ensure Nix flakes are enabled ────────────────────────────
mkdir -p /etc/nix
if ! grep -q "experimental-features" /etc/nix/nix.conf 2>/dev/null; then
  echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf
  log "Enabled Nix flakes"
fi

# ── Step 2: Copy NixOS config ─────────────────────────────────────────
log "Copying NixOS configuration to $NIX_CFG ..."
mkdir -p "$NIX_CFG/modules"
cp "$APP_SRC/nix/flake.nix"              "$NIX_CFG/flake.nix"
cp "$APP_SRC/nix/configuration.nix"      "$NIX_CFG/configuration.nix"
cp "$APP_SRC/nix/modules/eiams-service.nix" "$NIX_CFG/modules/eiams-service.nix"

# Generate hardware config if it doesn't exist
if [[ ! -f "$NIX_CFG/hardware-configuration.nix" ]]; then
  warn "hardware-configuration.nix not found — generating ..."
  nixos-generate-config --show-hardware-config > "$NIX_CFG/hardware-configuration.nix"
  log "Generated hardware-configuration.nix — review it before production!"
fi

# ── Step 3: Copy application code ─────────────────────────────────────
log "Deploying application code to $APP_DEST ..."
mkdir -p "$APP_DEST"
rsync -av --delete \
  --exclude='.git' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='*.sqlite3' \
  --exclude='media/' \
  --exclude='nix/' \
  "$APP_SRC/" "$APP_DEST/"

chown -R eiams:eiams "$APP_DEST" || true

# ── Step 4: Create secrets file ───────────────────────────────────────
SECRETS_FILE="/etc/eiams/secrets.env"
if [[ ! -f "$SECRETS_FILE" ]]; then
  mkdir -p /etc/eiams
  cp "$APP_SRC/nix/secrets.env.example" "$SECRETS_FILE"
  chmod 600 "$SECRETS_FILE"
  chown eiams:eiams "$SECRETS_FILE"
  warn "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  warn " SECRETS FILE CREATED: $SECRETS_FILE"
  warn " Edit it now before continuing:"
  warn "   nano $SECRETS_FILE"
  warn "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  read -rp "Press ENTER after editing secrets.env to continue..."
else
  log "Secrets file already exists at $SECRETS_FILE"
fi

# ── Step 5: Apply NixOS configuration ─────────────────────────────────
log "Applying NixOS configuration (this may take several minutes) ..."
nixos-rebuild switch --flake "$NIX_CFG#eiams-server"

# ── Step 6: Verify services ───────────────────────────────────────────
log "Checking service status ..."
sleep 3

SERVICES=("postgresql" "nginx" "eiams-gunicorn")
ALL_OK=true
for svc in "${SERVICES[@]}"; do
  if systemctl is-active --quiet "$svc"; then
    log "  ✓ $svc"
  else
    err "  ✗ $svc is NOT running. Check: journalctl -xe -u $svc"
    ALL_OK=false
  fi
done

if $ALL_OK; then
  log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  log " EIAMS deployed successfully!"
  log " Access: https://eiams.yourdomain.com"
  log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi
