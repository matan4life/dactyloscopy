# INV-006 — The terms stated in the archive the image's tools are built from

Date: 2026-09-07

## Numbering

This record takes 006, the next free investigation number after `INV-005`. 002
to 005 are taken and 001 is reserved for the reason `REF-002` gives.

## Question

Two binaries have been in the runtime image since `630afae`, and no record in
the tree states on what terms they are there. `REF-003` settles the licence of
this repository's own code and documents and says nothing about anything else.

So: **what do the files those two binaries are built from state about the terms
on which they are distributed, and what third-party components reach them?**

This record establishes what the texts say and what the build links. It draws
no conclusion from either.

## Method

Everything below is read from the archive `manifests/MAN-tools.v1.json` pins,
or measured inside the image this repository's `Dockerfile` builds. Nothing is
read from a working copy on the host, and nothing is read from the third-party
mirror that manifest also records.

The archive is fetched and verified before it is unpacked, the way the build
does it:

    curl -fsSL -o nbis.zip https://nigos.nist.gov/nist/nbis/nbis_v5_0_0.zip
    echo "0adf8ab0f6b0e4208de50ca00ba21d3d77112ecd66288757ddfed21f6bee92c3  nbis.zip" \
      | sha256sum -c -            # nbis.zip: OK
    unzip -q nbis.zip             # unpacks into Rel_5.0.0/

Every path in this record was found by searching that unpacked archive, not by
following a path suggested from elsewhere. Where a search returned nothing, the
absence is stated as a result rather than passed over.

The library lists in `Makefile`s are conditional, and F-5 resolves the
conditions against the `rules.mak` the builder stage generates when it runs
`./setup.sh /usr/local/nbis --without-X11 --64`, not against any default. The
resolution is then checked against the link command the build actually issues.

Two things this record does not do. It reads texts and reports what they say;
it does not interpret them. And its subject is the two binaries the image
carries and the archive they are built from, and nothing else.

## F-1 — Where the terms are stated

**There is no top-level licence document.** Searching the archive root for a
file whose name begins with `licen`, `copying`, `copyright`, `notice` or
`legal`, in any case, returns nothing. The archive root holds `CHANGELOG.txt`,
three `INSTALL_*.txt` files, a `Makefile`, `setup.sh`, three `rules*.mak.src`
files, `am_big_endian.c` and the package directories, and no licence document
among them.

The terms are stated as a per-file header instead.

**How many files carry it.** Searching the whole archive for the string
`Pursuant to title 17 Section 105`:

- **658** files of any type contain it;
- **472** of those are `.c` or `.h` files;
- of those 472, the first 42 lines of **all 472** digest to
  `ea00488a1316df5ac5b7a6fc00b5b37d7043682683ee7f522ca4740b4b2a6eb6`. The
  header is byte-identical across every C source and header that carries it,
  not merely similar.

By package, over `.c` and `.h` files: `commonnbis` 141, `imgtools` 111,
`pcasys` 101, `an2k` 52, `mindtct` 36, `nfiq` 10, `bozorth3` 10, `nfseg` 4,
`misc` 3, `ijg` 3, and the top-level `am_big_endian.c`.

**The header, quoted in full**, from lines 1 to 42 of
`mindtct/src/bin/mindtct/mindtct.c`. Four of its lines end in a space, and they
are reproduced as they are:

    /*******************************************************************************

    License: 
    This software and/or related materials was developed at the National Institute
    of Standards and Technology (NIST) by employees of the Federal Government
    in the course of their official duties. Pursuant to title 17 Section 105
    of the United States Code, this software is not subject to copyright
    protection and is in the public domain. 

    This software and/or related materials have been determined to be not subject
    to the EAR (see Part 734.3 of the EAR for exact details) because it is
    a publicly available technology and software, and is freely distributed
    to any interested party with no licensing requirements.  Therefore, it is 
    permissible to distribute this software as a free download from the internet.

    Disclaimer: 
    This software and/or related materials was developed to promote biometric
    standards and biometric technology testing for the Federal Government
    in accordance with the USA PATRIOT Act and the Enhanced Border Security
    and Visa Entry Reform Act. Specific hardware and software products identified
    in this software were used in order to perform the software development.
    In no case does such identification imply recommendation or endorsement
    by the National Institute of Standards and Technology, nor does it imply that
    the products and equipment identified are necessarily the best available
    for the purpose.

    This software and/or related materials are provided "AS-IS" without warranty
    of any kind including NO WARRANTY OF PERFORMANCE, MERCHANTABILITY,
    NO WARRANTY OF NON-INFRINGEMENT OF ANY 3RD PARTY INTELLECTUAL PROPERTY
    or FITNESS FOR A PARTICULAR PURPOSE or for any purpose whatsoever, for the
    licensed product, however used. In no event shall NIST be liable for any
    damages and/or costs, including but not limited to incidental or consequential
    damages of any kind, including economic damage or injury to property and lost
    profits, regardless of whether NIST shall be advised, have reason to know,
    or in fact shall know of the possibility.

    By using this software, you agree to bear all risk relating to quality,
    use and performance of the software and/or related materials.  You agree
    to hold the Government harmless from any claim arising from your use
    of the software.

    *******************************************************************************/

