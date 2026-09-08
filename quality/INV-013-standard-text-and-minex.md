# INV-013 — The standard's previews, and NIST's card for generator 3F

Date: 2026-09-08

## Numbering

This record takes 013, the next free investigation number after `INV-012`. The
reservation at 001 is explained in `REF-002`.

## Question

`REF-006`'s Open section forbids a reader or a writer before an investigation
reads the standard's text, and `MAN-minutia.v1` freezes `"origin"` as
`"top-left"` and `"angle_direction"` as `"iso-19794-2"` while saying of the
second, in the field itself, that "The label is frozen here; its meaning is not
settled by this manifest." Both are attributions to a document this repository
has not read. `D-3` is that gap.

The standard is sold rather than given away. So: **how much of `D-3` closes
from the pages that are given away, and what does NIST publish about the
generator this repository builds from?**

## What this record is, and what it is not

**This record did not read ISO/IEC 19794-2.** It read two sample PDFs that
carry the first pages of it, and it says so in every finding. Nothing below may
be cited as the standard; every quotation is a quotation from a sample, and the
sample's page range is stated so that a reader knows what was outside it.

**The two editions are kept apart.** The tools this repository builds implement
the 2005 edition — `REF-012` B fixes `iso-extract`'s output format as ISO/IEC
19794-2:2005 and the `FingerJetFXOSE` README names the same. A sentence quoted
from the 2011 sample is a fact about 2011. Whether the 2005 edition carries the
same sentence is `UNVERIFIED` here unless the 2005 sample carries it too, and
F-2 says which sentences those are.

## Method

### How a web source is recorded here

`REF-005` rejected pinning a third-party artefact by URL, because a URL names a
location and not an artefact, and it keeps third-party material out of the
tree. Both rules apply to a fetched PDF. So each source below is recorded by
**URL, retrieval date and the sha256 of the bytes retrieved**, the bytes are
not committed, and every quotation is taken from those bytes with
`pdftotext -layout`. A later reader who fetches a different digest knows the
source moved and that the quotations below describe what was there on the date
given.

### The sources

Retrieved 2026-09-08, between 07:30 and 07:35 UTC, with
`curl -sS -L -o <file> <url>`.

| id | what it is | bytes | pages | sha256 |
| --- | --- | --- | --- | --- |
| S1 | sample PDF of ISO/IEC 19794-2:2005 | 2 220 374 | 13 | `016be8f6cb8a74732ddc3208abf7372bce7ef2d6cb472a997214fb6a77b1bd59` |
| S2 | sample PDF of ISO/IEC 19794-2:2011 | 834 494 | 15 | `a872c2b59b2c78d57241edeb490e5fccdb12b651f7fc2c0d57cac58030c12d7d` |
| S3 | Ongoing MINEX report card, template generator 3F | 727 780 | 22 | `e8f257166c0e2aa67d86a6ccd02a314f8f25c6947d20894fb0ae612183d26a83` |

- S1 `https://cdn.standards.iteh.ai/samples/38746/58533e0af1c34affb5c5f9108aa1d570/ISO-IEC-19794-2-2005.pdf`
- S2 `https://cdn.standards.iteh.ai/samples/50864/e8be1ecb9a0f4ad0be2aaad7ae55d818/ISO-IEC-19794-2-2011.pdf`
- S3 `https://pages.nist.gov/minex/results/reportcards/pdf/ominex/3F_generator_report.pdf`

### Two things about the sources that the reader is owed

**S1 and S2 are a reseller's samples, not the publisher's own preview.** Both
carry ISO/IEC's page layout, running headers, page numbering and copyright
notice, and both are overprinted on every page with `iTeh STANDARD PREVIEW
(standards.iteh.ai)` and a link into that reseller's catalogue. The publisher's
own site was tried: `https://www.iso.org/standard/38746.html` and the Online
Browsing Platform viewer both returned **HTTP 403** to the same `curl` on the
same date. So what is quoted below is a third party's copy of the publisher's
first pages, and this record cannot say it is the publisher's own preview. It
can say what bytes it read and what digest they had.

**Nothing was carried into this record from the brief that commissioned it.**
The brief supplied leads and stated, as its own most important instruction,
that its quotations were a summarising model's output from a chat container and
were not to be reused. Each URL was located again by a web search performed
here, each file was fetched here, and every sentence quoted below was taken
from the bytes whose digest is in the table. Where what was found differs from
what the brief expected — twice, in F-1 and in the paragraph above — the
finding is reported and not reconciled.

