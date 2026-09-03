# Licensing

What applies to what, and what was checked. The reasoning behind the decision
is in [quality/REF-003-licensing.md](../quality/REF-003-licensing.md); this
page says how, not why.

Code is licensed MIT, whose text is in `LICENSE`. Every file that is a
document rather than code is licensed CC BY 4.0, whose text is in
`LICENSES/CC-BY-4.0.txt`.

## The boundary

A file is code when a machine executes it or builds from it: a program, a
module, a script, a build file, a configuration that a tool reads in order to
run.

Everything else is a document. A record of an investigation is a document, and
so is a refinement, a manifest, an experiment declaration, a run record and
the observations that support a claim. A score vector is read by a machine and
is still a document: it records what was measured, it does not instruct a
machine to do anything.

The test is what a file is, not where it sits. A script that fetches a pinned
binary and verifies its checksum is code in whatever directory it lives; a
manifest is a document in whatever directory it lives. A directory listing
would rot the first time the layout changed, and the layout is not decided.

Today no tracked file carries a source extension (see "What was checked"), so
apart from the two licence texts every file in the repository is under
CC BY 4.0.

## Attribution

CC BY 4.0 states its conditions as obligations of the reuser — "You" in the
licence text — and they fall into three parts [1, Section 3(a)(1)]:

- retain, if the licensor supplied them, the identification of the creator, a
  copyright notice, a notice referring to the licence, a notice referring to
  the disclaimer of warranties, and a URI or hyperlink to the material;
- indicate whether the material was modified, and retain an indication of any
  previous modifications;
- indicate that the material is licensed under this licence, and include its
  text or a link to it.

Those conditions "may [be satisfied] in any reasonable manner based on the
medium, means, and context in which You Share the Licensed Material"
[1, Section 3(a)(2)].

**What a reuser owes.** Cite this repository as
[CITATION.cff](../CITATION.cff) describes; once a release has been archived
and a DOI exists, cite the DOI. Say that the material is under CC BY 4.0 and
link to the licence. If you changed anything — recomputed a metric under a
different protocol, corrected a record, extracted part of a table — say so, so
that a reader can tell your figure from the one published here. That last part
is yours alone: no citation of the source discharges it.

**What this repository owes.** The first condition only bites on what the
licensor supplied, so the work is to supply it: the creator and the citation
form in `CITATION.cff` and `.zenodo.json`, the copyright line in `LICENSE`,
the licence text in `LICENSES/CC-BY-4.0.txt`, the terms in `README.md`, and a
stable link to the material — the repository URL now, a DOI once a release is
archived.

## The licence texts themselves

`LICENSE` holds the MIT text with this repository's copyright line.
`LICENSES/CC-BY-4.0.txt` holds the Creative Commons text, byte for byte as
Creative Commons publishes it (see "What was checked").

Neither is under CC BY 4.0. A licence text is not this repository's work to
relicense, and both are reproduced on the terms their publishers set.
`.gitattributes` exempts `LICENSES/**` from git's whitespace check so that the
stored text stays identical to the published one, trailing blank line
included.

## What was checked

Commands run on 2026-09-03, with the output they printed.

Zenodo's licence vocabulary holds the lower-case identifier and not the SPDX
spelling:

    $ curl -s -o /dev/null -w "%{http_code}\n" https://zenodo.org/api/vocabularies/licenses/cc-by-4.0
    200
    $ curl -s -o /dev/null -w "%{http_code}\n" https://zenodo.org/api/vocabularies/licenses/CC-BY-4.0
    404
    $ curl -s https://zenodo.org/api/vocabularies/licenses/cc-by-4.0 | python -c "import json,sys;d=json.load(sys.stdin);print(d['id'], '|', d['title']['en'])"
    cc-by-4.0 | Creative Commons Attribution 4.0 International

The Citation File Format accepts a list for `license`, and refuses an
identifier that is not in its schema, so the acceptance means something. The
message of the second command is reproduced with its list of accepted
identifiers cut, marked here by ellipses:

    $ cffconvert --validate -i <a copy with license: [MIT, CC-BY-4.0]>
    Citation metadata are valid according to schema version 1.2.0.
    $ cffconvert --validate -i <a copy with license: NOT-A-LICENCE>
    jsonschema.exceptions.ValidationError: 'NOT-A-LICENCE' is not one of ['0BSD', 'AAL', ... 'CC-BY-4.0', ... 'MIT', ... 'ZPL-2.1']
    $ echo $?
    1

The same format defines what several licences mean together, and it is not
what a reader might assume from the list validating:

    $ curl -s https://raw.githubusercontent.com/citation-file-format/citation-file-format/main/schema-guide.md | grep -n "OR, not AND"
    336:licenses, it is assumed their relationship is OR, not AND.
    1428:- **description**: The [SPDX license identifier(s)](https://spdx.dev/ids/) for the license(s) under which a work is made available. When there are multiple licenses, it is assumed their relationship is OR, not AND.
    3165:When there are multiple licenses, it is assumed their relationship is OR, not AND.

These two checks belong together. The validator says a list parses; the schema
guide says a list means "either licence, at the reuser's choice". Acting on
the first alone would have published terms this repository never agreed to.
A schema saying "this parses" is not a schema saying "this means what you
intended", and only the pair records that.

The stored licence text is byte-identical to the canonical one:

    $ curl -s https://creativecommons.org/licenses/by/4.0/legalcode.txt | sha256sum
    9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411 *-
    $ sha256sum LICENSES/CC-BY-4.0.txt
    9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411 *LICENSES/CC-BY-4.0.txt

No tracked file carries a source extension:

    $ git ls-files | grep -Ei "\.(py|c|h|cc|cpp|rs|go|sh|js|ts)$"
    $ echo $?
    1

## References

1. Creative Commons Attribution 4.0 International, legal code: <https://creativecommons.org/licenses/by/4.0/legalcode.txt>, stored as `LICENSES/CC-BY-4.0.txt`
2. Citation File Format 1.2.0 schema guide: <https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md>
3. Zenodo licence vocabulary: <https://zenodo.org/api/vocabularies/licenses>
