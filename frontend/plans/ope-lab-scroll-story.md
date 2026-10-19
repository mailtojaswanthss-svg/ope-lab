# OPE Lab — "Two Worlds" Scroll Story: Implementation Plan

## Goal
Build a single-page, 11-section scroll-story site for **OPE Lab** (Off-Policy Evaluation Lab) in the existing React 19 + Vite 8 + Tailwind v4 app, built on the Astra design system (`@figma/astraui`). The story's main idea is **Two Worlds**: a solid, bright path for *reality* (what the logging policy did) and a faded, dotted path for the *counterfactual* (what the new policy would have done). Section 6 is a **live in-browser lab** that runs the six estimators from the attached `app.py`/`README.md`, rewritten in TypeScript.

Confirmed decisions:
- Astra tokens and components, plus a small OPE extension layer (brand colors, estimator colors, display type).
- Astra canvas (`bg-brand-tertiary` and `surface-bg` cards) for reading sections; full-bleed **navy story stages** for the Two Worlds moments (Hero, Two Worlds, Lab chart stage).
- Astra `SidebarNavigation` rail repurposed as an 11-item section jumper.
- Fonts: **DM Sans** for body/UI, **Fraunces** for display headlines (Google Fonts).
- Real Data and Team sections use honest placeholders. No fabricated metrics.