### How quotations are cited

Each quotation names its source, the page number **printed on the page**, and
the index of that page within the PDF, because the two differ: a sample carries
front matter that the standard numbers in roman and the PDF numbers from 1.

## F-1 — the 2005 sample

### What it contains

S1 is 13 PDF pages of a document the Contents ends at page 40:

| PDF pages | what |
| --- | --- |
| 1 | cover: `INTERNATIONAL STANDARD`, `ISO/IEC 19794-2`, `First edition 2005-09-15`, `Reference number ISO/IEC 19794-2:2005(E)` |
| 2 | the PDF disclaimer and copyright page, printed `ii` |
| 3-4 | Contents, printed `iii` and `iv` |
| 5 | Foreword, printed `v` |
| 6 | Introduction, printed `vi` |
| 7-13 | printed pages **1 to 7** |

So the sample carries clauses 1 to 6.3.4 and stops inside clause 6.3.

### The coordinate system — stated in full

Printed page 6, PDF page 12, clause **6.3.1 Coordinate System**, quoted whole:

    The coordinate system used to express the minutiae of a fingerprint shall
    be a Cartesian coordinate system. Points shall be represented by their X
    and Y coordinates. The origin of the coordinate system shall be the upper
    left corner of the original image with X increasing to the right and Y
    increasing downward. Note that this is in agreement with most imaging and
    image processing use. When viewed on the finger, X increases from right to
    left as shown in Figure 1. All X and Y values are non-negative.

    The X and Y coordinates of the minutiae shall be in pixel units, with the
    spatial resolution of a pixel given in the "X Resolution" and "Y
    Resolution" fields of the format. X and Y resolutions are stated
    separately.

`MAN-minutia.v1` freezes `"origin"` as `"top-left"`. The sentence above is the
first text in this repository's possession that says the same thing in the
standard's own words. What follows from that is a decision and is not taken
here.

### The minutia types — named, and not coded

Printed page 5, PDF page 11, clause **6.2 Minutia Type**:

    Each minutia has a "type" associated with it. There are two major types of
    minutiae: a "ridge skeleton end point" and a "ridge skeleton bifurcation
    point" or split point. There are other types of "points of interest" in
    the friction ridges that occur much less frequently and are more difficult
    to define precisely. More complex types of minutiae are usually a
    combination of the basic types defined above. Some points are neither a
    ridge ending nor a bifurcation. This standard therefore defines
    additionally a type named "other", which shall be used in such a way that
    the matching conditions specified in 6.6 apply. The "other" minutiae type
    shall not be used for minutiae that are ridge endings or ridge
    bifurcations.

    Therefore, the following types are distinguished:

         - ridge ending (also identifiable as a valley skeleton bifurcation
           point);

         - ridge bifurcation

         - other.

and, continuing on printed page 6:

    A ridge ending may -- alternatively -- be regarded as a valley bifurcation
    depending on the method to determine its position (see below). The format
    type of the biometric information template indicates the use of ridge
    endings or valley bifurcations.

**The numeric codes are not in the sample.** Three types are named; no clause
in printed pages 1 to 7 assigns them values. The Contents places `7.4.2 Finger
Minutiae Data` at page 14, outside the sample. So the sample does not confirm
that a ridge ending is 1 and a bifurcation 2, which is what `INV-012` F-6 read
out of the library's own `matchData.h`.

### The angle — absent, and not in the way the brief expected

**The brief expected the angle clause's heading to be present with its text
missing. It is not: neither the heading nor the text is on any page of the
sample.** The last clause the sample reaches is 6.3.4, on printed page 7, and
it ends mid-subject with "(see Figure 4)"; Figure 4 is on page 8 and page 8 is
not in the sample.

What the sample does carry about the angle is three things, and they are worth
separating.

- **Contents lines only.** Printed page iii, PDF page 3, lists
  `6.4 Minutia Direction ... 8`, `6.4.1 Angle Conventions ... 8`,
  `6.4.2 Minutia Direction of a Ridge Ending (encoded as Valley Skeleton
  Bifurcation Point) ... 9`, `6.4.3 ... 9` and
  `6.4.4 Minutia Direction of a Ridge Skeleton End Point ... 9`. Every one of
  those pages is outside the sample.
