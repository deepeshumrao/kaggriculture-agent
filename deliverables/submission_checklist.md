# Final Submission Checklist

> Deliverable hub. Work top to bottom before you submit on Kaggle.
> Status legend: ✅ done · ⏳ needs the real competition env cells · ⬜ your action.

## 0. Confirm the real competition details (do this FIRST)
- [x] ✅ Identified the real game: spatial, 2-player, 30 days = 720 turns.
- [x] ✅ Decoded the real obs/action contract (see `real-kaggriculture-api` memo
      + `deliverables/MECHANICS_CALIBRATION.md`).
- [ ] ⏳ Note the **exact submission deadline** from the live Kaggle page.
- [ ] ⏳ Confirm the **env creation** call (e.g. `make("<name>")` / `kagglehub`)
      and **how agents are submitted** (function vs notebook).
- [ ] ⏳ Note the **scoring formula** and leaderboard mechanics.

## 1. Adapt to the real sim  ✅ (built) / ⏳ (final wiring)
- [x] ✅ Real-protocol agent implemented: `src/kaggriculture_agent/real/`
      (`protocol`, `local_env`, `brain`, `submission`).
- [x] ✅ Local simulator reproduces the real obs/action shapes for dev + tests.
- [ ] ⏳ Set the real env name in `scripts/run_kaggle.py --env <name>`.
- [ ] ⏳ (Optional) Calibrate `local_env.Mechanics` from one real episode — see
      `MECHANICS_CALIBRATION.md`. *Does not affect leaderboard correctness.*

## 2. Account setup
- [ ] ⬜ Kaggle account with **verified phone number**.
- [ ] ⬜ Joined the competition (unlocks Data/Code tabs).
- [ ] ⬜ Google AI Studio account + free API key (only if adding an LLM planner).

## 3. The four deliverables
- [x] ✅ **Writeup** — `notebooks/kaggle_writeup.ipynb` (real agent; runs clean).
- [x] ✅ **Rationale** — `deliverables/rationale.md` (real agent).
- [x] ✅ **Video script** — `deliverables/video_script.md` (real agent).
- [ ] ⬜ **Video** — record from the script, upload, paste the link.
- [ ] ⬜ **Code link** — repo or Kaggle notebook, public/accessible.
- [ ] ⬜ Paste video + code links into the writeup header cell.

## 4. Quality gates (all should pass)
- [x] ✅ `python -m pytest -q` → 66 green.
- [x] ✅ `python scripts/run_real.py --verbose` → full 720-turn game, prints score.
- [x] ✅ `python scripts/run_kaggle.py` → runs the shipped submission (local
      fallback until `kaggle_environments` + real env are available).
- [x] ✅ No secrets committed (`.env` is git-ignored).
- [ ] ⬜ README quickstart works on a fresh clone.

## 5. Submit
- [ ] ⏳ Submit `deliverables/kaggriculture_submission.py` (top-level `agent(obs)`)
      per the competition's instructions (function or notebook).
- [ ] ⬜ Writeup submitted with all links.
- [ ] ⬜ Screenshot your leaderboard score for the writeup.

## 6. After submitting
- [ ] ⬜ Confirm badge/certificate appears on Kaggle profile.
- [ ] ⬜ Save final score + leaderboard rank in `BUILD_JOURNAL.md`.

---
**Bottom line:** all code + written deliverables are ready. The only true blockers
are the competition-only details (⏳): env name, submit format, deadline, scoring —
grab them from the joined competition page, then submit.
