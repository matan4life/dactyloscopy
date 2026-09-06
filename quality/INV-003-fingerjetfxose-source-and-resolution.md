# INV-003 — FingerJetFXOSE: units, layout and resolution, from its source

Date: 2026-09-06

## Numbering

This record takes 003, the next free investigation number after `INV-002`. The
reservation at 001 is explained in `REF-002`.

## Question

1. What do the FingerJetFXOSE sources say about the angle units, the record
   layout and the handling of image resolution in the templates it writes?
2. How does what the tool produces depend on the resolution the caller
   declares?

The first question is answerable in this repository: the source is public and
can be pinned to a commit, and reading a line of it is a fact anyone can check.
The second is not: it needs a built tool, and FingerJetFXOSE is not in the
image. Answers to it are recorded as reported, with the method, and are not
`VERIFIED`.

## Method

Two methods, carrying different weight, and the record keeps them apart.

**Source confirmation, done here.** The project's own repository was cloned
into a scratch directory outside this tree at commit
`1726ba08bf7f2137d2f861ac1ae124d5cd355eee`, tree
`e523e7b7ad5ab6d6e8b0a6fd163696f13e4a8b48`, dated 2026-01-15. Every quotation
below was located in that checkout, read, and recorded with its path and line
number. The clone was then deleted.

Two notes on paths and pinning:

- The sources sit under an inner `FingerJetFXOSE/` directory. Paths reported to
  this investigation as `libFRFXLL/src/...` are relative to that inner
  directory; every path below is relative to the clone root.
- Files are pinned by **git blob id**, not by a digest of the checked-out
  bytes. The clone had `core.autocrlf = true`, so a content digest of the
  working tree would be a fact about this machine rather than about the
  commit.

| file | blob id at this commit |
| --- | --- |
| `FingerJetFXOSE/libFRFXLL/src/algorithm/serializeFpData.h` | `cfba519962b3c3b6c65f1dc5a8d0b66f53e889e0` |
| `FingerJetFXOSE/libFRFXLL/src/algorithm/FeatureExtraction.h` | `5a775d0ccdceb776211f8ab296f87e401a8fe981` |
| `FingerJetFXOSE/libFRFXLL/src/algorithm/matchData.h` | `1f8420e705087ea1dec5f2603e6a24884603daf1` |
| `FingerJetFXOSE/libFRFXLL/src/algorithm/intmath.h` | `a7528d07f9bfff8f9a616465aad08e70e53d4656` |
| `FingerJetFXOSE/libFJFX/src/FJFX.cpp` | `bc3cf90dd14ba0c4ee6f85c4f74710f7c01d147e` |
| `FingerJetFXOSE/libFJFX/samples/fjfxSample/fjfxSample.c` | `e75bee868de245863f64a39f26baafa7120c8256` |
| `FingerJetFXOSE/libFRFXLL/samples/FRFXLLSample/frfxllLSample.c` | `5cb561283a8edfa9245f555d65ac10aa4eedcc2d` |

Below, `serializeFpData.h`, `FeatureExtraction.h`, `matchData.h` and
`intmath.h` are the four files under
`FingerJetFXOSE/libFRFXLL/src/algorithm/`; the other three are given in full.

**Reported measurements, not made here.** The behavioural facts in the last
section were obtained outside this repository, with FingerJetFXOSE built in a
throwaway environment and driven by a throwaway caller written for the purpose.
Neither the build nor the caller is available to this investigation. They are
recorded as reported, with the method, and are `UNVERIFIED`.

## S — the source, confirmed here

Every quotation in this section was found at the stated line and reads as
quoted. Status: `VERIFIED`, in the sense that the line exists and reads so at
the pinned commit. What follows *from* these lines is separated into the next
section.

### S-1 — The two serializers write the angle differently — VERIFIED

`serializeFpData.h`, `IsoFmdSerializer` at 367 and `AnsiFmdSerializer` at 391:

    386:        virtual void WriteTheta(Writer & wr, uint8 theta) {
    387:          wr << uint8(theta);
    388:        }

    411:        virtual void WriteTheta(Writer & wr, uint8 theta) {
    412:          theta = muldiv(theta, 180, 256);
    413:          wr << uint8(theta);
    414:        }

The ISO serializer writes the internal 8-bit value unchanged. The ANSI
serializer scales it by 180/256 first. The angle unit is therefore a property
of the serializer, not of the extractor.

### S-2 — How muldiv rounds — VERIFIED

`intmath.h:324` defines `muldiv(x, y, z)` as `divide(x * y, z)` in a
double-width type, and `divide` at `intmath.h:313-315` is

    return (x + (y >> 1)) / y;

