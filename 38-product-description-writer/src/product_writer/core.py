"""Core business logic for Product Description Writer."""

import logging
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "llm": {"temperature": 0.7, "max_tokens": 4096},
    "product": {
        "platforms": ["amazon", "shopify", "etsy", "ebay", "generic"],
        "lengths": ["short", "medium", "long"],
        "default_variants": 2,
    },
    "seo": {"keyword_count": 10, "min_keyword_density": 1.0, "max_keyword_density": 3.0},
    "export": {"output_dir": "output"},
}

PLATFORM_CONFIGS = {
    "amazon": {
        "name": "Amazon",
        "icon": "🛒",
        "tips": "Use bullet points for features, include A+ content structure, focus on benefits over features. Title max 200 chars. Use backend keywords.",
        "title_max": 200,
        "bullet_count": 5,
        "char_limit": 2000,
    },
    "shopify": {
        "name": "Shopify",
        "icon": "🏪",
        "tips": "Storytelling approach, lifestyle-focused, brand voice consistency. Use rich HTML formatting. Include meta description.",
        "title_max": 70,
        "char_limit": 5000,
    },
    "etsy": {
        "name": "Etsy",
        "icon": "🎨",
        "tips": "Handmade/unique angle, personal touch, craftsmanship details. Use all 13 tags. Emphasize materials and process.",
        "title_max": 140,
        "tag_count": 13,
        "char_limit": 3000,
    },
    "ebay": {
        "name": "eBay",
        "icon": "🏷️",
        "tips": "Clear specifications, condition details, competitive positioning. Include item specifics. Be factual and precise.",
        "title_max": 80,
        "char_limit": 4000,
    },
    "generic": {
        "name": "Generic",
        "icon": "📦",
        "tips": "Versatile format suitable for any e-commerce platform. Balance SEO with readability.",
        "title_max": 150,
        "char_limit": 3000,
    },
}

FEATURE_BENEFIT_MAP = {
    "waterproof": "Stay dry and protected in any weather",
    "lightweight": "Carry effortlessly without fatigue",
    "bluetooth": "Connect wirelessly to all your devices",
    "noise-canceling": "Immerse yourself in pure, distraction-free sound",
    "organic": "Made with natural ingredients, free from harmful chemicals",
    "rechargeable": "Save money and reduce waste with reusable power",
    "portable": "Take it anywhere - compact design fits your lifestyle",
    "adjustable": "Customize the perfect fit for your comfort",
}

LENGTH_GUIDE = {
    "short": {"words": "50-100", "description": "Brief and punchy"},
    "medium": {"words": "150-250", "description": "Balanced detail"},
    "long": {"words": "300-500", "description": "Comprehensive coverage"},
}


def load_config(config_path: Optional[str] = None) -> dict:
    config = DEFAULT_CONFIG.copy()
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
        _deep_merge(config, user_config)
    return config


def _deep_merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def get_platform_configs() -> dict:
    return PLATFORM_CONFIGS


def get_feature_benefit_map() -> dict:
    return FEATURE_BENEFIT_MAP


def map_features_to_benefits(features: list[str]) -> list[dict]:
    """Map product features to customer benefits."""
    mapped = []
    for feat in features:
        feat_lower = feat.strip().lower()
        benefit = FEATURE_BENEFIT_MAP.get(feat_lower, f"Enjoy the advantage of {feat.strip()}")
        mapped.append({"feature": feat.strip(), "benefit": benefit})
    return mapped


def calculate_seo_score(text: str, keywords: list[str]) -> dict:
    """Calculate an SEO score for the given text."""
    text_lower = text.lower()
    word_count = len(text.split())
    scores = {}
    total_density = 0
    found = 0
    for kw in keywords:
        count = text_lower.count(kw.lower())
        density = (count / word_count * 100) if word_count > 0 else 0
        scores[kw] = {"count": count, "density": round(density, 2)}
        total_density += density
        if count > 0:
            found += 1

    coverage = (found / len(keywords) * 100) if keywords else 0
    overall = min(100, int(coverage * 0.6 + min(total_density * 10, 40)))
    return {
        "overall_score": overall,
        "keyword_coverage": round(coverage, 1),
        "word_count": word_count,
        "keyword_details": scores,
    }


