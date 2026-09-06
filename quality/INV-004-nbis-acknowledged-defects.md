# INV-004 — What NBIS's own authors say is wrong with the code we run

Date: 2026-09-07

## Numbering

This record takes 004, the next free investigation number after `INV-003`. The
reservation at 001 is explained in `REF-002`.

## Question

`mindtct` and `bozorth3` are this repository's reference tools. Twice, reading
an external tool's source changed a decision here, and both times the finding
sat in a comment the authors wrote about their own code. That question had
never been asked of NBIS.

So: **in the code this repository actually executes, what do NBIS's own authors
say is wrong, limited, or a workaround?** And, for each thing they say, does it
touch what we do — extraction of minutiae from a 500 dpi greyscale PNG, and
matching of two `.xyt` files?

Two further questions were asked of the source because the record has gaps
where the answers would go:

- how `mindtct`'s `.xyt` quality and its `.min` reliability are each computed
  (`INV-002` F-10, F-12);
- whether `bozorth3`'s score has a stated bound, scale or saturation point
  (`INV-002` F-11's neighbourhood, and the score column of any future run).

This record did not come back empty.

## Method

**The archive.** The same one the `Dockerfile` fetches:
`https://nigos.nist.gov/nist/nbis/nbis_v5_0_0.zip`, sha256
`0adf8ab0f6b0e4208de50ca00ba21d3d77112ecd66288757ddfed21f6bee92c3`, verified
before unpacking. It was unpacked into a scratch directory outside this
repository and deleted when the pass finished. Nothing from it is committed.

**The search set came from the link lines, not from a guess.** The builder
stage of this repository's own `Dockerfile` was materialised, both binaries
were deleted, and the two tools were relinked so that the link commands could
be read. They are quoted verbatim in "Reproducing this". From them the search
set is:

| linked archive | source directory | authorship |
| --- | --- | --- |
| `libmindtct.a` | `mindtct/src/lib/mindtct` | NBIS |
| `liban2k.a` | `an2k/src/lib/an2k` | NBIS |
| `libimage.a` | `imgtools/src/lib/image` | NBIS |
| `libihead.a` | `imgtools/src/lib/ihead` | NBIS |
| `libwsq.a` | `imgtools/src/lib/wsq` | NBIS |
| `libjpegl.a` | `imgtools/src/lib/jpegl` | NBIS |
| `libfet.a` | `commonnbis/src/lib/fet` | NBIS |
| `libcblas.a` | `commonnbis/src/lib/cblas` | NBIS |
| `libioutil.a` | `commonnbis/src/lib/ioutil` | NBIS |
| `libutil.a` | `commonnbis/src/lib/util` | NBIS |
| `libbozorth3.a` | `bozorth3/src/lib/bozorth3` | NBIS |
| `libjpegb.a` | `ijg/src/lib/jpegb` | third party (IJG) |
| `libopenjp2.a` | `openjp2/src/lib/openjp2` | third party (OpenJPEG) |
| `libpng.a` | `png/src/lib/png` | third party (libpng) |
| `libz.a` | `png/src/lib/zlib` | third party (zlib) |

plus the two program directories, `mindtct/src/bin/mindtct` and
`bozorth3/src/bin/bozorth3`, and the `include/` directory of each package.

The NBIS-authored part of that set is **238 files, 89 854 lines**. The bundled
third-party part is **531 files, 306 724 lines**.

**The brief that commissioned this pass said not to search `an2k`, on the
grounds that nothing here depends on it. That is not so, and the correction
matters**: `liban2k.a` is on `mindtct`'s link line, `is_ANSI_NIST_file()` is
called on **every** input (`mindtct.c:105`), and the PNG decoder itself lives in
an2k — `png_decode_mem` is defined in `an2k/src/lib/an2k/dec_png.c:186` and is
what `imgtools/src/lib/image/imgdecod.c:444` calls for a PNG. an2k was
therefore searched. `pcasys`, `nfiq` and `nfseg` were not searched: they appear
on no link line.

**What was counted as a finding.** A comment, or a `#cat:` documentation block,
in which the authors state that the behaviour is wrong, limited, incomplete, a
workaround, or a deliberate simplification. **Excluded, and filtered out rather
than reported**: style notes, stale refactoring TODOs, commented-out debug
code, notes about platforms this repository does not use, the forty-line NIST
licence header that begins every file, ordinary parameter documentation
containing the words "should be", and runtime error strings.

**How the reading was done.** A keyword sweep located candidates; every
candidate was then read in its surrounding code, and its enclosing function was
resolved so that reachability could be judged rather than assumed. Every
quotation below was finally re-read directly from the file, at the line given,
before being recorded here.

**Reachability was traced, not guessed.** NBIS carries V1 and V2 versions of
much of the detector, and `mindtct` calls only the V2 chain
(`getmin.c` -> `lfs_detect_minutiae_V2` -> `detect_minutiae_V2` ->
`remove_false_minutia_V2`). Several of the most quotable admissions are in the
V1 twins and are recorded below as not executed. In addition, the symbol tables
of the built binaries were compared against each archive:

| archive | symbols in archive | of those, in the mindtct binary |
| --- | --- | --- |
| `mindtct` | 312 | 236 |
| `an2k` | 367 | 241 |
| `image` | 227 | 97 |
| `ihead` | 119 | 46 |
| `wsq` | 183 | 76 |
| `jpegl` | 153 | 64 |
| `jpegb` | 316 | 185 |
| `fet` | 92 | 27 |
| **`cblas`** | 92 | **0** |
| `ioutil` | 43 | 22 |
| `util` | 86 | 43 |
| `openjp2` | 691 | 442 |
| `png` | 510 | 274 |
| `z` | 132 | 34 |

`libbozorth3.a` contributes 61 of its 95 symbols to the `bozorth3` binary,
which has 104 defined symbols in total.

**`libcblas.a` contributes nothing.** It is on the link line and no object of
it is pulled in; no BLAS symbol appears in the binary. It cannot affect any
result, and it was searched only to establish that.

## Findings on the execution path

Everything in this section is executed when this repository runs `mindtct` on a
PNG or `bozorth3` on two `.xyt` files. Status `VERIFIED`: each quotation was
read at the line given, in the archive whose checksum is above.

### M-1 — Two bits of every pixel are thrown away, and the author says so — VERIFIED

`mindtct/src/lib/mindtct/detect.c:515-521`, inside `lfs_detect_minutiae_V2`:

    /* Scale input image to 6 bits [0..63] */
    /* !!! Would like to remove this dependency eventualy !!!     */
    /* But, the DFT computations will need to be changed, and     */
    /* could not get this work upon first attempt. Also, if not   */
    /* careful, I think accumulated power magnitudes may overflow */
    /* doubles.                                                   */
    bits_8to6(pdata, pw, ph);

and again at the definition, `mindtct/src/lib/mindtct/imgutil.c:103-109`:

    #cat: bits_8to6 - Takes an array of unsigned characters and bitwise shifts
    #cat:             each value 2 postitions to the right.  This is equivalent
    #cat:             to dividing each value by 4.  This puts original values
    #cat:             on the range [0..256) now on the range [0..64).  Another
    #cat:             way to say this, is the original 8-bit values now fit in
    #cat:             6 bits.  I would really like to make this dependency
    #cat:             go away.

The body is unconditional (`imgutil.c:125-128`): `*iptr++ >>= 2` over the whole
padded image. The reduced image is what `binarize_V2` and `gen_image_maps`
receive.

**What it means for us, measured rather than predicted.** The first prediction
made from this reading was that masking the low two bits of every pixel would
change nothing. That prediction was wrong, and the measurement is the fact:
over all 80 images of FVC2002 `Db1_b`, with every pixel replaced by
`pixel & 0xFC`,

| field | unchanged |
| --- | --- |
| minutia count | 80/80 images |
| x and y | **3946/3946** |
| theta | **3946/3946** |
| `.xyt` quality | 2418/3946 |
| `.min` reliability | 226/3946 |

At least one quality moved on **80 of 80** images. So the geometry is computed
from the 6-bit reduction and is exactly insensitive to the low two bits, while
the confidence is computed from the untouched 8-bit image — `quality.c:251`
passes `idata`, not the reduced copy. A pixel-level difference smaller than one
quantum of four grey levels — a different encoder, a different decoder, a
rounding difference in a conversion — cannot move a minutia's position or
angle, and will move its quality.

**How we would detect it:** exactly the experiment above, which is now a
measurement in this record.

### M-2 — The resolution declared in a PNG never reaches the extractor — VERIFIED

`mindtct/src/bin/mindtct/mindtct.c:139-143`:

    /* If image ppi not defined, then assume 500 */
    if(ippi == UNDEFINED)
       ippmm = DEFAULT_PPI / (double)MM_PER_INCH;
    else 
       ippmm = ippi / (double)MM_PER_INCH;

`UNDEFINED` is `-1` (`mindtct/include/lfs.h:717`) and `DEFAULT_PPI` is `500`
(`lfs.h:293`). The comment is the authors' statement of the assumption. What
makes the assumption unconditional for us carries no comment at all:
`an2k/src/lib/an2k/dec_png.c:335` sets

    img_dat->ppi = -1;

with no attempt to read the PNG's `pHYs` chunk. So for PNG input the branch is
always the assuming one.

**What it means for us, measured.** The same pixels were written as PNG
declaring 500, 1000 and 72 dpi, and with no declaration at all. All four
produced a byte-identical `.xyt`, sha256 beginning `4aebdeeeab9fe3dd` — the
value `manifests/MAN-tools.v1.json` already records for `101_1`. Pillow writes
no `pHYs` chunk unless asked, so this repository's own conversion declares
nothing in any case.

On our path the assumed resolution reaches exactly one computation:
`quality.c:237`, `radius_pix = sround(RADIUS_MM * ppmm)`, the radius of the
neighbourhood the reliability heuristic measures. Our images are 500 dpi, so
the assumption is true for us and the value is right. It would be silently
wrong for a corpus at another resolution fed as PNG, and no diagnostic would
be printed.

**How we would detect it:** as above; and for a non-500 dpi corpus, by feeding
the same pixels through an ANSI/NIST record carrying the true resolution and
comparing the quality column.

### M-3 — Block margins do not line up on an image that is not a multiple of the block size — VERIFIED

Two comments, both in `remove_near_invblock_V2`
(`mindtct/src/lib/mindtct/remove.c:1541`), which is step two of
`remove_false_minutia_V2` (`remove.c:206`).

`remove.c:1639-1644`:

    /* NOTE: The margins used here will not necessarily correspond to */
    /* the actual block boundaries used to compute the map values.    */
    /* This will be true when the image width and/or height is not an */
    /* even multiple of 'blocksize' and we are processing minutia     */
    /* located in the right-most column (or bottom-most row) of       */
    /* blocks.  I don't think this will pose a problem in practice.   */

`remove.c:1696-1700`:

    /* NOTE: This is true when the image width and/or height   */
    /* is an even multiple of blocksize.  When the image is not*/
    /* an even multiple, then some minutia may not be detected */
    /* as being in the margin of "the image" (not the block).  */
    /* In practice, I don't think this will impact performance.*/

**The condition the authors name holds for every image in our fixture.** The
block size on the V2 path is `MAP_BLOCKSIZE_V2 = 8` (`lfs.h:341`). Our images
are 388 x 374 (`INV-002` F-1). 388 = 48*8 + 4 and 374 = 46*8 + 6, so neither
dimension is an even multiple, and by `block.c`'s `block_offsets` the map is
49 x 47 blocks with the last column overlapping its neighbour by 4 pixels and
the last row by 2.

The dismissal — "I don't think this will pose a problem in practice" — is the
authors' judgement and is not supported by anything in the source. This
repository has not measured it either.

**How we would detect it:** compare the minutiae found in the last block column
and row against those found after re-running on an image cropped or padded to
an exact multiple of 8. The comparison is not clean, because changing the image
changes the detection for reasons of its own, and that is why this is recorded
as unmeasured rather than resolved.

### M-4 — A clockwise loop, and the minutia that found it, are discarded — VERIFIED

`mindtct/src/lib/mindtct/minutia.c:3313-3327`, inside
`adjust_high_curvature_minutia_V2` (`minutia.c:3272`), reached from
`remove_or_adjust_side_minutiae_V2`:

    /* If the order of the contour is clockwise, then the loops's     */
    /* contour pixels are outside the corresponding edge pixels.  We  */
    /* definitely do NOT want to fill based on the feature pixel in   */
    /* this case, because it is OUTSIDE the loop.  For now we will    */
    /* ignore the loop and the minutia that triggered its tracing.    */
    /* It is likely that other minutia on the loop will be            */
    /* detected that create a contour on the "inside" of the loop.    */
    /* There is another issue here that could be addressed ...        */
    /* It seems that many/multiple minutia are often detected within  */
    /* the same loop, which currently requires retracing the loop,    */
    /* locating minutia on opposite ends of the major axis of the     */
    /* loop, and then determining that the minutia have already been  */
    /* entered into the minutiae list upon processing the very first   */
    /* minutia detected in the loop.  There is a lot of redundant     */
    /* work being done here!                                          */

A minutia is dropped, and the compensation offered is a likelihood — "It is
likely that other minutia on the loop will be detected". This is minutia
detection, so it acts directly on the count and the set that reach a score.

**How we would detect it:** count how often the branch is taken, which needs
either the tool's own logging (`print2log`, compiled out here) or an
instrumented build. Neither exists in this repository.

### M-5 — An incomplete contour is discarded rather than returned — VERIFIED

`mindtct/src/lib/mindtct/contour.c:197-203`, the `#cat:` block documenting
`get_high_curvature_contour` (`contour.c:228`), which
`adjust_high_curvature_minutia_V2` calls at `minutia.c:3301`:

    #cat:            with a return code of (LOOP_FOUND).  If the process fails
    #cat:            to extract a contour of total specified length, then
    #cat:            the returned contour length is set to Zero, NO allocated
    #cat:            memory is returned in this case, and the return code is set
    #cat:            to Zero.  An alternative implementation would be to return
    #cat:            the incomplete contour with a return code of (INCOMPLETE).
    #cat:            For now, NO allocated contour is returned in this case.

The authors name the alternative they did not implement. Same effect as M-4:
information the detector had is dropped near a high-curvature region.

### M-6 — An isolated pixel is left alone, and the author is unsure — VERIFIED

`mindtct/src/lib/mindtct/contour.c:993-998`, in `next_contour_pixel`, which
`trace_contour` and `search_contour` call:

    /* If we get here, then we did not find the next contour pixel */
    /* within the 8 neighbors of the current feature pixel so      */
    /* return (FALSE==>Failure).                                   */
    /* NOTE: This must mean we found a single isolated pixel.      */
    /*       Perhaps this should be filled?                        */
    return(FALSE);

An open question left in the code, on a path we execute.

### B-1 — A matching condition was changed because it was assumed to be a typo — VERIFIED

`bozorth3/src/lib/bozorth3/bozorth3.c:1288-1290`:

    				/* Was: if ( SQUARED(kk) > TXS && kk < CTXS ) : assume typo */
    				if ( kk > TXS && kk < CTXS )
    					continue;

with `TXS 121` and `CTXS 121801` (`bozorth3/include/bozorth.h:133-134`). The
condition that decides whether a candidate pair is skipped was rewritten on an
assumption about the original author's intent, and the assumption is recorded
in the comment rather than resolved. The two readings are not close: comparing
`kk` against 121 and comparing `kk*kk` against 121 select different sets.

This is inside the scoring loop. It affects **every** score this repository
computes, including the six in `manifests/MAN-tools.v1.json`.

**How we would detect it:** there is nothing to detect. The tool has one
behaviour and it is the one in the fixture; the finding is that the behaviour
rests on somebody's guess, not that it varies.

### B-2 — A hard cap on how much evidence a match may accumulate — VERIFIED

`bozorth3/src/lib/bozorth3/bozorth3.c:1570-1571`:

    if ( *ww >= WWIM )	/* This limits the number of endpoint groups that can be constructed */
    	return;

`WWIM` is `10` (`bozorth.h:137`). The comment states the limit plainly. It is a
fixed constant with no relation to the size of either template.

### B-3 — The score has a sentinel value in the same range as a real score — VERIFIED

`bozorth3/include/bozorth.h:139-141`:

    #define QQ_SIZE 4000

    #define QQ_OVERFLOW_SCORE QQ_SIZE

`QQ_OVERFLOW_SCORE` is **returned as the match score** at six places in
`bozorth3.c` — lines 754, 776, 806, 833, 878 and 1346 — when the internal
`qq[]` table overflows. A warning is printed to the error stream first, for example at
`bozorth3.c:752`, but the value on stdout is an integer 4000 that sits in the
same column as a genuine score.

Adjacent, and worth having beside it: `bozorth.h:124` defines
`DEFAULT_MAX_MATCH_SCORE 400`, and that name appears in no other `.c` or
`.h` file of the archive. It is not a cap and it is not used; a reader who takes it for the
maximum score will be wrong. The fixture in `manifests/MAN-tools.v1.json`
contains a score of 499.

**How we would detect it:** a score of exactly 4000 in a score vector, or a
`qq[] overflow` line on the error stream. Neither has been seen here, and the
error stream is not currently captured by anything in this repository.

## Findings that are linked but never executed

Recorded so that a later task does not have to find them again, and marked so
that nobody acts on them. Each was confirmed at the line given; each sits in a
V1 routine that `mindtct` does not call, or in a codec that a PNG input never
reaches.

| where | what the authors say | why it is not on our path |
| --- | --- | --- |
| `mindtct/src/lib/mindtct/minutia.c:244-245` | "Otherwise, IMAP is INVALID, so ignore the block.  This seems / quite drastic!" | in `detect_minutiae`, the V1 routine; `detect_minutiae_V2` runs |
| `mindtct/src/lib/mindtct/remove.c:1466-1470` | the same margin admission as M-3 | in `remove_near_invblock`, the V1 twin |
| `mindtct/src/lib/mindtct/minutia.c:3117-3126` | the same loop admission as M-4 | in `adjust_high_curvature_minutia`, the V1 twin |
| `mindtct/src/lib/mindtct/minutia.c:1400, 1661` | "For now, we will not adjust for IMAP edge" | in `scan4minutiae_horizontally` / `_vertically`, the V1 twins; the V2 versions carry no such comment |
| `imgtools/src/lib/wsq/cropcoeff.c:660-667` | admission in `wsq_dehuff_mem` | WSQ decoding; never reached from PNG |
| `imgtools/src/lib/wsq/encoder.c:223-226` | admission about the Huffman buffer size | WSQ encoding; `mindtct` encodes nothing |
| `imgtools/src/lib/image/writihdr.c:112-116` | an admission in `writeihdrfile` | IHead writing; `mindtct` writes no image |
| `imgtools/include/grp4comp.h:63-72` | `#define SHORT int` with a note that the type was widened because images with more than 2^15 rows broke | Group 4 compression; not reached |
| `imgtools/src/lib/image/grp4comp.c:772-775` | admission in the compressor | as above |
| `an2k/src/lib/an2k/to_iafis.c:785-788` | admission in IAFIS conversion | ANSI/NIST conversion; not reached |
| `an2k/src/lib/an2k/lookup.c:422-423` | a stale comment about pixel density lookup | ANSI/NIST field lookup; not reached for PNG |

The V1/V2 pattern is the main reason a keyword sweep alone would have
misreported this pass: four of the most quotable admissions in `mindtct` are in
code the tool does not run, and two of them have V2 twins that say the same
thing and do run.

## The changelog

`CHANGELOG.txt` was read in full, all 387 lines, covering releases 1.0.0
(2007-03-05) to 5.0.0 (2015-03-04).

**It names no defect in `mindtct` or in `bozorth3`.** That is the result, and
it is recorded as one. What it does contain that bears on this repository:

- **Rel 5.0.0**, the release we build, lists "Various minor enhancements and
  bug fixes" and enumerates none of them. What changed between 4.2.0 and the
  version in our image is therefore not knowable from the release notes.
- **Rel 4.0.0** carries a standing warning that survives into 5.0.0:
  "Big-endian compilation is no longer being tested and support as an official
  release. Warning: This version of NBIS may compile on a big-endian machine;
  however, undesired behavior may occur." Our builder and runtime are x86-64,
  so this does not touch us.
- **Rel 3.2.0** warns that six named applications "exhibit 64-bit operational
  issues and should not be used until further notice". All six are `pcasys`
  tools; none is ours.
- **Rel 3.1.0** (2009-05-29) is where `bozorth3` entered NBIS at all, in the
  same release that added 64-bit support.
- **Rel 4.1.0** notes "JASPER library support is deprecated", which is
  consistent with our build linking `libopenjp2.a` and not `libjasper.a`.

## The two questions the record had gaps for

### The `.xyt` quality and the `.min` reliability — answered in full

There is **one** internal value and both files are projections of it, which is
what `INV-002` F-12 hypothesised from measurement. The source says how.

`mindtct/src/lib/mindtct/quality.c:218-291`, `combined_minutia_quality`,
computes a single double `minutia->reliability` on [0,1] by combining a
grayscale heuristic with the quality map's class:

    reliability = 0.50 + (0.49 * gs_reliability);   /* quality map class 4 */
    reliability = 0.25 + (0.24 * gs_reliability);   /* class 3 */
    reliability = 0.10 + (0.14 * gs_reliability);   /* class 2 */
    reliability = 0.05 + (0.04 * gs_reliability);   /* class 1 */
    reliability = 0.01;                             /* class 0 */

`gs_reliability` comes from `grayscale_reliability` (`quality.c:325`), whose
own documentation says it "returns 0.0 .. 1.0 based on stdev and Mean of a
localized histogram where 'ideal' stdev is >=64; 'ideal' Mean is 127", over a
radius of `sround(RADIUS_MM * ppmm)` pixels — the radius M-2 fixes at the
assumed 500 ppi. The image it reads is `idata`, the **unreduced** 8-bit image,
which is what M-1's measurement shows.

The two projections:

- `.min` — `mindtct/src/lib/mindtct/minutia.c:789` prints the double with
  `%6.3f`, three decimals. The line above it records when that precision
  changed: "/* Precision of reliablity added one decimal position */
  /* on 09-13-04 */".
- `.xyt` — `mindtct/src/lib/mindtct/results.c:321`:
  `oq = sround(minutia->reliability * 100.0);` and `sround` is
  `((int) (((x)<0) ? (x)-0.5 : (x)+0.5))` (`lfs.h:96`), which is rounding half
  away from zero on the **unrounded** double.

So `INV-002` F-10 is explained exactly: the integer in `.xyt` is round-half-up
of a value the `.min` file only ever shows to three places, and no function of
the printed string can recover it. `INV-002` F-11's best closed form,
`round(r*100)` at 94.58%, is the right shape and fails only where the third
decimal has already discarded what `sround` saw.

### `bozorth3`'s score — the source states no bound and no normalisation

The score is `match_score`, the largest `tot` found over the candidate clusters
(`bozorth3.c`, tail of `bz_final_loop`: "If the current total is larger than the
running total ... then set match_score to the new total"). `tot` counts
compatible edge pairs. Nothing divides by a minutia count, by a template size,
or by anything else; `INV-002`'s observation that the score is not normalised
is what the source does.

There is no stated upper bound. The only special value is B-3's
`QQ_OVERFLOW_SCORE` of 4000, which is a failure sentinel and not a maximum, and
`DEFAULT_MAX_MATCH_SCORE 400` is defined and never used. The constants that do
bound the computation are `MAX_BOZORTH_MINUTIAE 200`,
`DEFAULT_BOZORTH_MINUTIAE 150`, `MIN_COMPUTABLE_BOZORTH_MINUTIAE 10`
(`bozorth.h:119-122`, already in `manifests/MAN-tools.v1.json`),
`MAX_FILE_MINUTIAE 1000` for the loader (`bozorth.h:188`), and B-2's `WWIM 10`.

## What this closes elsewhere

`INV-002` recorded, under what was left unchecked, that "the tool's source was
not read" and that no further image could separate the angle rule it derived
from the true one. The source is now read, and it agrees exactly.

`mindtct/src/lib/mindtct/xytreps.c:98-107`, `lfs2nist_minutia_XYT`:

    degrees_per_unit = 180 / (float)NUM_DIRECTIONS;

    t = (270 - sround(minutia->direction * degrees_per_unit)) % 360;
    if(t < 0){
       t += 360;
    }

with `NUM_DIRECTIONS 16` (`lfs.h:356`), so `degrees_per_unit` is 11.25 and
`sround` is round half away from zero. That is `INV-002` F-7's third rule,
`(270 - round_half_up(11.25 d)) mod 360`, character for character — and it is
not the rule reported to that investigation, which F-7 had already measured to
fail on 952 of 3946 minutiae.

`xytreps.c:135-145`, `lfs2m1_minutia_XYT`, gives `x = minutia->x`,
`y = minutia->y`, `t = (90 - sround(...)) % 360` normalised to non-negative and
then `t = t / 2` in integer arithmetic, with the comment "range of theta is
0..179 because angles are in units of 2 degress". Combined with the native
routine's `y = ih - minutia->y`, that is `INV-002` F-13's four relations
exactly, including that the halving truncates.

## Reproducing this

The link lines, which define the search set, come from this repository's own
builder stage:

    docker build --target nbis-builder -t nbis-builder:read .
    docker run --rm nbis-builder:read bash -c '
      cd /src && rm -f mindtct/bin/mindtct bozorth3/bin/bozorth3
      make -C mindtct/src/bin/mindtct
      make -C bozorth3/src/bin/bozorth3'

which printed, with paths as shown:

    gcc -m64 -fPIC .../mindtct.o /src/exports/lib/libmindtct.a /src/exports/lib/liban2k.a
      /src/exports/lib/libimage.a /src/exports/lib/libihead.a /src/exports/lib/libwsq.a
      /src/exports/lib/libjpegl.a /src/exports/lib/libjpegb.a /src/exports/lib/libfet.a
      /src/exports/lib/libcblas.a /src/exports/lib/libioutil.a /src/exports/lib/libutil.a
      /src/exports/lib/libopenjp2.a /src/exports/lib/libpng.a /src/exports/lib/libz.a
      -lm -o /src/mindtct/bin/mindtct

    gcc -m64 -fPIC .../bozorth3.o .../usage.o /src/exports/lib/libbozorth3.a
      -lm -o /src/bozorth3/bin/bozorth3

The source is fetched and verified the way the `Dockerfile` does it:

    curl -fsSL -o nbis.zip https://nigos.nist.gov/nist/nbis/nbis_v5_0_0.zip
    echo "0adf8ab0f6b0e4208de50ca00ba21d3d77112ecd66288757ddfed21f6bee92c3  nbis.zip" | sha256sum -c -
    unzip -q nbis.zip

The sweep, over the NBIS-authored directories of the table in Method, with the
licence header filtered out:

    NBIS="mindtct/src/bin/mindtct mindtct/src/lib/mindtct mindtct/include \
          bozorth3/src/bin/bozorth3 bozorth3/src/lib/bozorth3 bozorth3/include \
          an2k/src/lib/an2k an2k/include \
          imgtools/src/lib/image imgtools/src/lib/ihead imgtools/src/lib/wsq \
          imgtools/src/lib/jpegl imgtools/include \
          commonnbis/src/lib/fet commonnbis/src/lib/cblas \
          commonnbis/src/lib/ioutil commonnbis/src/lib/util commonnbis/include"

    FILT='WARRANTY|PATRIOT|EAR \(see|permissible to distribute|reason to know|hold the Government|licensed product'

    grep -rniE 'broken|does not work|known issue|not implemented|\bhack|workaround|\
    temporary|fixme|\bbug\b|\bwrong|\bassume|only works|hardcoded|arbitrary|kludge|\
    not supported|\bXXX\b|\bTODO\b|for now|currently|never happen|may not|ignore' \
      --include='*.c' --include='*.h' $NBIS | grep -viE "$FILT"

Which archive contributed which symbols:

    nm --defined-only <binary> | awk '{print $3}' | sort -u > bin.syms
    nm --defined-only /src/exports/lib/lib<name>.a | awk '{print $3}' | sort -u > lib.syms
    comm -12 lib.syms bin.syms | wc -l

The reachability of a comment is settled by finding its enclosing function and
then following `mindtct.c:151` -> `get_minutiae` -> `lfs_detect_minutiae_V2` ->
`detect_minutiae_V2` / `remove_false_minutia_V2`. Any function whose name lacks
`_V2` and has a `_V2` sibling is not on the path.

M-1's and M-2's measurements were made in the runtime image, with the fixture
directory mounted read-only, by writing each image twice — once unchanged, once
with `pixel & 0xFC`, and once per declared dpi — running `mindtct` on each and
comparing the four `.xyt` columns and the `.min` reliability field by position.
No derived file left the container.

To repeat this pass against a future NBIS release: take the link lines again
rather than reusing the table above, since the set of archives has changed
between releases before; re-run the sweep; and re-check the V1/V2 split, which
is the thing most likely to move.

## Adjacent facts, which are not findings of the kind sought

Recorded because they were established during the pass and bear on what we
execute, but they are not admissions by NBIS's authors and were not sought.

- The bundled `libpng` is **1.2.23** (`png/src/lib/png/png.h:378`) and the
  bundled `zlib` is **1.2.3** (`png/src/lib/zlib/zlib.h:40`). Both are executed
  when `mindtct` reads a PNG. NBIS 5.0.0 is dated 2015 and these are the
  versions it ships. This repository has not assessed either against any
  vulnerability record, and states no conclusion about them.
- A keyword sweep of `libpng` and `zlib` for the strongest terms returned
  matches that are, on inspection, almost entirely runtime warning strings
  ("Incorrect tRNS chunk length" and its neighbours), which the definition
  above excludes. No authors' admission was found in the two third-party
  libraries on our path.
- `libopenjp2.a` and `libjpegb.a` were not swept. They are on the link line and
  contribute symbols, but neither is reached when the input is a PNG, and
  together they are 267 000 lines.

## What was left unchecked

- **The third-party libraries were not read.** 306 724 lines of `openjp2`,
  `jpegb`, `png` and `zlib` were left to their own upstreams, except for the
  keyword pass on `png` and `zlib` noted above. The question asked was what
  *NBIS's* authors acknowledge.
- **Only comments were counted.** A defect the authors did not write a comment
  about is invisible to this method. `dec_png.c:335` is the example: the line
  that makes M-2 unconditional carries no comment, and it was found only by
  tracing the value, not by the sweep.
- **M-3, M-4, M-5 and M-6 were not measured.** Their consequences are stated as
  what the authors say, not as what this repository has observed. M-4 in
  particular would need an instrumented build to count how often the branch is
  taken.
- **B-1 was not resolved.** Whether the original condition was a typo, and what
  the intended one was, is not established here. The change is in the released
  code and every score rests on it.
- **The error stream is not captured.** B-3's overflow prints a warning that
  nothing in this repository currently reads.
- **One release.** Everything above is NBIS 5.0.0 at the checksum named. The
  changelog shows the V1/V2 split and the library set both moved between
  releases.
- **`nfiq`, `nfseg` and `pcasys` were not searched**, correctly: they appear on
  no link line. `an2k` was searched despite the brief excluding it, because the
  link line and the call graph both contradict the exclusion.
