# Methodology

## The question

Does the Pittsburgh Water board deliberate in public, or does it ratify in public what was decided
elsewhere? The question is falsifiable. A board that deliberates leaves a record of dissent, of
questions, of decisions changed by what was said in the room. A board that ratifies leaves a record
of unanimous consent moving quickly past items no one asks about. The minutes hold whichever record
is true.

## The unit and the source of record

The unit of analysis is the individual resolution. The source of record is the official meeting
minutes the authority publishes at pgh2o.com; every figure traces to them, and no figure rests on a
secondary account of what a meeting contained. The window is 24 consecutive regular board meetings,
October 27, 2023 through September 26, 2025.

## The four variables

Each resolution, and each meeting, was coded on four variables chosen because each one distinguishes
deliberation from ratification.

1. **Vote outcome.** Unanimous, split, or carrying an abstention, with the abstaining member named.
   A split vote is the clearest single mark of a board that decides in the room, and Pittsburgh Water
   recorded none across the two years.
2. **Board questions.** The count of questions each member asked, attributed by name. Questions are
   how a board tests what staff brings it. Counted per meeting, the board asked 131; counted against
   specific resolutions, 96. The two counts and their definitions are reconciled in `FACT-CHECK.md`.
3. **Discussion quality.** Whether an item drew recorded discussion, and whether any decision was
   visibly changed by it. Across 228 resolutions, the minutes record no decision altered on the floor.
4. **Public participation.** The number of residents who spoke, per meeting. Ten spoke in two years,
   across five of the 24 meetings.

## The unanimity-rate denominator

The board's unanimity rate "when all members voted" is 223 unanimous divided by 223, or 100%. The
five abstentions are excluded from the denominator because each was the chair recusing himself for a
conflict of interest, not a member dissenting. Excluding recusals isolates the question that matters:
when the board actually voted, did anyone ever break from consensus? The answer is no. The peer rate,
by contrast, counts all 29 sampled votes in its denominator, because the peer boards' abstentions
were part of genuine division rather than routine recusal. That asymmetry is deliberate and is stated
so a reader can weigh it.

## The peer design

A single board's unanimity means little without a baseline. To build one, a random-number generator
selected three meetings from each of two comparable water boards, the Niagara Falls Water Board in
New York and the North Harris County Regional Water Authority in Texas, over the same 24-month
window. Every vote in those six meetings was coded on the same four variables. The peers were chosen
as governance analogues: appointed boards overseeing mid-size public water utilities. Random meeting
selection guards against cherry-picking the peers' most contentious sessions. Six meetings produced
29 votes, 20 of them unanimous.

## Benchmarks outside the water sector

Two reference points frame the finding. The Office of the Comptroller of the Currency's guidance on
board effectiveness holds that approval rates approaching 99 to 100% can indicate a board has stopped
providing active oversight. A Kennesaw State analysis of 848 Enron board votes found a 99.5% unanimity
rate, and cautioned that even a board that asks questions can still function as a rubber stamp. Both
documents are archived and hashed in this repository.

## Limits

The minutes are a summary, not a transcript; a question paraphrased in the minutes counts the same as
one quoted at length. The coding was done by the reporter, and the reproduction harness checks the
arithmetic on that coding, not the judgment calls inside it. The peer sample is small by design, three
meetings per board, and is a comparison rather than a population estimate. None of these limits is
hidden inside a smoothed number; each figure that carries a seam is reconciled in `FACT-CHECK.md`.
