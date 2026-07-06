# Kaggriculture Capstone — Project Plan

> Living document. Last updated: 2026-07-02
> Companion to `capstone_summary.txt` (competition facts).

---

## 1. What We Are Building

An **autonomous farming agent** for the Kaggle "Kaggriculture" capstone. The
agent plays a farming simulation, making sequential decisions (what to plant,
when to water/fertilize, when to harvest, how to spend budget, how to react to
weather/market events) to maximize its score on the **live leaderboard**.

**Design thesis:** a Google ADK agent with a small, reliable **tool layer**
that talks to the simulation, a **decision policy** (LLM reasoning + guardrails),
and a **memory/state layer** so the agent learns within and across episodes.

### Success criteria
- Runs end-to-end against the sim without crashing (robust error handling).
- Beats a naive baseline (e.g., "always plant the cheapest crop") on score.
- Reproducible: anyone can clone, set a key, and run.
- Ships all 4 deliverables: writeup, video, rationale, code link.

---

## 2. Architecture (high level)

```
                    ┌─────────────────────────────┐
                    │        Root ADK Agent        │
                    │  (planner / orchestrator)    │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                         │
   ┌──────▼──────┐         ┌───────▼───────┐         ┌───────▼───────┐
   │  Tools      │         │  Policy /     │         │  Memory /     │
   │  (sim API,  │         │  Reasoning    │         │  State        │
   │  market,    │         │  (strategy)   │         │  (sessions,   │
   │  weather)   │         │               │         │   history)    │
   └─────────────┘         └───────────────┘         └───────────────┘
```

- **Root agent** decides each turn using observations + memory.
- **Tools** are thin, deterministic wrappers around the sim / env.
- **Policy** encodes the strategy prompt + guardrails (budget limits, no illegal moves).
- **Memory** stores what worked (crop yields, weather patterns, price history).

---

## 3. Planned File Structure (everything we'll create)

```
Capstone Project/
├── PROJECT_PLAN.md              # this file
├── capstone_summary.txt         # competition facts & rules (done)
├── README.md                    # how to install & run; project pitch
├── .env.example                 # template for API keys (no secrets committed)
├── .gitignore                   # ignore .env, __pycache__, logs, venv
├── requirements.txt             # python deps (google-adk, etc.)
│
├── src/
│   └── kaggriculture_agent/
│       ├── __init__.py
│       ├── agent.py             # root ADK agent definition (entrypoint)
│       ├── config.py            # model name, constants, thresholds, budgets
│       ├── prompts.py           # system/strategy prompts (the "vibe")
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── sim_tools.py     # observe(), plant(), water(), harvest(), sell()
│       │   ├── market_tools.py  # price lookups / forecasts
│       │   └── weather_tools.py # weather observations / forecasts
│       │
│       ├── policy/
│       │   ├── __init__.py
│       │   ├── strategy.py      # decision logic / heuristics + LLM planning
│       │   └── guardrails.py    # legal-move checks, budget caps, safety
│       │
│       └── memory/
│           ├── __init__.py
│           ├── state.py         # per-episode state (sessions)
│           └── knowledge.py     # cross-episode learnings (yields, prices)
│
├── scripts/
│   ├── run_local.py             # run one episode locally, print score
│   ├── evaluate.py              # run N episodes, report avg score vs baseline
│   └── submit.py                # package/submit to the leaderboard
│
├── tests/
│   ├── test_tools.py            # tools return valid, well-typed results
│   ├── test_guardrails.py       # never makes illegal/over-budget moves
│   └── test_agent_smoke.py      # agent completes an episode end-to-end
│
├── notebooks/
│   └── kaggle_writeup.ipynb     # the Kaggle submission writeup notebook
│
└── deliverables/
    ├── rationale.md             # brief design rationale (submission)
    ├── video_script.md          # script/storyboard for the explainer video
    └── submission_checklist.md  # final pre-submit checklist
```

---

## 4. File-by-File Purpose

| File | Purpose |
|---|---|
| `README.md` | One-glance pitch, setup, run commands, results. |
| `.env.example` | `GOOGLE_API_KEY=`, `KAGGLE_*` placeholders. |
| `requirements.txt` | `google-adk`, `google-genai`, `python-dotenv`, `pytest`, sim client libs. |
| `agent.py` | Defines the root ADK `Agent`, wires tools + memory, exposes runner. |
| `config.py` | Model id (`gemini-*`), budgets, turn limits, tunable thresholds. |
| `prompts.py` | Strategy/system prompts — the natural-language "brain". |
| `sim_tools.py` | Typed wrappers for every sim action + observation. |
| `market_tools.py` / `weather_tools.py` | Extra signals for smarter decisions. |
| `strategy.py` | Turns observations + memory into an action each step. |
| `guardrails.py` | Blocks invalid/over-budget/unsafe actions before they execute. |
| `state.py` | Tracks current episode (cash, plots, day, inventory). |
| `knowledge.py` | Remembers crop yields, weather/price patterns across runs. |
| `run_local.py` | Fast dev loop: play one game, print the score. |
| `evaluate.py` | Statistical check vs baseline over many episodes. |
| `submit.py` | Formats and pushes the submission. |
| `tests/*` | Confidence: tools, guardrails, and full-episode smoke test. |
| `kaggle_writeup.ipynb` | The graded writeup (deliverable #1). |
| `rationale.md` | Short "why we built it this way" (deliverable #3). |
| `video_script.md` | Plan for the explainer video (deliverable #2). |

---

## 5. Build Phases (roadmap)

1. **Scaffold** — create folders, README, requirements, .env.example, .gitignore.
2. **Connect the sim** — get `sim_tools.observe()` + a random/greedy baseline running via `run_local.py`.
3. **First agent** — minimal ADK root agent that picks legal actions; beat "do nothing".
4. **Strategy + guardrails** — real decision logic; never make illegal moves.
5. **Memory** — persist learnings; improve across episodes.
6. **Evaluate** — `evaluate.py` vs baseline; tune `config.py`.
7. **Harden** — tests, error handling, retries, logging.
8. **Deliverables** — writeup notebook, rationale, video, submit.

Maps to the course: Days 1-2 -> phases 1-3, Day 3 -> phase 5, Day 4 -> phase 7, Day 5 -> deploy/submit.

---

## 6. Open Questions (confirm on live Kaggle page)

- Exact sim API / how the agent submits moves (notebook? endpoint? package?).
- Scoring formula and leaderboard mechanics.
- Allowed models / rate limits / runtime limits.
- Exact submission deadline.

---

## 7. Deliverables Tracker

- [ ] Working agent that beats baseline
- [ ] Kaggle writeup (`kaggle_writeup.ipynb`)
- [ ] Explainer video (script in `video_script.md`)
- [ ] Rationale (`rationale.md`)
- [ ] Code link (repo / notebook)
- [ ] Final submission
