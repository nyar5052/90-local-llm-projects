"""
Core business logic for Code Translator.
Handles language detection, translation, validation, and batch processing.
"""

import os
import logging
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "python": {"ext": ".py", "name": "Python"},
    "javascript": {"ext": ".js", "name": "JavaScript"},
    "typescript": {"ext": ".ts", "name": "TypeScript"},
    "java": {"ext": ".java", "name": "Java"},
    "go": {"ext": ".go", "name": "Go"},
    "rust": {"ext": ".rs", "name": "Rust"},
    "csharp": {"ext": ".cs", "name": "C#"},
    "cpp": {"ext": ".cpp", "name": "C++"},
    "ruby": {"ext": ".rb", "name": "Ruby"},
    "php": {"ext": ".php", "name": "PHP"},
}

SYSTEM_PROMPT = """You are an expert polyglot programmer. Translate code between programming languages accurately.

When translating:
1. Preserve the logic and functionality exactly
2. Use idiomatic patterns of the target language
3. Translate data structures to their equivalents
4. Handle language-specific features (e.g., error handling, async patterns)
5. Add comments where the translation involves non-obvious changes
6. Note any limitations or differences in the translation

Provide:
- The translated code in a code block
- A brief explanation of key translation decisions
- Any important differences between the source and target implementations"""


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    defaults = {
        "ollama_base_url": "http://localhost:11434",
        "model": "gemma3:1b",
        "temperature": 0.3,
        "max_code_chars": 5000,
        "batch_output_dir": "translations",
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
            defaults.update(user_config)
            logger.info("Loaded config from %s", config_path)
        except Exception as e:
            logger.warning("Failed to load config: %s", e)
    return defaults


def detect_source_language(filepath: str) -> str:
    """Detect the source language from file extension."""
    _, ext = os.path.splitext(filepath)
    for lang, info in SUPPORTED_LANGUAGES.items():
        if info["ext"] == ext:
            return lang
    return ""


def get_language_name(lang: str) -> str:
    """Get display name for a language code."""
    return SUPPORTED_LANGUAGES.get(lang, {}).get("name", lang)


def get_language_ext(lang: str) -> str:
    """Get file extension for a language code."""
    return SUPPORTED_LANGUAGES.get(lang, {}).get("ext", ".txt")


def read_source_file(filepath: str) -> str:
    """Read the source code file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found.")
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def translate_code(code: str, source_lang: str, target_lang: str, chat_fn,
                   config: Optional[dict] = None) -> str:
    """Translate code from one language to another using the LLM."""
    if config is None:
        config = load_config()

    source_name = get_language_name(source_lang)
    target_name = get_language_name(target_lang)

    prompt = f"""Translate the following {source_name} code to {target_name}:

```{source_lang}
{code[:config.get('max_code_chars', 5000)]}
```

Provide the complete translated code with explanations of key translation decisions."""

    messages = [{"role": "user", "content": prompt}]
    logger.info("Translating %s → %s (%d chars)", source_name, target_name, len(code))

    response = chat_fn(messages, system_prompt=SYSTEM_PROMPT, temperature=config.get("temperature", 0.3))
    return response


def validate_syntax(code: str, language: str) -> dict:
    """Basic syntax validation for common languages."""
    issues = []

    if language == "python":
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            issues.append(f"Line {e.lineno}: {e.msg}")

    elif language in ("javascript", "typescript"):
        # Basic bracket matching
        opens = code.count("{") + code.count("(") + code.count("[")
        closes = code.count("}") + code.count(")") + code.count("]")
        if opens != closes:
            issues.append(f"Unbalanced brackets: {opens} opens vs {closes} closes")

    elif language == "java":
        if "class " not in code and "interface " not in code:
            issues.append("No class or interface declaration found")

    return {"valid": len(issues) == 0, "issues": issues}


def compare_codes(source: str, translated: str) -> dict:
    """Generate comparison metrics between source and translated code."""
    src_lines = source.splitlines()
    tgt_lines = translated.splitlines()

    return {
        "source_lines": len(src_lines),
        "target_lines": len(tgt_lines),
        "line_ratio": round(len(tgt_lines) / max(len(src_lines), 1), 2),
        "source_chars": len(source),
        "target_chars": len(translated),
    }


def batch_translate_files(
    file_paths: list[str],
    target_lang: str,
    chat_fn,
    output_dir: str = "translations",
    config: Optional[dict] = None,
) -> list[dict]:
    """Translate multiple files in batch."""
    if config is None:
        config = load_config()

    os.makedirs(output_dir, exist_ok=True)
    results = []

    for filepath in file_paths:
        try:
            code = read_source_file(filepath)
            source_lang = detect_source_language(filepath)
            if not source_lang:
                source_lang = "unknown"

            translation = translate_code(code, source_lang, target_lang, chat_fn, config)

            base_name = os.path.splitext(os.path.basename(filepath))[0]
            ext = get_language_ext(target_lang)
            output_path = os.path.join(output_dir, f"{base_name}{ext}")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(translation)

            results.append({
                "source": filepath,
                "output": output_path,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "status": "success",
            })
            logger.info("Translated %s → %s", filepath, output_path)

        except Exception as e:
            results.append({
                "source": filepath,
                "status": "error",
                "error": str(e),
            })
            logger.error("Failed to translate %s: %s", filepath, e)

    return results


def generate_translation_notes(source_lang: str, target_lang: str, chat_fn) -> str:
    """Generate general notes about translating between two languages."""
    source_name = get_language_name(source_lang)
    target_name = get_language_name(target_lang)

    prompt = f"""Provide key notes and gotchas when translating code from {source_name} to {target_name}.

Cover:
1. Major syntax differences
2. Type system differences
3. Error handling patterns
4. Standard library equivalents
5. Common pitfalls"""

    messages = [{"role": "user", "content": prompt}]
    response = chat_fn(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)
    return response
