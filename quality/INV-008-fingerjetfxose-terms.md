# INV-008 — The terms stated in the FingerJetFXOSE source this repository builds

Date: 2026-09-07

## Numbering

This record takes 008, the next free investigation number after `INV-007`. The
reservation at 001 is explained in `REF-002`.

## Question

`REF-011` decided three things and could ground only one of them, because no
record in this tree had read this project's terms. `INV-006` is scoped to what
is already in the image and says so; `INV-007` excludes licence reading in its
own "Not in this record". So `REF-011` left an acknowledgement unwritten rather
than guess its wording, and settled a name on a ground that was available
instead of the one that was not.

So: **what do the documents and the source files in this project state about
the terms it is distributed under?**

This record establishes what those texts say. It draws nothing from them. It is
shaped like `INV-006`, which asked the same question of the other tools, so
that the two can be read against each other; the shape is the only thing the
two records share.

## Method

**The pin.** The project's own repository at commit
`1726ba08bf7f2137d2f861ac1ae124d5cd355eee`, tree
`e523e7b7ad5ab6d6e8b0a6fd163696f13e4a8b48`. Both were verified before anything
was read, the way `INV-007` verified them:

    git rev-parse HEAD          -> 1726ba08bf7f2137d2f861ac1ae124d5cd355eee   match: yes
    git rev-parse HEAD^{tree}   -> e523e7b7ad5ab6d6e8b0a6fd163696f13e4a8b48   match: yes

**Documents are pinned by git blob id, not by a digest of the checked-out
bytes.** The clone carried `core.autocrlf = true`, so a content digest of the
working tree would be a fact about this machine and not about the commit, which
is what `INV-003`'s Method found for the same reason. Every quotation below was
produced with `git cat-file -p HEAD:<path>`, which yields the blob, not the
checkout.

**Paths are hints.** Every path named below was confirmed to exist at the
pinned commit before it was read, and a path that does not exist there is
reported as absent rather than passed over. F-6 reports one such absence.

**What this record does not do.** It reads texts and reports what they say. It
does not interpret them, it assigns no identifier to any of them, and it says
nothing about what follows for this repository: `REF-010` decided that frame
and a record of facts may not reopen it.

## F-1 — Which documents state terms

**A top-level licence document exists, and there are three of them.** The
repository root at this commit holds `.gitignore`, `.gitmodules`,
`COPYING.LESSER.txt`, `COPYING.txt`, `COPYRIGHT.txt`, `README.txt`, the
directory `FingerJetFXOSE` and the submodule directory `cxxtest`.

Searching the whole tree for a file whose name contains `licen`, `copying`,
`copyright`, `notice` or `legal`, in any case, returns exactly three, all at
the top level:

| path | blob id | bytes | lines |
| --- | --- | --- | --- |
| `COPYRIGHT.txt` | `850ce3cb8dd375b0ba36087582b7a947a932a6b2` | 6493 | 116 |
| `COPYING.txt` | `94a9ed024d3859793618152ea559a168bbcbb5e2` | 35147 | 674 |
| `COPYING.LESSER.txt` | `65c5ca88a67c30becee01c5a8816d964b03862f9` | 7651 | 165 |

A fourth document states terms without being named for it:

| path | blob id | bytes | lines |
| --- | --- | --- | --- |
| `README.txt` | `6955065d66f6ba86c9f5fc43c07b5e045dc17626` | 5487 | 132 |

Its first sixteen lines carry the same copyright line, the same trademark
sentence and the same granting sentence that F-2 quotes.

The terms are additionally stated as a per-file header on source files; F-5
counts them.

## F-2 — The grant

The sentence that grants rights, quoted in full from the per-file header of
`FingerJetFXOSE/libFJFX/samples/fjfxSample/fjfxSample.c`, lines 10 to 15. Three
of its lines end in a space and they are reproduced as they are:

    FingerJetFX OSE is open source software that you may modify and/or
    redistribute under the terms of the GNU Lesser General Public License
    as published by the Free Software Foundation, either version 3 of the 
    License, or (at your option) any later version, provided that the 
    conditions specified in the COPYRIGHT.txt file provided with this 
    software are met.

