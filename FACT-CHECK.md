# Fact-check

Every number the two Public Source stories reported, traced to the data file that produces it
and to the archived source that data was coded from. The numeric claims are not only listed here;
they are asserted in code. Run `python 03-harness/build.py` and it recomputes each one and exits
non-zero if any has drifted. What follows is the human-readable face of that check, plus the three
places where the underlying data disagrees with itself and how each disagreement resolves.

## Headline figures

| Claim (as published) | Value | Produced from | Status |
|---|---|---|---|
| Board meetings analyzed, Oct 2023–Sep 2025 | 24 | `02-data/meetings.csv` | reproduces |
| Resolutions voted | 228 | `meetings.csv` (sum of `total_resolutions`) | reproduces |
| Unanimous votes | 223 | `meetings.csv` | reproduces |
| Split votes / no votes | 0 | `meetings.csv` | reproduces |
| Abstentions (all Chair Sciulli, conflict recusals) | 5 | `meetings.csv` | reproduces |
| Unanimity rate when all members voted | 100% | `peer_comparison.csv` (223 / (228−5)) | reproduces |
| Spending authorized | $871.25M | `meetings.csv` (sum of `dollars_millions`) | reproduces |
| Resolutions that drew ≥1 question | 72 of 228 | `questions_by_resolution.csv` (row count) | reproduces |
| Resolutions that drew none | 156 | derived, 228 − 72 | reproduces |
| Public speakers, two years | 10 | `meetings.csv` | reproduces |
| Meetings with any public speaker | 5 of 24 | `meetings.csv` | reproduces |
| Chair's share of questions | 47 of 131 (36%) | `questions_by_member.csv` | reproduces |
| Peer unanimity, sampled | 20 of 29 (69%) | `peer_comparison.csv` | reproduces |
| Questions at first post-publication meeting | 40 | `follow_up.csv` | reproduces |
| Ratio to the 24-month average | ~7× | derived, 40 ÷ (131/24) | reproduces |

The archived sources these trace back to are listed in `01-sources-archive/sources.json` and hashed
in `MANIFEST.md`; `python 03-harness/verify.py` confirms none has changed since capture.

## The three reconciliations

A dataset built by hand over two years carries seams. Three of them matter enough to state plainly,
because each is a place a careful reader will find two numbers and deserve to know which governs.

**1. Two question totals: 131 and 96.** The data counts questions two ways. Counted per meeting and
per member, the board asked **131** questions across 24 meetings (`meetings.csv`, `questions_by_member.csv`
column `questions_by_meeting`). Counted only where a question attaches to a specific numbered resolution,
the total is **96** (`questions_by_resolution.csv`, `questions_by_member.csv` column `questions_by_resolution`).
The gap is questions asked in general discussion, on staff reports, or during an agenda item that carried
no resolution number. Both totals are correct for what they measure. The published "72 of 228 resolutions
drew a question" uses the resolution-attributed count; the per-member portraits ("the chair asked about a
third of all questions") use the per-meeting count. `build.py` checks both totals against their own
definitions so neither can quietly change.

**2. Unquestioned resolutions: 156, not 142.** The authoritative figure is **156** — 228 resolutions
minus the 72 that drew a question. An earlier enumerated list of zero-question resolutions ran to only
142 rows; that list was incomplete, an artifact of transcribing resolution numbers by hand rather than a
different finding. The count that governs is the subtraction, and it is the one the story reported.

**3. The draft carried 218 / 215 / $1.78B; the published stories carry 228 / 223 / >$870M.** An early
November draft, preserved in the master fact-check document, reported 218 resolutions, 215 unanimous, and
$1.78 billion. Continued coding of the minutes corrected those to 228, 223, and $871.25 million before
publication. This repository ships only the published figures. The correction is recorded here rather than
hidden, because a reproducible archive that quietly matched a superseded draft would be the opposite of the
thing it claims to be.

## The peer test

The comparison to peer boards was an empirical design, not a rhetorical one. A random-number generator
selected three meetings from each of two peer water boards — the Niagara Falls Water Board and the North
Harris County Regional Water Authority — across the same 24-month window. Every vote in those six meetings
was coded on the same four variables. The six meetings produced 29 votes; 20 were unanimous and nine
involved split votes, failed motions, or abstentions, a combined unanimity rate of 69% against Pittsburgh
Water's 100%. The Niagara Falls minutes of April 28, 2025 are archived and hashed in this repository
(`nfwb-2025-04-28`); the North Harris County minutes are cited pending relocation of the source PDF.

## One figure that is not here, on purpose

An early draft framed 215 consecutive unanimous votes as roughly a one-in-6.9-billion event, the odds of
215 independent coin flips landing the same way. Public Source cut that framing before publication, and
this repository does not restore it. Board votes are not independent coin flips: executive sessions, staff
briefings, and consensus norms correlate them by design, as the reporting itself documents. The finding
that carries the story is the observed contrast with peer boards, which needs no probability model to stand.

## The full article-level fact-check

Beyond these figures, every quotation and secondary citation in the baseline story was verified
claim-by-claim in a 22-section master fact-check document: the interview quotations from Myron Arnowitt,
Linnea Warren Mears, Erika Strassburger, Aly Shaw, and Emily Ruth; the written responses from CEO Will
Pickering and Chair Alex Sciulli; and the documentary citations (the OCC board-effectiveness guidance, the
Kennesaw State Enron analysis, Pennsylvania's Sunshine Act, *Smith v. Township of Richmond*, and the
academic literature on group decision-making). The interview sourcing is organized in `05-sources/`.