**The two texts are identical, by comparison and not by impression.** Lines 1
to 42 of `mindtct/src/bin/mindtct/mindtct.c` and lines 1 to 42 of
`bozorth3/src/bin/bozorth3/bozorth3.c` were written to two files and compared:
`cmp` reports no difference, both blocks are 2376 bytes, and both digest to
`ea00488a1316df5ac5b7a6fc00b5b37d7043682683ee7f522ca4740b4b2a6eb6`.

**One file in a library on a link line carries a different notice.** Of the ten
`.c` and `.h` files in `imgtools/src/lib/wsq`, nine carry the header above and
one does not: `imgtools/src/lib/wsq/cropcoeff.c`, sha256
`e7750d294e552f45ceeb12276c0a4c0061eef9ff78d79ebcc67071bf650abda9`. Its first
lines read:

    /************************************************************************
                                   NOTICE
     
    This MITRE-modified NIST code was produced for the U. S. Government
    under Contract No. W15P7T-07-C-F700. Pursuant to Title 17 Section 105 
    of the United States Code, this software is not subject to copyright 
    protection and is in the public domain. NIST and MITRE assume no 
    responsibility whatsoever for use by other parties of its source code 
    or open source server, and makes no guarantees, expressed or implied,
    about its quality, reliability, or any other characteristic.

## F-2 — What the header claims

Five statements, each quoted from the block above. They are claims the text
makes; this record establishes that the text makes them and nothing further.

**1. Who developed it.**

    This software and/or related materials was developed at the National Institute
    of Standards and Technology (NIST) by employees of the Federal Government
    in the course of their official duties.

**2. What title 17 section 105 is said to imply.**

    Pursuant to title 17 Section 105
    of the United States Code, this software is not subject to copyright
    protection and is in the public domain. 

**3. The export-control statement.**

    This software and/or related materials have been determined to be not subject
    to the EAR (see Part 734.3 of the EAR for exact details) because it is
    a publicly available technology and software, and is freely distributed
    to any interested party with no licensing requirements.  Therefore, it is 
    permissible to distribute this software as a free download from the internet.

**4. The warranty disclaimer.**

    This software and/or related materials are provided "AS-IS" without warranty
    of any kind including NO WARRANTY OF PERFORMANCE, MERCHANTABILITY,
    NO WARRANTY OF NON-INFRINGEMENT OF ANY 3RD PARTY INTELLECTUAL PROPERTY
    or FITNESS FOR A PARTICULAR PURPOSE or for any purpose whatsoever, for the
    licensed product, however used. In no event shall NIST be liable for any
    damages and/or costs, including but not limited to incidental or consequential
    damages of any kind, including economic damage or injury to property and lost
    profits, regardless of whether NIST shall be advised, have reason to know,
    or in fact shall know of the possibility.

**5. The clause about bearing risk.**

    By using this software, you agree to bear all risk relating to quality,
    use and performance of the software and/or related materials.  You agree
    to hold the Government harmless from any claim arising from your use
    of the software.

The block contains one further paragraph, quoted here so that the separation
accounts for every line of it and none is dropped. It sits under the heading
`Disclaimer:` together with statement 4:

    This software and/or related materials was developed to promote biometric
    standards and biometric technology testing for the Federal Government
    in accordance with the USA PATRIOT Act and the Enhanced Border Security
    and Visa Entry Reform Act. Specific hardware and software products identified
    in this software were used in order to perform the software development.
    In no case does such identification imply recommendation or endorsement
    by the National Institute of Standards and Technology, nor does it imply that
    the products and equipment identified are necessarily the best available
    for the purpose.

## F-3 — Every licence document in the archive

Fifteen files, found by searching the whole archive for a name matching
`licen*`, `copying*`, `copyright*`, `notice*`, `legal*` or `*.license`, in any
case. Path and sha256, in path order:

    cc32790553f3c5ab1b7743cc75ec62bb2c36b10ff4850c80d4ad943b76b3bfe0  jpeg2k/src/lib/jasper/COPYRIGHT
    edf9f4257cc33a1f396f9b062ca4a01dca7c79747c7d85b8947e603e5166760e  jpeg2k/src/lib/jasper/LICENSE
    c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4  misc/nistmeshlab/meshlab/src/distrib/plugins/U3D_W32/License.txt
    92cb47d36059a39bb06dd6cb97354ca18412da5a96104d85d972434009c91f6d  misc/nistmeshlab/meshlab/src/distrib/plugins/U3D_W32/LicensesAdditional.txt
    c20ebf6c7a24f387a8deeedd1399e3484b2c59a72088e74761006bd1b3543574  misc/nistmeshlab/meshlab/src/external/ann_1.1.1/Copyright.txt
    81d15b6bb9472b2eccac12b2799afa0b0ddefaca91d5dfb01bfe1ea3a2fd52cd  misc/nistmeshlab/meshlab/src/external/ann_1.1.1/License.txt
    38a38de1748714672193f12c6412489a00ff65a61e1bd2da9f360db990d156cf  misc/nistmeshlab/meshlab/src/external/glew-1.5.1/LICENSE.txt
    944f423020fc842c54be3818a1c58431814331c751d285d087aa19904ec6cc31  misc/nistmeshlab/meshlab/src/external/muparser_v130/License.txt
    ea5cccab7bfd94b3bc74e2d950cde63c3f6e726deb253268a4a5effc572aef03  misc/nistmeshlab/meshlab/src/external/qhull-2003.1/COPYING.txt
    417ec1bd27fb246004799dd3cf69b5756c7fc9f6697207b2d478a9d6830520ba  misc/nistmeshlab/meshlab/src/meshlabplugins/filter_poisson/license.txt
    a6af136f3e15038a666b61f376612a07d9a4e48cb7c01adbf3e33b3f14ab49b6  openjp2/src/lib/openjp2/LICENSE
    8081c33f6953950dcf424aa844714658b73ada0fcaea16e4487f5fa07ef0960d  openjp2/src/lib/openjp2/src/bin/wx/OPJViewer/source/license.txt
    91ac8ae445d9d6e2d5be01747eb2bd459119fe446c6fc69cc618fb0d7ff32005  openjp2/src/lib/openjp2/thirdparty/liblcms2/COPYING
    6f9c08ec7ea54f33508bf7ac1b5c9f694206440e92d134c1c30d8aa22ec01351  openjp2/src/lib/openjp2/thirdparty/libpng/LICENSE
    80547593e770340d546deb5c6d9ef7e690ffcab8dafbc093d83fd627331fcef6  png/src/lib/png/LICENSE

## F-4 — What is linked into `bozorth3`

`bozorth3/src/bin/bozorth3/Makefile`, lines 58 to 67, verbatim. The file has no
conditional:

    PROGRAM	:= bozorth3
    #
    SRC	:= bozorth3.c \
    	usage.c
    #
    LIBS	:= $(EXPORTS_LIB_DIR)/libbozorth3.a 
    #
    EXT_INCS	:= -I$(EXPORTS_INC_DIR)
    #
    EXT_LIBS	:= -lm

One archive, `libbozorth3.a`, and the C mathematics library.

## F-5 — What is linked into `mindtct`

`mindtct/src/bin/mindtct/Makefile`, lines 67 to 108. The unconditional list:

    LIBS	:= \
    	$(EXPORTS_LIB_DIR)/libmindtct.a \
    	$(EXPORTS_LIB_DIR)/liban2k.a \
    	$(EXPORTS_LIB_DIR)/libimage.a \
    	$(EXPORTS_LIB_DIR)/libihead.a \
    	$(EXPORTS_LIB_DIR)/libwsq.a \
    	$(EXPORTS_LIB_DIR)/libjpegl.a \
    	$(EXPORTS_LIB_DIR)/libjpegb.a \
    	$(EXPORTS_LIB_DIR)/libfet.a \
    	$(EXPORTS_LIB_DIR)/libcblas.a \
    	$(EXPORTS_LIB_DIR)/libioutil.a \
    	$(EXPORTS_LIB_DIR)/libutil.a

then three conditionals adding `libjasper.a`, `libopenjp2.a`, and
`libpng.a` with `libz.a`, and a fourth on `MSYS_FLAG` adding `-liberty` to
`EXT_LIBS`.

**The flags, quoted from the `rules.mak` the builder stage generated**, lines
82 to 88 of `/src/rules.mak` in the image built by this repository's
`Dockerfile`:

    82:NBIS_JASPER_FLAG		:= 
    83:NBIS_OPENJP2_FLAG		:= -D__NBIS_OPENJP2__
    84:NBIS_PNG_FLAG			:= -D__NBIS_PNG__
    88:MSYS_FLAG			:= 

`NBIS_JASPER_FLAG` and `MSYS_FLAG` are empty, so neither equals the value its
`ifeq` tests and neither block is taken. The other two match, so both blocks
are taken.

**The resolved list is fourteen archives and `-lm`:** the eleven above, plus
`libopenjp2.a`, `libpng.a` and `libz.a`. Not `libjasper.a`, and not
`-liberty`.

Checked against the link command the build issues, by deleting the binary and
re-linking it in the builder stage, which named exactly:

    libmindtct.a liban2k.a libimage.a libihead.a libwsq.a libjpegl.a
    libjpegb.a libfet.a libcblas.a libioutil.a libutil.a libopenjp2.a
    libpng.a libz.a -lm

## F-6 — The components that reach a shipped binary and are not NIST's own code

The criterion used, and its limit. Each library directory on a link line was
counted for `.c` and `.h` files carrying the header of F-1:

| library | directory | `.c`/`.h` files | carrying the header |
| --- | --- | --- | --- |
| `libbozorth3` | `bozorth3/src/lib/bozorth3` | 6 | 6 |
| `libmindtct` | `mindtct/src/lib/mindtct` | 31 | 31 |
| `liban2k` | `an2k/src/lib/an2k` | 28 | 28 |
| `libimage` | `imgtools/src/lib/image` | 25 | 25 |
| `libihead` | `imgtools/src/lib/ihead` | 8 | 8 |
| `libwsq` | `imgtools/src/lib/wsq` | 10 | 9 |
| `libjpegl` | `imgtools/src/lib/jpegl` | 9 | 9 |
| `libjpegb` | `ijg/src/lib/jpegb` | 92 | 3 |
| `libfet` | `commonnbis/src/lib/fet` | 11 | 11 |
| `libcblas` | `commonnbis/src/lib/cblas` | 18 | 18 |
| `libioutil` | `commonnbis/src/lib/ioutil` | 9 | 9 |
| `libutil` | `commonnbis/src/lib/util` | 11 | 11 |
| `libopenjp2` | `openjp2/src/lib/openjp2` | 393 | 0 |
| `libpng` | `png/src/lib/png` | 21 | 0 |
| `libz` | `png/src/lib/zlib` | 25 | 0 |

The header settles which files carry NIST's notice. It does not settle where a
file came from, and one entry shows the difference: see `libcblas` below.

### `libjpegb`, from `ijg/src/lib/jpegb`

**No licence file.** No file in that directory has a name matching the F-3
search. The terms are in `ijg/src/lib/jpegb/README`, sha256
`4a41c9bce116ce56d3d12532088e819ebfd7f41248019ac72bcc9cdc1165f484`, 385 lines,
in a section headed `LEGAL ISSUES` beginning at line 111.

**The name the file states.** The section names no licence. It refers to the
software as follows:

    This software may be referred to only as "the Independent JPEG Group's
    software".

and states three numbered conditions, of which the first bears on this record:

    (1) If any part of the source code for this software is distributed, then this
    README file must be included, with this copyright and no-warranty notice
    unaltered; and any additions, deletions, or changes to the original files
    must be clearly indicated in accompanying documentation.
    (2) If only executable code is distributed, then the accompanying
    documentation must state that "this software is based in part on the work of
    the Independent JPEG Group".

### `libopenjp2`, from `openjp2/src/lib/openjp2`

**Licence file:** `openjp2/src/lib/openjp2/LICENSE`, sha256
`a6af136f3e15038a666b61f376612a07d9a4e48cb7c01adbf3e33b3f14ab49b6`, 39 lines.

**The name the file states**, in its first sentence:

     * The copyright in this software is being made available under the 2-clauses 
     * BSD License, included below. This software may be subject to other third 
     * party and contributor rights, including patent rights, and no such rights
     * are granted under this license.

### `libpng`, from `png/src/lib/png`

**Licence file:** `png/src/lib/png/LICENSE`, sha256
`80547593e770340d546deb5c6d9ef7e690ffcab8dafbc093d83fd627331fcef6`, 109 lines.

**The name the file states: none.** Its heading is

    COPYRIGHT NOTICE, DISCLAIMER, and LICENSE:

and where it refers to the terms it refers to them by version of libpng rather
than by a name, for example at line 13:

    distributed according to the same disclaimer and license as libpng-1.2.5

The same form appears at lines 20, 38 and 47. No line of the file gives the
licence a name.

### `libz`, from `png/src/lib/zlib`

**No licence file.** No file in that directory has a name matching the F-3
search. The terms appear twice: in `png/src/lib/zlib/README`, sha256
`365db9b693fda6c66ddd97d81ae3eb17be32c890909553973a77439d85900494`, from line
93 under the heading `Copyright notice:`; and in `png/src/lib/zlib/zlib.h`,
sha256 `ebceab9efa0d906fcc28dabb864ae63d99da8e5efe56e030cb9cb96578622245`, at
lines 4 to 23:

      Copyright (C) 1995-2005 Jean-loup Gailly and Mark Adler
    
      This software is provided 'as-is', without any express or implied
      warranty.  In no event will the authors be held liable for any damages
      arising from the use of this software.
    
      Permission is granted to anyone to use this software for any purpose,
      including commercial applications, and to alter it and redistribute it
      freely, subject to the following restrictions:
    
      1. The origin of this software must not be misrepresented; you must not
         claim that you wrote the original software. If you use this software
         in a product, an acknowledgment in the product documentation would be
         appreciated but is not required.
      2. Altered source versions must be plainly marked as such, and must not be
         misrepresented as being the original software.
      3. This notice may not be removed or altered from any source distribution.

**The name the file states: none.** Neither text names a licence.

### `libcblas`, from `commonnbis/src/lib/cblas`

Every one of its 18 `.c` files carries the header of F-1, so the table above
places it with NIST's own code. Every one of the same 18 files also states a
retrieval from elsewhere. From `commonnbis/src/lib/cblas/sgemm.c`, lines 45 to
53:

    /*
    * ======================================================================
    * NIST Guide to Available Math Software.
    * Source for module SGEMM.C from package CBLAS.
    * Retrieved from NETLIB on Tue Mar 14 10:54:01 2000.
    *
    * UPDATED: 03/09/2005 by MDG
    * ======================================================================
    */