- **A statement that direction matters, with no definition.** Printed page 5,
  clause 6.1: "Describing a fingerprint in terms of the location and direction
  of these ridge endings and bifurcations provides sufficient information to
  reliably determine whether two fingerprint records are from the same
  finger." And clause 6.3, printed page 6: "If other methods are applied, they
  should approximate the skeleton method, i.e. location and angle of the
  minutia should be equivalent to the skeleton method."
- **Two figures that draw an angle.** Printed page 7 carries Figure 2,
  captioned "Location and direction of a ridge ending (encoded as valley
  skeleton bifurcation point)", and Figure 3, "Location and direction of a
  ridge bifurcation (encoded as ridge skeleton bifurcation point)". Each
  shows a marked point, a horizontal reference line drawn to the right of it,
  an arrowhead-terminated ray, and `θ` between them. F-3 says what can and
  cannot be taken from that.

The clause that places the ridge-ending minutia is in the sample, printed page
7, and defines a location and not a direction:

    The minutia for a ridge ending shall be defined as the point of forking of
    the medial skeleton of the valley area immediately in front of the ridge
    ending. If the valley area were thinned down to a single-pixel-wide
    skeleton, the point where the three legs intersect is the location of the
    minutia. In simpler terms, the point where the valley Y's, or
    (equivalently) where the three legs of the thinned valley area intersect
    (see Figure 2).

## F-2 — the 2011 sample

This finding is about the **2011** edition. The tools in this image implement
2005. Nothing here is transferred to 2005 except where it is said in terms that
the 2005 sample carries the same sentence.

### What it contains

S2 is 15 PDF pages of a document the Contents ends at page 93:

| PDF pages | what |
| --- | --- |
| 1 | cover: `Second edition 2011-12-15`, `Reference number ISO/IEC 19794-2:2011(E)` |
| 2 | the copyright page, printed `ii` |
| 3-5 | Contents, printed `iii` to `v` |
| 6 | Foreword, printed `vi` |
| 7 | Introduction, printed `vii` |
| 8 | a page carrying only the reseller's overprint |
| 9-15 | printed pages **1 to 7** |

Seven printed pages again, but the 2011 edition renumbered its clauses, so the
same seven pages reach further into the subject: the whole of clause 6,
Minutiae extraction, ends on printed page 7 with 6.7.

### The coordinate system, which is the same sentence

Printed page 4, PDF page 12, clause **6.4.2 Coordinate system**: the first
paragraph is word for word the 6.3.1 paragraph quoted in F-1 — "shall be the
upper left corner of the original image with X increasing to the right and Y
increasing downward". The paragraph that follows it differs:

    For the finger minutiae record format, clause 7.2, the X and Y coordinates
    of the minutiae shall be measured in pixel units, with the spatial
    sampling rate of a pixel given in the "X Spatial sampling rate" and "Y
    Spatial sampling rate" fields of the record header. The spatial sampling
    rates are stated separately as described in clauses 8.4.11 and 8.4.12.

**This is the one place where a 2011 sentence may be carried to 2005**, because
the 2005 sample carries the same sentence for the origin and the axes. The
renamed fields are 2011's and are not.

### The angle convention, which 2005's sample does not carry

Printed page 6, PDF page 14, clause **6.5.1 Angle conventions**, quoted whole:

    The minutia angle is measured increasing counter-clockwise starting from
    the horizontal axis to the right.

    In the finger minutiae record format, the angle of a minutia is scaled to
    fit the granularity of 1.40625 (360/256) degrees per least significant bit
    as described in clause 8.4.19.1.4.

    The angle coding for the on-card biometric comparison formats is scaled to
    fit the granularity of 5.625 (360/64) degrees per least significant bit as
    described in clause 9.2.5.

and **6.5.2 Minutia direction of a ridge ending (encoded as valley skeleton
bifurcation point)**, printed page 6:

    A ridge ending (encoded as valley skeleton bifurcation point) has three
    arms of valleys meeting in one point. Two valleys enclosing the ridge
    ending line encompass an acute angle. The direction of a valley
    bifurcation is defined by the mean direction of their tangents and is
    measured as the angle the tangent of the ending ridge forms with the
    horizontal axis to the right (see Figure 2).