Integer division after adding half the divisor: rounding half up, for the
unsigned case that applies here.

### S-3 — Record header lengths — VERIFIED

`serializeFpData.h:372` in `IsoFmdSerializer`: `recordHeaderLength = 24;`
`serializeFpData.h:396` in `AnsiFmdSerializer`: `recordHeaderLength = 26;`

### S-4 — The record header fields — VERIFIED

    258:          wr << uint32(0x464D5200);        // Format Identifier
    259:          wr << uint32(0x20323000);        // Version of this standard
    264:          wr << uint16(resolutionX);       // X (horizontal) Resolution
    265:          wr << uint16(resolutionY);       // Y (vertical) Resolution

### S-5 — Six bytes per minutia, then a two-byte block length — VERIFIED

    246:            wr << uint16((pos.x & 0x3FFF) | (md.minutia[i].type << 14));    // X
    247:            wr << uint16(pos.y & 0x3FFF);                                   // Y
    248:            WriteTheta(wr, md.minutia[i].theta);                            // Theta
    249:            uint8 currQ = QualityFromConfidence(md.minutia[i].conf);
    250:            wr << currQ;                                                    // Quality

    287:          wr << uint16(viewEDBLength);     // Extended Data Block Length

    293:          viewDataLength = 6 + 6 * md.numMinutia; // 4 = view header length; 2 = EDB Length length

Two bytes of x with the type in the top two bits, two of y, one of theta, one
of quality.

### S-6 — Quality from confidence — VERIFIED

`serializeFpData.h:203-205`:

    static uint8 QualityFromConfidence(uint8 confidence) {
      return min<uint8>((confidence + 1) / 2, 100);
    }

### S-7 — The ISO angle fix, and what it is defined against — VERIFIED

`FeatureExtraction.h:150-151`:

    // this code fixes the angles to be ISO compliant (was in the serializer)
    std::for_each(&md.minutia[0],&md.minutia[md.numMinutia], [](Minutia &m) {int theta = (int) m.theta; theta = -theta + 64; m.theta = (unsigned int) theta;});

The comment reported to this investigation is quoted here in full: it carries a
trailing `(was in the serializer)` that the report omitted. The transform is
applied to the library's own internal angle before serialization.

### S-8 — The resolution is pinned, and the authors say so — VERIFIED

`FeatureExtraction.h:176-177`:

    //      md.minutia_resolution_ppi = imageResolution;		// this is what it should be..
          md.minutia_resolution_ppi = 500;	// its currently broken!

`matchData.h:269`:

    unsigned int minutia_resolution_ppi = 500;	// sad default

The line that would carry the declared resolution into the minutia data is
commented out, and a literal 500 stands in its place.

### S-9 — A second pinned constant — VERIFIED

`FeatureExtraction.h:168`:

    #define StdFmdDeserializer_Resolution 167	// this was a constant in deserializeFpData... (it needs to be fixed)

Used two lines later:

    172:		  m.position.x = muldiv(m.position.x, 197, StdFmdDeserializer_Resolution);
    173:		  m.position.y = muldiv(m.position.y, 197, StdFmdDeserializer_Resolution);

The comment is quoted here in full; the report abridged it to its parenthesis.

### S-10 — The library's own self-test pins the defect — VERIFIED

`FingerJetFXOSE/libFRFXLL/samples/FRFXLLSample/frfxllLSample.c:310-311`:

    //  UT_ASSERT(minutia_ppi == test_raw_image_333.resolution);	// this should be how it works, but it is not! all minutia scaled to 500
      UT_ASSERT(minutia_ppi == 500);

This is two lines, not three: the sentence the report gave as a line of its own
is a trailing comment on the commented-out assertion. The correct assertion is
disabled and the defective behaviour is asserted in its place.

At line 333 the same check on a 500 dpi image keeps the real assertion:

    UT_ASSERT(minutia_ppi == test_raw_image_500.resolution);

It passes because the pinned value and the image's resolution coincide there.

The file sits under `samples/`, not under `test/`, though it is written with
`UT_ASSERT` macros and functions as a self-test.

### S-11 — The resampler's window, and what it does inside it — VERIFIED

