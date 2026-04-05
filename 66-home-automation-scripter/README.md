# 🏠 Home Automation Scripter

Generate home automation scripts from natural language descriptions using a local Gemma 4 LLM via Ollama.

## Features

- **Natural Language Rules**: Describe automations in plain English
- **Multi-Platform Support**: Home Assistant, IFTTT, openHAB, Node-RED
- **Script Explanation**: Understand existing automation scripts
- **Smart Suggestions**: Get automation ideas based on your devices
- **Rule Storage**: Save and manage generated rules
- **Syntax Highlighting**: Beautiful code output with syntax highlighting

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally with Gemma 4 model

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Generate Automation Script
```bash
python app.py generate-rule --rule "turn off lights at 11pm" --platform homeassistant
python app.py generate-rule --rule "adjust thermostat when nobody is home" --platform ifttt
```

### Save Generated Rule
```bash
python app.py generate-rule --rule "motion-activated lights" --platform homeassistant --save
```

### Explain a Script
```bash
python app.py explain --script automation.yaml --platform homeassistant
```

### Get Suggestions
```bash
python app.py suggest --devices "lights, thermostat, motion sensor, door lock"
```

### List Saved Rules
```bash
python app.py list
```

## Supported Platforms

| Platform       | Format          | Use Case              |
|---------------|-----------------|------------------------|
| Home Assistant | YAML automation | Full home automation   |
| IFTTT         | If-Then rules    | Simple trigger-action  |
| openHAB       | DSL rules        | Complex rule engine    |
| Node-RED      | Flow JSON        | Visual flow automation |

## Example Output

```yaml
automation:
  - alias: "Turn off lights at 11pm"
    trigger:
      platform: time
      at: "23:00:00"
    action:
      service: light.turn_off
      entity_id: group.all_lights
```

## Testing

```bash
pytest test_app.py -v
```

## License

MIT
