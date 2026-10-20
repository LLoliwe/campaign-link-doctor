"""Pure URL parser, campaign parameter policies, and redacted reports. No network."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import re

UTM_REQUIRED = ("utm_source", "utm_medium", "utm_campaign")
UTM_ALL = (*UTM_REQUIRED, "utm_content", "utm_term")
TRACKER_KEYS = {"fbclid", "gclid", "gbraid", "wbraid", "msclkid", "ttclid", "twclid", "mc_cid", "mc_eid"}
SENSITIVE_KEYS = {"email", "e-mail", "e_mail", "phone", "mobile", "password", "passwd", "token", "auth", "authorization",
                  "api_key", "apikey", "access_token", "refresh_token", "session", "sessionid", "ssn", "dob",
                  "date_of_birth", "idfa", "gaid"}
EMAIL = re.compile(r"(?<![\w.-])[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}", re.I)
INVALID_PERCENT = re.compile(r"%(?![0-9A-Fa-f]{2})")
CONTROL = re.compile(r"[\x00-\x1f\x7f]")

@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str
    def as_dict(self):
        return asdict(self)

@dataclass(frozen=True)
class Result:
    parameter_count: int
    findings: tuple[Finding, ...]
    def as_dict(self):
        return {"parameter_count": self.parameter_count,
                "findings": [f.as_dict() for f in self.findings]}

def _parse(raw: str):
    if not isinstance(raw, str) or not raw or len(raw) > 8192:
        raise ValueError("URL is missing or exceeds 8192 characters")
    if CONTROL.search(raw):
        raise ValueError("URL contains control characters")
    if INVALID_PERCENT.search(raw):
        raise ValueError("URL has malformed percent-encoding")
    try:
        u = urlsplit(raw)
        host = u.hostname
        port = u.port
    except ValueError as exc:
        raise ValueError("URL authority is invalid") from exc
    if u.scheme.lower() not in ("http", "https"):
        raise ValueError("Only http:// and https:// URLs are supported")
    if not host or any(c.isspace() for c in host):
        raise ValueError("URL hostname is missing or invalid")
    if u.username is not None or u.password is not None:
        raise ValueError("URLs containing embedded user credentials are refused")
    if u.netloc.endswith(":") or (port is not None and port == 0):
        raise ValueError("Invalid URL port")
    return u, parse_qsl(u.query, keep_blank_values=True, strict_parsing=False)

def _sensitive(name: str, value: str) -> bool:
    name = name.strip().lower().replace("-", "_")
    return name in SENSITIVE_KEYS or EMAIL.search(value) is not None

def check_url(url: str) -> Result:
    try:
        u, pairs = _parse(url)
    except ValueError as exc:
        return Result(0, (Finding("error", "CLD001", str(exc)),))
    found: list[Finding] = []
    keys = [key.lower() for key, _ in pairs]
    counts = {key: keys.count(key) for key in set(keys)}
    if u.scheme.lower() == "http":
        found.append(Finding("warning", "CLD101", "Link uses HTTP, not HTTPS."))
    if any(counts[k] > 1 for k in counts if k.startswith("utm_") or k in TRACKER_KEYS):
        found.append(Finding("error", "CLD002", "Duplicate query parameter names detected (case-insensitive)."))
    for name, value in pairs:
        lower = name.lower()
        if _sensitive(name, value):
            found.append(Finding("error", "CLD003", "Potential personal information or secret in URL query; value never reported."))
        if lower in UTM_ALL and value.strip() == "":
            found.append(Finding("error", "CLD004", "A campaign parameter has an empty value."))
        if lower in UTM_ALL and (name != lower or value != value.strip()):
            found.append(Finding("warning", "CLD102", "Campaign parameter naming or whitespace needs normalization."))
        if lower in TRACKER_KEYS:
            found.append(Finding("info", "CLD201", "A platform click identifier is present; evaluate whether sharing is appropriate."))
    any_utm = any(x.startswith("utm_") for x in keys)
    if any_utm:
        missing = sum(key not in keys for key in UTM_REQUIRED)
        if missing:
            found.append(Finding("warning", "CLD103", f"{missing} required campaign parameter(s) absent: source, medium, campaign are recommended."))
    if u.fragment and any(x.startswith("utm_") for x in u.fragment.lower().split("&")):
        found.append(Finding("warning", "CLD104", "Campaign parameters appear in URL fragment; standard analytics may not receive them."))
    return Result(len(pairs), tuple(found))

def build_url(base: str, *, source: str, medium: str, campaign: str,
              content: str = "", term: str = "", replace: bool = False) -> str:
    u, pairs = _parse(base)
    if any(_sensitive(name, value) for name, value in pairs):
        raise ValueError("Base URL contains possible secret or PII in query; refusing to copy into output")
    values = {"utm_source": source, "utm_medium": medium, "utm_campaign": campaign,
              "utm_content": content, "utm_term": term}
    for key in UTM_REQUIRED:
        if not values[key] or not values[key].strip() or CONTROL.search(values[key]):
            raise ValueError("Required source, medium and campaign values must be nonblank and contain no control characters")
    if any(CONTROL.search(value) or EMAIL.search(value) for value in values.values()):
        raise ValueError("Campaign fields must not contain control characters or email addresses")
    if any(key.lower().startswith("utm_") for key, _ in pairs) and not replace:
        raise ValueError("Base URL already contains campaign parameters; pass --replace to remove old ones")
    kept = [(key, value) for key, value in pairs if not key.lower().startswith("utm_")]
    kept += [(key, value.strip()) for key, value in values.items() if value.strip()]
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(kept), u.fragment))

def strip_url(url: str) -> tuple[str, int]:
    """Explicit opt-in output. Remove tracking params and query-based sensitive fields."""
    u, pairs = _parse(url)
    kept = [(key, value) for key, value in pairs
            if not (key.lower() in TRACKER_KEYS or key.lower().startswith("utm_") or _sensitive(key, value))]
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(kept), u.fragment)), len(pairs) - len(kept)

