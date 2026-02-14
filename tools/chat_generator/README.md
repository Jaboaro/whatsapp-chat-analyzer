# Synthetic WhatsApp Chat Generator

This module provides a deterministic, configurable CLI tool to generate synthetic WhatsApp chat exports.

It exists exclusively as an auxiliary tool to support:

- Testing the parsing pipeline
- Generating reproducible demo datasets
- Stress-testing analysis modules
- Simulating heterogeneous user behavior

It is **not** part of the core application logic.

---

## 🎯 Purpose

The main WhatsApp Chat Analyzer application operates on exported `.txt` chat files.

To ensure:

- Reliable automated testing
- Consistent demo data
- Realistic behavioral distributions
- Controlled edge cases

This tool generates synthetic WhatsApp exports that mimic real-world conversational patterns.

---

## 🧠 Behavioral Modeling

Unlike naive generators, this tool does not distribute messages uniformly across users.

Each participant is assigned a `UserProfile` representing a behavioral archetype:

- **Talker** – High message volume
- **Media Sender** – High probability of sending media
- **Balanced** – Moderate activity
- **Lurker** – Low participation

Profiles affect:

- Message rate multiplier
- Media probability
- Media type distribution

This creates non-uniform distributions, producing realistic analytics outputs.

---

## 🏗 Architecture

```
chat_generator/
│
├── generate.py # CLI entry point
├── generator.py # Core simulation logic
├── profiles.py # ExportProfile & UserProfile definitions
├── distributions.py # Statistical distributions & randomness control
```

### Design Principles

- Deterministic randomness via `seed`
- Separation of formatting and behavior
- Locale abstraction through `ExportProfile`
- No dependency on Streamlit or analysis modules
- Self-contained simulation engine

---

## 🌍 Export Profiles

The generator supports multiple WhatsApp export formats:

- English (`en`)
- Spanish (`es`)

Each locale defines:

- Date-time formatting
- Media placeholder strings
- Line formatting rules

New locales can be added by defining a new `ExportProfile`.

---

## 🚀 CLI Usage

Basic example:

```bash
python -m tools.chat_generator.generate \
  --profile es \
  --users Alice Bob Carol Daniel \
  --start-date 2020-01-01 \
  --days 120 \
  --avg-messages-per-day 150 \
  --seed 42 \
  --output data/sample_chats/sample_chat_es.txt

```
| Argument                 | Description                       |
| ------------------------ | --------------------------------- |
| `--profile`              | Export locale (`en` or `es`)      |
| `--users`                | List of chat participants (min 2) |
| `--start-date`           | Start date in `YYYY-MM-DD` format |
| `--days`                 | Number of days to simulate        |
| `--avg-messages-per-day` | Baseline message volume           |
| `--seed`                 | Random seed for reproducibility   |
| `--output`               | Output file path                  |
## 🔁 Determinism

When a seed is provided:

-   User profile assignment becomes reproducible
    
-   Message timing is deterministic
    
-   Media distribution remains consistent
    

This allows:

-   Snapshot testing
    
-   Regression testing
    
-   Reproducible demos
    

---

## 📊 Simulation Logic Overview

For each day:

1.  Sample number of messages using statistical distribution
    
2.  Generate conversation bursts
    
3.  Select sender based on activity multiplier
    
4.  Determine message type (text or media)
    
5.  Format output using selected `ExportProfile`
    

Output is a raw `.txt` file compatible with the main analyzer.

---

## ⚙ Extensibility

The generator can be extended to support:

-   Directed replies
    
-   Conversation clusters
    
-   Time-of-day activity bias per user
    
-   Group dominance patterns
    
-   Social network simulation models
    

The current implementation intentionally remains lightweight and focused.

---

## 📌 Why This Tool Is Separate

The generator is isolated from the main app to:

-   Avoid coupling simulation logic with analysis
    
-   Keep the Streamlit layer clean
    
-   Maintain modular architecture
    
-   Allow independent evolution of the simulator
    

---

## 👨‍💻 Engineering Notes

-   Uses `dataclasses` for profile modeling
    
-   Avoids mutable objects as dictionary keys
    
-   Explicit type hints throughout
    
-   No side effects outside CLI entry point
    
-   Fully compatible with Python module execution (`-m`)
    

---

This tool exists to support the analytical core of the project —  
the true focus remains the WhatsApp Chat Analyzer application.

```yaml
---