def build_prompt(
    product: str,
    features: list[str],
    platform: str,
    length: str,
    variants: int,
    keywords: Optional[list[str]] = None,
) -> str:
    """Build the product description generation prompt."""
    feat_str = "\n".join(f"- {f.strip()}" for f in features) if features else "- Not specified"
    plat = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["generic"])
    lg = LENGTH_GUIDE.get(length, LENGTH_GUIDE["medium"])

    benefits = map_features_to_benefits(features) if features else []
    benefit_section = ""
    if benefits:
        benefit_lines = "\n".join(f"- {b['feature']} → {b['benefit']}" for b in benefits)
        benefit_section = f"\n**Feature-Benefit Mapping:**\n{benefit_lines}\n"

    keyword_section = ""
    if keywords:
        keyword_section = f"\n**Target SEO Keywords:** {', '.join(keywords)}\nNaturally incorporate these keywords.\n"

    return (
        f"Create {variants} product description variant(s) for:\n\n"
        f"**Product:** {product}\n"
        f"**Key Features:**\n{feat_str}\n"
        f"{benefit_section}"
        f"\n**Platform:** {plat['name']}\n"
        f"**Platform Tips:** {plat['tips']}\n"
        f"**Length:** {lg['words']} words ({lg['description']})\n"
        f"{keyword_section}\n"
        f"For each variant provide:\n"
        f"1. **Product Title** (SEO-optimized, keyword-rich, max {plat.get('title_max', 150)} chars)\n"
        f"2. **Short Description** (1-2 sentences for search results)\n"
        f"3. **Full Description** (complete product copy)\n"
        f"4. **Bullet Points** (5-7 key selling points)\n"
        f"5. **SEO Keywords** (10 relevant search terms)\n\n"
        f"Label each variant as 'Variant 1:', 'Variant 2:', etc.\n"
        f"Focus on benefits, use power words, and create urgency.\n"
    )


def generate_descriptions(
    product: str,
    features: list[str],
    platform: str,
    length: str,
    variants: int,
    keywords: Optional[list[str]] = None,
    config: Optional[dict] = None,
) -> str:
    """Generate product descriptions using the LLM."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import chat

    cfg = config or DEFAULT_CONFIG
    system_prompt = (
        "You are an expert e-commerce copywriter and SEO specialist. "
        "You write product descriptions that convert browsers into buyers. "
        "You understand platform-specific best practices and consumer psychology."
    )
    user_prompt = build_prompt(product, features, platform, length, variants, keywords)
    messages = [{"role": "user", "content": user_prompt}]
    logger.info("Generating %d variants for '%s' on %s", variants, product, platform)
    return chat(
        messages,
        system_prompt=system_prompt,
        temperature=cfg["llm"]["temperature"],
        max_tokens=cfg["llm"]["max_tokens"],
    )


def generate_ab_variants(product: str, features: list[str], platform: str, config: Optional[dict] = None) -> dict:
    """Generate A/B test variants with different approaches."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from common.llm_client import chat

    cfg = config or DEFAULT_CONFIG
    prompt = (
        f"Create 2 A/B test variants for this product listing:\n\n"
        f"Product: {product}\nFeatures: {', '.join(features)}\nPlatform: {platform}\n\n"
        f"Variant A: Benefits-focused, emotional appeal\n"
        f"Variant B: Features-focused, data-driven\n\n"
        f"For each variant provide title, description, and 5 bullet points.\n"
    )
    messages = [{"role": "user", "content": prompt}]
    result = chat(messages, system_prompt="You are an e-commerce A/B testing expert.", temperature=cfg["llm"]["temperature"], max_tokens=cfg["llm"]["max_tokens"])
    return {"variants": result, "generated_at": datetime.now().isoformat()}
