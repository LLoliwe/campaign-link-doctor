"""Privacy-aware campaign URL checker. Reports never echo user-provided input URLs."""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path
from .core import check_url, build_url, strip_url

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_LINKS = 5000

def load_file(path):
    if path == "-":
        return [s.strip() for s in sys.stdin if s.strip()][:MAX_LINKS + 1]
    source = Path(path)
    if not source.is_file() or source.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Input file is absent or over 2 MiB")
    if source.suffix.lower() == ".csv":
        with source.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames or "url" not in [x.lower() for x in reader.fieldnames]:
                raise ValueError("CSV requires a url column")
            field = next(x for x in reader.fieldnames if x.lower() == "url")
            values = [str(row.get(field, "")).strip() for row in reader]
            return [x for x in values if x]
    return [x.strip() for x in source.read_text(encoding="utf-8-sig").splitlines() if x.strip()]

def run_check(urls, fmt, strict):
    reports = [check_url(url) for url in urls]
    errors = sum(f.level == "error" for r in reports for f in r.findings)
    warnings = sum(f.level == "warning" for r in reports for f in r.findings)
    if fmt == "json":
        print(json.dumps({"summary": {"links": len(reports), "errors": errors, "warnings": warnings},
                          "links": [{"index": i, **r.as_dict()} for i, r in enumerate(reports, 1)]}, indent=2))
    elif fmt == "csv":
        out = csv.writer(sys.stdout)
        out.writerow(["link_index", "level", "code", "message"])
        for i, report in enumerate(reports, 1):
            for f in report.findings:
                out.writerow([i, f.level, f.code, f.message])
    else:
        for i, report in enumerate(reports, 1):
            print(f"Link {i}: {report.parameter_count} query parameter(s)")
            for f in report.findings:
                print(f"  {f.level.upper()} {f.code}: {f.message}")
        print(f"Scanned {len(reports)} link(s), {errors} error(s), {warnings} warning(s).")
    return 1 if errors or (strict and warnings) else 0

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="campaign-link-doctor",
        description="Offline campaign URL linting, PII alerts, canonical builders and tracking-link cleanup.")
    sub = parser.add_subparsers(dest="action", required=True)
    check = sub.add_parser("check", help="Report defects without ever echoing input URLs")
    check.add_argument("urls", nargs="*", help="URL(s) to check")
    check.add_argument("--file", help="Newline text / CSV file (url column), or - for stdin")
    check.add_argument("--format", choices=["text", "json", "csv"], default="text")
    check.add_argument("--strict", action="store_true", help="Warnings also fail")
    build = sub.add_parser("build", help="Generate a consistent link; outputs final URL by explicit request")
    build.add_argument("--base", required=True)
    build.add_argument("--source", required=True)
    build.add_argument("--medium", required=True)
    build.add_argument("--campaign", required=True)
    build.add_argument("--content", default="")
    build.add_argument("--term", default="")
    build.add_argument("--replace", action="store_true", help="Replace existing UTMs")
    strip = sub.add_parser("strip", help="Remove tracking/PII query parameters; outputs final URL")
    strip.add_argument("url")
    args = parser.parse_args(argv)
    try:
        if args.action == "check":
            urls = list(args.urls)
            if args.file:
                urls.extend(load_file(args.file))
            if not urls:
                parser.error("check needs URLs or --file")
            if len(urls) > MAX_LINKS:
                parser.error("Limit is 5000 URLs per run")
            return run_check(urls, args.format, args.strict)
        if args.action == "build":
            print(build_url(args.base, source=args.source, medium=args.medium,
                            campaign=args.campaign, content=args.content,
                            term=args.term, replace=args.replace))
            return 0
        if args.action == "strip":
            cleaned, removed = strip_url(args.url)
            print(cleaned)
            print(f"Removed {removed} tracking or sensitive query parameter(s).", file=sys.stderr)
            return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 2

if __name__ == "__main__":
    sys.exit(main())

