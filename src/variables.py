"""
Target variables to extract from Finnish financial statements.

These are the standardized variable keys that your parser must output.
Monetary values should be numeric (integers or floats representing euros).
"""

# Required identifier
REQUIRED_VARIABLES = [
    "fiscal_year",  # The fiscal year as integer (e.g., 2023)
]

# Income Statement Variables
INCOME_STATEMENT_VARIABLES = [
    "revenue",
    "operating_profit",
    "profit_before_taxes",
    "net_profit",
]

# Balance Sheet Variables
BALANCE_SHEET_VARIABLES = [
    "fixed_assets",
    "current_assets",
    "total_assets",
    "equity",
    "liabilities",
    "total_equity_and_liabilities",
]

# All target variables
TARGET_VARIABLES = REQUIRED_VARIABLES + INCOME_STATEMENT_VARIABLES + BALANCE_SHEET_VARIABLES
