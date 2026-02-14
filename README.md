# WhatsApp Chat Analyzer

A data-driven WhatsApp chat analysis tool built with **Python + Streamlit**, designed to extract insights from exported conversations.

This project focuses on transforming raw chat exports into meaningful visual analytics — message distribution, participation dynamics, media usage patterns, and conversational structure.


## 🚀 Live Application

*(Add deployment link here if available)*



## 🎯 Project Goals

* Parse raw WhatsApp exported chat files
* Normalize multi-locale export formats (EN / ES supported)
* Generate structured conversation datasets
* Provide clear and interpretable visual insights
* Maintain deterministic reproducibility for testing
* Separate analysis logic from UI concerns

This is not a toy dashboard — it is built with clean architecture and extensibility in mind.



## 🧠 Core Features

### 📊 Message Analytics

* Messages per user
* Messages over time
* Activity distribution by hour/day
* Conversation bursts & breaks

### 🖼 Media Analysis

* Media type distribution
* Media usage per participant
* Media vs text ratio

### 🗂 Multi-Locale Support

* English export format
* Spanish export format
* Extensible profile system

### 🧪 Deterministic Testing

* Reproducible synthetic chat generation
* Seed-based simulation
* Heterogeneous user behavior modeling



## 🏗 Architecture Overview

The project follows separation of concerns:

```
app/
    streamlit_app.py      → UI layer
    analysis/             → Data processing logic
    parsing/              → WhatsApp export parsing
    visualization/        → Chart generation

tools/
    chat_generator/       → Synthetic chat generator (auxiliary tool)
```

### Key Design Principles

* Explicit export formatting profiles
* Deterministic randomness via seeds
* Clean data flow: raw → parsed → structured → analyzed → visualized
* UI is thin, logic is reusable



## 🧪 Synthetic Chat Generator (Auxiliary Tool)

To support testing and demonstration, the project includes a CLI tool that generates realistic WhatsApp chat exports.

It is intentionally separated from the main app logic.

### Why it exists

* Enables reproducible demo data
* Stress-tests parsing logic
* Simulates heterogeneous user behavior
* Generates controlled edge cases

### Example usage

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

### Behavioral Modeling

Each participant is assigned a behavior profile:

* Talker (high message volume)
* Media Sender (high media probability)
* Balanced user
* Lurker (low participation)

This removes uniform bias and produces realistic insight distributions.



## 📦 Installation

```bash
git clone <repo-url>
cd whatsapp-chat-analyzer
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app/streamlit_app.py
```


## 📌 Supported Export Formats

The system currently supports:

* WhatsApp English export format
* WhatsApp Spanish export format

The architecture allows additional locales via `ExportProfile`.

---
# 🧩 Design Decisions

## 1️⃣ Separation of Simulation and Analysis

The synthetic chat generator is intentionally isolated under `tools/`.

**Why?**

-   Prevents coupling between data generation and analysis logic
    
-   Keeps the Streamlit app clean and focused
    
-   Allows independent evolution of the simulator
    
-   Preserves architectural clarity
    

The main application must work with *real exported chats*.  
The generator only exists to support testing and demonstrations.



## 2️⃣ ExportProfile Abstraction

WhatsApp export formats vary by locale.

Instead of hardcoding parsing rules, the project defines an `ExportProfile` abstraction that encapsulates:

-   Date-time format
    
-   Media placeholder strings
    
-   Line formatting structure
    

This allows:

-   Multi-locale support
    
-   Clean extension to new formats
    
-   Zero conditional logic in the parsing core
    



## 3️⃣ Deterministic Randomness

The generator supports explicit seeds.

This enables:

-   Reproducible datasets
    
-   Snapshot testing
    
-   Regression validation
    
-   Controlled experimentation
    

Non-deterministic tools are difficult to test.  
This system avoids that problem by design.


## 4️⃣ Heterogeneous Behavioral Modeling

Uniform distributions produce misleading analytics.

Each synthetic participant is assigned a behavioral profile:

-   Activity multiplier
    
-   Media probability
    
-   Media type distribution
    

This produces realistic non-uniform distributions that generate meaningful insights in the visualization layer.



## 5️⃣ Thin UI Philosophy

The Streamlit layer is intentionally thin.

-   UI triggers analysis
    
-   Analysis logic lives outside the UI
    
-   Visualization functions are reusable
    

This keeps the app maintainable and testable.



# 🏗 Architecture Deep Dive

This section explains the internal data flow from raw chat to insight.

---

## 🔁 Data Flow Pipeline

