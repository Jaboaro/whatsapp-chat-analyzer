# Synthetic WhatsApp Chat Generator

A standalone tool to generate WhatsApp chat exports for testing, demos, and development.

This generator produces `.txt` files that are compatible with the WhatsApp Chat Analyzer parser, supporting multiple locales and configurable chat dynamics.



## Overview

The generator simulates:

- Multiple participants
- Varying message frequencies
- Media vs text messages
- Behavioral patterns per user
- Locale-specific export formatting

It is used by the main application for demo purposes and can also be used independently via CLI.



## Features

- **Multiple participants** with non-uniform behavior
- **Seed-based reproducibility** for consistent datasets
- **Locale support** via export profiles (e.g., English, Spanish)
- **Randomized response timing** and conversation bursts
- **Media message probability control**



## Installation

The generator is part of the WhatsApp Chat Analyzer project.

If you haven’t already:

```bash
git clone https://github.com/Jaboaro/whatsapp-chat-analyzer.git
cd whatsapp-chat-analyzer
pip install -r requirements.txt
```



## Usage

### CLI

Run the generator from the command line:

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

### Parameters

| Option                   | Description                                |
| ------------------------ | ------------------------------------------ |
| `--profile`              | Export profile / locale (e.g., `en`, `es`) |
| `--users`                | List of participant names                  |
| `--start-date`           | Chat start date (YYYY-MM-DD)               |
| `--days`                 | Duration of the chat in days               |
| `--avg-messages-per-day` | Average message volume per day             |
| `--seed`                 | Optional seed for reproducible output      |
| `--output`               | Output file path for the generated `.txt`  |



##  Export Profiles

Export profiles determine the formatting of the generated `.txt` file:

-   **English**: uses US-style timestamps and placeholders
    
-   **Spanish**: uses EU-style timestamps and Spanish placeholders
    

Profiles are defined in `profiles.py`.



##  How It Works

The generator:

1.  Determines message count per day using a probabilistic distribution.
    
2.  Picks random timestamps within active hours.
    
3.  Assigns senders with simple behavioral heuristics.
    
4.  Chooses between text and media messages.
    
5.  Formats each message according to the selected `ExportProfile`.
    
6.  Outputs a `.txt` file compatible with WhatsApp exports.
    



##  Integration with the Analyzer

The main app uses the generator for:

-   Demo mode on Streamlit Cloud
    
-   Generating sample chats via UI button
    
-   Producing reproducible test data
    

In demo mode, the generated chat is kept in memory and passed directly into the parser.



##  Tuning

You can extend the generator by:

-   Adding new locales (profiles)
    
-   Modifying behavioral patterns
    
-   Customizing active hours per user
    
-   Adding more message snippet variations
    
-   Adding new media categories