"""
Financial Statement Parser

YOUR TASK: Implement the parse_financial_statement function below.

Given a path to a PDF containing Finnish financial statements,
extract the target variables and return a list of FinancialStatement objects.

Some PDFs contain data for multiple fiscal years - return one object per year.

You may:
- Use the provided pdf_reader module or implement your own extraction
- Add helper functions, classes, or modules as needed
- Use any approach you think is appropriate

Run tests with: docker compose run test
"""

from __future__ import annotations

import re
from pathlib import Path

from src.pdf_reader import extract_pdf
from src.schema import FinancialStatement
from datetime import datetime

mapping = {
    "Tilinpäätös": "fiscal_year",
    "Tilikausi": "fiscal_year",
    "Liikevaihto": "revenue",
    "LIIKEVAIHTO": "revenue",
    "Liiketulos": "operating_profit",
    "LIIKEVOITTO": "operating_profit",
    "LIIKETOIMINNAN TULOS": "operating_profit",
    "Liiketoiminnan tulos": "operating_profit",
    "Voitto ennen tilinpäätössiirtoja ja veroja": "profit_before_taxes",
    "Tulos ennen tilinpäätössiirtoja ja veroja": "profit_before_taxes",
    "VOITTO ENNEN VEROJA": "profit_before_taxes",
    "VOITTO (TAPPIO) ENNEN VEROJA": "profit_before_taxes",
    "TULOS ENNEN VEROJA": "profit_before_taxes",
    "Tulos ennen veroja": "profit_before_taxes",
    "Tulos (tappio) ennen veroja": "profit_before_taxes",
    "Tilikauden tulos": "net_profit",
    "TILIKAUDEN VOITTO": "net_profit",
    "TILIKAUDEN TULOS": "net_profit",
    "TILIKAUDEN VOITTO (TAPPIO)": "net_profit",
    "Pysyvät vastaavat yhteensä": "fixed_assets",
    "Pysyvät vastaavat yht.": "fixed_assets",
    "Vaihtuvat vastaavat yhteensä": "current_assets",
    "Vaihtuvat vastaavat yht.": "current_assets",
    "VASTAAVAA YHTEENSÄ": "total_assets",
    "Vastaavaa yhteensä": "total_assets",
    "Oma pääoma yhteensä": "equity",
    "Oma pääoma yht.": "equity",
    "Vieras pääoma yhteensä": "liabilities",
    "Vieras pääoma yht.": "liabilities",
    "VASTATTAVAA YHTEENSÄ": "total_equity_and_liabilities",
    "Vastattavaa yhteensä": "total_equity_and_liabilities",
}

# Longer keys first so e.g. "Tilikauden tulos" wins over "Tilikausi"
_SORTED_KEYS = sorted(mapping.keys(), key=len, reverse=True)

# Single Finnish number token (one amount, not multiple columns)
_FI_NUM_ONE = re.compile(
    r"-?(?:\d{1,3}(?:\s+\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?=\s|$|€)"
)


def _parse_fi_number(token: str) -> float | None:
    t = token.strip().replace("€", "").replace("\u00a0", " ")
    t = re.sub(r"\s+", "", t)
    t = t.replace(",", ".")
    if not t or t == "-":
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _extract_fi_numbers(text: str) -> list[float]:
    out: list[float] = []
    for m in _FI_NUM_ONE.finditer(text):
        v = _parse_fi_number(m.group(0))
        if v is not None:
            out.append(v)
    return out


def _extract_column_numbers(after: str) -> list[float]:
    """Split on 2+ spaces to separate columns; parse one number per cell."""
    parts = re.split(r"\s{2,}", after.strip())
    nums: list[float] = []
    for p in parts:
        if not p.strip():
            continue
        n = _parse_fi_number(p)
        if n is not None:
            nums.append(n)
    return nums


def _all_row_numbers(after: str) -> list[float]:
    """Prefer wide-space column split; if that yields too few cells, use regex tokens."""
    cols = _extract_column_numbers(after)
    tok = _extract_fi_numbers(after)
    # Some PDFs collapse spacing during extraction; token regex then recovers values
    # better than fixed column splitting.
    if len(tok) > len(cols):
        return tok
    return cols if cols else tok


