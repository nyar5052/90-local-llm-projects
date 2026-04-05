# 🗃️ SQL Query Generator

AI-powered tool that converts natural language questions into SQL queries using a local Gemma 4 LLM.

## ✨ Features

- **Natural Language to SQL** — Describe what you want in plain English
- **Schema Aware** — Provide your database schema for accurate queries
- **Multi-dialect** — Supports PostgreSQL, MySQL, SQLite, and standard SQL
- **Query Explanation** — Step-by-step explanation of generated queries
- **Optimization Tips** — Suggests indexes and query improvements
- **Schema-free Mode** — Works even without a schema definition

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# With a schema file
python app.py --schema schema.sql --query "show top customers by revenue"

# With specific dialect
python app.py --schema schema.sql --query "monthly sales" --dialect postgresql

# Without schema (infers table structure)
python app.py --query "find all users who signed up last month"

# With inline schema
python app.py --schema-text "users(id, name, email)" --query "count users"
```

## 📋 Example Output

```
╭──────────────────────────────────────────╮
│  🗃️ SQL Query Generator                │
│  Convert natural language to SQL         │
╰──────────────────────────────────────────╯

Tables found: customers, orders, products

╭── 📝 Generated SQL ───────────────────╮
│ ```sql                                 │
│ SELECT c.name,                         │
│        SUM(o.amount) as total_revenue  │
│ FROM customers c                       │
│ JOIN orders o ON c.id = o.customer_id  │
│ GROUP BY c.name                        │
│ ORDER BY total_revenue DESC            │
│ LIMIT 10;                              │
│ ```                                    │
│                                        │
│ This query joins customers with their  │
│ orders and calculates total revenue.   │
╰────────────────────────────────────────╯
```

## 🧪 Testing

```bash
pytest test_app.py -v
```

## ⚙️ Requirements

- Python 3.10+
- Ollama running locally with Gemma 4 model