The activities it names are the ones in the words "modify and/or redistribute".

The same sentence appears in `COPYRIGHT.txt` at lines 10 to 14 and in
`README.txt` at lines 9 to 14, with one difference between them, in how each
names the document that carries the conditions:

- `COPYRIGHT.txt` line 14, byte-exact, with two spaces between `file` and
  `provided` and with no extension on the name:

      specified in the COPYRIGHT file  provided with this software are met.

- the per-file header and `README.txt`, byte-exact, with one space and with the
  extension:

      conditions specified in the COPYRIGHT.txt file provided with this 

Only one file at this commit is named `COPYRIGHT.txt`; no file is named
`COPYRIGHT`.

## F-3 — The conditions

`COPYRIGHT.txt` numbers its conditions 1 to 10. Each is quoted below in full,
in the document's own numbering, from the blob named in F-1. Before the
numbered list the document states, at lines 18 to 20:

    REDISTRIBUTIONS IN ANY FORMAT, WHETHER MODIFIED OR NOT, MUST RETAIN THE 
    ABOVE COPYRIGHT NOTICE, THIS LIST OF CONDITIONS, AND THE FOLLOWING 
    DISCLAIMERS. 

**1.** (lines 22 to 26)

    1. If the software is MODIFIED, then the following must be added to the top
    of this document:

       This is (or this includes) a MODIFIED version of the Digital Persona
       FingerJetFX OSE fingerprint feature extractor.

**2.** (lines 28 to 30)

    2. Redistributions in any form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the code and the
    documentation and/or other materials provided with the distribution.

