# ════════════════════════════════════════════════════════════════════
#  EIAMS — Nix Development Shell (no-flakes fallback)
#  Usage: nix-shell   (or use direnv: echo "use nix" > .envrc)
#
#  Provides: Python 3.12, pip, virtualenv, PostgreSQL client,
#            all system libraries needed by Pillow/reportlab/etc.
# ════════════════════════════════════════════════════════════════════

let
  pkgs = import <nixpkgs> { };
in
pkgs.mkShell {
  name = "eiams-dev";

  nativeBuildInputs = with pkgs; [
    # Python
    python312
    python312Packages.pip
    python312Packages.virtualenv

    # C libraries required by Python packages
    zlib zlib.dev
    libjpeg libjpeg.dev
    libpng libpng.dev
    freetype freetype.dev
    gcc
    gnumake
    pkg-config

    # Database client (for psql CLI, pg_dump)
    postgresql_16

    # Image preview / QR testing
    qrencode

    # Dev tools
    git
    curl
    jq
  ];

  # Ensure pip can find C libraries
  LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
    zlib libjpeg libpng freetype
  ];

  shellHook = ''
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo " EIAMS Development Shell (Python $(python --version 2>&1 | cut -d' ' -f2))"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Create and activate virtual environment
    if [ ! -d ".venv" ]; then
      python -m venv .venv
      echo " Created .venv"
    fi
    source .venv/bin/activate

    # Install dependencies
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt

    echo " Virtualenv: .venv  (activated)"
    echo " Database:   SQLite (dev) / PostgreSQL (production)"
    echo ""
    echo " Quick commands:"
    echo "   python manage.py runserver      # Start dev server"
    echo "   python manage.py migrate        # Apply migrations"
    echo "   python manage.py seed_data      # Load sample data"
    echo "   python manage.py createsuperuser"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  '';
}
