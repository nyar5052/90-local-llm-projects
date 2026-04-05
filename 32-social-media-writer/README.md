# Social Media Writer

Create engaging, platform-specific social media posts using a local Gemma 4 LLM via Ollama.

## Features

- **Multi-Platform Support**: Generates posts for Twitter/X, LinkedIn, and Instagram
- **Platform-Aware**: Adapts content length, style, and hashtag count per platform
- **Multiple Tones**: Professional, casual, excited, informative, or humorous
- **Variant Generation**: Create multiple post variants for A/B testing
- **Hashtag Integration**: Automatically includes relevant hashtags

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with the Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# LinkedIn post
python app.py --platform linkedin --topic "new product launch" --tone excited

# Twitter post with variants
python app.py --platform twitter --topic "tech conference recap" --tone casual --variants 3

# Instagram post saved to file
python app.py --platform instagram --topic "behind the scenes" --tone humorous -o post.txt
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--platform` | Target platform: twitter/linkedin/instagram (required) | - |
| `--topic` | Post topic (required) | - |
| `--tone` | Writing tone | professional |
| `--variants` | Number of post variants | 2 |
| `-o, --output` | Save output to file | None |

## Example Output

```
╭─ LinkedIn Posts ───────────────────────────────╮
│ Variant 1:                                     │
│ 🚀 Thrilled to announce our new product!       │
│ After months of development, we're ready to... │
│ #ProductLaunch #Innovation #Tech               │
│                                                │
│ Variant 2:                                     │
│ Big news! Our team has been working on...      │
│ #Launch #Startup #NewProduct                   │
╰────────────────────────────────────────────────╯
```

## Testing

```bash
pytest test_app.py -v
```
