# GitHub Development Events and Cryptocurrency Market Response

Event-study of whether observable development events in a crypto protocol's
public GitHub repository produce measurable market responses in its token.
Full research design, treatments, identification strategy, and sequencing:
[`new_design.md`](new_design.md).

Prior project (AI coding agents and code review) is archived at
[`archive/prior_project_ai_code_review/`](archive/prior_project_ai_code_review/) —
its GitHub extraction plumbing (`src/github_client.py`) is reused here.

## Status

**Phase 0 (feasibility count) — not yet run at scale.** Per `new_design.md`
§8, nothing else should be built out until this count exists.

## Setup

```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

`.env` needs `GITHUB_TOKEN=ghp_...` (already present; never commit this file
— it's gitignored).

## Layout

```
src/
  github_client.py      GitHub REST/GraphQL client (rate-limit aware)
  protocol_universe.py  DefiLlama -> candidate protocols with github + gecko_id
  prices.py             CoinGecko OHLCV, trading-history & volume checks
  events.py             Candidate event extraction for the 3 treatments (§2)
  legitimacy.py          Scam/dead-project filters (market cap, exchange, activity)
phase0_feasibility.py   Phase 0 orchestrator — the immediate next step
enrich_legitimacy.py   Second pass: applies legitimacy filters to Phase 0 survivors
output/                 phase0_candidates.csv and later run outputs (gitignored)
```

## Running Phase 0

```
python3 phase0_feasibility.py --limit 30      # smoke test, ~1-2 min
python3 phase0_feasibility.py                 # full sweep, hours (CoinGecko free tier is slow)
```

Writes `output/phase0_candidates.csv`: one row per DefiLlama protocol with a
GitHub link, whether a repo/token pair survived the sample criteria (§4), and
counts for each of the three event types (§2). The console summary is the
number `new_design.md` §4/§8 gates on: if fewer than ~100 protocols with
usable event counts survive, the design narrows to a single event type.

### Filtering out scams and dead projects

DefiLlama + CoinGecko's combined universe includes plenty of copy-pasted,
abandoned, or wash-traded tokens that "has a repo and trades somewhere" alone
doesn't screen out. Once Phase 0 has produced `output/phase0_candidates.csv`,
run:

```
python3 enrich_legitimacy.py                                # defaults below
python3 enrich_legitimacy.py --min-market-cap-usd 10000000 --exclude-forks
```

This only touches rows that already passed the base sample criteria (a small
fraction of the full sweep), adding:

| Check | Default | Targets |
|---|---|---|
| Market cap floor | ≥ $5M | micro-cap / wash-traded tokens |
| Listed on a major exchange | required | real order-book liquidity, not a spoofed DEX pool — checked by exchange identifier, since CoinGecko's `trust_score` field is null on the free tier |
| CoinGecko `public_notice` risk keywords | excluded | actual hacks/exploits/delistings — keyword-matched, not any notice (a benign rebrand notice would otherwise wrongly fail a real protocol) |
| Contributors | ≥ 3 | solo/throwaway repos |
| Days since last push | ≤ 180 | copy-pasted-and-abandoned repos |
| Is a fork | recorded, not excluded by default | many legitimate protocols (L2s forking geth, DEXs forking Uniswap) build real value on a fork — pass `--exclude-forks` for a stricter run |

Writes `output/phase0_candidates_legit.csv` with these columns plus a final
`passes_legitimacy` flag, and prints how many protocols and events survive —
the number that actually matters for the §4/§8 go/no-go gate.

### Known limitations (see `new_design.md` §9)

- **CoinGecko free tier caps historical queries at 365 days.** `prices.py`
  can confirm a token has *at least* ~364 days of history, not distinguish
  further. Fine for the §4 sample criterion (>=12 months); not fine for
  picking among candidate `[-120,-20]` estimation windows in §3 — that will
  need a paid key or an exchange API once a protocol clears Phase 0.
- **Repo-to-token mapping here is automated** (best-by-stars resolution of
  DefiLlama's `github` field), which §4 explicitly warns produces false
  links. Treat `output/phase0_candidates.csv`'s `repo` column as a
  candidate list requiring manual verification, not ground truth.
- **Security-fix detection is a commit-message regex** (`CVE-`, `GHSA-`,
  "vulnerability", ...), not the GitHub Security Advisories API — most repos
  never populate that API, but the regex will both miss real fixes and catch
  false positives (e.g. dependency bumps mentioning a CVE they patch
  upstream). §5/§10 call for quantifying this before treating the counts as
  real events.
- **Maintainer-departure ranking uses total commit count**, not pre-period
  commit share as §2C specifies — an approximation adequate for a
  feasibility count only.
