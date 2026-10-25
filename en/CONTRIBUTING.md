# Editing and translating documentation

[한국어](../CONTRIBUTING.md) | **English**

## Korean source and English translation

The Korean documentation at the original paths is the source of truth.
Keep each English translation at the same path under `en/`. For example,
the English version of `labs/lab02/README.md` is
`en/labs/lab02/README.md`. This applies to data descriptions and worksheets
as well as READMEs.

Lab code, data, tests, and Docker configuration are shared. Do not duplicate
executable files or data under `en/`. Commands in both languages use the
original `/workspace/labs/...` paths.

## Editing workflow

1. Edit the Korean document.
2. Apply the same change to its English translation. Preserve task scope,
   restrictions, commands, tables, and examples, and do not add answers only
   to the English version.
3. Check that each language link opens the corresponding document. English
   documentation links stay under `en/`; code and data links point to the
   shared files. Check existing section links when changing headings.
4. After reviewing both documents, record the translation baseline with:
   this command does not translate, so run it only after updating English.

   ```console
   python3 scripts/check_translations.py --record labs/lab02/README.md
   ```

   You can supply several document paths at once. Use the Korean document's
   path relative to the repository root.
5. Check the overall synchronization status:

   ```console
   python3 scripts/check_translations.py
   ```

Run these commands in a host terminal at the repository root or at
`/workspace` inside the course container. They use only the Python standard
library and require no additional packages.

The checker covers `README.md`, this guide, and Markdown files under `docker/`
and `labs/`. It exits with code 1 when either language has changed since the
last review, or a new document is missing a translation or baseline.
Baselines are stored in `en/.translation-status.json`. This detects file
changes; it does not evaluate translation quality or semantic equivalence.

The instructor can edit Korean first. In a later translation task, the agent
checks the status, updates the affected English documents, and records the
reviewed baseline. The checker runs when invoked and does not translate
automatically in the background.

## New documents and student releases

When adding a Korean document, add its English counterpart and language links
in both directions. Keep the shared code and data at their original paths.

For documents included in the student release, list both languages explicitly
in the file allowlist in `scripts/build_student_release.sh`. Do not include
`instructor/` in the translation scope or student release.