def _detect_years_scale_col_offset(lines: list[str]) -> tuple[list[int], float, int]:
    head = "\n".join(lines[:120])
    # Many statements report values in thousands ("1 000 euroa"), so we scale later.
    scale = 1000.0 if re.search(r"1\s*000\s*euroa", head, re.I) else 1.0
    col_offset = 0
    years: list[int] | None = None

    for line in lines[:100]:
        if "Budjetti" in line and "Toteutunut" in line:
            # In 3-column layouts the first numeric column can be budget; skip it.
            col_offset = 1
            ys = re.findall(r"\b(\d{4})\b", line)
            if len(ys) >= 3:
                years = [int(ys[1]), int(ys[2])]
            elif len(ys) >= 2:
                years = [int(ys[0]), int(ys[1])]
            break

    if years is None:
        for line in lines[:100]:
            ys = re.findall(r"\b(\d{4})\b", line)
            if len(ys) < 2:
                continue
            uniq: list[int] = []
            for y in ys:
                yi = int(y)
                if yi not in uniq:
                    uniq.append(yi)
            if len(uniq) < 2:
                continue
            # Prefer two-year headers (EUR columns, year pairs, or Tilikausi)
            if (
                "EUR" in line
                or "Tilikausi" in line
                or "Toteutunut" in line
                or re.search(r"31\.12\.\d{4}\s+31\.12\.\d{4}", line)
            ):
                years = [uniq[0], uniq[1]]
                break

    if years is None:
        for line in lines[:90]:
            m = re.search(r"Til(?:\s*)inpäätös(?:\s*)(\d{4})", line, re.I)
            if m:
                years = [int(m.group(1))]
                break
            m = re.search(r"Tilikausi(?:\s*)(\d{4})", line, re.I)
            if m:
                years = [int(m.group(1))]
                break
        if years is None:
            for line in lines[:90]:
                m = re.search(r"31\.12\.(\d{4})", line)
                if m:
                    years = [int(m.group(1))]
                    break

    if years is None:
        years = [datetime.now().year]

    return years, scale, col_offset


def _line_starts_with_key(stripped: str, key: str) -> bool:
    s = stripped
    if not s.upper().startswith(key.upper()):
        return False
    if len(s) == len(key):
        return True
    nxt = s[len(key) : len(key) + 1]
    if nxt and nxt not in " \t(":
        return False
    return True


def _match_key(line: str) -> tuple[str, str] | None:
    """Return (mapping_key, field_name) if the line starts with a financial label."""
    stripped = line.strip()
    if not stripped:
        return None
    for key in _SORTED_KEYS:
        if field := mapping.get(key):
            if not _line_starts_with_key(stripped, key):
                continue
            after = stripped[len(key) :]
            if _all_row_numbers(after):
                return key, field
    return None


def parse_financial_statement(pdf_path: str | Path) -> list[FinancialStatement]:
    """
    Parse a Finnish financial statement PDF and extract key metrics.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of FinancialStatement objects, one per fiscal year found in the PDF.
        Most PDFs have one year, but some have multiple (e.g., current + previous).

    Example:
        >>> results = parse_financial_statement("pdfs/test_01.pdf")
        >>> for stmt in results:
        ...     print(f"{stmt.fiscal_year}: revenue={stmt.revenue}")
    """
    extracted = extract_pdf(pdf_path)
    lines = extracted.text.splitlines()
    years, scale, col_offset = _detect_years_scale_col_offset(lines)

    by_year: dict[int, FinancialStatement] = {
        y: FinancialStatement(fiscal_year=y) for y in years
    }

    for line in lines:
        line = line.rstrip()
        matched = _match_key(line)
        if not matched:
            continue
        _key, field = matched
        if field == "fiscal_year":
            continue

        stripped = line.strip()
        after = stripped[len(_key) :]
        nums = _all_row_numbers(after)
        if not nums:
            continue

        if col_offset and len(nums) >= 3:
            nums = nums[col_offset:]
        if not nums:
            continue

        scaled = [n * scale for n in nums]

        if len(scaled) == 1:
            y = years[0]
            setattr(by_year[y], field, scaled[0])
        else:
            # Column order is assumed to follow detected year order in headers.
            n = min(len(scaled), len(years))
            for i in range(n):
                setattr(by_year[years[i]], field, scaled[i])

    return [by_year[y] for y in years]


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.parser <pdf_path>")
        sys.exit(1)

    results = parse_financial_statement(sys.argv[1])
    print(json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False))
