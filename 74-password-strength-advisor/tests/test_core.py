"""Tests for Password Strength Advisor core module."""

import pytest
from unittest.mock import patch

from src.password_advisor.core import (
    calculate_entropy,
    check_breach_database,
    generate_policy,
    generate_password,
    bulk_analyze,
    analyze_password_llm,
    analyze_policy_llm,
    StrengthLevel,
    EntropyResult,
)


class TestCalculateEntropy:
    def test_empty_password(self):
        result = calculate_entropy("")
        assert result.entropy_bits == 0
        assert result.strength == StrengthLevel.VERY_WEAK

    def test_simple_password(self):
        result = calculate_entropy("abc")
        assert result.entropy_bits < 25
        assert result.strength in (StrengthLevel.VERY_WEAK, StrengthLevel.WEAK)

    def test_strong_password(self):
        result = calculate_entropy("MyStr0ng!P@ssw0rd#2024")
        assert result.entropy_bits > 60
        assert result.strength in (StrengthLevel.STRONG, StrengthLevel.VERY_STRONG)

    def test_charset_detection(self):
        result = calculate_entropy("Aa1!")
        assert result.details["lowercase"] is True
        assert result.details["uppercase"] is True
        assert result.details["digits"] is True
        assert result.details["special"] is True
        assert result.details["char_types"] == 4

    def test_time_to_crack_instant(self):
        result = calculate_entropy("a")
        assert result.time_to_crack == "instant"

    def test_pattern_penalty(self):
        sequential = calculate_entropy("12345678")
        random_digits = calculate_entropy("83729461")
        # Sequential should have lower effective entropy
        assert sequential.details["pattern_penalty"] > 0


class TestBreachCheck:
    def test_known_password(self):
        result = check_breach_database("password")
        assert result.is_compromised is True
        assert result.occurrences > 0

    def test_leet_variation(self):
        result = check_breach_database("p@ssw0rd")
        assert result.is_compromised is True

    def test_unknown_password(self):
        result = check_breach_database("xK9#mP2!qR5@vL8&nJ3")
        assert result.is_compromised is False


class TestGeneratePassword:
    def test_default_generation(self):
        pwd = generate_password(16, "upper,lower,digits,special")
        assert len(pwd) == 16
        assert any(c.isupper() for c in pwd)
        assert any(c.islower() for c in pwd)
        assert any(c.isdigit() for c in pwd)

    def test_custom_length(self):
        pwd = generate_password(32, "upper,lower")
        assert len(pwd) == 32

    def test_minimum_mandatory(self):
        pwd = generate_password(4, "upper,lower,digits,special")
        assert len(pwd) == 4


class TestGeneratePolicy:
    def test_default_policy(self):
        rules = generate_policy()
        assert len(rules) >= 8
        names = [r.name for r in rules]
        assert "Minimum Length" in names
        assert "Multi-Factor Authentication" in names

    def test_custom_policy(self):
        rules = generate_policy({"min_length": "16"})
        min_rule = next(r for r in rules if r.name == "Minimum Length")
        assert "16" in min_rule.description


class TestBulkAnalyze:
    def test_bulk_analysis(self):
        passwords = ["password", "MyStr0ng!Pass#2024", "abc"]
        results = bulk_analyze(passwords)
        assert len(results) == 3
        assert results[0].strength in (StrengthLevel.VERY_WEAK, StrengthLevel.WEAK)
        assert "Found in breach database" in results[0].issues

    def test_empty_list(self):
        results = bulk_analyze([])
        assert results == []


class TestLLMFunctions:
    @patch("src.password_advisor.core.chat")
    def test_analyze_password_llm(self, mock_chat):
        mock_chat.return_value = "## Strength: Strong\nEntropy: ~80 bits"
        result = analyze_password_llm("MyStr0ng!Pass#2024")
        assert "Strong" in result or "Entropy" in result

    @patch("src.password_advisor.core.chat")
    def test_analyze_policy_llm(self, mock_chat):
        mock_chat.return_value = "## Policy Analysis\n- Length: ADEQUATE ⚠️"
        result = analyze_policy_llm("Min 8 chars, no MFA")
        assert "Policy" in result or "ADEQUATE" in result
