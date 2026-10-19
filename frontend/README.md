# ⚛️ OPE Lab — Frontend (React 19 + Vite 8)

The modern, ultra-high-fidelity web interface for **OPE Lab (Off-Policy Evaluation Laboratory)**. Built for the Perceptron Hackathon 2026 (Problem 3: *"Did the Policy Actually Work, or Did It Just Look Like It Did?"*).

---

## ✨ Features & User Experience

- **🌈 FlutedGlass Spectral Hero Banner (`src/ui/FlutedGlass.tsx`):**
  A dynamic, drifting rainbow-ribbed glass refraction overlay that delivers a futuristic, high-aesthetic presentation.
- **📜 Two Worlds Interactive Story (`src/pages/Story.tsx`):**
  Interactive causal DAG and step-by-step walkthrough of selection bias, unobserved confounding, and Simpson's Paradox.
- **🎛️ Interactive Simulation Lab (`src/pages/Home.tsx`):**
  Real-time client-side Monte Carlo contextual bandit generation ($N \in [500, 20\,000]$) with responsive sliders for Confounding ($c \in [0, 1]$), Overlap ($\alpha \in [0.05, 1]$), and Noise ($\sigma \in [0, 1]$).
- **📊 6 Estimators Deep-Dive (`src/pages/Estimators.tsx`):**
  Detailed mathematical formulas, asymptotic properties, and trade-off matrices for Naive Observational, Replay, Direct Method (DM), Inverse Propensity Weighting (IPW), Self-Normalized IPW (SNIPW), and Doubly Robust (DR).
- **💥 Failure Studies & Decision Map (`src/pages/Studies.tsx`):**
  Real-time bias and RMSE sweeps demonstrating when estimators fail and displaying the 3×3 Decision Map grid with the strict causal honesty rule.
- **📁 Real-World Benchmark (`src/pages/RealData.tsx`):**
  Visualizing empirical validation results on the Open Bandit Dataset (ZOZOTOWN 12M clicks, 80 items).

---

## 🛠️ Tech Stack & Architecture

- **Framework:** [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Bundler:** [Vite 8](https://vitejs.dev/) (lightning-fast HMR and optimized production bundling)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **Icons:** [Lucide React](https://lucide.dev/)
- **Causal Simulator:** Client-side TypeScript port (`src/ope/simulate.ts`) implementing the exact causal structural equation:
  $$R_i = 0.5 + 0.3 X_i + A_i(0.2 + 0.2 X_i + 0.5 U_i) + 0.4 U_i + \sigma \epsilon_i$$
  with interventional target ground truth $V^*(\pi_e) = 0.679788$.

---

## 🚀 Quickstart & Development

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
Runs the app in dev mode at `http://localhost:5173`.

### 3. Production Build & Preview
```bash
# Build production bundle
npm run build

# Preview production build locally
npm run preview -- --port 8443
```

---

## 📂 Project Structure

```
frontend/
├── public/                 # Static assets and icons
├── src/
│   ├── app/                # Shell, layout, navigation & top bar
│   │   ├── App.tsx
│   │   ├── TopBar.tsx
│   │   └── PageHeader.tsx
│   ├── ope/                # Causal simulation & statistical estimators
│   │   ├── simulate.ts     # Contextual bandit generator with confounding
│   │   └── estimators.ts   # IPW, SNIPW, DR, DM, Replay, Naive
│   ├── pages/              # Primary route views
│   │   ├── Home.tsx        # Interactive simulation laboratory
│   │   ├── Story.tsx       # Causal story & selection bias intuition
│   │   ├── Estimators.tsx  # Deep dive into statistical formulations
│   │   ├── Studies.tsx     # Confounding sweeps & Decision Map
│   │   ├── RealData.tsx    # Open Bandit Dataset ZOZOTOWN benchmark
│   │   └── Team.tsx        # Perceptron Hackathon team information
│   ├── ui/                 # Reusable UI primitives & glass styling
│   │   ├── FlutedGlass.tsx # Rainbow fluted glass spectral effect
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Slider.tsx
│   ├── styles/             # Global Tailwind and font styles
│   └── main.tsx            # React application entrypoint
├── package.json
├── tsconfig.json
└── vite.config.ts
```
