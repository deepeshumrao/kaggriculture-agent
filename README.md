# Kaggriculture Agent

![CI](https://github.com/deepeshumrao/kaggriculture-agent/actions/workflows/ci.yml/badge.svg)
![tests](https://img.shields.io/badge/tests-66%2F66%20passing-brightgreen)
![python](https://img.shields.io/badge/python-3.14-blue)
![agent](https://img.shields.io/badge/agent-real%20protocol-brightgreen)
![security](https://img.shields.io/badge/security-4%20threats%20guarded-brightgreen)
![cost](https://img.shields.io/badge/default%20cost-%240-blue)
![license](https://img.shields.io/badge/license-MIT-green)

> An autonomous agent for **Kaggriculture** — a two-player farming game
> (30 in-game days = **720 turns**) from the Google × Kaggle **"5-Day AI Agents
> Intensive: Vibe Coding"** capstone. Built **contract-first**: fully developed
> and tested against the real observation/action shapes *before* the competition
> API was public, using a local simulator that mirrors the real game.

## What it does

The game gives the agent one **farmer** on a tile grid. Each turn it returns a
single command — move a step, or work the tile it stands on — plus optional
market orders. The pipeline: **buy seeds → plant → water → clear weeds →
harvest → sell**, aiming to out-earn the opponent.

`FarmBrain` is a fast, explainable rule-based policy:
1. **Market first** (free, no movement): restock seeds, sell the shed.
2. **Nearest high-value tile**, by priority: `harvest → water → weed → plant`.
3. **Move-or-act**: if standing on the target, act; else step toward it.

*Nearest* matters — with only 720 turns, every wasted step is a lost turn.

## Quickstart

```bash
# 1. (optional) create a virtual env
python -m venv .venv && .venv/Scripts/activate    # Windows
# source .venv/bin/activate                         # macOS/Linux

# 2. install deps
pip install -r requirements.txt

# 3. run a full 720-turn game in the local simulator
python scripts/run_real.py --verbose

# 4. run the shipped submission (kaggle_environments if installed, else local)
python scripts/run_kaggle.py

# 5. run the test suite
python -m pytest -q
```

No API key or network needed — the agent is pure stdlib.

## Architecture

```
   Kaggle env ──calls──▶ agent(obs) ──returns──▶ {farmer, hands, market}
                              │
                          FarmBrain
                              │
        ┌──────────────────────┴──────────────────────┐
     protocol.py                                   local_env.py
 (real obs/action shapes)             (local simulator for dev + tests)
```

- **`src/kaggriculture_agent/real/protocol.py`** — the exact real obs/action
  contract (constants, action builders, coordinate helpers).
- **`src/kaggriculture_agent/real/local_env.py`** — `LocalKaggricultureEnv`, a
  deterministic simulator reproducing those shapes. All unconfirmed numbers are
  isolated in a `Mechanics` dataclass (see
  [`deliverables/MECHANICS_CALIBRATION.md`](deliverables/MECHANICS_CALIBRATION.md)).
- **`src/kaggriculture_agent/real/brain.py`** — `FarmBrain`, the decision policy.
- **`deliverables/kaggriculture_submission.py`** — the self-contained, single-file
  `agent(obs)` you submit to Kaggle. A **parity test** proves it behaves
  identically to the tested package code.

> **Honest framing:** local scores (e.g. 3005 vs an idle opponent over 720 turns)
> use *assumed* game mechanics against a do-nothing bot — a correctness and sanity
> signal, **not** a leaderboard result. The real Kaggle env supplies real
> mechanics and only calls our `agent(obs)`.

## Reliability & security

- **66 automated tests** covering the game mechanics, agent decisions, and
  submission parity.
- A **Security & Guardrail Monitor** (see [`SECURITY.md`](SECURITY.md)) defending
  four threat classes: prompt injection, secret leakage, data poisoning, and
  denial-of-wallet.

## Deliverables (capstone)

| Deliverable | File |
|-------------|------|
| Writeup notebook | [`notebooks/kaggle_writeup.ipynb`](notebooks/kaggle_writeup.ipynb) |
| Design rationale | [`deliverables/rationale.md`](deliverables/rationale.md) |
| Video script | [`deliverables/video_script.md`](deliverables/video_script.md) |
| Submission checklist | [`deliverables/submission_checklist.md`](deliverables/submission_checklist.md) |

## Project history

See [`BUILD_JOURNAL.md`](BUILD_JOURNAL.md) for the full, entry-by-entry build log.

## License

MIT — see [`LICENSE`](LICENSE).

---
_Built for the Google × Kaggle AI Agents Intensive — Vibe Coding Capstone._
