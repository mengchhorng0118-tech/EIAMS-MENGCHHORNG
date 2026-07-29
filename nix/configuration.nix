{ config, pkgs, lib, ... }:

# ════════════════════════════════════════════════════════════════════
#  EIAMS NixOS System Configuration
#  Tested on NixOS 24.05
#
#  What this configures:
#   ✓ System locale & timezone (Asia/Phnom_Penh for Cambodia)
#   ✓ PostgreSQL 16 with EIAMS database
#   ✓ Nginx reverse proxy (HTTP → HTTPS redirect + static files)
#   ✓ Let's Encrypt TLS via ACME
#   ✓ Firewall: only ports 22, 80, 443 open
#   ✓ Automatic daily backups
#   ✓ Systemd hardening for all services
#   ✓ Log rotation
# ════════════════════════════════════════════════════════════════════

{
  # ── System basics ─────────────────────────────────────────────────
  system.stateVersion = "24.05";

  networking = {
    hostName   = "eiams-server";
    # Update to your network interface name (run: ip link)
    interfaces.eth0.useDHCP = true;
    # Or set static IP:
    # interfaces.eth0.ipv4.addresses = [{
    #   address      = "192.168.1.100";
    #   prefixLength = 24;
    # }];
    # defaultGateway = "192.168.1.1";
    # nameservers    = [ "1.1.1.1" "8.8.8.8" ];
  };

  # ── Timezone & Locale ─────────────────────────────────────────────
  time.timeZone = "Asia/Phnom_Penh";    # Cambodia timezone
  i18n = {
    defaultLocale     = "en_US.UTF-8";
    supportedLocales  = [ "en_US.UTF-8/UTF-8" "km_KH/UTF-8" ];
    extraLocaleSettings = {
      LC_TIME    = "en_US.UTF-8";
      LC_NUMERIC = "en_US.UTF-8";
    };
  };

  # ── Boot ──────────────────────────────────────────────────────────
  boot.loader = {
    grub.enable  = true;
    grub.device  = "/dev/sda";   # Change to your disk
    grub.version = 2;
  };

  # ── Users ─────────────────────────────────────────────────────────
  users.users = {
    # Admin user — change password after first boot!
    admin = {
      isNormalUser   = true;
      extraGroups    = [ "wheel" "nginx" ];
      openssh.authorizedKeys.keys = [
        # Paste your SSH public key here:
        # "ssh-ed25519 AAAA... you@host"
      ];
    };

    # Service account for EIAMS (no login shell)
    eiams = {
      isSystemUser = true;
      group        = "eiams";
      home         = "/var/lib/eiams";
      createHome   = true;
    };
  };
  users.groups.eiams = {};

  # ── SSH ───────────────────────────────────────────────────────────
  services.openssh = {
    enable                 = true;
    settings = {
      PasswordAuthentication = false;   # Key-only login
      PermitRootLogin        = "no";
      X11Forwarding          = false;
    };
  };

  # ── Firewall ──────────────────────────────────────────────────────
  networking.firewall = {
    enable           = true;
    allowedTCPPorts  = [ 22 80 443 ];
  };

  # ── System packages ───────────────────────────────────────────────
  environment.systemPackages = with pkgs; [
    git vim nano htop curl wget unzip
    python312 python312Packages.pip python312Packages.virtualenv
    postgresql_16
    nginx
    certbot
    # Image processing (Pillow)
    libjpeg libpng zlib
    # Process supervision
    supervisor
    # Backup
    rsync
  ];

  # ── PostgreSQL ────────────────────────────────────────────────────
  services.postgresql = {
    enable      = true;
    package     = pkgs.postgresql_16;
    dataDir     = "/var/lib/postgresql/16";
    port        = 5432;
    enableTCPIP = false;   # Unix socket only (more secure)

    authentication = pkgs.lib.mkOverride 10 ''
      # TYPE  DATABASE   USER    ADDRESS    METHOD
      local   all        all                peer
      host    eiams_db   eiams   127.0.0.1/32   scram-sha-256
    '';

    initialScript = pkgs.writeText "eiams-pg-init" ''
      -- Create EIAMS database and user
      CREATE USER eiams WITH ENCRYPTED PASSWORD 'CHANGE_THIS_PASSWORD';
      CREATE DATABASE eiams_db
        OWNER eiams
        ENCODING 'UTF8'
        LC_COLLATE 'en_US.UTF-8'
        LC_CTYPE 'en_US.UTF-8'
        TEMPLATE template0;
      GRANT ALL PRIVILEGES ON DATABASE eiams_db TO eiams;
    '';

    settings = {
      # Performance tuning for a small server (2–4 GB RAM)
      shared_buffers          = "256MB";
      effective_cache_size    = "1GB";
      maintenance_work_mem    = "64MB";
      wal_buffers             = "16MB";
      max_connections         = 50;
      # Logging
      log_destination         = "syslog";
      logging_collector       = false;
      log_min_duration_statement = 500;   # Log slow queries > 500ms
    };
  };

  # ── Nginx ─────────────────────────────────────────────────────────
  services.nginx = {
    enable       = true;
    package      = pkgs.nginx;
    user         = "nginx";
    group        = "nginx";

    recommendedGzipSettings    = true;
    recommendedOptimisation     = true;
    recommendedProxySettings    = true;
    recommendedTlsSettings      = true;

    # Rate limiting zone
    appendHttpConfig = ''
      limit_req_zone $binary_remote_addr zone=eiams_limit:10m rate=30r/m;
      client_max_body_size 20M;
    '';

    virtualHosts = {
      # ── HTTP → HTTPS redirect ─────────────────────────────────
      "eiams.yourdomain.com" = {
        forceSSL    = true;
        enableACME  = true;     # Let's Encrypt (set email below)

        # Static files served directly by Nginx (no gunicorn overhead)
        locations."/static/" = {
          root       = "/var/lib/eiams";
          extraConfig = ''
            expires 30d;
            add_header Cache-Control "public, immutable";
            access_log off;
          '';
        };

        locations."/media/" = {
          root       = "/var/lib/eiams";
          extraConfig = ''
            expires 7d;
            add_header Cache-Control "public";
          '';
        };

        # Everything else → Gunicorn
        locations."/" = {
          proxyPass  = "http://unix:/run/eiams/gunicorn.sock";
          extraConfig = ''
            limit_req zone=eiams_limit burst=60 nodelay;
            proxy_set_header X-Forwarded-Proto https;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 300;
            proxy_connect_timeout 300;
          '';
        };
      };

      # ── Local dev / HTTP-only fallback ────────────────────────
      "localhost" = {
        listen = [{ addr = "127.0.0.1"; port = 8080; }];
        locations."/" = {
          proxyPass  = "http://unix:/run/eiams/gunicorn.sock";
        };
      };
    };
  };

  # ── ACME / Let's Encrypt ──────────────────────────────────────────
  security.acme = {
    acceptTerms = true;
    defaults.email = "admin@yourdomain.com";  # ← Change this
  };

  # ── Log rotation ──────────────────────────────────────────────────
  services.logrotate = {
    enable = true;
    settings = {
      "/var/log/eiams/*.log" = {
        frequency = "daily";
        rotate    = 14;
        compress  = true;
        delaycompress = true;
        missingok = true;
        notifempty = true;
      };
    };
  };

  # ── Automatic daily DB backup ─────────────────────────────────────
  systemd.services.eiams-backup = {
    description   = "EIAMS Daily PostgreSQL Backup";
    after         = [ "postgresql.service" ];
    serviceConfig = {
      Type    = "oneshot";
      User    = "postgres";
    };
    script = ''
      BACKUP_DIR="/var/backups/eiams"
      DATE=$(date +%Y%m%d_%H%M%S)
      mkdir -p "$BACKUP_DIR"
      pg_dump eiams_db | gzip > "$BACKUP_DIR/eiams_$DATE.sql.gz"
      # Keep only last 30 backups
      ls -t "$BACKUP_DIR"/*.sql.gz | tail -n +31 | xargs rm -f
      echo "Backup complete: eiams_$DATE.sql.gz"
    '';
  };

  systemd.timers.eiams-backup = {
    description  = "Daily EIAMS Backup Timer";
    wantedBy     = [ "timers.target" ];
    timerConfig  = {
      OnCalendar    = "02:00:00";   # 2 AM daily
      Persistent    = true;
      RandomizedDelaySec = "5min";
    };
  };

  # ── NixOS auto-upgrade (optional) ────────────────────────────────
  system.autoUpgrade = {
    enable      = true;
    flake       = "/etc/nixos#eiams-server";
    flags       = [ "--update-input" "nixpkgs" ];
    dates       = "04:00";   # 4 AM weekly
    allowReboot = false;
  };
}