and **6.5.3**, printed page 7:

    A ridge bifurcation (encoded as ridge skeleton bifurcation point) has
    three arms of ridges meeting in one point. Two ridges enclosing the ending
    valley encompass an acute angle. The direction of a valley bifurcation is
    defined by the mean direction of their tangents and is measured as the
    angle the tangent of the ending valley forms with the horizontal axis to
    the right (see Figure 3).

and **6.5.4**, printed page 7:

    The direction of a ridge skeleton endpoint is defined as the angle that
    the tangent to the ending ridge encompasses with the horizontal axis to
    the right (see Figure 4).

The 2005 edition's counterpart clauses are 6.4.1 to 6.4.4 on pages 8 and 9,
which F-1 records as absent from S1. **Whether the 2005 edition says any of
this is `UNVERIFIED`.** The granularity in particular: 1.40625 = 360/256 is the
number `INV-003` F-1 derived from the library's source and `INV-012` F-7
observed in the templates, and 6.5.1 states it — for 2011.

### Two more clauses the 2011 sample reaches

**6.3.1 General**, printed page 3, names the same three types as 2005's 6.2 —
"ridge ending", "ridge bifurcation", "other" — with the wording modernised and,
again, **no numeric codes**; the Contents places Table 3, "Finger minutiae
representation format", at page 12, outside the sample.

**6.7 Encoding of multibyte quantities**, printed page 7:

    All multibyte quantities are represented in Big-Endian format; that is,
    the more significant bytes of any multibyte quantity are stored at lower
    addresses in memory than (and are transmitted before) less significant
    bytes. All numeric values are fixed-length integer quantities, and are
    unsigned quantities.

`INV-011` F-2 measured big-endian in the templates this repository produces.
The 2005 sample does not carry this clause: the Contents places 2005's own
`6.7 Encoding of multibyte quantities` at page 10.

## F-3 — what remains undefined by what was read

### What is closed

| question | closed by | edition |
| --- | --- | --- |
| the origin of the coordinate system | 2005 6.3.1 and 2011 6.4.2, the same sentence in both: the upper left corner of the original image | **both** |
| the direction of the axes | the same sentence: X increasing to the right, Y increasing downward | **both** |
| the unit of a coordinate | 2005 6.3.1: pixel units, resolution given in the format's own fields | **both**, with 2011 renaming the fields |
| the names of the minutia types | 2005 6.2, 2011 6.3.1: ridge ending, ridge bifurcation, other | **both** |
| where the angle's zero is, and which way it increases | 2011 6.5.1: counter-clockwise from the horizontal axis to the right | **2011 only** |
| the angle's granularity in the record format | 2011 6.5.1: 1.40625 = 360/256 degrees per least significant bit | **2011 only** |
| the byte order | 2011 6.7: Big-Endian | **2011 only** |

`MAN-minutia.v1`'s `"origin": "top-left"` is the first of these. It is a
label this repository chose; the sentence quoted in F-1 is the standard's own,
in an edition the tools implement, and it says the same. That is a fact about
two texts and not an instruction to change a status.

### What is not closed, and it is the reason this record exists

**A tangent has two senses, and neither clause picks one.** 2011 6.5.2 defines
a ridge ending's direction as "the angle the tangent of the ending ridge forms
with the horizontal axis to the right", and 6.5.4 a ridge skeleton endpoint's
as "the angle that the tangent to the ending ridge encompasses with the
horizontal axis to the right". A tangent is a line. A line makes two angles
with the horizontal axis to the right, and they differ by 180 degrees. **No
sentence quoted in F-1 or F-2 says which of the two is meant** — not whether
the ray runs from the minutia into the ridge that ends, or from the minutia
away from it.

That is exactly the 180 degrees `INV-012` measured. `INV-012` F-2 quotes
`xytreps.c` saying `mindtct`'s `.xyt` direction points "out and away from the
ridge ending or bifurcation valley", and measured 178.624 degrees against a
constructed direction that runs into the surviving line; F-3 there measured
`iso-extract` at 0.117 degrees against the same constructed direction. The two
tools sit on the two sides of the ambiguity above, and the text read here does
not adjudicate between them.

### The figures draw a sense; that is not the same as the text stating one

Figure 2 is present in both samples — 2005 printed page 7, 2011 printed page 5
— and the two drawings are the same drawing. Rendered from the fetched bytes at
300 dpi with `pdftoppm`, it shows: five grey bands running from lower left to
upper right, labelled `ridge`, separated by white bands labelled `valley`; a
marked point in a white band at the place where two white bands merge; a grey
band whose lower-left tip begins immediately up and to the right of that point;
a horizontal reference line from the point to the right; and a ray from the
point, arrowhead at its far end, running up and to the right **along the grey
band that begins at the point**, with `θ` marked between the ray and the
horizontal line.

