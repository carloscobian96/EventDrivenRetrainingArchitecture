# Event Driven Retraining Architecture

A modular, event-driven simulation of synaptic plasticity and retraining, built with Django.

---

## 🚀 Overview
This project models the **biochemical and computational processes of synaptic plasticity** in a brain-inspired architecture. The core logic and domain models are in the `synapse` app, which orchestrates a cascade of plasticity events on a per-synapse basis.

- **Domain:** Computational neuroscience, synaptic plasticity, event-driven modeling
- **Stack:** Python 3.13+, Django, SQLite (default), virtual environment (`venv`)

---

## 🧠 Key Features
- **Rich Synapse Model:**
  - Each `Synapse` aggregates all relevant biochemical components (cleft, membrane, receptors, cascades, etc.) as Django model relations.
  - Designed to support a full plasticity cycle: spike processing, dopamine modulation, STDP, AMPA trafficking, homeostatic scaling, consolidation, and more (extend as needed).
- **Event-Driven Cascade (Extensible):**
  - The architecture is ready for you to implement a plasticity cascade by adding methods to the `Synapse` model.
- **Web Interface:**
  - View synapse details in a clean HTML template (`plasticity_cycle_result.html`).
  - All model parameters are stored on the model itself—no step-specific arguments required.
- **Extensible:**
  - Add new biochemical components or plasticity steps by extending the `Synapse` model and its methods.

---

## 🗂️ Project Structure


```
├── event_driven_retraining/   # Django project config
├── synapse/                   # All domain logic, models, and views
│   ├── models.py              # Biochemical and plasticity models
│   ├── views.py               # Triggers and result rendering
│   ├── services/
│   │   └── simulator.py       # SynapseSimulator: full plasticity tick logic
│   ├── management/
│   │   └── commands/
│   │       └── run_sim.py     # Django command: run simulation ticks for a synapse
│   ├── templates/
│   │   └── synapse/
│   │       ├── plasticity_diagram.html
│   │       └── plasticity_report.html
│   └── ...
├── db.sqlite3                 # Default database
├── manage.py                  # Django management script
├── manage.ps1                 # PowerShell: run Django commands with venv automatically
├── .gitignore                 # Git exclusions
└── README.md                  # This file
```
---

## 🛠️ Key Scripts & Services

- **manage.ps1**
  - PowerShell script for running Django management commands using your project's virtual environment automatically.
  - Usage: `./manage.ps1 <command> [args]`
  - Example: `./manage.ps1 run_sim 1 --ticks 10`
  - No need to activate your venv or adjust execution policy every time—this script handles it for you.

- **synapse/services/simulator.py**
  - Contains the `SynapseSimulator` class, which encapsulates the full synaptic plasticity tick logic.
  - Each call to `tick()` simulates a full biochemical and computational update for a single synapse, including transmitter release, NMDA/AMPA logic, dopamine modulation, STDP, trafficking, tagging, and homeostasis.

- **synapse/management/commands/run_sim.py**
  - Custom Django management command to run simulation ticks for a given synapse.
  - Usage: `python manage.py run_sim <synapse_id> --ticks <n>` or with PowerShell: `./manage.ps1 run_sim <synapse_id> --ticks <n>`
  - Prints the synaptic weight after each tick for monitoring plasticity changes.

---

---

## ⚡ Quickstart

1. **Clone and enter the project:**
   ```powershell
   git clone <your-repo-url>
   cd EventDrivenRetrainingArchitecture
   ```
2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. **Install Django:**
   ```powershell
   pip install django
   ```
4. **Run migrations:**
   ```powershell
   & .\.venv\Scripts\python.exe manage.py migrate
   ```
5. **Start the development server:**
   ```powershell
   & .\.venv\Scripts\python.exe manage.py runserver
   ```
