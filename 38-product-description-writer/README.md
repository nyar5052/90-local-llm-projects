# Product Description Writer

Generate SEO-optimized e-commerce product descriptions using a local Gemma 4 LLM via Ollama.

## Features

- **Multi-Platform**: Optimized for Amazon, Shopify, Etsy, eBay, or generic
- **Platform Best Practices**: Each platform gets tailored copy style
- **SEO Keywords**: Includes relevant search terms for discoverability
- **Multiple Variants**: Generate several options for A/B testing
- **Configurable Length**: Short, medium, or long descriptions
- **Complete Copy**: Title, short description, full copy, and bullet points

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with the Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Amazon listing
python app.py --product "Wireless Headphones" --features "noise-cancel,bluetooth,40h battery" --platform amazon

# Etsy listing
python app.py --product "Handmade Ceramic Mug" --features "hand-glazed,dishwasher safe" --platform etsy --length long

# Multiple variants
python app.py --product "Standing Desk" --features "electric,memory presets" --variants 3 -o descriptions.md
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--product` | Product name (required) | - |
| `--features` | Comma-separated features | None |
| `--platform` | E-commerce platform | generic |
| `--length` | Description length (short/medium/long) | medium |
| `--variants` | Number of variants | 2 |
| `-o, --output` | Save to file | None |

## Example Output

```
╭─ 🛒 Product Descriptions ─────────────────────╮
│ ## Variant 1                                   │
│ **Title:** Premium ANC Wireless Headphones     │
│ with 40H Battery - Bluetooth 5.3               │
│                                                │
│ **Short:** Experience crystal-clear audio      │
│ with industry-leading noise cancellation...    │
│                                                │
│ **Bullet Points:**                             │
│ • 🎧 Active Noise Cancellation                │
│ • 🔋 40-Hour Battery Life                      │
│ • 📱 Bluetooth 5.3 Connectivity               │
│ ...                                            │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
