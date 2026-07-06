# 🛡️ Security & Guardrail Monitor

The Kaggriculture agent ships with a dedicated **Security & Guardrail Monitor**
(`src/kaggriculture_agent/security/`) that defends against four threat classes.
It is wired into the agent loop, the LLM policy, and the logging system, and is
**on by default** (`Agent()` creates a `SecurityMonitor` automatically).

On any detected threat it logs a `SECURITY VIOLATION` line, and either
**sanitizes** the data (poisoning) or **halts** the action and returns the agent
to a safe, neutral state (`WAIT` / raised `SecurityViolation`).

---

## Threat coverage

### 1. Prompt Injection & Hijacking  (`security/injection.py`)
- Scans all untrusted text that could reach the LLM prompt (crop names, messages,
  and the model's own response) for hijack patterns: *"ignore previous
  instructions"*, *"you are now…"*, role tags (`<system>`), secret-exfil requests,
  and catastrophic-action lures (*"sell everything for 0"*, *"transfer funds to…"*).
- **Outbound prompts** are checked before the API call; **responses** are checked
  before parsing. A hit blocks the action and falls back to the safe heuristic.

### 2. Secret Leakage  (`security/scrubber.py`)
- `scrub()` redacts credential-shaped strings: Google `AIza…` keys, `AQ.…`
  OAuth tokens, `KEY=value` assignments, bearer tokens, and long high-entropy
  blobs. It also redacts the **actual** values of `GOOGLE_API_KEY` /
  `GEMINI_API_KEY` / `KAGGLE_KEY` from the environment (exact-match).
- `SecretScrubbingFilter` is attached to the logger, so **no log line can leak a
  secret**, and every model response is scrubbed before use.

### 3. Data Poisoning & Manipulation  (`security/validation.py`)
- Every `GameState` from the (untrusted) sim is sanitized: NaN/Inf → safe values,
  negative/absurd cash → clamped, out-of-band prices → clamped, negative
  health/inventory/age → clamped, and injection text in crop names → dropped.
- The agent therefore **never acts on logically impossible data**.

### 4. Denial of Wallet (Unbounded Execution)  (`security/budget.py`)
- Hard caps enforced from `config.py`:
  - `max_turns` (default 500) — halts runaway game loops.
  - `max_llm_calls` (default 200) — halts runaway API spend, counted *before* each call.
  - `max_llm_response_chars` (default 20 000) — rejects oversized responses.
- Exceeding any cap raises `SecurityViolation(DENIAL_OF_WALLET)` and stops execution.

---

## Defense-in-depth layers
```
untrusted sim data ──▶ [3] sanitize_state ──▶ agent
                                              │
turn begins ─────────▶ [4] turn cap ─────────┤
                                              ▼
                        strategy.decide()
                          │  (LLM path)
                          ├─▶ [1] check prompt injection
                          ├─▶ [4] count LLM call (cap)
                          ├─▶ API call
                          ├─▶ [1] check response injection
                          └─▶ [2] scrub secrets
                                              │
proposed action ─────▶ guardrails.sanitize() (illegal ▶ WAIT)
                                              ▼
                                          sim.step()
all logs ────────────▶ [2] SecretScrubbingFilter
```

## Configuration
All caps live in `src/kaggriculture_agent/config.py` under the SECURITY sections.
Tune them there (or via env) for the real competition's limits.

## Tests
17 dedicated tests in `tests/test_security.py` cover every threat class plus an
integration test proving a normal game runs clean (0 violations). See
`TEST_RESULTS.md` (T-31..T-47).

## Note on scope
Detection is pattern/heuristic based (appropriate for this sim). For a
production, adversary-facing deployment you would add: allow-listed action
schemas from the model, semantic injection classifiers, per-key spend metering
via the provider dashboard, and signed/authenticated tool responses.
