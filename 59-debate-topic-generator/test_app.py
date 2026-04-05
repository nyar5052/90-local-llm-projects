"""Unit tests for Debate Topic Generator."""

import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner

from app import main, generate_debate_topics, display_debate_topics


SAMPLE_DEBATES = {
    "subject": "Technology",
    "complexity": "intermediate",
    "topics": [
        {
            "number": 1,
            "motion": "This house believes AI should be regulated by governments",
            "context": "AI is rapidly advancing and reshaping society.",
            "pro_arguments": [
                {
                    "point": "Prevents misuse",
                    "explanation": "Regulation ensures AI isn't used for harm.",
                    "evidence": "EU AI Act as a precedent."
                },
                {
                    "point": "Protects jobs",
                    "explanation": "Managed AI deployment protects workers.",
                    "evidence": "Studies show 30% of jobs at risk."
                },
                {
                    "point": "Ensures safety",
                    "explanation": "Regulations mandate safety testing.",
                    "evidence": "Self-driving car incidents."
                }
            ],
            "con_arguments": [
                {
                    "point": "Stifles innovation",
                    "explanation": "Over-regulation slows progress.",
                    "evidence": "US vs EU tech growth comparison."
                },
                {
                    "point": "Hard to enforce",
                    "explanation": "AI development is global and decentralized.",
                    "evidence": "Open-source AI models."
                },
                {
                    "point": "Government incompetence",
                    "explanation": "Legislators may not understand AI well enough.",
                    "evidence": "Past tech regulation failures."
                }
            ],
            "counterarguments": [
                "Self-regulation by industry could be more effective",
                "International cooperation is needed, not national regulation"
            ],
            "key_questions": [
                "What specific aspects of AI should be regulated?",
                "Who decides what constitutes harmful AI?"
            ],
            "difficulty": "medium"
        }
    ]
}


@patch("app.chat")
def test_generate_debate_topics_parses_json(mock_chat):
    """Test that generate_debate_topics correctly parses LLM JSON response."""
    mock_chat.return_value = json.dumps(SAMPLE_DEBATES)
    result = generate_debate_topics("Technology", "intermediate", 1)
    assert result["subject"] == "Technology"
    assert len(result["topics"]) == 1
    assert len(result["topics"][0]["pro_arguments"]) == 3


@patch("app.chat")
def test_generate_debate_topics_correct_prompt(mock_chat):
    """Test that the prompt includes subject and complexity."""
    mock_chat.return_value = json.dumps(SAMPLE_DEBATES)
    generate_debate_topics("Education", "advanced", 5)
    call_content = mock_chat.call_args[1]["messages"][0]["content"]
    assert "Education" in call_content
    assert "advanced" in call_content
    assert "5" in call_content


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_basic_run(mock_chat, mock_check):
    """Test CLI runs successfully."""
    mock_chat.return_value = json.dumps(SAMPLE_DEBATES)
    runner = CliRunner()
    result = runner.invoke(main, ["--subject", "technology", "--topics", "1"])
    assert result.exit_code == 0
    assert "Debate Topic Generator" in result.output


@patch("app.check_ollama_running", return_value=True)
@patch("app.chat")
def test_cli_save_output(mock_chat, mock_check, tmp_path):
    """Test CLI saves topics to JSON file."""
    mock_chat.return_value = json.dumps(SAMPLE_DEBATES)
    outfile = str(tmp_path / "debates.json")
    runner = CliRunner()
    result = runner.invoke(main, ["--subject", "tech", "--output", outfile])
    assert result.exit_code == 0
    with open(outfile) as f:
        data = json.load(f)
    assert data["subject"] == "Technology"


@patch("app.check_ollama_running", return_value=False)
def test_cli_ollama_not_running(mock_check):
    """Test CLI exits when Ollama is not running."""
    runner = CliRunner()
    result = runner.invoke(main, ["--subject", "tech"])
    assert result.exit_code != 0
    assert "Ollama is not running" in result.output