So the drawing does pick a sense: its ray runs from the minutia **into** the
ridge that ends, not away from it.

**This record does not treat that as closing the question**, for three reasons
which are separate and each sufficient. It is a drawing and not a sentence, and
the sentence is what F-3 is about. Whether a figure is normative for the
direction, or illustrative of a clause that carries the requirement, is
something the previewed pages do not say. And a sense read off a raster
rendering of one drawing is an inference from an image, which is the kind of
step this repository asks a measurement or a quotation to replace. The
observation is recorded because it is a fact about the bytes; the conclusion is
not drawn.

### The other things neither sample settles

- **The numeric type codes.** Both samples name three types; neither assigns a
  value. `INV-012` F-6 read 0, 1 and 2 out of the library's `matchData.h`,
  which is an implementation.
- **The record layout.** No offset, field width or header field of the record
  format appears in either sample: 2005's clause 7 begins on page 11 and
  2011's clause 8 on page 9, both outside. `INV-011` F-2 derived the layout
  from `serializeFpData.h` instead, and that is where it still stands.
- **Everything after printed page 7.** 2005 runs to page 40 and 2011 to 93.
  In particular the 2011 Contents lists **Annex F (normative), "Detailed
  description of finger minutiae location, direction, and type", page 71** —
  twenty-two pages on precisely the subject of this record, unread. Any
  sentence quoted above could be qualified there, and this record cannot say
  it is not.
- **`D-3` is not closed.** The part of it that `MAN-minutia.v1`'s `origin`
  rests on is now backed by the standard's own words. The part its
  `angle_direction` rests on — what the label `iso-19794-2` means as a
  physical direction — is not: the 2005 sample says nothing about the angle at
  all, and the 2011 sample says everything except which way along the tangent.
  A reader who takes `D-4` as settled by `INV-012` and `D-3` as settled by this
  record has taken from the two of them something neither contains.

## F-4 — NIST's Ongoing MINEX report card for template generator 3F

S3, 22 PDF pages, titled on its cover `Ongoing MINEX Report Card` /
`Template Generator 3F`, with `Last Updated: October 9, 2015` on the cover and
in the footer of every page.

### What the card says it is

PDF page 2, a note before the body:

    Note: This report card is for MINEX III compliance criteria only. Ongoing
    MINEX never released report cards, but instead published two tables: one
    for all participants and one for compliant participants.

    This report card shows results for an algorithm originally submitted to
    Ongoing MINEX being re-evaluated based on the MINEX III compliance
    criteria. If this report says that an algorithm has failed, it means that
    the algorithm did not meet the MINEX III compliance criteria and will not
    be included on the MINEX III Compliant Submissions list. For historical
    records, the old Ongoing MINEX Compliant Submissions list is still
    available.

    Ongoing MINEX tested for compliance of NIST Special Publication 800-76-1,
    which was withdrawn July 2013. MINEX III tested for compliance of NIST
    Special Publication 800-76-2, and added additional semantic checks for
    compliance of ANSI/INCITS 378-2004.

### The participant, the dates and the artefact

Printed page 1, PDF page 3:

    Participant Details

    Company: Digitalpersona Inc.
    Date Submitted: 6/16/2009
    Date Validated: 6/21/2011
    Date Completed: 7/21/2011

    Library     Size (bytes)   MD5 Checksum
    minex.dll   107008         f494da515f200b40afc98cb05a99827a

    NOTE: NIST plans to decertify Windows-based libraries in MINEX III.

### The determination, and the reason given for it

Printed page 1, PDF page 3, whole:

    Compliance Test Results

    The following presents PIV compliance results per the criteria detailed in
    NIST Special Publication 800-76-2: Biometric Specifications for Personal
    Identity Verification.

    PIV: FAIL

    - All certified matchers must be able to match templates from this
      template generator with an FNMR_FMR(0.01) <= 0.01 using two fingers
      (4.5.2.2-3).
    - Minutia density plots derived from generated templates do not exhibit a
      periodic, grid-like, or geometric structure without reasonable
      justification. (See Section 3.4)

