# The Journey Till the Full Build — Kaggriculture Agent

> A running log of every step taken to build the capstone agent.
> Started: 2026-07-02

---

## Guiding decision
The real Kaggriculture sim API is not yet known (Kaggle page is JS-rendered).
**Strategy:** build against a clean `SimClient` interface with a fully working
**mock simulation** so the entire project runs end-to-end locally with zero
errors *today*. When the real starter code arrives, we swap ONE file
(`mock_sim.py` -> real client) and everything else keeps working.

---

## Environment
- OS: Windows (darwin shell wrapper), zsh
- Python: 3.14.6 (`python`)
- Working dir: `Capstone Project/` (on Google Drive)

---

## Log

### [Entry 0] Planning + journal
- Created `BUILD_JOURNAL.md`.
- Confirmed Python 3.14.6 present.
- Decided on mock-sim-first architecture (see above).
- Todo list created (6 phases).

### [Entry 1] Phase 1 — Scaffold (DONE)
- Created `README.md`, `requirements.txt`, `.env.example`, `.gitignore`.
- Confirmed heuristic policy needs no key/cost; LLM optional.

### [Entry 2] Phase 2 — Sim layer + mock (DONE)
- `types.py` — GameState/Plot/Action/StepResult + enums (sim-agnostic).
- `sim/base.py` — `SimClient` abstract interface (the single seam).
- `sim/crops.py` — balanced 4-crop catalog (wheat/corn/tomato/potato).
- `sim/mock_sim.py` — full deterministic-by-seed farming engine: growth,
  water, weather effects (rain/drought/storm), market random walk,
  final settlement. Implements `SimClient`.
- Mechanics tuned so no single crop dominates -> strategy matters.

### [Entry 3] Phase 3 — Agent core (DONE)
- `config.py` — env-driven config, safe defaults, no-key operation.
- `memory/state.py` — per-episode session memory (price/weather history).
- `memory/knowledge.py` — cross-episode learning (avg profit per crop).
- `policy/guardrails.py` — legality checks + `sanitize()` (illegal -> WAIT).
- `policy/prompts.py` — Gemini system/user prompts (vibe-coding brain).
- `policy/strategy.py` — HeuristicStrategy (6-rule priority player).
- `policy/llm_strategy.py` — optional Gemini policy, graceful fallback.
- `agent.py` — Agent.play_episode(): sim + policy + guardrails + memory.

### [Entry 4] Phase 4 — Scripts + baseline (DONE)
- `baseline.py` — NaiveStrategy (plant cheapest, sell instantly).
- `scripts/run_local.py` — one game, verbose trace.
- `scripts/evaluate.py` — N games, smart vs baseline, lift + win rate.

### [Entry 5] Phase 5 — Tests (DONE)
- `tests/test_sim.py`, `test_guardrails.py`, `test_agent.py`.

### [Entry 6] Phase 6 — VERIFICATION (DONE, all green)
- Env note: bundled Python 3.14 had no pip; bootstrapped via `ensurepip`.
- `run_local.py` (seed 0, 20 days): completes cleanly, FINAL SCORE 6829.52.
- `pytest`: **13 passed in 0.64s**.
- `evaluate.py` (50 games): smart avg **5854.79** vs naive **938.95**
  = **+523.5% lift, 50/50 (100%) win rate**. Learned best crop: tomato.
- Fixed one cosmetic issue: em-dash garbled in Windows console -> ASCII.

## STATUS: FULL BUILD COMPLETE — runs end-to-end, zero errors, all tests green.
Next (optional): plug in real Kaggle sim (edit sim/), enable LLM policy,
write deliverables (writeup/rationale/video).

