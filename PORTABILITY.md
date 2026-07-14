# Portability — running this instrument on any board

Pittsburgh has dozens of appointed boards that spend public money with almost no elected oversight:
the airport authority, the transit authority, the redevelopment authority, the sanitary authority,
the housing authority, the sports and exhibition authority, the jail oversight board. Public Source's
Board Explorer already tracks who sits on them and when they meet. What it does not track is how they
vote. This instrument fills that gap, and it was built to be re-run.

## The instrument in five steps

1. **Pick a board and pull its minutes.** Any board that publishes meeting minutes qualifies. The
   minutes are the source of record; archive and hash each one before coding a figure from it, using
   the pattern in `03-harness/capture.py` and `01-sources-archive/sources.json`.

2. **Code every resolution on the four variables.** Vote outcome, board questions (attributed by
   name), discussion quality, public participation. The codebook is in `METHODOLOGY.md`. One row per
   meeting in a `meetings.csv`, one row per questioned resolution in a `questions_by_resolution.csv`,
   matching the schemas in `02-data/`.

3. **Sample two or three peer boards.** Use a random-number generator to select three meetings from
   each comparable board over the same window, and code them the same way. Random selection is what
   keeps the comparison honest.

4. **Run the harness.** Point `build.py` at the new `02-data/` and it recomputes the board's unanimity
   rate, question distribution, spending, and public-participation figures, and holds them against the
   values you expect. `verify.py` confirms the sources still hash clean. `gate.py` refuses to call it
   publishable until every source is captured and cited.

5. **Publish the scorecard, then watch what the board does next.** The Pittsburgh Water follow-up
   showed that a board can change its behavior once its deliberation record is public. That second
   measurement, taken at the first meeting after publication, is part of the method, not an accident.

## Why it is a franchise, not a one-off

The four variables are board-agnostic. The harness is data-agnostic; it reads CSVs and checks
arithmetic. The peer design generalizes to any sector with comparable public bodies. A vote-and-
deliberation layer over Board Explorer would be re-runnable every quarter, across every board it
already tracks, and each run would carry the same reproducible archive this one does. The Pittsburgh
Water case is the proof that the instrument finds something real and that the finding can move an
institution.