```java
Raw WhatsApp .txt
        ↓
Parsing Layer
        ↓
Structured Data Model (DataFrame)
        ↓
Analysis Layer
        ↓
Visualization Layer
        ↓
Streamlit UI
```

Each layer has a single responsibility.


## 📥 Parsing Layer

Responsibilities:

-   Recognize valid message lines
    
-   Extract timestamp
    
-   Extract sender
    
-   Detect media placeholders
    
-   Handle multiline messages
    

Parsing is locale-aware through `ExportProfile`.

No visualization or aggregation logic exists at this stage.

---

## 📊 Structured Representation

After parsing, the chat is represented as structured tabular data:

-   timestamp
    
-   sender
    
-   message\_type (text / media)
    
-   media\_type (if applicable)
    
-   content
    
-   derived temporal features
    

This normalized representation becomes the foundation for all analytics.


## 📈 Analysis Layer

This layer computes:

-   Message counts per user
    
-   Time-series aggregations
    
-   Hour-of-day distributions
    
-   Media ratios
    
-   Participation dominance
    

The analysis layer is:

-   UI-agnostic
    
-   Deterministic
    
-   Testable independently
    



## 📊 Visualization Layer

Visualization functions:

-   Receive precomputed aggregates
    
-   Generate charts
    
-   Avoid embedding business logic
    

This ensures charts are declarative, not computational.



## 🧠 Why This Architecture Matters

Many dashboard projects mix:

-   Parsing
    
-   Aggregation
    
-   Visualization
    
-   UI state
    

This project deliberately avoids that pattern.

Instead, it demonstrates:

-   Modular design
    
-   Clean layering
    
-   Reproducible simulation
    
-   Extensibility for future analytical features
    



# 🎯 Resulting Engineering Properties

-   Low coupling
    
-   High cohesion
    
-   Deterministic behavior
    
-   Clear extensibility path
    
-   Portfolio-grade architecture clarity
## 🧩 Future Improvements

* Network graph of interaction dynamics
* Sentiment analysis module
* Emoji frequency clustering
* Conversation topic modeling
* Multi-chat comparative analytics


# ⚖ Limitations & Tradeoffs

## 1️⃣ WhatsApp Export Dependency

The parser relies on exported `.txt` files generated by WhatsApp.

Tradeoff:

-   ✔ Simple and portable format
    
-   ✖ Dependent on WhatsApp’s export structure
    

If WhatsApp changes its export formatting, parsing rules must be updated.

The `ExportProfile` abstraction mitigates this risk by isolating format-specific logic.


## 2️⃣ No Direct Message Metadata

WhatsApp exports do not include:

-   Read receipts
    
-   Reactions
    
-   Threaded replies
    
-   Delivery states
    

This limits the ability to perform deeper interaction modeling.

The analysis is constrained to available textual data.



## 3️⃣ Synthetic Generator Simplifications

The chat generator models:

-   Message volume differences
    
-   Media usage variation
    
-   Activity multipliers
    

However, it does not simulate:

-   Directed replies
    
-   Social graph dynamics
    
-   Emotional tone shifts
    
-   Topic evolution
    
-   Real linguistic patterns
    

The goal is analytical realism, not linguistic realism.


## 4️⃣ Time Modeling Assumptions

Message timing uses probabilistic distributions and burst simulation.

This approximates real-world behavior but does not replicate:

-   Circadian rhythms per user
    
-   Weekend vs weekday patterns
    
-   Cultural activity differences
    

These could be introduced in future iterations.



## 5️⃣ Streamlit as UI Layer

Streamlit enables rapid development and clean visualization.

Tradeoff:

-   ✔ Fast prototyping
    
-   ✔ Low boilerplate
    
-   ✖ Less control compared to a full frontend framework
    

For a production-scale analytics platform, a decoupled frontend might be preferable.



## 6️⃣ Single-Chat Scope

The current design analyzes one chat at a time.

Future directions could include:

-   Cross-chat comparisons
    
-   Longitudinal behavioral tracking
    
-   Group vs 1-to-1 dynamics
    

The architecture supports extension, but it is intentionally scoped.



# 🧠 Why Document Limitations?

Explicitly documenting tradeoffs demonstrates:

-   Architectural awareness
    
-   Engineering maturity
    
-   Realistic system boundaries
    
-   Intentional scope control
    

No system is perfect.  
Strong systems are explicit about their constraints.


## 📄 License

MIT License



## 👨‍💻 Author

Built as a portfolio project to demonstrate:

* Clean architecture in Python
* Deterministic simulation modeling
* CLI tooling
* Data analysis pipelines
* Streamlit-based visualization apps



If you found this project interesting, feel free to reach out.