### [Entry 7] Deliverables (DONE)
- `deliverables/rationale.md` — design rationale (deliverable #3).
- `deliverables/video_script.md` — 3-4 min scene-by-scene script (#2).
- `deliverables/submission_checklist.md` — end-to-end submit checklist.
- `notebooks/kaggle_writeup.ipynb` — runnable writeup (#1); JSON validated.

### [Entry 8] LLM (Gemini) policy enabled + verified (DONE)
- Installed `google-genai` + `python-dotenv` (SDK import OK).
- `tests/test_llm_fallback.py` — 4 tests: graceful fallback + JSON parsing
  (plain, code-fenced, garbage-rejecting). No network calls.
- `scripts/test_llm.py` — manual runner; prints whether real Gemini or
  fallback is active; runs a full game either way.
- Verified: with NO key, LLM policy cleanly falls back to heuristic and
  completes a game (score 1631.12, seed 0, 6 days).
- Test suite now **17 passed in 0.48s**.
- NOTE: a real Gemini API call needs the user's GOOGLE_API_KEY (free from
  AI Studio). Code path is ready; set the key and run scripts/test_llm.py.

### [Entry 9] LIVE Gemini verified with real key (DONE)
- User supplied an API key; stored in `.env` (git-ignored, never echoed).
- Key AUTHENTICATED (a 429 quota error, not a 401 auth error, proved it valid).
- Default `gemini-2.0-flash` had `limit: 0` quota on this key. Probed models:
    gemini-2.5-flash    -> SUCCESS
    gemini-flash-latest -> SUCCESS
    gemini-1.5-flash    -> 404 (retired)
    gemini-2.0-flash-lite -> 429
- Switched default model to `gemini-2.5-flash` (config.py + .env.example).
- LIVE GAME with real Gemini (seed 0, 10 days): agent diversified crops
  (wheat + tomato), fertilized to protect, harvested, sold. SCORE 1329.24.
  -> Confirms the LLM policy genuinely drives decisions end-to-end.
- Made tests hermetic: conftest.py forces heuristic + drops key, so the
  suite never makes live calls regardless of .env. Still 17 passed.
- SECURITY: reminded user the key was shared in plaintext; rotate if chat
  not private. Only stored in .env.

## STATUS: LLM policy LIVE-VERIFIED. Full project runs on heuristic (free) or
real Gemini. All deliverables drafted. 17/17 tests green.

### [Entry 10] TEST_RESULTS.md — documented results file (DONE)
- Created `TEST_RESULTS.md` with 24 documented results:
  * T-01..T-17: the 17 automated unit/integration tests (all PASS, with a
    per-test table: ID / verifies / expected / actual / status + raw output).
  * T-18: 100-game eval -> +541.3%, 100/100 win, learned crop tomato.
  * T-19: per-seed table (seeds 0-7), smart beats naive on all.
  * T-20/T-21: edge cases (near-zero cash, 1-day game) -> no crash.
  * T-22..T-24: live Gemini (auth proof, model probe, real game trace).
- Includes exec summary, reproduce commands, coverage map, caveats.
- Guarded quota: a stray LLM-policy 100-game eval was killed (PID 3596)
  before it could burn the key; re-ran eval with heuristic forced.

### [Entry 11] Errors & exception handling hardening (DONE)
- `errors.py` — typed exception hierarchy (KaggricultureError + Sim/Policy/LLM).
- `logging_setup.py` — opt-in logging (silent by default via NullHandler;
  `enable_logging()` for scripts; KAGGRICULTURE_LOG env var for level).
- `mock_sim.py` — replaced `assert` with `SimNotStartedError` (safe under -O).
- `llm_strategy.py` — retry w/ exponential backoff on TRANSIENT errors
  (429/timeout/5xx), auto-disable after 3 consecutive failures (no quota
  hammering), full logging of retries/fallbacks.
- `agent.py` — episode loop now guards: strategy exception -> WAIT (game
  continues); sim.step exception -> raised as typed SimError (ends cleanly).
- Scripts (`run_local`, `evaluate`, `test_llm`) — top-level handlers,
  proper exit codes (0/1/130), opt-in logging.
- `tests/test_error_handling.py` — 6 new tests: typed errors before reset,
  agent survives exploding strategy, sim failure -> SimError, transient
  classifier, LLM auto-disable after repeated failures.
- Result: **23 passed** (17 -> 23). Gameplay unaffected.

### [Entry 12] Security & Guardrail Monitor (DONE)
- New `security/` package defending 4 threat classes, on by default:
  * violations.py — SecurityViolation + ThreatType enum.
  * injection.py  — [T1] prompt-injection / hijack pattern detector.
  * scrubber.py   — [T2] secret redaction + logging filter (scrubs AIza/AQ.
    keys, KEY=val, bearer, and real env secret VALUES).
  * validation.py — [T3] GameState sanitizer (NaN/Inf, neg/absurd cash,
    price bands, health/inventory clamps, injection in crop names dropped).
  * budget.py     — [T4] denial-of-wallet: max_turns / max_llm_calls /
    response-size caps -> raise SecurityViolation to halt.
  * monitor.py    — SecurityMonitor orchestrator; logs 'SECURITY VIOLATION'.
- config.py: added SECURITY caps (max_turns=500, max_llm_calls=200,
  max_llm_response_chars=20000, price/cash sanity bounds).
- Wiring: agent loop calls before_turn() + check_state(); LLM policy checks
  prompt+response injection, counts calls, scrubs secrets; logging_setup
  attaches SecretScrubbingFilter. SecurityViolation propagates (halts) and
  is NOT swallowed by the per-turn WAIT fallback.
- tests/test_security.py — 17 tests across all 4 threats + clean-game
  integration. Live demo confirmed all 4 fire; normal game 6829.52, 0 viol.
- Total suite: **40 passed**.
- Added SECURITY.md documenting the model + defense-in-depth diagram.

### [Entry 13] Regression fix — per-episode security budget reset (DONE)
- Resumed after a lost session; re-verified everything first.
- BUG found on re-verify: `evaluate.py` reuses ONE Agent (and its
  SecurityMonitor) across all games, but the denial-of-wallet turn counter
  never reset between episodes -> multi-game eval halted at
  `turn limit exceeded (501 > 500)`. The turn/LLM caps are per-GAME safety
  limits, not per-process, so they must reset each episode (long-term
  Knowledge still persists across games, by design).
- Fix: `BudgetMonitor.reset()`, `SecurityMonitor.begin_episode()`, called at
  the top of `Agent.play_episode()`.
- Regression test `test_budget_resets_between_episodes` (reused agent, 5
  games, tight cap -> no false halt).
- Re-verified: eval 50 games heuristic = smart 5854.79 vs naive 938.95,
  +523.5%, 50/50 (matches Entry 6 baseline exactly). Suite **41 passed**.

### [Entry 14] REAL Kaggriculture API decoded + real-protocol agent (DONE)
- User obtained the real env contract from a community Kaggle notebook's
  `def agent(obs)`. REALITY DIFFERS from our guessed API: the game is SPATIAL,
  2-PLAYER, movement-based (30 days = 720 turns, ~24/day). A farmer walks a grid
  (tiles[y][x]); one farmer command per turn (move OR act on current tile);
  seeds must be BOUGHT before planting; harvested crop -> shed -> SELL; weeds
  must be DUG. => NOT the one-file swap we assumed; needs a new agent brain.
  Full decoded contract saved to memory `real-kaggriculture-api.md`.
- New self-contained package `real/` speaking the ACTUAL contract:
  * protocol.py  — obs/action constants, `build_action`, `step_toward`, accessors.
  * local_env.py — `LocalKaggricultureEnv`: deterministic local simulator that
    reproduces the real obs/action shapes so we can develop/test WITHOUT the
    Kaggle package (mock-first, again). All UNCONFIRMED numeric mechanics
    (prices, yields, weed spawn, scoring, start money) isolated in `Mechanics`
    and marked [ASSUMPTION] for one-place reconciliation with the real spec.
  * brain.py     — `FarmBrain.decide(obs)`: pure stdlib policy (market-first,
    then nearest harvest>water>weed>plant target, move-or-act). Generalizes the
    reference agent (multi-crop, nearest-target routing). Kaggle-portable.
  * submission.py— top-level `agent(obs, config=None)` entrypoint.
- Script `scripts/run_real.py`: full 720-turn local game (brain vs idle bot).
  seed 0 -> our score 3005.00 vs opponent 100.00; 720 turns, no errors.
- Tests: `test_real_env.py` (12) + `test_real_agent.py` (11) covering contract
  shape, plant/water/harvest/market/movement/weeds/determinism/turn-limit, and
  agent targeting + full-game profit. Suite **41 -> 64 passed**.
- STILL NEEDED from the real notebook to finalize: env import/creation + run/
  submit cells; full crop list + real prices; scoring rule; `hands` semantics.
  When supplied, reconcile `Mechanics` and wire the actual submission path.

### [Entry 15] Submission wiring + parity + calibration map (DONE)
- Key realization: our local `Mechanics` assumptions DON'T affect leaderboard
  correctness — the real Kaggle env supplies real mechanics and only calls our
  `agent(obs)`. Assumptions only shape our OFFLINE practice scores. So the
  submission path can be finalized now; calibration is optional polish.
- `deliverables/kaggriculture_submission.py` — the SELF-CONTAINED single-file
  submission (stdlib only, zero repo imports): inlined constants + FarmBrain +
  top-level `agent(obs, config=None)`. This is the paste-into-Kaggle artifact.
- `scripts/run_kaggle.py` — runs the submission via `kaggle_environments.make`
  if installed, else transparently falls back to the local sim (same command
  works offline). Env name is a --flag (default guess "kaggriculture"; confirm).
- `tests/test_submission_parity.py` (2 tests) — drives a full local game and
  asserts the standalone `agent(obs)` == package brain for EVERY obs, so the
  shipped copy can never silently drift from the tested `real/` source.
- `deliverables/MECHANICS_CALIBRATION.md` — maps every [ASSUMPTION] to the real
  value's source + the exact `Mechanics` field; lists the 4 open contract
  questions (env name, run/submit shape, `hands`, opponent slots).
- Verified: run_kaggle (local fallback) = our 3005 vs idle 100, 720 turns.
  Suite **64 -> 66 passed**.
- REMAINING to actually submit: paste real env setup/run cells -> set --env name
  and confirm the delivery format; (optional) calibrate Mechanics from one real
  episode; then update deliverables writeup/video to describe the real agent.

### [Entry 16] Deliverables rewritten for the REAL agent (DONE)
- The Jul-2 deliverables still described the OLD abstract agent (plots/prices/
  tomato). Rewrote all of them around the real spatial farmer agent, keeping the
  numbers HONEST (local 3005-vs-idle-100 is under ASSUMED mechanics vs a
  do-nothing bot -> labeled a sanity signal, NOT a leaderboard score):
  * `deliverables/rationale.md` — contract-first story, FarmBrain priority logic,
    self-contained parity-tested submission, assumptions isolated, honest limits.
  * `deliverables/video_script.md` — 7 scenes re-cut: real game, run_real.py,
    brain priority, parity/tests; captions flag the honest framing.
  * `notebooks/kaggle_writeup.ipynb` — every cell now runs the REAL agent
    (imports real/, obs->action demo, full 720-turn game, submission parity
    check). Verified all code paths: imports OK, action ok, 3005 vs 100, 0
    parity mismatches. (No jupyter in venv; validated by running cell logic
    directly + JSON valid, 12 cells.)
  * `deliverables/submission_checklist.md` — rewritten to real state with ✅/⏳/⬜
    status; only true blockers are competition-only details (env name, submit
    format, deadline, scoring).
- Suite still **66 passed**. Written deliverables + code are submission-ready;
  remaining items are the user's Kaggle-side actions (join, record video, links)
  and the competition-only env/run details.