## Section outline (in order)
| # | id | Rail icon (lucide, verified) | Surface | Content |
|---|---|---|---|---|
| 1 | `hero` | `Sparkles` | navy stage | Eyebrow badge "Perceptron Hackathon 2026 · Problem 3". Fraunces headline "Did the policy actually work — or did it just look like it did?" Subhead. Animated Two Worlds SVG: solid teal reality path, dotted faded counterfactual path that splits from it. Primary `Button` "Open the Lab" (scrolls to #lab), neutral `Button` "Read the story". |
| 2 | `dilemma` | `Ticket` | canvas + cards | The Coupon Dilemma: $150 vs $80 stat cards. Orange insight callout: "Was it the coupon, or were they already big spenders?" |
| 3 | `two-worlds` | `Split` | navy stage | The idea itself: logged world (π₀, solid) vs target world (πₑ, dotted). We only ever see one world, and OPE reconstructs the other. 3-step strip: Log → Reweight/Model → Estimate. |
| 4 | `ground-truth` | `Sigma` | canvas + cards | Data-generating process (X, hidden U, logging policy σ(L·X + 3c·U), reward, target policy 1[X>0]). V* ≈ 0.6798, highlighted in orange. Note: "Estimators only see X — never U." |
| 5 | `estimators` | `Scale` | canvas + cards | 6 cards, each with its color, marker shape, a one-line intuition, a compact formula, and a "fails when…" line. |
| 6 | `lab` | `FlaskConical` | canvas controls + navy chart stage | Live simulation (spec below). |
| 7 | `failure` | `TrendingDown` | canvas + card | Failure Study: absolute error vs confounding c ∈ [0, 1] (11 steps × 5 seeds), one line per estimator. Uses the Lab's current overlap/noise. |
| 8 | `decision-map` | `Grid3x3` | canvas + card | 3×3 Decision Map (20 reps/cell, n=2000). Each cell shows the winner's color, marker, name, and RMSE, or "Tie". |
| 9 | `sensitivity` | `ShieldCheck` | canvas + card | Marginal sensitivity bounds band over Λ ∈ [1, 3] (40 pts), V* line, Λ* banner. |
| 10 | `real-data` | `Database` | canvas + card | Open Bandit Dataset (ZOZOTOWN) placeholder: "Not loaded in this browser demo." Steps to run with `obp` locally. `Badge variant="secondary" label="No data loaded"`. Zero numbers. |
| 11 | `team` | `Users` | canvas + cards | Placeholder member cards ("Team member — name & role to be added"), Avatar initials, and a hackathon credit line. Clearly marked as a placeholder. |

The Lab stays at position 6 so the explanation (1–5) comes before the hands-on part, and the studies (7–9) build on the Lab's settings.

## Dependencies (edit `package.json` directly, then `pnpm install`)
The top-level `node_modules` exposes only `@figma/*`, React, and tooling. Add direct deps, pinned to versions the kit already resolves:
- `lucide-react`: `0.487.0` (icons; the kit requires lucide)
- `@radix-ui/react-slider`: `1.2.3` (Astra has no slider; this is the base for a local `RangeSlider`)

No chart library. All charts are hand-built SVG, which gives exact control over dotted counterfactual paths and per-estimator marker shapes, and no extra dependency.

## Files
```
src/index.css                 Google Fonts @import, astraui styles import, tailwind, OPE @theme extension, base font wiring, reduced-motion
src/main.tsx                  unchanged
src/App.tsx                   ThemeProvider + shell (rail + main) + section list
src/story/sections.ts         SECTIONS: { id, label, icon }[] (single source for rail + mobile bar)
src/story/useActiveSection.ts IntersectionObserver → active id; scrollToSection(id)
src/story/Reveal.tsx          fade/translate-in on enter (IntersectionObserver + CSS; respects reduced motion)
src/story/SectionRail.tsx     SidebarNavigation + SidebarButton×11 + Tooltip labels + theme toggle footer
src/story/MobileProgress.tsx  <md sticky bar: current section label + progress
src/story/Stage.tsx           navy full-bleed stage wrapper; Card.tsx surface-bg card wrapper
src/sections/Hero.tsx … Team.tsx   one file per section (11 files)
src/viz/TwoWorldsPath.tsx     reusable solid-vs-dotted path illustration
src/viz/Marker.tsx            estimator marker shapes (SVG)
src/viz/DotWhisker.tsx        Lab results chart
src/viz/FailureChart.tsx, DecisionGrid.tsx, SensitivityBand.tsx
src/ope/rng.ts                mulberry32 + Box–Muller normal
src/ope/simulate.ts           DGP
src/ope/estimators.ts         propensity/ridge fits + 6 estimators + ESS/max-w
src/ope/bootstrap.ts, study.ts (failure + decision map), sensitivity.ts
src/ope/meta.ts               ESTIMATORS: { key, name, colorClass(fill/stroke/text/bg), marker, blurb, formula, failsWhen }
src/ope/worker.ts             Web Worker running bootstrap/failure/decision-map/sensitivity
src/ope/useOpe.ts             hook: debounced params → sync point estimates + worker results
src/ui/RangeSlider.tsx        Radix slider styled with Astra tokens (label, value readout, aria)
```

## Design system usage
- Setup per `setup.md`: `@import '@figma/astraui/styles.css'` in `index.css`, `<ThemeProvider>` at the root, no `@source` for astraui.
- Components: `SidebarNavigation`, `SidebarButton`, `Tooltip`, `Button` (primary/neutral/subtle, `iconStart`), `Badge`, `RadioGroup` (presets), `SelectField` (sample size 1000/2000/5000/10000/20000; bootstrap B 50/100/200), `Tabs` (Lab: "Estimates" / "Weight health"), `Avatar` (Team, initials; confirm props in `avatar.d.ts`), `SwitchField` (Lab: "Show counterfactual path"), `IconButton` (re-roll seed, `Shuffle`).
- No raw `<button>/<input>/<select>/<a>/<h1–h6>`. Headings use `<p>`/`<div>` with type classes plus `role="heading" aria-level`, matching the kit's pattern. CSV download uses a `Button` that creates a Blob URL programmatically.
- Spacing/radius: Astra tokens only (`gap-xl`, `p-2xl`, `rounded-corner-lg`, …). Cards are `bg-surface-bg rounded-corner-lg p-xl`, with no borders between regions.
- Text on the canvas uses `text-text-primary/secondary`. Text on navy stages uses extension tokens (below).
- Rail repurpose (approved deviation from the "Home/Film/Book/Folder" standard config): 11 section buttons with `active` driven by scroll; footer has a theme toggle `SidebarButton` (`Moon`/`Sun` via `useTheme`). The rail is `fixed` on the left at ≥md, and `main` gets left padding equal to the rail width using Astra's spacing scale. Below md the rail is hidden and `MobileProgress` shows instead.

## Extension layer (`src/index.css`)
Order: Google Fonts `@import url(...)` (Fraunces opsz 9–144 wght 400/600, DM Sans 400/500/600) → `@import '@figma/astraui/styles.css'` → `@import 'tailwindcss'` → `@theme` block → base rules.

`@theme` tokens (hex only lives here):
- Story palette: `--color-ope-navy #10233f`, `--color-ope-navy-deep` (darker navy for stage gradient), `--color-ope-teal #0f766e`, `--color-ope-teal-bright #2dd4bf`, `--color-ope-violet #3b2a7a`, `--color-ope-insight #f97316`, `--color-ope-on-stage` (near-white), `--color-ope-on-stage-muted` (white @ ~65%), `--color-ope-counterfactual` (white @ ~35%, for dotted paths).
- Estimators: `--color-est-naive` red `#ef4444`, `--color-est-replay` amber `#f59e0b`, `--color-est-dm` blue `#3b82f6`, `--color-est-ipw` purple `#a855f7`, `--color-est-snipw` teal `#14b8a6`, `--color-est-dr` green `#22c55e`. These generate `fill-est-*`, `stroke-est-*`, `text-est-*`, `bg-est-*`.
- Fonts: `--font-sans: "DM Sans", system-ui, sans-serif` (user-requested override of Instrument Sans) and `--font-story: "Fraunces", Georgia, serif`.
- Display type (Astra tops out at 24px): `--text-display-xl` (clamp ~44→88px, lh 1.05, Fraunces 600), `--text-display-lg` (clamp ~32→56px), `--text-stat` (clamp ~40→72px, tabular numerals). Everything else uses Astra's composite classes (`text-title`, `text-heading`, `text-label`, `text-label-sm`, `text-video-title`).
- Base: `body { font-family: var(--font-sans) }`, and `@media (prefers-reduced-motion: reduce)` disables reveal/path animations.
- If an Astra utility class isn't in the precompiled CSS (found during build), map it in a small `@theme inline` block to the Astra CSS variable instead of hardcoding values.

Estimator marker shapes (`Marker.tsx`, reused everywhere): Naive ✕ cross, Replay ▲ triangle, DM ■ square, IPW ◆ diamond, SNIPW ⬟ pentagon, DR ● circle. Color is never the only signal: every marker also has a text label.

## Simulation spec (`src/ope/*`)
All ported from README/app.py. The `ope` Python package was not attached, so internals follow the README definitions below. The code comments and Lab footnote will say the results match the Python app statistically, not bit for bit (different RNG).
- RNG: `mulberry32(seed)`; normals via Box–Muller. Default seed 42; `IconButton` re-rolls (1000–99999).
- DGP: X, U ~ N(0,1); L = 0.5 + 5(1−overlap); p₀ = σ(L·X + 3c·U); A ~ Bern(p₀); R = 0.5 + 0.3X + A(0.2+0.2X) + 0.4U + noise·ε. πₑ(X) = 1[X>0]. V* = 0.6 + 0.2/√(2π) ≈ 0.679788 (constant).
- Propensity: logistic regression of A on [1, X] by Newton/IRLS (≤25 iters, tol 1e-8), p̂ clipped to [0.01, 0.99]. Weight w = 1[A=πₑ(X)] / p̂(A|X).
- Outcome model: ridge (α=1.0, intercept unpenalized) of R on [1, X, A, A·X], solved 4×4 in closed form. q̂(x,a).
- Estimators: Naive = mean(R | A=1). Replay = mean(R | A=πₑ(X)). DM = mean q̂(X, πₑ(X)). IPW = mean(w·R). SNIPW = Σ(wR)/Σw, clamped to [min R, max R]. DR = mean(q̂(X,πₑ) + w(R − q̂(X,A))).
- Weight health: ESS = (Σw)²/Σw² (also as % of N), max w. Low-ESS warning `Badge variant="warning"` when ESS < 10% N.
- Bootstrap: percentile 95% CI + SE, B from control (default 100); if N > 10,000 then B = min(B, 50). Resample rows and refit both models each replicate.
- Failure study: c = 0, 0.1, …, 1.0 × 5 seeds (base seed + k), n = min(N, 5000), current overlap/noise → mean |error| per estimator.
- Decision map: confounding rows {0.0, 0.4, 0.8} × overlap columns {0.2, 0.5, 0.9}, 20 reps × n=2000, current noise. Winner = lowest RMSE excluding Naive. **Tie** if the runner-up's paired squared-error difference vs the winner has mean < 1.96·SE.
- Sensitivity (MSM, on SNIPW over matched rows): for Λ in linspace(1, 3, 40), each matched row's weight lies in [w/Λ, w·Λ]. Upper bound = max over sorted-reward thresholds of the self-normalized mean with w·Λ above the threshold and w/Λ below. The lower bound is the mirror. Λ* = smallest Λ where lower ≤ V* ≤ upper, using prefix sums (O(n log n) per Λ). Banner: Λ* ≤ 1.3 → success tone, otherwise warning tone. No coverage → "Λ* > 3.0", danger tone.
- Execution: point estimates and weight health run synchronously on the main thread (debounced 150 ms after control changes; n ≤ 20k is fast). Bootstrap, failure study, decision map, and sensitivity run in `worker.ts` (Vite `new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' })`). Each request carries a request id, and stale responses are dropped. While a result is pending, the panel shows the previous result dimmed plus a "Computing…" `Badge`. Worker errors show an inline message in that card and are logged to the console; the rest of the page keeps working. The decision map runs once on first view (IntersectionObserver) and again only when noise or seed changes.

## Lab (section 6) UX
- Left column (card): presets as `RadioGroup` — Easy case (c 0.0, overlap 0.9), Low overlap (c 0.0, overlap 0.1), Hidden confounder (c 0.8, overlap 0.8), plus a "Custom" state shown automatically when the sliders move. Sliders: Confounding c 0–1 step 0.05; Overlap 0.05–1 step 0.05; Noise 0–1 step 0.05. Selects: sample size, bootstrap B. Seed readout + re-roll. Defaults: c 0.5, overlap 0.7, N 5000, noise 0.3, B 100, seed 42.
- Right (navy stage): `DotWhisker` with the V* line drawn in orange as a solid "reality" reference. Each estimator gets a marker and a 95% CI whisker. The lowest-|error| non-Naive estimator gets a soft halo. A `SwitchField` toggles a dotted "naive world" ghost line at the Naive estimate (Two Worlds motif).
- Below: 6 metric tiles (value, signed error vs V*, colored by estimator; error text uses `text-success`/`text-warning`/`text-danger` at thresholds |err| < 0.02 / < 0.08 / ≥ 0.08). `Tabs`: "Estimates" (tiles) / "Weight health" (ESS, max w, propensity range). `Button variant="neutral" iconStart={<Download/>}` "Download results (CSV)" with columns estimator, estimate, error, ci_low, ci_high, se, plus a params header comment.
- An orange insight line updates live, e.g. "Naive overshoots by +0.18. DR lands within 0.01 of the truth."

## Motion & responsiveness
- `Reveal` fades and lifts content in on enter. The Two Worlds paths draw in with `stroke-dashoffset`. All motion is off under reduced motion.
- Breakpoints: single column <md; Lab is two-column at ≥lg; estimator cards are 1/2/3 columns. SVG charts use `viewBox` with width 100%.
- Rail: scroll-spy (IntersectionObserver with rootMargin centered on the viewport). Clicking calls `scrollIntoView({ behavior: smooth|auto per reduced motion })` and moves focus to the section heading for keyboard users. `aria-label` = section label, `aria-current="true"` when active.

## Accessibility
- Every section is a `<section aria-labelledby>`. Chart SVGs have `role="img"` + `<title>`/`<desc>` summarizing the values, plus a visually hidden table of estimates for screen readers.
- Contrast on navy: body text uses `ope-on-stage`. The dotted counterfactual is decorative, so labels are always solid.

## Verification
1. `pnpm install` after the package.json edits.
2. Numerical sanity (temporary script under `/tmp`, run via `node --experimental-strip-types` or vite-node equivalent; not committed): with seed 42, N 5000, noise 0.3, check
   - Easy case: DM, IPW, SNIPW, DR all within ~0.03 of 0.6798.
   - Hidden confounder: Naive ≈ 0.8–0.9 (error ≳ +0.12, matching the README's ~0.86), DR closer to V* than Naive.
   - Low overlap: ESS% drops sharply and the max weight grows (≥ ~10× the Easy case).
   - Sensitivity returns a finite Λ* for the confounder preset.
3. `pnpm build` (the production build the DS skill requires) must pass, with type errors fixed.
4. Scan the produced files: no hex outside `index.css`, no `px`/`rem` literals in classNames/inline styles, no raw interactive/heading HTML elements, nothing changed under `node_modules`.
5. The existing dev server preview should show all 11 sections rendering, rail jumping and highlighting correctly, presets changing results, CSV downloading, and the worker panels populating.

## Out of scope
Real OBP loading in the browser, backend, routing, persisted settings, i18n.
