# apps/inventory/barcodes.py
"""
Barcode & QR Code Generation Utilities — EIAMS
===============================================

Provides helper functions that generate barcode and QR code images
and return them as base64-encoded PNG strings suitable for embedding
directly in HTML <img> tags without writing any files to disk.

Functions
---------
generate_qr(data, size=10, border=2)
    Generate a QR code PNG and return as a base64 data-URI string.

generate_barcode(value, barcode_class='code128')
    Generate a Code128 barcode SVG/PNG and return as a base64 data-URI.

Dependencies
------------
    qrcode[pil]==8.0
    python-barcode==0.15.1
    Pillow (pulled in by qrcode[pil])
"""

from __future__ import annotations

import base64
import io
import logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# QR Code
# ─────────────────────────────────────────────────────────────────────────────

def generate_qr(data: str, size: int = 10, border: int = 2) -> str | None:
    """
    Generate a QR code for *data* and return a base64 PNG data-URI.

    Parameters
    ----------
    data : str
        The content to encode — typically a URL, item code, or asset code.
    size : int
        Box size in pixels per QR module.  Default 10.
    border : int
        Number of quiet-zone modules around the QR matrix.  Default 2.

    Returns
    -------
    str or None
        ``"data:image/png;base64,<...>"`` ready for use in an <img src>.
        Returns ``None`` if generation fails (logs the error).
    """
    try:
        import qrcode
        from qrcode.image.pure import PyPNGImage

        qr = qrcode.QRCode(
            version=None,               # auto-size
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Use the PIL backend when Pillow is available, fall back to pure PNG
        try:
            from PIL import Image as _PilImg  # noqa: F401 — availability check
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
        except ImportError:
            img = qr.make_image(image_factory=PyPNGImage)
            buffer = io.BytesIO()
            img.save(buffer)

        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    except Exception as exc:
        logger.error("QR generation failed for data=%r: %s", data, exc)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Barcode (Code 128)
# ─────────────────────────────────────────────────────────────────────────────

def generate_barcode(value: str) -> str | None:
    """
    Generate a Code128 barcode for *value* and return a base64 PNG data-URI.

    Code128 can encode any printable ASCII string, making it suitable for
    both ``item_code`` (e.g. ``INV-0001``) and ``barcode`` field values.

    Parameters
    ----------
    value : str
        The string to encode in the barcode.

    Returns
    -------
    str or None
        ``"data:image/png;base64,<...>"`` ready for use in an <img src>.
        Returns ``None`` if generation fails (logs the error).
    """
    if not value:
        return None
    try:
        import barcode
        from barcode.writer import ImageWriter

        CODE128 = barcode.get_barcode_class("code128")
        buffer  = io.BytesIO()
        CODE128(
            value,
            writer=ImageWriter(),
        ).write(
            buffer,
            options={
                "module_height": 10.0,   # bar height in mm
                "module_width":  0.2,    # bar width scaling
                "quiet_zone":    3.0,    # quiet zones on left/right
                "font_size":     8,      # text size below bars
                "text_distance": 3.5,    # gap between bars and text
                "background":    "white",
                "foreground":    "black",
                "write_text":    True,
            },
        )
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    except Exception as exc:
        logger.error("Barcode generation failed for value=%r: %s", value, exc)
        return None