In the page as rendered, the first bullet ends with a green check mark and the
second with a red cross; the text extraction does not carry either glyph, so
the marks are read from the page image and the criteria from the text. **The
determination is FAIL, and of the two criteria the accuracy one is marked met
and the minutia-placement one is not.**

Printed page 11, PDF page 13, section 3.4, which the second bullet points to:

    Minutia density plots show where the template generator tends to find
    minutia in fingerprint images. They are 2D histograms where the degree of
    illumination at an (x, y) coordinate indicates how frequently the software
    located a minutiae point at that location. The purpose of showing minutia
    density plots is to determine whether the template generator exhibits
    regional preference when locating minutia.

    NIST has determined that this template generator produces minutia
    exhibiting a periodic structure. This is an indication that the template
    generator is departing from the minutia placement requirements of INCITS
    378, clause 5. The expected pattern is a locally uniform distribution, and
    the appearance of local structure indicates systematic non-conformance
    with the standard. Given such behavior negatively affects
    interoperability[8], developers are asked to determine the cause of such
    behavior - for example, as an artifact of a tilebased image processing
    algorithms applied to the input fingerprint image and to resubmit
    corrected algorithms.

The four plots of Figure 9 on that page are captioned "Minutia density plot for
251 874 368x368 right indexes", the same for left, and two more for
"123 120 500x500" right and left.

### The format the card names, and the one it does not

Over the whole 22 pages, extracted as text: `378` occurs four times — the note
above, section 3.4's "INCITS 378, clause 5", one number inside a results table,
and a reference titled "Performance and Interoperability of the INCITS 378
Fingerprint Template"; `800-76` occurs four times. **The string `19794` does not
occur anywhere in the card, and neither does `FingerJet`.** `Digitalpersona`
occurs once, in the line quoted above.

## F-5 — the `FingerJetFXOSE` README's claim, beside F-4

`INV-008` pinned the top-level `README.txt` at blob
`6955065d66f6ba86c9f5fc43c07b5e045dc17626`. Quoted from that blob with its own
line breaks, lines 58 to 64. The rule of hyphens is 92 characters in the file
and is shortened in both blocks below; lines 60, 61 and 91 end in a space that
is not shown, and no other quoted line does:

    Performance and Recognition Accuracy
    --------------------------------------------------------------------
    The initial contribution by DigitalPersona, Inc. (www.digitalpersona.com)
    has met the required PIV performance thresholds for fingerprint minutiae generation
    in MINEX test (SDK 3F).

    See http://www.nist.gov/itl/iad/ig/ominex_test-results.cfm for details.

and lines 89 to 92:

    Standards and Compatibility
    --------------------------------------------------------------------
    The output from FingerJetFX OSE is formatted according to the ANSI INSITS 378-2004
    or ISO/IEC 19794-2:2005 specifications for fingerprint minutiae data.

**Where the two agree.** Both are about the same submission: the README names
`SDK 3F` and the card is the report card for template generator 3F, and both
name DigitalPersona. The README's claim is about **performance thresholds**,
and the card's accuracy criterion — matchers matching this generator's
templates at FNMR ≤ 0.01 — is the one it marks met.

**Where they do not.** The card's determination is `PIV: FAIL`. The README says
nothing about a determination, and a reader who takes "has met the required PIV
performance thresholds" as meaning the generator is PIV compliant is reading
something the card contradicts. The card's own second page says why the two can
both be true: Ongoing MINEX published a compliant-participants table rather than
report cards, and this card is a **later re-evaluation under MINEX III
criteria**, against `SP 800-76-2` rather than the withdrawn `SP 800-76-1`, with
semantic checks the earlier programme did not apply.

**The link in the README no longer names the page it named.** Fetched
2026-09-08, `http://www.nist.gov/itl/iad/ig/ominex_test-results.cfm` returns
HTTP 200 after redirection to
`https://www.nist.gov/itl/iad/btg/ongoing-minex-evaluation-results`. The URL in
the README resolves; where it lands is not the file this record read.

**This record decides nothing about it.** `INV-003` and `INV-008` both rest on
this README in places. `REF-012` B, which chose the ISO output format, does
not: it rests on `INV-003` F-1 and S-3 and on `REF-006` decisions 1, 2 and 3,
and the README's format sentence is not among its grounds. Whether anything
that does rest on the README needs revisiting is a refinement's question and
not this record's.

## F-6 — four gaps between the report card and this repository

