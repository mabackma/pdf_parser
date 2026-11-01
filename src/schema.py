"""
Output schema for parsed financial statements.

Your parser should return data matching this schema.
"""

from dataclasses import dataclass, asdict
from typing import Optional
import json


@dataclass
class FinancialStatement:
    """
    Extracted financial statement data for a single fiscal year.

    All monetary values should be in euros. Use positive numbers for assets,
    revenue, and profit. Use the sign convention that makes the balance sheet balance.

    Set a field to None if the value cannot be extracted.
    """

    # Fiscal year (required)
    fiscal_year: int = 0

    # Income Statement
    revenue: Optional[float] = None
    operating_profit: Optional[float] = None
    profit_before_taxes: Optional[float] = None
    net_profit: Optional[float] = None

    # Balance Sheet
    fixed_assets: Optional[float] = None
    current_assets: Optional[float] = None
    total_assets: Optional[float] = None
    equity: Optional[float] = None
    liabilities: Optional[float] = None
    total_equity_and_liabilities: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> "FinancialStatement":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, json_str: str) -> "FinancialStatement":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))