**3.** (lines 32 to 41)

    3. Redistributions of any form whatsoever must retain the following 
    acknowledgment:

       "This product includes the DigitalPersona FingerJetFX OSE fingerprint 
       feature extractor. (http://digitalpersona.com/fingerjetfx)" 
     
       This acknowledgement must be included in the end-user documentation 
       included with the redistribution.  Alternately, this acknowledgement 
       may appear in the software itself, if and wherever such third-party 
       acknowledgements normally appear.

**4.** (lines 43 to 47)

    4. All advertising materials mentioning features or use of this software 
    must display the following acknowledgment:

       "This product includes the DigitalPersona FingerJetFX OSE fingerprint 
       feature extractor. (http://digitalpersona.com/fingerjetfx)"  

**5.** (lines 49 to 52)

    5. Advertising or marketing materials must include acknowledgment of 
    FingerJetFX as required herein but may not imply endorsement by 
    DigitalPersona without prior written permission.  For written permission,
    please contact FingerJetFX-OSE@digitalpersona.com.

**6.** (lines 54 to 56)

    6. Products derived from this software may not be called "FingerJet" 
    or "FingerJetFX" nor may "FingerJet" or "FingerJetFX" appear in their names
    without prior written permission from DigitalPersona, Inc.

**7.** (lines 58 to 69)

    7. Disclaimers: The software is not designed, made, or intended for use 
    in an application where failure, malfunction or inaccuracy of the software
    may cause death, serious bodily injury, including, without limitation, use 
    in medical equipment, nuclear facilities, aircraft operation, air traffic 
    control, or life support.  Any such use is prohibited.  You agree that 
    DigitalPersona will not be liable, in whole or in part, for any claims, 
    losses, costs or damages arising out of or in connection with the use and 
    performance of the software in such applications.  If You use the software 
    for such applications, You agree to indemnify, defend and hold 
    DigitalPersona harmless from all claims, actions, losses, liabilities, 
    damages, costs and expenses (including attorney fees) arising out of or 
    relating to such prohibited uses.

**8.** (lines 71 to 80)

    8. Export Restrictions.  You acknowledge and agree that the software is 
    subject to United States export restrictions, and that You will comply with
    all applicable United States and international laws relating to the 
    importing and/or exporting of the Software Product, and will not, directly
    or indirectly, export the software and related technical data in violation
    of the Export Administration Regulations of the U.S. Department of Commerce
    and other applicable laws. You agree to indemnify, defend and hold 
    DigitalPersona harmless from all claims, actions, losses, liabilities, 
    damages, costs and expenses (including attorney fees) arising out of or 
    relating to any breach of such export restrictions. 

**9.** (lines 82 to 92)

    9. Notice to U.S. Government End users:  The software and documentations 
    are "Commercial Items" as that term is defined in 48 C.F.R 2.101, 
    consisting of "Commercial Computer Software" and "Commercial Computer 
    Software Documentation", as such terms are used in 48 C.F.R. 12.212 or 48
    C.F.R. 227.7202, as applicable.  Consistent with 48 C.F.R. 12.212 or 48
    C.F.R. 227.7202-1 through 227.7202-4, as applicable, the Commercial 
    Computer Software and Commercial Computer Software Documentation are being
    licensed to U.S. Government end users (a) only as Commercial Items and 
    (b) with only those rights as are granted to all other end users pursuant 
    to the terms and conditions herein.  Unpublished-rights reserved under the 
    copyright laws of the United States.     

**10.** (lines 94 to 113)

    10. TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL 
    DIGITALPERSONA BE LIABLE TO YOU OR ANY THIRD PARTY FOR ANY SPECIAL, 
    INCIDENTAL, INDIRECT, PUNITIVE OR CONSEQUENTIAL DAMAGES WHATSOEVER, WHETHER
    IN TORT, PRODUCT LIABILITY AND/OR NEGLIGENCE  (INCLUDING, WITHOUT 
    LIMITATION, DAMAGES FOR LOSS OF BUSINESS PROFITS, GOODWILL, BUSINESS 
    INTERRUPTION, LOSS OF BUSINESS INFORMATION, LOSS OF DATA, PRIVACY OR 
    CONFIDENTIALITY, BREACH OF SECURITY SYSTEMS OR ANY OTHER PECUNIARY LOSS) 
    ARISING OUT OF OR RELATING IN ANY WAY TO, THE USE OF, OR INABILITY TO USE 
    THE SOFTWARE, EVEN IF DIGITALPERSONA HAS BEEN ADVISED OF THE POSSIBILITY OF
    SUCH DAMAGES OR LOSSES.  THE SOFTWARE IS SUPPLIED "AS IS", AND THE ENTIRE 
    RISK OF ACCURACY AND SATISFACTORY PERFORMANCE IS WITH YOU. YOU ASSUME ALL 
    RESPONSIBILITY FOR SELECTING THE SOFTWARE PRODUCT TO ACHIEVE YOUR INTENDED 
    RESULTS, AND FOR THE INSTALLATION OF, USE OF, AND RESULTS OBTAINED FROM THE
    SOFTWARE.  DIGITALPERSONA DOES NOT GUARANTEE THAT THE SOFTWARE WILL MEET 
    YOUR REQUIREMENTS OR ALL REQUIREMENTS OF THE SOFTWARE OR HARDWARE WITH 
    WHICH IT INTERACTS.  IN ANY CASE, DIGITALPERSONA'S ENTIRE LIABILITY UNDER 
    ANY PROVISION HEREUNDER SHALL BE LIMITED TO THE AMOUNT ACTUALLY PAID BY YOU
    FOR THE SOFTWARE OR FIVE DOLLARS (US$5.00), WHICHEVER IS GREATER.  SOME 
    JURISDICTIONS DO NOT PERMIT THESE EXCLUSIONS OR LIMITATIONS, SO SUCH 
    EXCLUSIONS OR LIMITATIONS MAY NOT APPLY TO YOU.

After the numbered list the document ends, at lines 115 to 116:

    If you are interested in obtaining a copy of this software under a 
    commercial license, please contact FingerJetFX-OSE@digitalpersona.com.

### The sentence conditions 3 and 4 ask to be reproduced

It occurs twice. **The two occurrences are not byte-identical**, and the
difference is trailing whitespace, so it matters to a record that may have to
reproduce one of them. Shown with `cat -A`, where `$` marks the end of the
line:

- condition 3, lines 35 and 36 — **one** trailing space on the second line:

      "This product includes the DigitalPersona FingerJetFX OSE fingerprint $
      feature extractor. (http://digitalpersona.com/fingerjetfx)" $

- condition 4, lines 46 and 47 — **two** trailing spaces on the second line:

      "This product includes the DigitalPersona FingerJetFX OSE fingerprint $
      feature extractor. (http://digitalpersona.com/fingerjetfx)"  $

A `diff` of the two two-line ranges reports them as differing. The words, the
punctuation, the URL and the line break after `fingerprint` are the same in
both.

## F-4 — The licence texts the project ships

Two full licence texts are in the tree, both at the top level, both listed in
F-1.

| path | blob id | what the text names itself as, in its first two lines |
| --- | --- | --- |
| `COPYING.txt` | `94a9ed02...` | `GNU GENERAL PUBLIC LICENSE` / `Version 3, 29 June 2007` |
| `COPYING.LESSER.txt` | `65c5ca88...` | `GNU LESSER GENERAL PUBLIC LICENSE` / `Version 3, 29 June 2007` |

Each carries, on its fifth and sixth lines, `Everyone is permitted to copy and
distribute verbatim copies of this license document, but changing it is not
allowed.`

**How the granting sentence relates them to the conditions document.** F-2's
sentence names one of the two by name — the lesser one — and names no version
of it beyond "either version 3 of the License, or (at your option) any later
version". It then makes the grant conditional, in the words "provided that the
conditions specified in the COPYRIGHT.txt file provided with this software are
met". So the document that carries the conditions is named inside the grant,
and the conditions of F-3 are reached through it rather than through either
licence text.

`README.txt` lists all three in its own contents, at lines 117 to 119:

    COPYRIGHT.txt        COPYRIGHT NOTICE
    COPYING.txt          GNU GENERAL PUBLIC LICENSE
    COPYING.LESSER.txt   GNU LESSER GENERAL PUBLIC LICENSE

## F-5 — The per-file headers

The same measurement `INV-006` F-1 made for the other tools, so the two records
can be read against each other.

**How many files carry it.** Of the **98** files under `FingerJetFXOSE/` whose
name ends in `.c`, `.cpp`, `.h` or `.hpp`, **all 98** contain the sentence
`FingerJetFX OSE is open source software`.

**Whether it is byte-identical across them: it is not.** Taking each file's
leading comment block, from line 1 to the first line containing `*/`, there are
**five** distinct blocks:

| files | what distinguishes the block |
| --- | --- |
| 83 | the majority block, 18 lines, sha256 `51661f1c45bc73422817d659686a700a788030c599e12deaa7f391396537b504` |
| 7 | line 4 reads `Copyright (c) 2019 by HID Global, Inc. All rights reserved.` instead of `Copyright (c) 2011 by DigitalPersona, Inc. All rights reserved.` |
| 5 | the same change at line 4, and lines 6 and 7 name `HID Global` where the majority names `DigitalPersona` |
| 2 | the same two changes, and line 18 is `*/` where the majority has `*/ ` with a trailing space |
| 1 | the same, and line 2 reads `Minex 3 Wrapper for FingerJetFX OSE -- Fingerprint Feature Extractor, Open Source Edition`, line 6 names `HID, HID Global`, and the line `For more information, please visit digitalpersona.com/fingerjetfx.` is absent |

**The files whose header differs, named.**

- The seven: `libFRFXLL/src/algorithm/matchData.h`,
  `libFRFXLL/src/algorithm/serializeFpData.h`,
  `libFRFXLL/src/lib/CreateFtrSet.h`,
  `libFRFXLL/src/lib/FRFXLLCreateFeatureSetFromRaw.cpp`,
  `libFRFXLL/src/lib/FRFXLLCreateFeatureSetInPlaceFromRaw.cpp`,
  `libFRFXLL/src/lib/FRFXLLCreateLibraryContext.cpp`,
  `libFRFXLL/src/lib/FRFXLLGetMinutiae.cpp`.
- The five: `libFRFXLL/include/FRFXLL.h`,
  `libFRFXLL/samples/FRFXLLSample/frfxllLSample.c`,
  `libFRFXLL/samples/FRFXLLSample/testRawImage.c`,
  `libFRFXLL/src/algorithm/FeatureExtraction.h`,
  `libFRFXLL/test/TestVectors/TestRawImage.c`.
- The two: `libFRFXLL/include/FRFXLL_Results.h`, `libMINEX/src/minex.cpp`.
- The one: `libMINEX/include/minex.h`.

All paths are relative to `FingerJetFXOSE/`.

**The grant itself does not vary.** Taking lines 10 to 15 of each of the 98
files — the six lines F-2 quotes — there is exactly **one** distinct block. The
copyright holder named in the header differs across files; the sentence
granting rights does not.

`COPYRIGHT.txt`, `COPYING.txt`, `COPYING.LESSER.txt` and `README.txt` name only
`DigitalPersona`. No document at the top level names `HID Global`.

## F-6 — Anything under different terms inside what is built

The subtrees that compile into the artefacts `INV-007` F-2 records are
`FingerJetFXOSE/libFRFXLL`, `FingerJetFXOSE/libFJFX` and
`FingerJetFXOSE/libMINEX`.

**Among the C and C++ sources, nothing is outside F-5's header**: F-5 counts 98
of 98 carrying the granting sentence, so there is no source file in the built
subtrees under a different statement of terms. Stated either way, as required:
the search was for a source file not carrying it, and there is none.

**The files in those subtrees that are not C or C++ sources**, 37 of them, are
build files and documentation — `CMakeLists.txt`, `Makefile`, `README.txt`, one
`dpResults.dbg` — and, in `libFJFX/samples/`, **10 files with the extension
`.pgm` and 9 with the extension `.ist`**, in the directories
`libFJFX/samples/images-pgm` and `libFJFX/samples/templates-iso`. None of them
was opened by this record.

**The third-party components `README.txt` names.** At lines 82 to 86 it states:

    FingerJetFX OSE requires
     - CxxTest - open source test framework
     - STLport - portable implementation of Standard Template Library (STL)
    These third party components are included in the folder src/ExternalDependencies for your 
    convenience to ensure that the library builds correctly.

**The folder it names does not exist at this commit.** `git cat-file -t
HEAD:src/ExternalDependencies` reports no such object, and neither do
`HEAD:src`, `HEAD:include`, `HEAD:samples`, `HEAD:Makefile` or
`HEAD:FingerJetFXOSE/src/ExternalDependencies`. `README.txt`'s own contents
list, at lines 116 to 124, describes `Makefile`, `include`, `src` and `samples`
at the top level, and none of those four is present.

Of the two components it names, `CxxTest` is present at this commit, as the
submodule F-7 records and not as a folder inside the tree. `STLport` is named
in `README.txt` and in two files, `libFRFXLL/test/testFRFXLL/Makefile` and
`libFRFXLL/test/testFRFXLLInternals/Makefile`, and no directory or source file
of that name is in the tree.

## F-7 — The fourth party

`cxxtest`, at the submodule commit `INV-007`'s Method records, verified here:

    git rev-parse HEAD  -> a19f85fdf90f97e16d6e3e7e3d2d68c31cd89e3c   match: yes

**It ships one licence document.** Searching its tree for a file whose name
contains `licen`, `copying`, `copyright`, `notice` or `legal`, in any case,
returns exactly one:

| path | blob id | bytes |
| --- | --- | --- |
| `COPYING` | `65c5ca88a67c30becee01c5a8816d964b03862f9` | 7651 |

**The licence that document names itself as**, in its first two lines, which
are centred in the file and are reproduced here with their own leading
whitespace:

                       GNU LESSER GENERAL PUBLIC LICENSE
                           Version 3, 29 June 2007

**That blob id is the same as `COPYING.LESSER.txt`'s** in F-1 and F-4: the two
files are the same bytes.

**What it builds.** `INV-007` F-3 records that the two artefacts run as test
suites, `testFRFXLL` and `testFRFXLLInternals`, are built from this submodule,
and `INV-007` F-2 lists them among the twelve artefacts of the build. `INV-007`
records no other artefact as built from it. This record states that separation
and draws nothing from it.

## Reproducing this

    git clone https://github.com/FingerJetFXOSE/FingerJetFXOSE.git src
    cd src
    git checkout 1726ba08bf7f2137d2f861ac1ae124d5cd355eee
    git rev-parse HEAD
    git rev-parse 'HEAD^{tree}'

Every document is addressed through the blob, never through the checkout:

    git rev-parse HEAD:COPYRIGHT.txt        # 850ce3cb8dd375b0ba36087582b7a947a932a6b2
    git cat-file -s HEAD:COPYRIGHT.txt      # 6493
    git cat-file -p HEAD:COPYRIGHT.txt      # the text F-3 quotes

and the same three commands for `COPYING.txt`, `COPYING.LESSER.txt` and
`README.txt`.

F-1's search for documents by name:

    git ls-files | grep -iE '(licen|copying|copyright|notice|legal)'

F-2 and F-3 quote by line range from the blob:

    git cat-file -p HEAD:COPYRIGHT.txt | sed -n '<range>p'
    git cat-file -p HEAD:FingerJetFXOSE/libFJFX/samples/fjfxSample/fjfxSample.c \
      | sed -n '10,15p'

and the byte-exact forms with `cat -A` appended to the same pipe. The
comparison of the two acknowledgement occurrences:

    diff <(git cat-file -p HEAD:COPYRIGHT.txt | sed -n '35,36p') \
         <(git cat-file -p HEAD:COPYRIGHT.txt | sed -n '46,47p')

F-5's counts, over every file under `FingerJetFXOSE/` ending in `.c`, `.cpp`,
`.h` or `.hpp`: for each, `git cat-file -p HEAD:<path>`, then the presence of
the string `FingerJetFX OSE is open source software`; then the leading comment
block, taken from line 1 to the first line containing `*/`, grouped by its
sha256; then lines 10 to 15 alone, grouped the same way.

F-6's absences:

    git cat-file -t HEAD:src/ExternalDependencies    # reports no such object
    git ls-files FingerJetFXOSE/libFRFXLL FingerJetFXOSE/libFJFX \
                 FingerJetFXOSE/libMINEX | grep -vE '\.(c|cpp|h|hpp)$'
    git grep -il stlport HEAD -- .

F-7:

    git submodule update --init cxxtest
    cd cxxtest && git rev-parse HEAD
    git ls-files | grep -iE '(licen|copying|copyright|notice|legal)'
    git rev-parse HEAD:COPYING && git cat-file -s HEAD:COPYING
    git cat-file -p HEAD:COPYING | head -2

The clone was deleted when this record was finished.

## What was left unchecked

- **Whether any condition applies to this repository.** `REF-010` decided the
  frame within which that question is asked, and a record of facts does not
  reopen it. Nothing above says what follows from any sentence it quotes.
- **Whether the conditions of F-3 are consistent with the licence text F-4
  names.** The grant makes one conditional on the other; whether the two can
  both hold is not a question this record asks, and nothing here compares them.
- **Whether the terms differ at any other revision of the project.** One commit
  was read. `INV-007` records that the repository carries no tag, so there is
  no released version to read instead.
- **Anything about the wording's legal effect**, in any jurisdiction. The
  record establishes what the words are.
- **The two full licence texts were not read beyond their first six lines and
  the lines F-4 quotes.** Their blob ids and sizes are recorded, so the text
  each names is addressable, but neither was read through.
- **The 19 sample images and templates F-6 counts.** They were counted by
  extension and directory and none was opened.
- **Why 15 of the 98 headers name a different holder from every top-level
  document.** F-5 records that they do and where; it does not establish how
  that came about.
- **`cxxtest` beyond its one licence document.** Its sources were not read, and
  no per-file header measurement was made on it.
