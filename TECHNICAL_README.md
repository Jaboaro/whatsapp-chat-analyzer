# WhatsApp Chat Analyzer – Technical Deep Dive

This document explains the internal design, parsing strategy, architecture decisions, and simulation tooling.

Intended for developers and technical reviewers.



## 1️⃣ Project Structure
```
app/
├─ app.py
├─ analysis/
├─ parser/
├─ filters/
└─ ui/

tools/
└─ chat_generator/
```
### Responsibilities

- `parser/` → Raw text → Structured messages
- `analysis/` → Aggregations & metrics
- `ui/` → Visualization helpers
- `app.py` → Streamlit interface (thin UI layer)
- `tools/chat_generator/` → Synthetic chat creation

Separation ensures testability and maintainability.



## 2️⃣ Parsing Layer

### Message Flow

1. Read file
2. Segment multi-line messages
3. Parse timestamp, sender, message
4. Detect media placeholders
5. Detect quoted replies
6. Return structured dataframe



### ExportProfile Abstraction

`ExportProfile` defines:

- Date format
- Message separator
- Media placeholder strings
- Locale-specific patterns

This allows supporting multiple WhatsApp export formats (EN / ES) without modifying parsing logic.

Example:

```python
from parser.whatsapp_parser import parse_chat
from parser.profiles import EN_PROFILE

df, stats = parse_chat(file, export_profile=EN_PROFILE)
```
This decouples format definition from parsing behavior.



## 3️⃣ Data Representation

Each parsed message becomes a structured record:

| Field          | Description      |
| -------------- | ---------------- |
| datetime       | Parsed timestamp |
| sender         | Message author   |
| message        | Raw content      |
| quoted_message | Boolean flag     |

Derived temporal features are computed in the analysis layer.



## 4️⃣ Analysis Layer

Fully UI-agnostic.

Includes:

-   Messages per day
    
-   Rolling averages
    
-   Hour-of-day distribution
    
-   Participation share
    
-   Media usage metrics
    
-   Weekday × hour heatmaps
    

All functions are deterministic and independently testable.



## 5️⃣ Visualization Layer

Receives precomputed aggregates and renders charts.

No business logic lives inside Streamlit components.

This keeps:

-   Testing easier
    
-   Logic reusable
    
-   UI lightweight
    



## 6️⃣ Synthetic Chat Generator

Located in:

```bash
tools/chat_generator/
```

### Purpose

-   Stress-test parsing
    
-   Demonstrate features
    
-   Generate reproducible demo data
    

### Features

-   Multiple participants
    
-   Behavioral profiles:
    
    -   Talker
        
    -   Media-heavy
        
    -   Balanced
        
    -   Lurker
        
-   Seed-based reproducibility
    
-   Multi-locale export formatting
    

Example usage:

```bash
python -m tools.chat_generator.generate \
  --profile es \
  --users Alice Bob Carol \
  --start-date 2020-01-01 \
  --days 120 \
  --avg-messages-per-day 150 \
  --seed 42 \
  --output sample_chat.txt
```



## 7️⃣ Key Design Decisions

### 1\. Thin UI Philosophy

Streamlit is only a presentation layer.

### 2\. ExportProfile Abstraction

Separates format definition from parsing logic.

### 3\. Deterministic Simulation

Seeds guarantee reproducibility.

### 4\. Modular Structure

Parser, analysis, and UI do not depend tightly on each other.

### 5\. Privacy by Design

-   Online demo only uses built-in sample data
    
-   Personal chat analysis requires local execution
    



## 8️⃣ Limitations

-   Depends on WhatsApp `.txt` export format
    
-   Does not currently parse WhatsApp reactions or system metadata events.
    
-   Synthetic chats simplify real-world behavior
    
-   Single-chat analysis only
    



## 9️⃣ Future Improvements

-   Sentiment analysis
    
-   Emoji frequency metrics
    
-   Network interaction graph
    
-   Topic modeling
    
-   Multi-chat comparisons
    



## Privacy Note

All real chat processing occurs locally.

The public demo version disables file uploads and only uses a synthetic sample dataset.
## Design Philosophy

This project prioritizes:
- Determinism over randomness
- Explicit parsing rules over heuristics
- Testable pure functions over UI-driven logic
- Clear separation of responsibilities
## General documentation


For general documentation:

See [General README](README.md)

    

