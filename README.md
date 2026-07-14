# The Pittsburgh Water Deliberation Record

A reproducible archive behind two published Public Source stories about the board that governs
water and sewer service for 300,000 people in Pittsburgh. Every figure the stories reported can be
recomputed here from coded data, and every coded figure traces to an archived, hashed source. You
do not have to trust the reporter; you can run the check.

Reporting by Brian Nuckols for Public Source:

- [Two years, zero 'no' votes on Pittsburgh Water board as rate hike looms](https://www.publicsource.org/pittsburgh-water-board-unanimous-votes-oversight/)
- [Pittsburgh Water board asks questions after transparency investigation](https://www.publicsource.org/pittsburgh-water-board-transparency-rate-hike/)

## What the reporting found

Across 24 board meetings from October 2023 through September 2025, the Pittsburgh Water board voted
on 228 resolutions. It was unanimous 223 times and split zero times; the only five abstentions were
the chair recusing himself for conflicts of interest. It authorized more than $871 million while it
did so. Of the 228 resolutions, 156 drew no recorded question from any board member. Ten residents
spoke to the board in two years.

Then a second thing happened, the kind that rarely gets measured. At the first board meeting after
the investigation published, the board asked 40 questions, about seven times its 24-month average,
and issued a stop-work order against a contractor. Reporting changed the institution's behavior, and
the change is in the minutes.

## How to check my work

Nothing below needs a network or a key you do not already have in this repository.

| The promise | How you check it |
|---|---|
| Every headline figure recomputes from the data | `python 03-harness/build.py` |
| Every archived source is the file that was captured | `python 03-harness/verify.py` |
| Both, plus a single verdict | `python 03-harness/check.py` |
| The archive is complete enough to publish | `python 03-harness/gate.py` |

`build.py` recomputes 228, 223, $871.25M, 72, 156, the 69% peer rate, and the 40-question follow-up,
and exits non-zero if any of them has drifted from what the stories reported. `verify.py` re-hashes
each source PDF against `01-sources-archive/MANIFEST.md`. Neither reaches the network.

## What is here

```
02-data/            the coded data, one row per meeting and per questioned resolution (CC BY 4.0)
03-harness/         build / verify / gate / check / capture (MIT)
01-sources-archive/ the hashed source PDFs, the manifest, the provenance, the chain of custody
04-charts/          five charts, self-contained, light and dark
widget/             the peer test, an interactive comparison against peer water boards
05-sources/         the human sourcing: interviews, roles, and the claims each supports
FACT-CHECK.md       every published figure mapped to its source, and three reconciliations in the open
METHODOLOGY.md      the four-variable codebook and the peer sampling design
PORTABILITY.md      how to run this instrument on any other board
```

## What is honest about the gaps

Four source PDFs are captured and hashed (the Niagara Falls peer minutes and three governance
references). The 24 individual Pittsburgh Water meeting-minute PDFs are cited to the board's document
portal and are the next capture step; the coding of them reproduces from `02-data/`. Several sources
still await a Wayback snapshot. `gate.py` reports these as incomplete rather than passing them, which
is the behavior a trustless gate is supposed to have.

## License

Data under CC BY 4.0, code under MIT. See `LICENSE`. Credit reads: Brian Nuckols / Public Source.
