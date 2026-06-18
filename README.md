# SQL Projects

A collection of SQL projects and exercises developed while studying databases, covering schema design, querying, views, and data analysis. Projects are sourced from Harvard's CS50's Introduction to Databases with SQL and original applied work using real-world datasets.

---

## Overview

The repository is organized under the `SQL/` directory, with each subdirectory representing a self-contained project or exercise set.

### CS50 SQL — Foundational Exercises

| Project | Database | Description |
|---|---|---|
| [src0/](SQL/src0/) | `longlist.db` (book awards) | Introductory query exercises covering `SELECT`, `LIMIT`, `WHERE`, `NULL`, `LIKE`, compound conditions, ranges, `ORDER BY`, dates, and aggregate functions |
| [cyberchase/](SQL/cyberchase/) | `cyberchase.db` | 13-query problem set practicing core SQL filtering and retrieval patterns |
| [dese/](SQL/dese/) | `dese.db` (Massachusetts education data) | 13-query problem set querying the Massachusetts Department of Elementary and Secondary Education dataset |
| [views/](SQL/views/) | `views.db` | 10-query problem set focused on creating and querying SQL views |
| [packages/](SQL/packages/) | `packages.db` | SQL mystery investigation: trace lost and misdirected packages through a delivery database using multi-step queries |

### Applied Projects

#### Bank System

**Path:** [`SQL/bank_system/`](SQL/bank_system/)

A fully designed SQLite database that models the core operations of a bank account system. Built to practice schema design, normalization, and query writing end-to-end.

**Entities:**

| Table | Description |
|---|---|
| `customer` | Personal information and credentials |
| `account` | Account type (credit/debit), balance, and account number |
| `transactions` | Individual deposits, withdrawals, and payments with status |
| `transfers` | Account-to-account transfers with status tracking |
| `budget` | Named savings budgets with limits and current amounts |
| `loans` | Loan records with interest rate, amount, and remaining balance |

**Files:**
- [`schema.sql`](SQL/bank_system/schema.sql) — table definitions with constraints and indices
- [`queries.sql`](SQL/bank_system/queries.sql) — sample queries for common operations
- [`Design.md`](SQL/bank_system/Design.md) — full scope, entity descriptions, relationships, and limitations
- [`ER_diagram.png`](SQL/bank_system/ER_diagram.png) — entity-relationship diagram

---

#### Superstore Analysis

**Path:** [`SQL/store_analysis/`](SQL/store_analysis/)

Business analysis of a retail superstore dataset (Kaggle) using SQL for data exploration and Python for visualization and modeling. The goal is to identify which products, regions, categories, and customer segments are most profitable.

**Analysis pipeline:**
1. Load CSV into SQL, inspect nulls, types, and date ranges
2. Business performance queries (revenue trends, segment profitability)
3. Deep exploratory data analysis (EDA)
4. Regression model to predict sales or profit
5. Insights and recommendations

**Key questions answered:**
- Is the business growing over time?
- Which customer segment (Consumer, Corporate, Home Office) is most profitable?
- Which geographic regions are most and least profitable?

**Files:**
- [`superstore-analysis.ipynb`](SQL/store_analysis/superstore-analysis.ipynb) — full analysis notebook
- [`ER.png`](SQL/store_analysis/ER.png) — entity-relationship diagram for the dataset schema
- [`README.md`](SQL/store_analysis/README.md) — dataset description and analysis plan

---

## Usage

### Requirements

- SQLite 3
- Python 3.8+ with Jupyter (for the store analysis notebook)

```bash
pip install pandas matplotlib seaborn scikit-learn jupyter
```

### Running SQL Queries

Open any `.db` file with the SQLite CLI and run the corresponding `.sql` files:

```bash
# Example: run a query from the dese problem set
sqlite3 SQL/dese/dese.db < SQL/dese/1.sql

# Example: load the bank system schema
sqlite3 bank.db < SQL/bank_system/schema.sql

# Example: explore the longlist database interactively
sqlite3 SQL/src0/longlist.db
```

### Running the Store Analysis Notebook

```bash
git clone https://github.com/cristian0831/SQL-Projects.git
cd SQL-Projects
jupyter notebook SQL/store_analysis/superstore-analysis.ipynb
```

---

## Contributing

Contributions, suggestions, and improvements are welcome. To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request describing what you changed and why.

Please include a brief description of the dataset or problem being solved when adding a new project.

---

## Tech Stack

- **SQLite** — primary database engine
- **SQL** — querying, schema design, and views
- **Python / Jupyter** — data analysis and visualization (store analysis)
- **Pandas / Matplotlib / Seaborn** — EDA and plotting
