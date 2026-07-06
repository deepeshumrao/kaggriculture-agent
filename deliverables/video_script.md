# Explainer Video — Script & Storyboard

> Deliverable #2. Target length: **3–4 minutes**. Screen recording + voiceover.
> Tools: OBS / Loom (free) + your terminal + the writeup notebook.

---

## Before you record (checklist)
- [ ] Terminal open in the project folder, font size bumped up.
- [ ] `python scripts/run_real.py --verbose` ready to run.
- [ ] `python -m pytest -q` ready (shows 66 passing).
- [ ] `deliverables/kaggriculture_submission.py` open in the editor.
- [ ] Quiet room, mic tested.

---

## Scene 1 — Hook (0:00–0:20)
**On screen:** title slide "Kaggriculture Agent" + the competition goal.
**Say:**
> "Meet my Kaggriculture agent — built for the Google × Kaggle Vibe Coding
> capstone. Kaggriculture is a two-player farming game: you drive a farmer around
> a field for 720 turns and try to out-earn your opponent. Here's how my agent
> plays it — and how I built it to run before I even had the real game's code."

## Scene 2 — The real game (0:20–0:50)
**On screen:** a simple diagram of the tile grid + farmer + the obs/action loop.
**Say:**
> "Each turn the agent sees the board — its farmer's position, every tile, its
> money, seeds, and shed — and returns exactly one action: move a step, or work
> the tile it's on. The full loop is: buy seeds, plant, water, pull weeds,
> harvest into the shed, and sell. Simple pieces, but 720 turns of them."

## Scene 3 — The build story: contract-first (0:50–1:35)
**On screen:** the `real/` folder — `protocol.py`, `local_env.py`, `brain.py`.
**Say:**
> "The interesting part: the real competition API wasn't public when I started.
> So I built contract-first. `protocol.py` pins down the exact observation and
> action shapes. `local_env.py` is a local simulator that reproduces those shapes
> — so I could develop and test the whole agent *without* the Kaggle package. An
> agent that works here plugs into the real environment unchanged."

## Scene 4 — The brain (1:35–2:10)
**On screen:** `brain.py`, highlight the priority list.
**Say:**
> "The decision policy is a fast, explainable rule-based farm manager. First it
> handles the market for free — restock seeds, sell the shed. Then it picks the
> nearest high-value tile in priority order: harvest-ready, then thirsty crops,
> then weeds, then empty ground to plant. Nearest, because every step costs one
> of my 720 turns. No LLM in the hot loop — just fast, deterministic decisions."

## Scene 5 — Live demo (2:10–2:55)
**On screen:** run `python scripts/run_real.py --verbose` — let day-by-day scroll.
**Say:**
> "Let's watch a full game in my local simulator. You can see money climb day by
> day as it plants, waters, harvests, and sells — playing all 720 turns cleanly
> against an idle opponent. One honest caveat: these local numbers use *assumed*
> game constants, so they're a sanity check, not a leaderboard score — the real
> environment supplies the real economics."

## Scene 6 — Reliability & the submission (2:55–3:30)
**On screen:** run `pytest -q` (66 passing), then show `kaggriculture_submission.py`.
**Say:**
> "Reliability is tested, not hoped for — 66 automated tests cover the game
> mechanics and the agent's every decision. And the whole agent ships as one
> self-contained file with a top-level `agent(obs)` — the thing you paste into
> Kaggle. A parity test guarantees that file behaves identically to the code I
> tested, so what I ship is exactly what I verified."

## Scene 7 — Close (3:30–3:50)
**On screen:** back to title + repo link.
**Say:**
> "That's my Kaggriculture agent: a contract-first, rule-driven farmer that was
> runnable before the real API existed and drops straight into it now. Built with
> the vibe-coding workflow. Thanks for watching — code's linked below."

---

## Editing notes
- Keep cuts tight; speed up long terminal scrolls 2×.
- Caption the honest framing once: **"local sim, assumed mechanics — not a
  leaderboard score."** Integrity reads well to graders.
- Caption the build hook: **"built before the real API was available."**
- End card: repo URL + "Built for the Google × Kaggle AI Agents Intensive."
