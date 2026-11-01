# PDF Financial Statement Parser

Parse Finnish company financial statements (tuloslaskelma / tase) from PDF to structured JSON.

## Quick Start

```bash
# Run tests
docker compose run test

# Interactive shell for debugging
docker compose run shell
```

## Your Task

Implement the parser function in `src/parser.py`. This is the only file you should modify.

Given a PDF containing a Finnish financial statement, extract key financial metrics and return them as structured data. Some PDFs contain data for multiple fiscal years - return one result per year.

### Target Variables

Your parser should extract these 11 values per fiscal year:

**Required:**
- `fiscal_year` - The fiscal year (e.g., 2023)

**Income Statement:**
- `revenue` - Liikevaihto
- `operating_profit` - Liikevoitto
- `profit_before_taxes` - Voitto ennen veroja
- `net_profit` - Tilikauden voitto

**Balance Sheet:**
- `fixed_assets` - Pysyvät vastaavat
- `current_assets` - Vaihtuvat vastaavat
- `total_assets` - Vastaavaa yhteensä
- `equity` - Oma pääoma
- `liabilities` - Vieras pääoma
- `total_equity_and_liabilities` - Vastattavaa yhteensä

### Test PDFs

Five PDFs are provided in `pdfs/`:
- `test_01.pdf` - Single year, standard layout
- `test_02.pdf` - Single year, different terminology
- `test_03.pdf` - Two years (2023 + 2022)
- `test_04.pdf` - Two years (2024 + 2023), negative profits, decimal values, cash flow & notes as noise
- `test_05.pdf` - Two years (2024 + 2023), values in thousands (1 000 €), 3-column layout with budget column, function-based income statement, AKTIVA/PASSIVA headers, key figures & board proposal as noise

Expected outputs are in `expected/`. All monetary values should be in euros.

## Project Structure

```
├── pdfs/                  # Test PDF files
├── expected/              # Expected JSON outputs
├── src/
│   ├── pdf_reader.py      # PDF extraction helper (provided)
│   ├── schema.py          # Output data types (provided)
│   ├── variables.py       # Target variable list (provided)
│   └── parser.py          # YOUR IMPLEMENTATION
└── tests/                 # Test infrastructure
```

## Running Tests

```bash
docker compose run test
```

Tests show exactly which variables are wrong for each PDF.

## Running on a Single PDF

You can test your parser on individual PDFs using the interactive shell:

```bash
$ docker compose run shell
root@6235f73e0409:/app# python src/parser.py pdfs/test_01.pdf
```

Once implemented, this will print the extracted JSON for that PDF.

## How to Submit

1. Fill in `SUBMISSION.md` with your approach and AI usage
2. Create a git bundle:

```bash
git init
git add -A
git commit -m "My solution"
git bundle create solution.bundle --all
```

3. Upload `solution.bundle` through the candidate dashboard

### What we look for

1. **Working code** - Your implemented parser
2. **SUBMISSION.md** - Document your approach and AI usage

## Rules

- Use any AI tools you want
- Use any approach you want
- Ask questions if you need clarification

Good luck!