6. **Open your browser:**
   [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🧩 How It Works
- The main entry point is the `plasticity_cycle` view in `synapse/views.py`.
- It selects a `Synapse` instance and renders its details in `plasticity_cycle_result.html`.
- All biochemical components are modeled as Django relations for easy extension and inspection.
- You can implement your own plasticity cascade by adding methods to the `Synapse` model and updating the view accordingly.

---

## 📝 Requirements
- Python 3.13+
- Django (install in your venv)

---

## 📚 Further Reading
- [Django documentation](https://docs.djangoproject.com/)
- [Synaptic plasticity (Wikipedia)](https://en.wikipedia.org/wiki/Synaptic_plasticity)

---

## 🧑‍💻 Author & License
- Created by you, for research and experimentation.
- MIT License (add a LICENSE file if you wish)

---

> “The brain is a world consisting of a number of unexplored continents and great stretches of unknown territory.” — Santiago Ramón y Cajal

---

## 🧬 Plasticity Cascade Steps
```
┌───────────────┐
│  SynapticCleft│ ──┐
└────┬──────────┘   │
     ▼              ▼
┌───────────────┐ ┌──────────────┐
│PostSyn Membrane│ │NMDA Receptor│
└────┬──────────┘ └────┬─────────┘
     ▼                 ▼
┌──────────────────────────┐
│       Ca²⁺ Influx        │ ← step 1
└────┬─────────────────────┘
     ▼
┌─────────────┐   ┌─────────────────┐
│DopamineCleft│ → │Dopamine Receptor│
└─────────────┘   └────┬────────────┘
                       ▼
              ┌─────────────────────┐
              │ Modulatory Cascade │ ← step 2
              └────┬────────────────┘
                   ▼
          ┌────────────────┐
          │ SpineHead Ca²⁺ │ ← sensitivity updated
          └────┬───────────┘
               ▼
      ┌─────────────────────┐
      │   STDP Parameters   │
      └────┬────────────────┘
           ▼
      ┌─────────────────────┐
      │   Synaptic Weight   │ ← step 3
      └────┬────────────────┘
           ▼
 ┌───────────────────────────────┐
 │ AMPA Trafficking Parameters   │
 └────┬──────────────────────────┘
      ▼
┌────────────┐    ┌────────────────┐
│Endosome AMPA│ ←→│  PSD AMPA Pool │ ← step 4
└────────────┘    └────────────────┘

         ↓ (global feedback)
┌─────────────────────────┐
│     Astrocyte Unit      │ ← step 5
└────┬────────────────────┘
     ▼
   scaling signal
     ▼
┌───────────────────────────┐
│ Consolidation Protein Pool│
└────┬──────────────────────┘
     ▼
┌──────────────────────────┐
│   Synaptic Tagging Logic │ ← step 6
└──────────────────────────┘
```


## 🧠 Event-Driven AI Retraining ⇄ Biology
```
┌────────────────────────────────────────────────────┐
│      Event-Driven AI Retraining ⇄ Biology         │
└────────────────────────────────────────────────────┘

[Event Signal]                               [Biological Signal]
┌───────────────┐                          ┌────────────────────────┐
│ New Input /   │── anomaly spike ─────▶  │ Pre & Post action      │
│ Error Signal  │                          │ potentials (spikes)    │
└───────────────┘                          └────────────────────────┘
                                                    │
                                                    ▼

[Watcher]                                            [Coincidence Detector]
┌───────────────────────┐ ◀─ "Which spike pair" ──▶ ┌────────────────────┐
│ Attention Gate        │     to focus on?           │ NMDA receptor      │
│ (selects event)       │     gating feedback        │ activation (Ca²⁺)  │
└───────────────────────┘                            └────────────────────┘
                                                         │
                                                         ▼

[Neuromodulatory Gate]                                   [Dopamine / Acetylcholine]
┌──────────────────────────┐ ◀─ "Reward / Salience?" ─▶ ┌─────────────────┐
│ Global Reward Signal     │     adjust plasticity       │ VTA / Basal     │
│ (modulates plasticity)   │                             │ forebrain       │
└──────────────────────────┘                             └─────────────────┘
                                                    │
                                                    ▼

[Weaver]                                                    [Calcium-Driven Update]
┌───────────────────────┐ ◀─ Δweight = f(Δt, neuromod) ─▶ ┌────────────────────┐
│ Local Update Logic    │     update magnitude & sign      │ STDP rule (LTP/LTD)│
│ (computes weight Δ)   │                                  │ via Ca²⁺ influx     │
└───────────────────────┘                                  └────────────────────┘
                                                    │
                                                    ▼

[Binder]                                   [Receptor Trafficking]
┌────────────────────────┐ ── Commit Δ to synapse ─▶ ┌──────────────────────────┐
│ Parameter Adjustment   │     new synaptic strength  │ AMPA receptor insertion/ │
│ (apply local Δ)        │◀──────────────────────────┤ removal (weight change)  │
└────────────────────────┘     baseline synchronization └──────────────────────────┘
                                                    │
                                                    ▼

[Homeostatic Control]                     [Glial & Astrocyte Support]
┌────────────────────────┐ ◀─ Keep network stable ─▶ ┌──────────────────────────┐
│ Global Activity Scaling│     adjust overall gains  │ Astrocyte Ca²⁺ waves     │
│ (synaptic scaling)     │                           │ & gliotransmission       │
└────────────────────────┘                           └──────────────────────────┘
                                                    │
                                                    ▼

[Memory Consolidation]                   [Systems-Level Stabilization]
┌────────────────────────┐ ◀─ Lock in useful Δ ─▶ ┌──────────────────────────┐
│ Store updated weights  │    gene expression &   │ Sleep-driven replay &    │
│ for future inference   │    protein synthesis   │ hippocampo-cortical loop │
└────────────────────────┘                        └──────────────────────────┘
                                                    │
                                                    ▼

[Adapted Behavior]                        [Modified Network Output]
┌──────────────────────────┐ ◀─ ongoing loop ─▶ ┌─────────────────────┐
│ Improved predictions /   │                   │ Enhanced circuit     │
│ decisions on next input  │                   │ efficacy & dynamics  │
└──────────────────────────┘                   └─────────────────────┘
```