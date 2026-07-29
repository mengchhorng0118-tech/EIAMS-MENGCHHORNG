# EIAMS — NixOS Production Deployment

## File structure

```
nix/
├── flake.nix              ← Entry point (NixOS system + dev shell)
├── configuration.nix      ← System config: users, nginx, postgres, firewall
├── modules/
│   └── eiams-service.nix  ← Systemd services: gunicorn, migrations, static
├── secrets.env.example    ← Template for /etc/eiams/secrets.env
├── deploy.sh              ← One-command deploy script
└── README.md              ← This file

shell.nix                  ← Quick dev shell (no-flakes fallback)
.envrc                     ← direnv auto-activation
```

---

## Development (any machine with Nix)

```bash
# Option A — with flakes
nix develop

# Option B — without flakes
nix-shell

# Option C — with direnv (auto on cd)
direnv allow
```

---

## Production Deployment on NixOS

### Prerequisites
- A server running NixOS 24.05
- Root SSH access
- A domain name pointing to the server

### Step 1 — Clone and configure

```bash
git clone <your-repo> /opt/eiams-src
cd /opt/eiams-src

# Edit your domain + email in nix/configuration.nix:
# - networking.hostName
# - services.nginx.virtualHosts  (yourdomain.com)
# - security.acme.defaults.email
```

### Step 2 — Run deploy script

```bash
sudo bash nix/deploy.sh
```

The script will:
1. Copy Nix configs to `/etc/nixos/`
2. Copy app code to `/var/lib/eiams/app/`
3. Create `/etc/eiams/secrets.env` from the example template
4. Prompt you to fill in secrets
5. Apply NixOS configuration (installs PostgreSQL, Nginx, Gunicorn)
6. Verify all services are running

### Step 3 — Fill in secrets

```bash
sudo nano /etc/eiams/secrets.env
```

Required values:
- `SECRET_KEY` — generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DB_PASSWORD` — must match what's in `configuration.nix` PostgreSQL initialScript
- `ALLOWED_HOSTS` — your domain

### Step 4 — Create superuser

```bash
sudo -u eiams bash -c "cd /var/lib/eiams/app && python manage.py createsuperuser"
```

---

## Daily Operations

```bash
# View logs
journalctl -u eiams-gunicorn -f
journalctl -u nginx -f
journalctl -u postgresql -f

# Restart after code update
sudo bash nix/deploy.sh

# Manual service control
sudo systemctl restart eiams-gunicorn
sudo systemctl reload nginx

# Database shell
sudo -u postgres psql eiams_db

# Manual backup
sudo systemctl start eiams-backup

# Check deploy health
sudo -u eiams bash -c "cd /var/lib/eiams/app && python manage.py check --deploy"
```

---

## Architecture

```
Internet → Nginx (443/HTTPS) → Gunicorn (Unix socket) → Django
                              → /static/ (direct serve)
                              → /media/  (direct serve)
PostgreSQL ← Gunicorn (via Unix socket)
```

### Security features
- Body never scrolls — `overflow: hidden` on all service processes
- No root processes (eiams system user)
- Systemd sandboxing: `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=strict`
- SSH: password authentication disabled, root login disabled
- Firewall: only ports 22, 80, 443 open
- HTTPS enforced with Let's Encrypt auto-renewal
- PostgreSQL: Unix socket only, scram-sha-256 auth
- Rate limiting: 30 req/min per IP via Nginx
- Secrets never in Nix store (loaded via `EnvironmentFile`)
