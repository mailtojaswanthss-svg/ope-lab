# 🐍 OPE Lab — Backend & Statistical Engine

The Python computational backend and interactive Streamlit application for **OPE Lab (Off-Policy Evaluation Laboratory)**.

Built for the Perceptron Hackathon 2026 (Problem 3: *"Did the Policy Actually Work, or Did It Just Look Like It Did?"*).

---

## 🏛️ Core Modules & Statistical Architecture

The backend is built around a rigorous causal simulation and statistical evaluation pipeline:

```
backend/
├── .streamlit/
│   └── config.toml         # Streamlit theme and server configuration
├── ope/                    # Core statistical and causal engine
│   ├── simulator.py        # Contextual bandit DGP with hidden confounding U
│   ├── estimators.py       # 6 estimators: Naive, Replay, DM, IPW, SNIPW, DR
│   ├── diagnostics.py      # Kish's Effective Sample Size (ESS) & weight health
│   ├── bootstrap.py        # Vectorized percentile bootstrap 95% CIs
│   ├── sensitivity.py      # Marginal Sensitivity Model (MSM) odds ratio bounds & Λ*
│   ├── realdata.py         # Open Bandit Dataset (ZOZOTOWN) benchmark loader
│   ├── analysis.py         # Multi-seed Monte Carlo sweep generators
│   └── logging_config.py   # Structured logging configuration
├── ui/                     # UI components, theme, and visualizations
│   ├── theme.py            # Dark/light theme injection & glassmorphic styling
│   ├── components.py       # Metric cards, status chips, and inspector panels
│   └── charts.py           # Colorblind-safe Plotly visualizations with distinct markers
├── tests/                  # 36 unit and smoke tests (100% pass rate)
│   ├── test_simulator.py
│   ├── test_estimators.py
│   ├── test_diagnostics.py
│   ├── test_bootstrap.py
│   ├── test_sensitivity.py
│   ├── test_realdata.py
│   ├── test_analysis.py
│   └── test_app_smoke.py
├── scripts/
│   ├── make_abstract_facts.py      # Reproducible facts pipeline for research paper
│   └── compute_step2_benchmark.py  # Monte Carlo verification script
├── app.py                  # Main Streamlit web application entrypoint
└── requirements.txt        # Frozen Python dependencies
```

---

## 📐 Causal Ground Truth

The simulator implements a known interventional Data Generating Process (DGP):
- **User Covariate:** $X_i \sim \mathcal{N}(0, 1)$
- **Unobserved Confounder:** $U_i \sim \mathcal{N}(0, 1)$ (hidden from all estimators)
- **Logging Policy:** $\pi_0(A=1 \mid X_i, U_i) = \sigma(L \cdot X_i + 3c \cdot U_i)$ where $L = 0.5 + 5(1 - \text{overlap})$
- **Structural Reward Equation:**
  $$R_i = 0.5 + 0.3 X_i + A_i(0.2 + 0.2 X_i + 0.5 U_i) + 0.4 U_i + \sigma_{\text{noise}} \epsilon_i$$
- **Target Policy Ground Truth:**
  $$V^*(\pi_e) = \mathbb{E}[R \mid \text{do}(A = \mathbb{I}(X > 0))] = 0.679788$$

---

## ⚡ Quickstart & Installation

### 1. Create and Activate Virtual Environment
```bash
# From repository root or backend folder:
py -3.11 -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing & Code Quality

```bash
# Run the complete test suite (36 tests)
pytest -q

# Run static analysis and linting
ruff check .

# Generate abstract facts and empirical verification tables
python scripts/make_abstract_facts.py
```