`FeatureExtraction.h:51`: `static const size_t int_resolution = 333;`

    247:      if (imageResolution <= 550 && imageResolution >= 450) {
    248:        // 500/333 = 1500/999 ~= 3/2
    250:        width  = in_width  / 6 * 4; // width should be multiple of 4
    251:        height = in_height / 6 * 4;
    252:      } else {
    253:        width  = (in_width  * int_resolution / imageResolution) & ~(ori_scale - 1);

    285:      if (imageResolution <= 550 && imageResolution >= 450) {
    286:        imresize23<maxwidth>(buffer, width, size, in_img, in_width);

Inside the window the target size and the resize routine are fixed and do not
mention `imageResolution` at all; outside it both are computed from it. What
happens after the resampler was not traced: see "What was left unchecked".

### S-12 — Two different bounds on the declared resolution — VERIFIED

`FeatureExtraction.h:36-37`, enforced at `213-214`:

    #define FRFXLL_EXTRACT_MIN_DPI 300
    #define FRFXLL_EXTRACT_MAX_DPI 1008

`FingerJetFXOSE/libFJFX/src/FJFX.cpp:77`, in the public entry point:

    if (dpi < 300 || dpi > 1024)                               return FJFX_FAIL_IMAGE_SIZE_NOT_SUP;

The two upper bounds differ.

### S-13 — How a declared resolution reaches the template — VERIFIED

`FingerJetFXOSE/libFJFX/src/FJFX.cpp`, inside `fjfx_create_fmd_from_raw`:

     91:  switch ( FRFXLLCreateFeatureSetFromRaw(hContext, ..., width, height, dpi, FRFXLL_FEX_ENABLE_ENHANCEMENT, &hFtrSet ) ) {
     99:  const unsigned short dpcm = (dpi * 100 + 50) / 254;
    103:  FRFXLL_OUTPUT_PARAM_ISO_ANSI param = {sizeof(FRFXLL_OUTPUT_PARAM_ISO_ANSI), CBEFF, finger_position, 0, dpcm, dpcm, width, height, 0, finger_quality, impression_type};

The declared `dpi` goes to two places: into the extraction, and — converted to
pixels per centimetre — into the serializer's resolution parameters.

On the serializer side, `serializeFpData.h`:

    161:        static const uint16 DefaultResolution = 197; // 500DPI / 2.54
    195:          resolutionX =     DefaultResolution;
    231:          unsigned int mr_ppcm = muldiv(md.minutia_resolution_ppi,197,500);
    236:            if (resolutionX != mr_ppcm) {
    237:				pos.x = muldiv(pos.x,resolutionX,mr_ppcm);
    314:          if (version >= 1 && pParams->resolutionX != FRFXLL_RESOLUTION_NOT_SPECIFIED) resolutionX = pParams->resolutionX;

`resolutionX` defaults to 197 and is overridden only by an export parameter. It
is written into the header at S-4 line 264, **and** it is the numerator of the
coordinate rescale at line 237. One variable drives both.

`serializeFpData.h:72` bounds it: `resolution >= 99 && resolution <= 1000`.

### S-14 — The hardcoded 500 is in the sample, not in the library — VERIFIED

`FingerJetFXOSE/libFJFX/samples/fjfxSample/fjfxSample.c:85`:

    err = fjfx_create_fmd_from_raw(image, 500, height, width, FJFX_FMD_ISO_19794_2_2005, tmpl, &size);

The function it calls takes the resolution as its second parameter
(`FJFX.cpp:65-73`). The literal is the sample program's choice. Nothing in the
library requires a caller to pass 500.

### Every quotation matched

No quotation reported to this investigation failed to appear at the pinned
commit. Three differences of rendering are recorded above rather than silently
smoothed: the comment at S-7 and the comment at S-9 are longer than reported,
and S-10 is two lines rather than three. In each case the words that were
quoted appear, in that order, in the line named.

## F — what follows from the source, by arithmetic

Exact arithmetic on the lines above, checkable by anyone. `VERIFIED` as
arithmetic.

### F-1 — 256 levels against 180 — VERIFIED

By S-1 and S-2 the ANSI value is `(theta * 180 + 128) / 256` for `theta` in
0..255, which is 0 at 0 and 179 at 255. So ISO/IEC 19794-2:2005 as written by
this library carries **256** levels of 360/256 = **1.40625** degrees, and ANSI
INCITS 378-2004 carries **180** levels of **2** degrees. The two standards are
not the same unit, and this library is where the difference is made.

### F-2 — The reported record sizes match the confirmed layout exactly — VERIFIED

By S-3 and S-5 an ISO record is `24 + 6 + 6n` bytes for `n` minutiae: 24 of
record header, 4 of view header plus 2 of extended-data-block length, and 6 per
minutia. The three sizes reported in the last section fit with no remainder:

| reported minutiae | 24 + 6 + 6n | reported bytes |
| --- | --- | --- |
| 26 | 186 | 186 |
| 16 | 126 | 126 |
| 60 | 390 | 390 |

This is a consistency check performed here. It does not establish that the tool
produced those counts; it establishes that the reported pairs cannot both be
wrong independently, since either number determines the other.

### F-3 — What 64 means, and what it does not — VERIFIED

By S-1 the ISO unit is 360/256 degrees, so the 64 of S-7 is exactly **90**
degrees, and `theta -> -theta + 64` is a reflection followed by a quarter turn.
It is defined against this library's own internal angle, which no line quoted
here relates to any other tool's. Nothing in this investigation connects it to
the NBIS convention.

### F-4 — Where the declared resolution equals the default — VERIFIED

By S-13, `dpcm = (dpi * 100 + 50) / 254`:

| declared dpi | dpcm | equals `DefaultResolution` 197 |
| --- | --- | --- |
| 450 | 177 | no |
| 500 | 197 | **yes** |
| 550 | 216 | no |
| 569 | 224 | no |

And by S-8, `md.minutia_resolution_ppi` is 500 whatever is declared, so
`mr_ppcm` of S-13 line 231 is `muldiv(500, 197, 500)` = **197**.

Over the whole domain a caller can pass through `fjfx_create_fmd_from_raw` —
integer dpi from 300 to 1024, by the check S-12 quotes — the guard at line 236
is false at exactly **three** declared resolutions, **500, 501 and 502**, and
true at every other. The three collapse to one `dpcm` because the conversion of
S-13 line 99 is an integer division: 50050, 50150 and 50250 all give 197, while
499 gives 196 and 503 gives 198.

Whether an extraction at 501 differs in any other respect from one at 500 is
not established here. By S-11 all three lie inside the resampler's fixed
window.

### F-5 — A gap between the two bounds — VERIFIED

By S-12 a declared resolution of 1009 to 1024 passes the public entry point's
check and fails the extractor's assertion. The interval is not empty.

## X — a reported observation the source contradicts

### X-1 — The template's resolution field against its coordinates — CONFLICT

Reported: *"The header records whichever resolution was declared, while the
coordinates stay in the image's pixel grid regardless. The template's
resolution field is therefore a statement about what the caller declared, not
about the minutiae."*

The source has **one** variable behind both halves. By S-13, `resolutionX` is
written into the header (S-4, line 264) and is the numerator of the coordinate
rescale (line 237), whose denominator is fixed at 197 by S-8 and F-4. The two
cannot move independently:

- If the caller leaves the export resolution unset, `resolutionX` stays at
  `DefaultResolution` 197. The header then reads 197 for **every** declared
  resolution, and the coordinates are never rescaled.
- If the caller sets it, as `fjfx_create_fmd_from_raw` does, the header reads
  the declared value and the coordinates **are** rescaled, by `dpcm/197`. At
  450 and 550 that is 177/197 and 216/197, which moves a coordinate near 200 by
  about 20 and 19 pixels.

The reported conjunction — a header that varies and coordinates that do not —
is not producible by the code as read. Each half is consistent with one of the
two branches, and they are different branches.

The status is `CONFLICT`: a report and a source disagree. By this repository's
own rule a `CONFLICT` field is forbidden to read, and no decision may rest on
it. What would settle it: the source of the throwaway caller, or one template
produced and decoded inside this repository.

The reported detail that coordinates differ by *at most two pixels* inside the
450-550 window belongs to the same conflict. Under the first branch the
resampling is the same fixed path at every declared value (S-11), so a
difference of zero would be expected unless something after the resampler
depends on the declared value, which was not traced here. Under the second
branch the difference would be about twenty pixels. Two is neither.

`INV-002` R-6 reported a decoded header reading 197 px/cm on an image extracted
at 500 dpi. That is the value both branches produce at 500, so it does not
separate them.

## R — reported, not established here

Obtained outside this repository, with FingerJetFXOSE built in a throwaway
environment and driven by a throwaway caller. Method: the same image,
`Db1_b/101_1`, with the declared resolution varied. Neither the build nor the
caller is available here. Status `UNVERIFIED` throughout; nothing in the
sections above rests on any of them.

- **R-1 — UNVERIFIED.** Minutiae found as the declared resolution varies:
  400 dpi -> 22, 450 -> 26, 500 -> 26 (the reference), 550 -> 26, 569 -> 23,
  600 -> 25. One image.
- **R-2 — UNVERIFIED.** Inside the 450-550 window the angles, types and
  qualities are identical to the 500 result, and coordinates differ by at most
  two pixels. Outside it the detection genuinely differs. The second sentence
  is consistent with S-11; the first is entangled in X-1.
- **R-3 — UNVERIFIED.** The build is clean: `./runCMake.sh x64` then `make`,
  zero errors. Also recorded as `INV-002` R-3, at the same commit, which S
  above confirms exists and is the project's own repository.
- **R-4 — UNVERIFIED.** Output on `Db1_b` is deterministic: `101_1` 26 minutiae
  in 186 bytes, `101_2` 16 in 126, `102_1` 60 in 390. Also `INV-002` R-6. F-2
  shows these pairs are internally consistent with the confirmed layout.

## Reproducing this

Every S fact is a line of a public repository at a named commit, so the
reproduction is a clone, a checkout and a read. Nothing here needs the tool
built, and nothing here reads an image.

    git clone https://github.com/FingerJetFXOSE/FingerJetFXOSE.git fjfx
    cd fjfx
    git checkout 1726ba08bf7f2137d2f861ac1ae124d5cd355eee
    git log -1 --format='%H%n%T%n%ad'      # the commit and tree in Method

The blob ids in Method are read without depending on how the clone checked the
files out:

    git rev-parse HEAD:FingerJetFXOSE/libFRFXLL/src/algorithm/serializeFpData.h

and likewise for the other six paths. Each quotation is then

    sed -n '<lines>p' <path>

with the lines below. Paths are relative to the clone root; the four files of
`FingerJetFXOSE/libFRFXLL/src/algorithm/` are given by name alone.

| fact | where |
| --- | --- |
| S-1 | `serializeFpData.h` 367, 386-388, 391, 411-414 |
| S-2 | `intmath.h` 313-315, 324 |
| S-3 | `serializeFpData.h` 372, 396 |
| S-4 | `serializeFpData.h` 258-259, 264-265 |
| S-5 | `serializeFpData.h` 246-250, 287, 293 |
| S-6 | `serializeFpData.h` 203-205 |
| S-7 | `FeatureExtraction.h` 150-151 |
| S-8 | `FeatureExtraction.h` 176-177; `matchData.h` 269 |
| S-9 | `FeatureExtraction.h` 168, 172-173 |
| S-10 | `.../libFRFXLL/samples/FRFXLLSample/frfxllLSample.c` 310-311, 333 |
| S-11 | `FeatureExtraction.h` 51, 247-255, 285-294 |
| S-12 | `FeatureExtraction.h` 36-37, 213-214; `.../libFJFX/src/FJFX.cpp` 77 |
| S-13 | `.../libFJFX/src/FJFX.cpp` 91, 99, 103; `serializeFpData.h` 72, 161, 195, 231, 236-241, 314 |
| S-14 | `.../libFJFX/samples/fjfxSample/fjfxSample.c` 85; `.../libFJFX/src/FJFX.cpp` 65-73 |

In the last four rows `...` stands for the inner `FingerJetFXOSE/` directory
named in Method.

The F facts need no clone. Each is integer arithmetic on the lines above and
reproduces in any language with integer division:

- **F-1** — `[(t*180 + 128)//256 for t in range(256)]` spans 0 to 179 and takes
  180 distinct values.
- **F-2** — `24 + 6 + 6*n` for `n` in 26, 16, 60.
- **F-3** — `64 * 360/256`.
- **F-4** — `[d for d in range(300, 1025) if (d*100 + 50)//254 == 197]`.
- **F-5** — the two bounds of S-12, compared.

The clone is then deleted. It is a third-party source tree, and this repository
does not keep one.

## What was left unchecked

- **Nothing was built and no template was produced here.** Every behavioural
  claim is reported. The confirmations above are readings of source, not
  observations of a running tool.
- **The pipeline between the resampler and the serializer was not traced.**
  Only the lines quoted were read. Whether anything after S-11's resize uses
  the declared resolution is unknown, and it is what would explain a small
  coordinate difference inside the window.
- **The throwaway caller's source was unavailable**, which is precisely what
  leaves X-1 unresolved.
- **The deserializers were not read.** Only the ISO and ANSI serializers and
  the feature-extraction entry points.
- **The standard's own text was still not read.** Everything above establishes
  what one implementation *encodes*; nothing establishes what the standard
  *says*, and an implementation is not a specification.
- **Nothing here relates FingerJetFXOSE's angle to NBIS's.** F-3 states the
  transform in the library's own units and stops there.
- **The dataset resolutions are unverified.** That FVC2002 DB1, DB3 and DB4 are
  500 dpi and DB2 is 569 was reported in `INV-002` R-5 and is not established;
  no dataset manifest exists to carry the field.
- **`muldiv`'s overflow behaviour** was not analysed beyond the rounding rule of
  S-2.
- **One commit.** Whether any of this holds at another revision of the project
  was not examined, and the project publishes no tagged releases (`INV-002`
  R-3).
