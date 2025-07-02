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
│   ├── templates/
│   │   └── synapse/
│   │       └── plasticity_cycle_result.html
│   └── ...
├── db.sqlite3                 # Default database
├── manage.py                  # Django management script
├── .gitignore                 # Git exclusions
└── README.md                  # This file
```

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
          └────┬────────────┘
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
 │ AMPA Trafficking Parameters  │
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
