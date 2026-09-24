from pathlib import Path


def test_caddy_security_headers_are_explicit() -> None:
    caddyfile = Path("Caddyfile").read_text(encoding="utf-8")

    assert 'X-Frame-Options "DENY"' in caddyfile
    assert 'X-Content-Type-Options "nosniff"' in caddyfile
    assert "Permissions-Policy" in caddyfile
    assert "Content-Security-Policy" in caddyfile
    assert "default-src 'self'" in caddyfile
    assert "object-src 'none'" in caddyfile
    assert "frame-ancestors 'none'" in caddyfile
    assert "img-src 'self' data: blob:" in caddyfile