Other files in the directory name origins outside NIST in the same way, for
example `commonnbis/src/lib/cblas/lsame.c` at lines 73 to 75:

    /*  -- LAPACK auxiliary routine (version 2.0) --   
           Univ. of Tennessee, Univ. of California Berkeley, NAG Ltd.,   
           Courant Institute, Argonne National Lab, and Rice University   

**No licence file.** No file in `commonnbis/src/lib/cblas` has a name matching
the F-3 search, and the string `Retrieved from NETLIB` appears in 18 of its 18
`.c` files and in no file of any other library on a link line.

`INV-004` records a separate measurement about this archive: of the 92 symbols
`libcblas.a` defines, 0 appear in the `mindtct` binary. It is on the link line
and contributes no code to the binary.

## F-7 — Alteration

**The search, so that its completeness can be judged.** Three passes over the
four third-party directories on the link lines — `ijg/src/lib/jpegb`,
`openjp2/src/lib/openjp2`, `png/src/lib/png`, `png/src/lib/zlib`:

1. every file whose name contains `nist`, in any case;
2. every file containing `NIST` or `NBIS` as a whole word;
3. every line matching `modified (to|for|by)`, `was modified`,
   `modification[s]? (to|by|for)`, `added (by|for) (NIST|NBIS)` or
   `changed (by|for) (NIST|NBIS)`, case-insensitively.

The second pass was first run without word boundaries and gave a false count.
Both are reported, because the difference is what makes the result judgeable:

| directory | files matching `-i 'NIST\|NBIS'` | files matching the same as whole words |
| --- | --- | --- |
| `ijg/src/lib/jpegb` | 4 | 4 |
| `openjp2/src/lib/openjp2` | 24 | 6 |
| `png/src/lib/png` | 1 | 1 |
| `png/src/lib/zlib` | 5 | **0** |

Every one of zlib's five naive matches is a substring of another word. The
matched contexts are `for unistd.h in`, `for unistd.h...`, `HAVE_UNISTD_H --`,
`HAVE_UNISTD_H th`, `HAVE_UNISTD_H/s%`, `eterministic (no` and
`ude <unistd.h>`. **The bundled zlib names NIST and NBIS nowhere.**

**What the passes found.**

`png/src/lib/png/README.NIST`, sha256
`893af50ce4e4085b3b41b8dc7cb8c280108a4910242fb4f4da0d058595b58d12`, 68 bytes,
one line, in full:

    This PNG library was modified to fit the need of the NBIS software.

`openjp2/src/lib/openjp2` — four of the six whole-word matches are in the
library's own sources, which are what `libopenjp2.a` is built from:

- `src/lib/openjp2/jp2.c` at lines 111, 762, 772, 1451, 1458 and 1751, for
  example line 111, `/* NIST: Writes custom RES box`, and line 772,
  `/* NIST: Convert PPI values above 1664 */`;
- `src/lib/openjp2/jp2.h` at lines 63 and 187, `/* NIST (The future is now) */`
  and `OPJ_UINT32 samplerate; /* NIST */`;
- `src/lib/openjp2/openjpeg.c` at lines 643, 646 and 662, of which line 643
  records a changed default:

      parameters->rsiz = OPJ_NIST_PROFILE;	/* Use NIST Profile (Profile 1) by default (Previous value: OPJ_PROFILE_NONE) */

- `src/lib/openjp2/openjpeg.h` at lines 193, 245 and 406, which define
  `OPJ_NIST_PROFILE` and `OPJ_NIST_RSIZ`.

The other two are in `src/bin/jp2/`, which is not part of the library. One of
them states the alteration in a help message, at
`openjp2/src/lib/openjp2/src/bin/jp2/opj_compress.c` line 190:

    "\nmodified by NIST to compress various image formats using the JPEG 2000 "

`ijg/src/lib/jpegb` — five of its 92 `.c` and `.h` files name a NIST author in
an `AUTHORS:` line: `decoder.c`, `encoder.c`, `marker.c`, `membuf.c` and
`ppi.c`. Three of those five, `marker.c`, `membuf.c` and `ppi.c`, carry the
header of F-1. Two state the derivation in prose; from
`ijg/src/lib/jpegb/decoder.c` lines 13 to 16, and identically in `encoder.c` at
the same lines:

          This software uses the Independent JPEG Group's (IJG)
          libraries for decompressing JPEGB images.  In fact
          these routines were derived from their code and
          modified to fit our needs.

`png/src/lib/zlib` — nothing. No file in the bundled zlib states an alteration,
and none names NIST or NBIS.

**The one further alteration statement inside a NIST library**, found by the
same passes applied to the libraries the table in F-6 counts as NIST's, is the
MITRE notice quoted in F-1 at `imgtools/src/lib/wsq/cropcoeff.c`. `libwsq` is
on `mindtct`'s link line.

**What the search would not have found.** An alteration made without a comment
saying so is invisible to all three passes. This record establishes what is
stated, not what was done.

## F-8 — The base image, as one number

Measured inside the image this repository's `Dockerfile` builds:

    files matching /usr/share/doc/*/copyright : 105
    the path pattern                          : /usr/share/doc/<package>/copyright

Nothing else about the base image is measured here.

## Reproducing this

The archive, verified and unpacked as in Method, then from `Rel_5.0.0/`:

F-1, the absence of a top-level document, the counts, and the identity of the
two headers:

    ls -a | grep -iE '^(licen[cs]e|copying|copyright|notice|legal)'
    grep -rlF 'Pursuant to title 17 Section 105' . | wc -l
    grep -rlF --include='*.c' --include='*.h' 'Pursuant to title 17 Section 105' . | wc -l
    for f in $(grep -rlF --include='*.c' --include='*.h' \
                 'Pursuant to title 17 Section 105' .); do
      sed -n '1,42p' "$f" | sha256sum
    done | sort | uniq -c
    sed -n '1,42p' mindtct/src/bin/mindtct/mindtct.c   > /tmp/h_min.txt
    sed -n '1,42p' bozorth3/src/bin/bozorth3/bozorth3.c > /tmp/h_boz.txt
    cmp /tmp/h_min.txt /tmp/h_boz.txt && sha256sum /tmp/h_min.txt /tmp/h_boz.txt
    sed -n '1,20p' imgtools/src/lib/wsq/cropcoeff.c

F-2 quotes lines 3-8, 10-14, 16-25, 27-35 and 37-40 of that same header, each
by `sed -n '<range>p' mindtct/src/bin/mindtct/mindtct.c`.

F-3:

    find . -type f \( -iname 'licen*' -o -iname 'copying*' -o -iname 'copyright*' \
      -o -iname 'notice*' -o -iname 'legal*' -o -iname '*.license' \) \
      | sort | while read f; do sha256sum "$f"; done

F-4 and the Makefile part of F-5:

    sed -n '58,67p'  bozorth3/src/bin/bozorth3/Makefile
    sed -n '67,108p' mindtct/src/bin/mindtct/Makefile

F-5's flags and its check, in the builder stage of this repository:

    docker build --target nbis-builder -t nbis-terms:read .
    docker run --rm nbis-terms:read bash -c \
      "grep -nE '^(NBIS_JASPER_FLAG|NBIS_PNG_FLAG|NBIS_OPENJP2_FLAG|MSYS_FLAG)' /src/rules.mak"
    docker run --rm nbis-terms:read bash -c \
      "cd /src && rm -f mindtct/bin/mindtct && make -C mindtct/src/bin/mindtct"

F-6's table, per directory:

    find <dir> -name '*.[ch]' | wc -l
    grep -rlF --include='*.c' --include='*.h' \
      'Pursuant to title 17 Section 105' <dir> | wc -l

and the quotations by `sed -n '<range>p'` at the paths and line numbers given,
with each digest by `sha256sum <path>`.

F-7's three passes:

    find <the four dirs> -type f -iname '*nist*'
    grep -rlEi 'NIST|NBIS' <dir> | wc -l          # the naive count
    grep -rlEw 'NIST|NBIS|NISTCOM' <dir> | wc -l  # the whole-word count
    grep -rniE 'modified (to|for|by)|was modified|modification[s]? (to|by|for)|added (by|for) (NIST|NBIS)|changed (by|for) (NIST|NBIS)' <the four dirs>
    grep -rlE 'AUTHORS?:.*(Michael Garris|Craig Watson)' ijg/src/lib/jpegb

F-8:

    docker run --rm dactyloscopy:dev bash -c 'ls -1 /usr/share/doc/*/copyright | wc -l'

## What was left unchecked

- **Whether title 17 section 105 has any effect outside the United States.**
  It is a legal question and nothing in this repository can measure it. What is
  established is that the header states what F-2 statement 2 quotes.
- **Whether the export-control statement is current.** It is a claim NIST made
  at the release this archive is. Nothing here checks it against anything, and
  the archive carries no date on the statement itself.
- **Whether any obligation attaches to this repository.** Nothing in this
  record addresses it. It depends on facts this record does not establish,
  among them whether the image is ever published.
- **What the base image's packages are licensed under.** Only the count in F-8
  was measured, deliberately. No file under `/usr/share/doc/` was opened.
- **Whether a file carrying the header of F-1 is originally NIST's work.** The
  header is a notice, and `libcblas` in F-6 is a case where files carrying it
  also state a retrieval from elsewhere. The same question was not asked of the
  other twelve libraries beyond the `Retrieved from NETLIB` search, which found
  nothing in any of them.
- **Alterations made without a comment.** F-7 finds statements, not changes. No
  bundled component was compared against an upstream release of the same
  version, and this archive carries no upstream copy to compare against.
- **The other eleven licence documents of F-3.** Their paths and digests are
  recorded; their contents were not read, because none of them belongs to a
  component on a link line of F-4 or F-5.
- **`jpeg2k/src/lib/jasper`.** Two licence documents of F-3 are in it. F-5
  resolves `NBIS_JASPER_FLAG` to empty, so no part of it is linked into either
  binary, and nothing further about it was examined.