Each is stated rather than left for a reader to notice.

**One — the format.** The card's criteria are `SP 800-76-2`'s, its semantic
checks are "for compliance of ANSI/INCITS 378-2004", and the reason it gives
for the failure is a departure from "the minutia placement requirements of
INCITS 378, clause 5". `REF-012` B fixes this repository's output as ISO/IEC
19794-2:2005 and `iso-extract` passes `FJFX_FMD_ISO_19794_2_2005`; the string
`19794` does not appear in the card. Two of `INV-003` S-1's serializers exist
precisely because the two formats differ: the ANSI one rescales the angle by
180/256 and the ISO one does not.

**Two — the artefact, and eleven years of it.** The card names one file,
`minex.dll`, 107 008 bytes, MD5 `f494da515f200b40afc98cb05a99827a`, submitted
2009-06-16. This repository builds `libFJFX.so` from source at commit
`1726ba08bf7f2137d2f861ac1ae124d5cd355eee`, a merge dated 2026-01-15 in a
history of 67 commits whose first is dated 2011-11-14, and `MAN-tools.v2`
records that library's sha256 as
`ba453c674a82f4e9dd74985a4840285a07e5681defcde790d32473a7f4de1bf1`. The tree at
that commit is not one company's: `INV-008` F-5 records that of the 98 source
files carrying the licence header, **15 name `HID Global, Inc.` at line 4 where
the other 83 name `DigitalPersona, Inc.`**, and two of those 15 are
`serializeFpData.h` and `FeatureExtraction.h` — the files `INV-003`, `INV-011`
and `INV-012` quote for the angle, the coordinates and the resolution. The same
tree carries `FingerJetFXOSE/libMINEX`, whose `include/minex.h` opens

    Minex 3 Wrapper for FingerJetFX OSE -- Fingerprint Feature Extractor, Open Source Edition

    Copyright (c) 2019 by HID Global, Inc. All rights reserved.

and which the builder stage compiles as `libFJFX_MINEX.so`; `REF-011`
decision 2 sends only `libFJFX.so` into the runtime image, so this repository
does not use it.

**Three — a profile's criteria, not correctness.** The card reports "PIV
compliance results per the criteria detailed in NIST Special Publication
800-76-2: Biometric Specifications for Personal Identity Verification". PIV is
a credentialing profile with its own thresholds. A `FAIL` under it is a
statement about those criteria; it is not a statement that the extractor's
output is wrong, and a `PASS` would not have been a statement that it is right.
`REF-007` decision 5 already adopts these tools as reproducible baselines
rather than as correct ones, and nothing here changes that either way.

**Four — a submitted product, not the open source contribution.** The card's
subject is a Windows DLL a company submitted for evaluation. What this
repository builds is source from a public repository, on Linux, at a commit
made long after. The README frames the relation itself — "The initial
contribution by DigitalPersona, Inc. … has met…" — and neither the card nor
this record establishes that the code in the pinned commit behaves as the card
describes.

## Reproducing this

Every command was run on 2026-09-08 against the tree at `5953036`. `$SP` is a
scratch directory outside the tree. Nothing fetched was written into the
repository.

**W — how the three URLs were found.** By web search performed here, for the
2005 sample, the 2011 sample and a MINEX report card naming template generator
3F. The brief that commissioned this record supplied the same three leads and
its own quotations; the leads were re-derived and the quotations were not used.

**F — the fetch and the digest.**

    curl -sS -L --max-time 90 -o iso2005.pdf \
      https://cdn.standards.iteh.ai/samples/38746/58533e0af1c34affb5c5f9108aa1d570/ISO-IEC-19794-2-2005.pdf
    curl -sS -L --max-time 90 -o iso2011.pdf \
      https://cdn.standards.iteh.ai/samples/50864/e8be1ecb9a0f4ad0be2aaad7ae55d818/ISO-IEC-19794-2-2011.pdf
    curl -sS -L --max-time 90 -o minex3f.pdf \
      https://pages.nist.gov/minex/results/reportcards/pdf/ominex/3F_generator_report.pdf
    sha256sum iso2005.pdf iso2011.pdf minex3f.pdf
      016be8f6cb8a74732ddc3208abf7372bce7ef2d6cb472a997214fb6a77b1bd59  iso2005.pdf
      a872c2b59b2c78d57241edeb490e5fccdb12b651f7fc2c0d57cac58030c12d7d  iso2011.pdf
      e8f257166c0e2aa67d86a6ccd02a314f8f25c6947d20894fb0ae612183d26a83  minex3f.pdf

