"""
accessibility.py — WCAG 2.1 AA+ Accessibility Utilities

Provides accessibility features including skip navigation, ARIA
landmark injection, high-contrast mode toggle, screen reader
announcements, and keyboard navigation helpers.
"""

from typing import Optional


# ---------------------------------------------------------------------------
# Skip Navigation
# ---------------------------------------------------------------------------

SKIP_NAV_HTML: str = """
<a href="#main-content" class="skip-nav" aria-label="Skip to main content">
    Skip to main content
</a>
"""
"""HTML for the skip-navigation link, hidden visually but accessible."""


SKIP_NAV_CSS: str = """
<style>
.skip-nav {
    position: absolute;
    top: -40px;
    left: 0;
    background: #f59e0b;
    color: #000000;
    padding: 8px 16px;
    z-index: 10000;
    font-weight: 700;
    font-size: 0.9rem;
    text-decoration: none;
    border-radius: 0 0 8px 0;
    transition: top 0.2s ease;
}
.skip-nav:focus {
    top: 0;
    outline: 3px solid #38bdf8;
    outline-offset: 2px;
}

/* High contrast mode overrides */
.high-contrast * {
    border-color: #ffffff !important;
}
.high-contrast .feat-card,
.high-contrast .stat-box,
.high-contrast .icon-card,
.high-contrast .myth-card,
.high-contrast .step-item,
.high-contrast .party-card {
    border: 2px solid #ffffff !important;
    background: #000000 !important;
}
.high-contrast .hero-title {
    -webkit-text-fill-color: #fbbf24 !important;
}
.high-contrast p, .high-contrast span, .high-contrast div {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Focus indicator enhancement */
*:focus-visible {
    outline: 3px solid #f59e0b !important;
    outline-offset: 2px !important;
}

/* Reduced motion preference */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Screen reader only utility */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}
</style>
"""
"""CSS for skip-navigation, high-contrast mode, and reduced motion."""


# ---------------------------------------------------------------------------
# ARIA Landmarks
# ---------------------------------------------------------------------------

def get_main_content_wrapper(content_html: str) -> str:
    """Wrap content in a main ARIA landmark with proper ID.

    Args:
        content_html: The HTML content to wrap.

    Returns:
        HTML string with ``<main>`` landmark and ``id="main-content"``.

    Examples:
        >>> html = get_main_content_wrapper("<p>Hello</p>")
        >>> assert 'id="main-content"' in html
        >>> assert 'role="main"' in html
    """
    return (
        f'<main id="main-content" role="main" '
        f'aria-label="Primary content">'
        f'{content_html}</main>'
    )


def get_nav_landmark(nav_html: str, label: str = "Primary navigation") -> str:
    """Wrap content in a navigation ARIA landmark.

    Args:
        nav_html: The navigation HTML content.
        label: Accessible label for the navigation region.

    Returns:
        HTML string with ``<nav>`` landmark and ARIA label.

    Examples:
        >>> html = get_nav_landmark("<ul><li>Home</li></ul>")
        >>> assert 'role="navigation"' in html
    """
    return (
        f'<nav role="navigation" aria-label="{label}">'
        f'{nav_html}</nav>'
    )


def get_live_region(message: str, politeness: str = "polite") -> str:
    """Create a live region for screen reader announcements.

    Args:
        message: The announcement text.
        politeness: ARIA live politeness level (``"polite"`` or ``"assertive"``).

    Returns:
        HTML for an ARIA live region that screen readers will announce.

    Examples:
        >>> html = get_live_region("Vote recorded successfully!")
        >>> assert 'aria-live="polite"' in html
    """
    return (
        f'<div aria-live="{politeness}" aria-atomic="true" '
        f'class="sr-only" role="status">{message}</div>'
    )


# ---------------------------------------------------------------------------
# Accessible Form Helpers
# ---------------------------------------------------------------------------

def get_form_field_html(
    field_id: str,
    label: str,
    field_type: str = "text",
    required: bool = False,
    help_text: Optional[str] = None,
    error_text: Optional[str] = None,
) -> str:
    """Generate accessible form field HTML with proper labeling.

    Creates form fields with associated labels, help text, and
    error messages linked via ARIA attributes.

    Args:
        field_id: Unique ID for the form field.
        label: Visible label text.
        field_type: Input type (default ``"text"``).
        required: Whether the field is required.
        help_text: Optional help text displayed below the field.
        error_text: Optional error message for validation failures.

    Returns:
        HTML string for the accessible form field.

    Examples:
        >>> html = get_form_field_html("pin_code", "PIN Code", required=True)
        >>> assert 'aria-required="true"' in html
    """
    required_attr: str = 'aria-required="true" required' if required else ""
    described_by_parts: list[str] = []

    help_html: str = ""
    if help_text:
        help_id: str = f"{field_id}_help"
        help_html = f'<span id="{help_id}" class="ic-desc">{help_text}</span>'
        described_by_parts.append(help_id)

    error_html: str = ""
    if error_text:
        error_id: str = f"{field_id}_error"
        error_html = (
            f'<span id="{error_id}" role="alert" '
            f'style="color:#ef4444;font-size:0.85rem;">{error_text}</span>'
        )
        described_by_parts.append(error_id)

    described_by: str = ""
    if described_by_parts:
        described_by = f'aria-describedby="{" ".join(described_by_parts)}"'

    invalid_attr: str = 'aria-invalid="true"' if error_text else ""

    return (
        f'<div class="form-field">'
        f'<label for="{field_id}">{label}</label>'
        f'<input type="{field_type}" id="{field_id}" name="{field_id}" '
        f'{required_attr} {described_by} {invalid_attr}>'
        f'{help_html}{error_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Color Contrast Checker
# ---------------------------------------------------------------------------

def check_contrast_ratio(
    fg_hex: str,
    bg_hex: str,
) -> dict[str, float | bool | str]:
    """Check WCAG 2.1 color contrast ratio between foreground and background.

    Calculates the relative luminance contrast ratio and checks
    against WCAG AA (4.5:1 for normal text) and AAA (7:1) standards.

    Args:
        fg_hex: Foreground color as hex string (e.g., ``"#ffffff"``).
        bg_hex: Background color as hex string (e.g., ``"#0f172a"``).

    Returns:
        A dict with:
            - ``ratio`` (float): The contrast ratio.
            - ``aa_pass`` (bool): Whether it passes WCAG AA.
            - ``aaa_pass`` (bool): Whether it passes WCAG AAA.
            - ``level`` (str): The highest passing level.

    Examples:
        >>> result = check_contrast_ratio("#ffffff", "#000000")
        >>> assert result["aa_pass"] is True
        >>> assert result["ratio"] == 21.0
    """
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )

    def _relative_luminance(r: int, g: int, b: int) -> float:
        def _linearize(channel: int) -> float:
            c: float = channel / 255.0
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)

    fg_rgb: tuple[int, int, int] = _hex_to_rgb(fg_hex)
    bg_rgb: tuple[int, int, int] = _hex_to_rgb(bg_hex)

    l1: float = _relative_luminance(*fg_rgb)
    l2: float = _relative_luminance(*bg_rgb)

    lighter: float = max(l1, l2)
    darker: float = min(l1, l2)
    ratio: float = round((lighter + 0.05) / (darker + 0.05), 1)

    aa_pass: bool = ratio >= 4.5
    aaa_pass: bool = ratio >= 7.0

    level: str = "AAA" if aaa_pass else ("AA" if aa_pass else "FAIL")

    return {
        "ratio": ratio,
        "aa_pass": aa_pass,
        "aaa_pass": aaa_pass,
        "level": level,
    }
