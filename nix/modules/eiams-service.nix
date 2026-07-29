{ config, pkgs, lib, ... }:

# ════════════════════════════════════════════════════════════════════
#  EIAMS Systemd Service Module
#  Manages:
#   - Gunicorn WSGI server (Django)
#   - Static file collection
#   - Database migration on deploy
#   - Environment variable injection from secrets file
# ════════════════════════════════════════════════════════════════════

let
  # Python with all EIAMS dependencies
  python = pkgs.python312.withPackages (ps: with ps; [
    django               # 4.2.x
    pillow               # Image processing
    reportlab            # PDF generation
    openpyxl             # Excel export
    xlsxwriter
    python-dateutil
    python-decouple      # .env file support
    psycopg2             # PostgreSQL driver
    gunicorn             # WSGI server
    django-crispy-forms
    crispy-bootstrap5
    django-widget-tweaks
    qrcode
    python-barcode
    django-cors-headers
    whitenoise           # Static files in production
  ]);

  # Application directory
  appDir   = "/var/lib/eiams/app";
  staticDir = "/var/lib/eiams/static";
  mediaDir  = "/var/lib/eiams/media";
  logDir    = "/var/log/eiams";
  sockDir   = "/run/eiams";

in
{
  # ── Runtime directories ───────────────────────────────────────────
  systemd.tmpfiles.rules = [
    "d ${appDir}    0750 eiams eiams -"
    "d ${staticDir} 0755 eiams nginx -"
    "d ${mediaDir}  0755 eiams nginx -"
    "d ${logDir}    0755 eiams eiams -"
    "d ${sockDir}   0750 eiams nginx -"
  ];

  # ── Gunicorn WSGI service ─────────────────────────────────────────
  systemd.services.eiams-gunicorn = {
    description   = "EIAMS Gunicorn WSGI Server";
    documentation = [ "https://docs.djangoproject.com" ];
    after         = [ "network.target" "postgresql.service" ];
    requires      = [ "postgresql.service" ];
    wantedBy      = [ "multi-user.target" ];

    environment = {
      DJANGO_SETTINGS_MODULE = "inventory_system.settings";
      PYTHONPATH             = appDir;
    };

    # Secrets loaded from /etc/eiams/secrets.env (never in Nix store)
    # Format: KEY=value  (one per line, no quotes needed)
    serviceConfig = {
      Type            = "notify";
      User            = "eiams";
      Group           = "eiams";
      WorkingDirectory = appDir;

      # Load secrets from encrypted file
      EnvironmentFile = "/etc/eiams/secrets.env";

      ExecStartPre = [
        # Collect static files
        "${python}/bin/python ${appDir}/manage.py collectstatic --noinput --clear"
        # Run migrations
        "${python}/bin/python ${appDir}/manage.py migrate --noinput"
        # Compile translations
        "${python}/bin/python ${appDir}/manage.py compilemessages --ignore=.venv"
      ];

      ExecStart = ''
        ${python}/bin/gunicorn \
          --name eiams \
          --workers 4 \
          --worker-class gthread \
          --threads 2 \
          --bind unix:${sockDir}/gunicorn.sock \
          --log-level info \
          --access-logfile ${logDir}/access.log \
          --error-logfile  ${logDir}/error.log \
          --timeout 120 \
          --graceful-timeout 30 \
          --max-requests 1000 \
          --max-requests-jitter 50 \
          --forwarded-allow-ips="127.0.0.1" \
          inventory_system.wsgi:application
      '';

      ExecReload    = "${pkgs.coreutils}/bin/kill -HUP $MAINPID";
      ExecStop      = "${pkgs.coreutils}/bin/kill -TERM $MAINPID";
      KillMode      = "mixed";
      TimeoutStopSec = 30;
      Restart        = "on-failure";
      RestartSec     = "5s";

      # ── Systemd hardening ──────────────────────────────────────
      NoNewPrivileges       = true;
      PrivateTmp            = true;
      ProtectSystem         = "strict";
      ProtectHome           = true;
      ReadWritePaths        = [ appDir staticDir mediaDir logDir sockDir "/tmp" ];
      PrivateDevices        = true;
      ProtectKernelTunables = true;
      ProtectKernelModules  = true;
      ProtectControlGroups  = true;
      RestrictNamespaces    = true;
      LockPersonality       = true;
      RestrictRealtime      = true;
      SystemCallFilter      = "@system-service";
      SystemCallErrorNumber = "EPERM";
      CapabilityBoundingSet = "";
      AmbientCapabilities   = "";
    };
  };

  # ── Deployment helper service (run on each nixos-rebuild) ─────────
  systemd.services.eiams-deploy = {
    description   = "EIAMS Post-Deploy Tasks";
    after         = [ "eiams-gunicorn.service" ];
    serviceConfig = {
      Type             = "oneshot";
      User             = "eiams";
      WorkingDirectory = appDir;
      EnvironmentFile  = "/etc/eiams/secrets.env";
      ExecStart        = ''
        ${python}/bin/python ${appDir}/manage.py check --deploy
      '';
      RemainAfterExit = true;
    };
  };
}
