# Sentinel-Plug-in
Agent middleware
# Prompt Security Framework Simulation

This repository contains a Python simulation of a multi-layered security framework for Large Language Model (LLM) agents. It is designed to demonstrate a defense-in-depth approach against prompt injection, malicious queries, and other security threats.

This project was created for the "LLM Security Kaggle Challenge" to showcase a conceptual architecture combining synchronous and asynchronous security checks.

## Architecture Overview

The framework consists of two main components:

1.  **Sentinel (Synchronous Gatekeeper)**: The first line of defense. It performs immediate, low-latency checks on incoming prompts before they reach the LLM.
    *   **Source Verification**: Checks if the request originates from a trusted source.
    *   **Keyword-Based Injection Detection**: Blocks prompts containing obvious injection signatures (e.g., "ignore previous instructions").

2.  **Aegis (Asynchronous Engine)**: A decoupled monitoring and response system. It runs deeper, more complex analysis in the background without blocking the main execution path unless a severe threat is detected.
    *   **Metric Extraction**: Calculates scores for heuristics like the `pliny_score` (detecting structural overrides) and `rogue_glyphs` (obfuscation).
    *   **Ensemble Voting**: Aggregates metrics to produce a final security `Verdict` (`clear`, `soft`, `hard`, `tripwire`).
    *   **Graduated Response**: Takes action based on the verdict, from trimming output (`soft`) to isolating the session (`hard`) or killing it entirely (`tripwire`).

!Architecture Diagram 
*Note: You would create and link to a diagram explaining the data flow.*

## How to Run the Simulation

### Prerequisites

*   Python 3.8+

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AdamBoxy/Sentinel-Plug-in.git
    cd Sentinel-Plug-in
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    *(While this project has no external dependencies, this is standard practice.)*
    ```bash
    pip install -r requirements.txt
    ```

### Running the Scenarios

Execute the main simulation script from the root directory:

```bash
python run_simulation.py
```

This will run three pre-defined scenarios:
1.  **Safe Input**: A benign prompt that should pass all checks.
2.  **Injected Input**: A malicious prompt designed to trigger the Aegis engine's `tripwire`.
3.  **Untrusted Source**: A prompt from an untrusted node, which is blocked immediately by Sentinel.

## For Kaggle Participants

This framework is designed to be extensible. You can contribute by:
*   **Adding New Metrics**: Create a new function and add it to the `extract_metrics` flow in `src/security.py`.
*   **Improving Heuristics**: Refine the `pliny_score` or `detect_prompt_injection` functions.
*   **Integrating a Real LLM**: Replace the `UniversalModelAgent` in `src/agents.py` with an actual client for a service like Google's Gemini or OpenAI's GPT.
