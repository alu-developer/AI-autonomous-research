"""Mechanical checks for reproduction audits (protocol v2).

confirm_pdf: confirms a published value I read from a paper by finding the exact printed string in the
    PDF text layer on the stated page. Counters copying errors (pilot 1 weak point 1).
check_diff: flags edits to the authors' code that touch estimation or sample lines.
    Counters silent analysis changes and reward hacking via "environment fixes".

Usage:
    python -m airesearch.checks confirm-pdf PAPER.pdf PAGE "0.214" [--near "Treatment"]
    python -m airesearch.checks check-diff outputs/code.diff
"""
import re
import subprocess
import sys
from pathlib import Path

ESTIMATION_PATTERNS = [
    # R
    r"\blm\s*\(", r"\bglm\s*\(", r"\bfeols\s*\(", r"\bfelm\s*\(", r"\blmer\s*\(", r"\bglmer\s*\(",
    r"\bivreg\s*\(", r"\bsubset\s*\(", r"\bfilter\s*\(", r"\bplm\s*\(", r"\blm_robust\s*\(",
    # Python
    r"\bsmf?\.(ols|logit|probit|glm)\b", r"\.query\s*\(", r"\.dropna\s*\(",
    # Stata
    r"^\s*(reg|regress|areg|xtreg|ivreg2?|ivregress|logit|probit|reghdfe)\b", r"^\s*(keep|drop)\b", r"\bif\b",
]
_EST = [re.compile(p) for p in ESTIMATION_PATTERNS]


def page_text(pdf: Path, page: int) -> str:
    out = subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
                         capture_output=True, text=True, check=True)
    return out.stdout


def _normalize(s: str) -> str:
    # unify minus signs and spaces; keep digits and punctuation as printed
    return s.replace("−", "-").replace("–", "-").replace(" ", " ")


def confirm_in_text(text: str, value: str, near: str | None = None, window: int = 400) -> bool:
    """True if `value` appears as a standalone number in text (and, if given, within `window` chars after `near`)."""
    text, value = _normalize(text), _normalize(value.strip())
    pat = re.compile(r"(?<![\d.])" + re.escape(value) + r"(?![\d])")
    if near is None:
        return bool(pat.search(text))
    for m in re.finditer(re.escape(_normalize(near)), text):
        if pat.search(text[m.start(): m.start() + window]):
            return True
    return False


def confirm_pdf(pdf: Path, page: int, value: str, near: str | None = None) -> bool:
    return confirm_in_text(page_text(pdf, page), value, near)


def flagged_lines(diff_text: str) -> list[str]:
    """Changed lines (+/-) in a unified diff that touch estimation or sample selection."""
    flagged = []
    for line in diff_text.splitlines():
        if line.startswith(("+++", "---")) or not line.startswith(("+", "-")):
            continue
        body = line[1:]
        if body.strip().startswith(("#", "*", "//")):
            continue
        if any(p.search(body) for p in _EST):
            flagged.append(line)
    return flagged


def main(argv: list[str]) -> int:
    if len(argv) >= 4 and argv[0] == "confirm-pdf":
        near = argv[argv.index("--near") + 1] if "--near" in argv else None
        ok = confirm_pdf(Path(argv[1]), int(argv[2]), argv[3], near)
        print("confirmed" if ok else "extraction_unconfirmed")
        return 0 if ok else 1
    if len(argv) == 2 and argv[0] == "check-diff":
        flags = flagged_lines(Path(argv[1]).read_text())
        for f in flags:
            print("FLAGGED:", f)
        print("modified" if flags else "clean")
        return 1 if flags else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
