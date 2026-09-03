# REF-003 — Licensing

Date: 2026-09-03
Rests on: no investigation. Every statement below about GitHub, Zenodo, the
Citation File Format or a licence text is either cited to documentation (see
References) or was verified by a command whose output is recorded in
`docs/licensing.md`. This refinement adds no fact of its own.

## Decision

Code is licensed MIT. Every file that is a document rather than code is
licensed CC BY 4.0. `README.md` states the terms; `docs/licensing.md` states
which files fall on which side, and what each party owes.

The boundary is drawn by what a file is, not by which directory it sits in.
A directory settles nothing: a script that fetches a pinned binary is code
wherever it lives, and a manifest is a document wherever it lives.

The terms arrive with the first commit. Whoever reads or forks a public
repository holds the terms that were published when they did so, and terms
settled afterwards never reach them.

MIT alone would be the wrong instrument for what is here. Its text grants
rights in "the Software" and permits a licensee to "sublicense" (`LICENSE`),
which is the vocabulary of a program. The repository contains no file with a
source extension (verified, `docs/licensing.md`), so MIT would today apply to
no code, because there is none.

### The single Zenodo licence field carries `cc-by-4.0`

`.zenodo.json` has one `license` field. It is a string, it is required while
`access_right` is `open`, and Zenodo states that "The selected license
applies to all files in this deposition, but not to the metadata which is
licensed under Creative Commons Zero" [2]. One value therefore stands for the
whole deposit. The deposit is documents, so `cc-by-4.0` describes what is
archived and `mit` would misdescribe it.

The identifier was checked against Zenodo's own vocabulary before it was
written: the lower-case form resolves and the SPDX spelling does not
(verified, `docs/licensing.md`).

Because one field cannot express the split, the split is stated in the
deposit's `description`, which is where a Zenodo reader sees it, and in
`README.md`, which is where a reader of the repository sees it.

### `CITATION.cff` carries `CC-BY-4.0`, and not both identifiers

The Citation File Format accepts a list for `license`, and its validator
refuses an identifier outside the schema, so the acceptance is evidence and
not silence (verified, `docs/licensing.md`). A list is nevertheless the wrong
thing to write: the format reads multiple licences as alternatives, not as
parts, and states that "When there are multiple licenses, it is assumed
their relationship is OR, not AND" [4]. `[MIT, CC-BY-4.0]` would therefore
offer the whole work under either licence at the reuser's choice, which is
not this decision and is wider than it.

The field carries the licence that covers the content, in the SPDX spelling
the format requires. That leaves the two files agreeing on the value and
differing only in notation, which is what the comment at the top of
`CITATION.cff` records.

### `LICENSE` at the repository root stays MIT

GitHub detects a licence with the Licensee library, which "compares the
repository's LICENSE file to a short list of known licenses", and observes
that "Most people place their license text in a file named LICENSE.txt (or
LICENSE.md or LICENSE.rst) in the root of the repository" [1]. That file is
therefore where the code licence goes, and the full CC BY 4.0 text lives in
`LICENSES/CC-BY-4.0.txt`. GitHub's own guidance for a repository whose
licensing has more than one part is to keep the `LICENSE` file simple and
"note the complexity somewhere else, such as your repository's README file"
[1]; `README.md` is where this repository notes it.

The cost, stated plainly rather than hidden: until code exists, the licence
GitHub displays will read MIT for a repository that is entirely documents.
That inaccuracy is accepted. It corrects itself the day code arrives, and
moving the root `LICENSE` back and forth in a published repository is a
worse thing to do than tolerating a badge that is early.

### Attribution

The licence conditions sharing on a set of notices being retained, and
permits them to be satisfied "in any reasonable manner based on the medium,
means, and context in which You Share the Licensed Material" [3, Section
3(a)(2)]. The reasonable manner chosen here is citation: the repository as
`CITATION.cff` describes it, and the DOI once a release has been archived.

That choice binds this repository to supply what a reuser is asked to retain,
which is why the creator, the copyright line, the terms and a stable link are
carried in the files rather than left implicit. Indicating a modification
stays the reuser's step; no citation of the source discharges it.
`docs/licensing.md` sets out both sides with the clauses that impose them.

## Rejected

- **MIT for everything.** It is the wrong instrument for a document, for the
  reason given above, and choosing it would license the whole deposit under
  terms written for a program that is not there.
- **CC0 for the machine-readable material** — manifests, pair lists, score
  vectors. It would spare a reuser the attribution burden when recomputing a
  metric, which is the one operation this repository most wants people to
  perform. Rejected on two grounds. It adds a third boundary that has to be
  maintained file by file, and the boundary between a document and a
  machine-readable observation is far less obvious than the one between code
  and everything else. More importantly, attribution on a reused observation
  is the point: this repository exists so that a number carries its origin,
  and a licence that permits the number to be severed from its source works
  against the design it is meant to serve.
- **Both licences as files at the root**, `LICENSE-CODE` and `LICENSE-DOCS`.
  Rejected: GitHub's guidance for licensing with more than one part is to
  "simplify your LICENSE file and note the complexity somewhere else, such
  as your repository's README file" [1], which is one root file and a README
  section, not two root files.

## Open

- ⟨OPEN⟩ What the metadata should say once the repository contains code.
  `.zenodo.json` carries `license: cc-by-4.0` and `upload_type: software`,
  and the two sit in one tension rather than two: the deposit is a
  repository, which is what `software` names, while its contents today are
  entirely documents, which is what `cc-by-4.0` names. `CITATION.cff` holds
  the same question in its own `license`. Every one of these fields holds a
  single value for the whole work and none of the formats expresses a split,
  so they are answered together on the day code lands.

## References

1. GitHub, licensing a repository: <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository>
2. Zenodo deposit metadata, the `license` field: <https://developers.zenodo.org/>
3. Creative Commons Attribution 4.0 International, legal code: <https://creativecommons.org/licenses/by/4.0/legalcode.txt>, stored as `LICENSES/CC-BY-4.0.txt`
4. Citation File Format 1.2.0 schema guide, the `license` key: <https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md>
