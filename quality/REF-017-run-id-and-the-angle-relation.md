# REF-017 — The run id names its tools, and `D-4` is closed

Date: 2026-09-22
Rests on: `quality/INV-018-second-extractor-through-the-matcher.md`, and for
`D-4` on `quality/INV-012-angle-conventions.md` and
`quality/INV-014-extractor-difference.md` as `INV-018` cites them. Amends
`REF-016` decision 5 and adds to its decision 2. Closes `D-4`, issue #8.
Every factual claim below is a reference to a fact of one of those
investigations, by its identifier. This refinement measures nothing and
states no fact of its own.

## Numbering

This refinement takes 017, the next free number after `REF-016`. The gaps at
001 and 004 are explained in `REF-002` and `REF-006`.

## Why this refinement exists

`REF-016` decision 5 named a run `<YYYYMMDD>-<subset>-<revision>` and said
that two runs on one day, one subset and one revision are the same run, since
nothing is drawn, reserving a counter suffix for the day that stopped being
true. `INV-018` made that day: it ran `mindtct` on `fvc2002/DB1_B` again at
the revision of its `iso-extract` run and lists both records, two runs on
one subset at one revision with different extractors and different numbers,
which `REF-016`'s form names the same. The counter the decision reserved
would number them without naming what differs.

`D-4`, how the ISO angle and the native `NBIS` angle are related, has been
open since `REF-006`. `INV-012` measured the relation on synthetic ridges,
`INV-014` on the corpus, and `INV-018` F-2 measured what the matcher does
under every reading of it. The facts reach a decision.

## Decision 1 — the run id carries the tool pair

**A run is named `<YYYYMMDD>-<subset>-<extractor>-<matcher>-<revision>`: the
date, the subset's manifest id with its slash replaced, the extractor and the
matcher by the names `MAN-tools.v2` gives them, and the revision's first
seven characters.** Two runs on one day, one subset, one tool pair and one
revision are the same run, since nothing is drawn; the counter suffix
`REF-016` reserved stays reserved for the day that stops being true.

The two records made under `REF-016`'s form,
`runs/20260922-fvc2002_DB1_B-a6fd834` and `runs/20260922-fvc2002_DB1_A-3030b18`,
keep their names: a record is never renamed, and each carries its tools in
`results.json`. A reader who needs the tool pair of a record reads it there,
which is where it was all along; the id is for telling records apart in a
listing and a commit subject, and from this decision on it does.

## Decision 2 — a refusal by the extractor is part of the observation

**`REF-016` decision 2's "whatever the tools say must accompany a score"
includes an extractor's refusal of an image, by image name and return code.**
`INV-018`'s Method carries it because an image the library refuses has an
empty template, every pair it is in scores 0, and a zero that is a refusal is
not a zero that is a verdict. `INV-011` F-3 saw the library return code 3 on a
synthetic image; `INV-014` and `INV-018` saw it refuse no corpus image, and
the field is empty in every record `INV-018` lists. The two records made
before it carry no such field, and are not amended.

## Decision 3 — `D-4` is closed: a half turn, which the matcher barely sees

**The angle `mindtct` writes to its `.xyt` and the angle `iso-extract` writes
to its ISO template increase the same way and differ by a half turn, and a
conversion between them applies `theta_xyt = theta_iso + 180` and nothing
else to the angle.** `INV-012` F-2 and F-3 measured the two against one
constructed direction: 178.624° and 0.117° over 648 points, concentrations
0.99825 and 0.99967. `INV-014` measured the difference between the two tools'
angles on corresponding corpus minutiae at 3.20° and 3.52° from a half turn
on the two `DB1` subsets. `INV-018` F-2 measured what the alternative
readings cost with the matcher: mirroring the angle's sense takes `eer@1`
from 0.0218 to 0.30 and the median genuine score from 98 to 30, so the sense
is not in doubt; and applying the half turn or not moves `eer@1` by 0.0018,
which is what a matcher scoring the angles between minutiae rather than their
absolute directions would show, though `INV-018` did not read `bozorth3`'s
source to say so.

So the relation is decided as measured, and the decision carries its own
weight: for the one matcher in the image, the turn barely reaches the number,
and the comparison `INV-018` F-3 makes does not rest on it. A matcher that
scores absolute direction would; that matcher does not exist here, and when
one does, `INV-018` F-2's reading is the measurement to repeat.

**What this does not decide.** `D-3`, what the label `iso-19794-2` means as
a physical direction, stays open: `INV-013` F-3 measured that the standard's
previews leave the sense of the tangent unstated. This decision relates two
tools' outputs to each other; it does not relate either to the standard.

## Rejected

- **A counter suffix, as `REF-016` reserved.** `-01` and `-02` tell two
  records apart and tell a reader nothing; the tool pair tells the reader
  what differs, which is the reason there are two.
- **Renaming the two existing records to the new form.** A record is never
  renamed: the `run:` commits that added them name them in their `Record:`
  trailers, and `INV-018` names them by their paths.
- **Closing `D-4` on `INV-012` alone.** `INV-012` measured synthetic ridges;
  `INV-014` measured the corpus; neither measured what a matcher does with
  the relation. The decision waited for `INV-018` so that its consequence
  was a number and not an argument.
- **Deciding the conversion's other parameters here.** The grid and the
  quality byte are choices of a conversion, not relations between
  conventions; `INV-018` F-2 measures what each costs, and a run record
  carries the values it used. A conversion that snaps to `mindtct`'s grid
  is a different conversion, recorded as such, not a wrong one.

## Open

- ⟨OPEN⟩ `D-3`, the standard's own sense of the angle.
- ⟨OPEN⟩ `D-1`, whether the `-m1` representation scores differently.
- ⟨OPEN⟩ Which part of `bozorth3`'s scoring keeps the absolute direction,
  giving the 0.0018 residual `INV-018` F-2 measured. It is not read from
  the source.