All three returned HTTP 200 with `content-type: application/pdf`, of 2 220 374,
834 494 and 727 780 bytes. The publisher's own site was tried and refused:

    curl -sS -o /dev/null -w "%{http_code}" -L https://www.iso.org/standard/38746.html
      403
    curl -sS -o /dev/null -w "%{http_code}" -L \
      "https://www.iso.org/obp/ui/en/#iso:std:iso-iec:19794:-2:ed-1:v1:en"
      403

**T — every quotation.** Taken from those bytes with

    pdftotext -f <first> -l <last> -layout <file> -

using the PDF page indexes this record gives beside each printed page number.
The counts in F-4's last paragraph are `grep -c -i` over
`pdftotext -layout minex3f.pdf card.txt`, which is the whole 22 pages.

**R — the figure.** Rendered from the same bytes and cropped, with no
adjustment other than scale:

    pdftoppm -f 13 -l 13 -r 300 -png iso2011.pdf fig
    pdftoppm -f 13 -l 13 -r 300 -png iso2005.pdf fig05

PDF page 13 is printed page 5 in the 2011 sample and printed page 7 in the 2005
sample; Figure 2 is on both.

**B — the README.** From the clone the `Dockerfile` pins, by the blob id
`INV-008` recorded:

    docker build --target fjfx-builder -t dactyloscopy:fjfx-audit .
    docker run --rm dactyloscopy:fjfx-audit \
      git -C /w/src cat-file blob 6955065d66f6ba86c9f5fc43c07b5e045dc17626

and the line numbers by piping that through `sed -n` and `cat -n`. The
`libMINEX` header and the commit's authorship and dates come from the same
clone, with `git cat-file blob HEAD:FingerJetFXOSE/libMINEX/include/minex.h`,
`git log -1 --format=...`, `git rev-list --count HEAD` and
`git log --format=%aI | tail -1`.

**L — the README's link.**

    curl -sS -o /dev/null -w "%{http_code} %{url_effective}" -L \
      http://www.nist.gov/itl/iad/ig/ominex_test-results.cfm
      200 https://www.nist.gov/itl/iad/btg/ongoing-minex-evaluation-results

## What was left unchecked

- **Whether the standard should be bought.** Not a question for an
  investigation. What this record supplies is how much the free pages settle,
  and F-3 says which part they do not.
- **Whether a reader or a writer may now be written.** `REF-006`'s Open section
  is what forbids it, and only a refinement can change that. Nothing here is
  permission.
- **Whether this repository's extractor output shows the structure section 3.4
  describes.** That is a measurement over images, and it belongs to the study,
  not to a record of what NIST published. Recording that NIST determined a
  periodic structure in one 2009 Windows library's output over 251 874 and
  123 120 sequestered images is not evidence about `libFJFX.so` built here, and
  this record must not be read as if it were. Nothing was extracted, plotted or
  counted for this record.
- **Anything about the FVC2002 corpus.** No corpus image was opened and no
  manifest of one was read.
- **Everything in both samples after printed page 7**, which is pages 8 to 40
  of the 2005 edition and 8 to 93 of the 2011 one, including the 2011 Annex F
  named in F-3.
- **Whether the samples are faithful.** They are a reseller's PDFs. Their
  content was not compared against the publisher's, which returned 403, or
  against any other copy.
- **Whether NIST publishes anything else about generator 3F.** One report card
  was located and fetched. An index page at
  `https://pages.nist.gov/minex/results/ominex.html` was tried and returned
  404; the two participant tables and the two compliant-submissions lists the
  card links were not fetched, and no MINEX III card was searched for.
- **The documents the card rests on.** `ANSI/INCITS 378-2004` and
  `NIST SP 800-76-2` are named by the card and were not read here. So "the
  minutia placement requirements of INCITS 378, clause 5" is quoted, not
  checked.
- **Whether `libFJFX_MINEX.so` was ever submitted or evaluated.** F-6 records
  that the pinned tree carries a 2019 MINEX 3 wrapper and that this repository
  does not ship it. Nothing was looked for about its evaluation.
- **`mindtct` and the NBIS side.** Neither the standard's previews nor the
  card says anything about it, and nothing here was read with it in mind.
