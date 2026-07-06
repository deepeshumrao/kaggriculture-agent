# Design Rationale — Kaggriculture Agent

> Deliverable #3. A concise explanation of *why* the agent is built the way it is.

## The problem, in one line
Kaggriculture is a **spatial, two-player** farming game (30 in-game days = **720
turns**). You control one **farmer** that moves around a tile grid; each turn it
takes exactly **one** action — move, or work the tile it stands on. You **buy
seeds**, **plant**, **water**, remove **weeds**, **harvest** into a shed, and
**sell** for money. The goal is to out-earn the opponent.

## The engineering journey (and why it matters)
This project was built **contract-first**. The real competition API wasn't public
at first, so an earlier prototype ran against a *guessed* single-player API behind
a `SimClient` seam. When the **real** environment contract surfaced (from a
community notebook's `agent(obs)`), it turned out to be materially different —
spatial, two-player, movement-based. Rather than force the old model to fit, I
built a **new agent brain against the real contract**, while **reusing the same
engineering rigor** (local simulator, guardrails mindset, exhaustive tests,
clean packaging). That adaptation *is* the "prototype → production" story.

## Core design decisions (the real agent)

### 1. Contract-first, with a local simulator standing in for Kaggle
All real-protocol code lives in `src/kaggriculture_agent/real/`. A single
`protocol.py` encodes the exact observation/action shapes. `local_env.py` is a
deterministic **local simulator that reproduces those shapes**, so the agent is
developed and tested end-to-end **without** the Kaggle package. An agent that
works against the local env plugs into the real env unchanged.

### 2. A strong, explainable rule-based "farm manager" brain
`FarmBrain` (in `brain.py`) is deliberately rule-based, not LLM-per-turn:
- **Market first** (free, no movement): keep seeds stocked, sell the shed.
- **Then the nearest high-value tile**, by priority:
  `harvest-ready → needs-water → weed → plantable`.
- **Move-or-act**: if standing on the target, act; else take one step toward it.
Choosing the **nearest** target (Manhattan distance) matters because movement
costs turns — and there are only 720 of them.

Why rule-based: **zero cost, deterministic, explainable, and dependency-free** —
which also lets it be shipped as a single self-contained file (below).

### 3. A self-contained, parity-tested submission
`deliverables/kaggriculture_submission.py` is one stdlib-only file with a
top-level `agent(obs)` — the artifact you paste into Kaggle. A **parity test**
drives a full game and asserts this flattened file returns the *identical* action
to the tested package for every observation, so the shipped copy can never drift.

### 4. Honesty about what isn't confirmed yet
The reference agent revealed the **contract** (shapes) but not the **numbers**
(prices, yields, weed rate, scoring). Every such value is isolated in one
`Mechanics` dataclass tagged `[ASSUMPTION]`, and `MECHANICS_CALIBRATION.md` maps
each to its real source. **Crucially, these assumptions do not affect leaderboard
correctness** — the real Kaggle env supplies real mechanics and only calls our
`agent(obs)`; the assumptions only make our *offline practice scores* realistic.

### 5. Reused reliability infrastructure
The earlier prototype's **guardrails, typed error handling, and a security
monitor** (prompt-injection / secret-scrubbing / denial-of-wallet) remain in the
codebase and demonstrate the course's "Agent Quality & Security" theme. The
real-protocol brain is pure and side-effect-free, which is its own safety
property: it can only ever return a well-formed action dict.

## What I explicitly rejected
- **LLM-every-turn:** 720 turns × 2 players is far too many calls to be fast,
  cheap, or deterministic — and a spatial pathing loop is exactly what rules do
  well. An LLM is better spent on *higher-level* strategy, a documented next step.
- **Forcing the old single-player model onto the real game:** the spatial,
  two-player contract is different enough that a clean rewrite of the *brain*
  (keeping the *engineering*) was the honest, lower-risk choice.
- **Guessing the env harness:** the run script uses `kaggle_environments` if
  present and falls back to the local sim, instead of hard-coding an unconfirmed
  API.

## Honest limitations / current status
- Local scores (e.g. **3005 vs an idle opponent** over 720 turns) are under
  **assumed** mechanics against a **do-nothing** bot — a correctness and sanity
  signal, **not** a leaderboard result.
- `hands` in the action dict is unused (always empty in the reference); if it
  drives a useful action, it's a small addition to `FarmBrain`.
- Opponent modeling is minimal (we farm efficiently; we don't yet contest the
  opponent). A clear avenue to climb the leaderboard.

## How it maps to the course
Tools/interoperability (protocol + env adapter) · Context engineering (turn-aware
nearest-target planning) · Quality & security (guardrails, security monitor, 66
tests, parity test) · Prototype → production (guessed API → real contract →
self-contained submission).
