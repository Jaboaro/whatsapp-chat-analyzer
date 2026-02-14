# WhatsApp Chat Analyzer

A data-driven WhatsApp chat analysis tool built with **Python + Streamlit**, designed to extract insights from exported conversations — message distribution, participation dynamics, media usage, and conversational structure.


![App screenshot](media/images/image1.png)


## Quick Try

You can try the app locally in a few steps. **All data remains on your PC** — nothing is uploaded.

```bash
git clone https://github.com/Jaboaro/whatsapp-chat-analyzer.git
cd whatsapp-chat-analyzer
pip install -r requirements.txt
streamlit run app.py
```

Use the **“Try sample chat”** button to explore the app without uploading your own chat.



## What It Does

-   Parses WhatsApp exported `.txt` files
    
-   Supports **English** and **Spanish** formats
    
-   Handles **multi-line messages**, **media placeholders**, and **quoted replies**
    
-   Generates structured datasets for analysis
    
-   Visualizes:
    
    -   Messages over time
        
    -   Messages per participant
        
    -   Activity by hour/day
        
    -   Media usage statistics
        



## Core Features

### Message Analytics

-   Messages per user
    
-   Daily & weekly activity trends
    
-   Hour-of-day distribution
    
-   Conversation bursts & gaps
    

### Media Insights

-   Media type distribution
    
-   Media per participant
    
-   Text vs media ratio
    

### Testing & Simulation

-   Deterministic synthetic chat generation
    
-   Seed-based reproducibility
    
-   Heterogeneous user behavior modeling
    

---

## Architecture Highlights

-   **Clean layering:** Parsing → Structured Data → Analysis → Visualization → UI
    
-   **Thin UI philosophy:** Streamlit handles interface only
    
-   **Locale-aware parsing:** Export profiles (EN/ES) for date and media formats
    
-   **Auxiliary tool:** Synthetic chat generator for testing or demo data (`tools/chat_generator`)
    

---

## Installation

```bash
git clone <repo-url>
cd whatsapp-chat-analyzer
pip install -r requirements.txt
streamlit run app.py
```

---

## Demo

![Video demo](media/videos/video1.gif)


---

##  Why This Project Matters

-   Demonstrates **modular Python architecture**
    
-   Combines **data parsing, analysis, and visualization**
    
-   Supports **deterministic simulation** for testing
    



