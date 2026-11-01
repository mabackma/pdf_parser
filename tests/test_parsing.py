"""
Tests for the financial statement parser.

Run with: docker compose run test
"""

import json
from pathlib import Path
from src.parser import parse_financial_statement
from src.schema import FinancialStatement

PDFS_DIR = Path(__file__).parent.parent / "pdfs"
EXPECTED_DIR = Path(__file__).parent.parent / "expected"

VARIABLES = [
    "fiscal_year",
    "revenue",
    "operating_profit",
    "profit_before_taxes",
    "net_profit",
    "fixed_assets",
    "current_assets",
    "total_assets",
    "equity",
    "liabilities",
    "total_equity_and_liabilities",
]


def load_expected(pdf_name: str) -> list[dict]:
    """Load expected output for a PDF."""
    json_path = EXPECTED_DIR / pdf_name.replace(".pdf", ".json")
    with open(json_path) as f:
        return json.load(f)


def compare_results(expected: list[dict], actual: list[FinancialStatement]) -> list[str]:
    """Compare expected vs actual and return list of error messages."""
    errors = []

    # Check count
    if len(actual) != len(expected):
        errors.append(
            f"Expected {len(expected)} fiscal year(s), got {len(actual)}"
        )
        return errors

    # Sort both by fiscal year for comparison
    expected_sorted = sorted(expected, key=lambda x: x["fiscal_year"], reverse=True)
    actual_sorted = sorted(actual, key=lambda x: x.fiscal_year, reverse=True)

    for exp, act in zip(expected_sorted, actual_sorted):
        year = exp["fiscal_year"]
        act_dict = act.to_dict()

        for var in VARIABLES:
            exp_val = exp.get(var)
            act_val = act_dict.get(var)

            if exp_val != act_val:
                errors.append(
                    f"[{year}] {var}: expected {exp_val}, got {act_val}"
                )

    return errors


def test_01():
    """Test parsing test_01.pdf (Esimerkki Oy - single year, standard layout)."""
    pdf_path = PDFS_DIR / "test_01.pdf"
    expected = load_expected("test_01.pdf")

    actual = parse_financial_statement(pdf_path)

    errors = compare_results(expected, actual)
    if errors:
        error_msg = "\n".join(errors)
        raise AssertionError(f"Parsing errors in test_01.pdf:\n{error_msg}")


def test_02():
    """Test parsing test_02.pdf (Teräs Rakennus Oy - single year, different terminology)."""
    pdf_path = PDFS_DIR / "test_02.pdf"
    expected = load_expected("test_02.pdf")

    actual = parse_financial_statement(pdf_path)

    errors = compare_results(expected, actual)
    if errors:
        error_msg = "\n".join(errors)
        raise AssertionError(f"Parsing errors in test_02.pdf:\n{error_msg}")


def test_03():
    """Test parsing test_03.pdf (Nordic Software Solutions - two years)."""
    pdf_path = PDFS_DIR / "test_03.pdf"
    expected = load_expected("test_03.pdf")

    actual = parse_financial_statement(pdf_path)

    errors = compare_results(expected, actual)
    if errors:
        error_msg = "\n".join(errors)
        raise AssertionError(f"Parsing errors in test_03.pdf:\n{error_msg}")


def test_04():
    """Test parsing test_04.pdf (Pohjoinen Energia Oy - negative profits, decimals, noise sections)."""
    pdf_path = PDFS_DIR / "test_04.pdf"
    expected = load_expected("test_04.pdf")

    actual = parse_financial_statement(pdf_path)

    errors = compare_results(expected, actual)
    if errors:
        error_msg = "\n".join(errors)
        raise AssertionError(f"Parsing errors in test_04.pdf:\n{error_msg}")


def test_05():
    """Test parsing test_05.pdf (Arktinen Teollisuus Oy - values in thousands, 3 columns, AKTIVA/PASSIVA, noise sections)."""
    pdf_path = PDFS_DIR / "test_05.pdf"
    expected = load_expected("test_05.pdf")

    actual = parse_financial_statement(pdf_path)

    errors = compare_results(expected, actual)
    if errors:
        error_msg = "\n".join(errors)
        raise AssertionError(f"Parsing errors in test_05.pdf:\n{error_msg}")
