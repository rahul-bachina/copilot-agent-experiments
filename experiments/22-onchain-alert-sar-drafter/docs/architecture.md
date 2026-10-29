# Architecture

Experiment 22. Catalogue UK07. Autonomy A1.

The analyst supplies one synthetic case and an as-of date. Either Copilot Studio harness calls `investigate()`. The Python core builds the timeline from synthetic tokens, calls Experiment 10 when a transfer is attached, Experiment 16 when a KYC file is attached, and Experiment 08 for the analyst note. Experiment 04 is cited for the registration-page pin. The draft comes back with `mlro_decision` null and `customer_facing.text` null.

The nominated officer decides whether section 330 or section 331 is met, whether to file, and whether to request a defence. Those steps are not tools. A stale source, a stale alert, or a future-dated event stays flagged until that officer relies on it. A supplied label is not a determination. Nothing is written for the customer.

```mermaid
flowchart TD
    A["1. Analyst supplies a synthetic case and the as-of date"] --> B["2. Either harness calls investigate()"]
    B --> C["3. Timeline, then Experiments 10, 16, and 08 where the case has that input"]
    C --> D["4. Internal note and SAR narrative. Decision is null. Customer text is null"]
    D --> E["5. Human approval: the nominated officer decides the section 330 or 331 test"]
    E --> F["6. Human approval: file or not file, and whether to request a defence"]
    F --> G["7. Human approval: rely on a stale or future fact, or on a marker"]
    style E fill:#fff3cd,stroke:#997404
    style F fill:#fff3cd,stroke:#997404
    style G fill:#fff3cd,stroke:#997404
```

The rendered picture is [architecture_diagram.png](architecture_diagram.png), produced by [generate_diagram.py](generate_diagram.py). Matplotlib is used only for that script. It is not a runtime dependency.

What is not a tool, even after the officer has decided: filing with the NCA, requesting a defence, drafting or sending customer text, freezing or moving a cryptoasset, assigning a glossary code, and querying a chain.
