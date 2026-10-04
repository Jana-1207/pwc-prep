# PwC Technology Interview Preparation: Modern Data Systems Handbook

**[PwC_Modern_Data_Systems_Interview_Handbook.pdf](PwC_Modern_Data_Systems_Interview_Handbook.pdf)** is a
396-page, interview-oriented study guide covering Modern Data Systems, SQL, databases, APIs and data
integration. It follows the seven modules of the Tekstac *Modern Data Systems* course and re-teaches every
topic in plain English, then adds what interviewers usually ask on top.

| Part | Contents |
|---|---|
| Start here | how to use the handbook, study plans (1, 3 and 7 days), the Course Coverage Map, and PwC interview orientation (common, reported, likely and recommended information kept separate) |
| I–VII | the seven course modules, each with a Course Coverage box, sessions, a Module Summary and a Rapid Revision Checklist |
| Final Interview Revision | 100 most important questions, a Top 50 SQL bank with executed solutions, top database, scenario and rapid-fire questions, project connection, a one-day revision sheet and an answering strategy |
| Appendix | a 162-term plain-language glossary and the coverage verification against the original brief |

Each session explains the idea simply (what, why, how, example, real-world use), then gives a 30–60 second
"How I Would Explain This in an Interview" answer, common traps, and interview questions grouped into
Basic, Intermediate, Scenario-based and Follow-up/Trap with model answers. Important topic groups end with
Level 1–3 practice questions and a separate Answer / Explanation box.

In numbers: 657 interview Q&As, 146 practice questions, 22 SQL interview patterns, 57 diagrams, and 261 SQL
examples whose outputs come from actually running them on PostgreSQL 16.

## About the source material

- The course screenshots were not available when this edition was produced. Session titles named in the
  brief are used as they are; the others were rebuilt from each module's topic list and are marked **†** in
  the Course Coverage Map. Every listed topic is covered.
- Material beyond the course is labelled **[INTERVIEW EXTENSION]** or **Recommended Prerequisite**.
- PwC-specific information comes from public candidate reports and PwC's published material. It is labelled
  as reported, kept separate from general advice, and is not an official question list.
- The handbook is independent study material. It is not affiliated with, sponsored by or endorsed by PwC or
  Tekstac.

## How the content is verified

- **SQL:** every ` ```sql run ` block runs against the sample database (`handbook/sql/sample_db.sql`) during the
  build, and the real output is printed under the query. A query that fails unexpectedly stops the build.
- **MongoDB:** shell examples are syntax-checked with Node.js (when available); their outputs were traced by
  hand, as no MongoDB server was used.
- **Python:** examples are compiled during the build.

## Repository layout

```
PwC_Modern_Data_Systems_Interview_Handbook.pdf   the deliverable
handbook/
  content/        the handbook text, one Markdown file per part (00-front … 90-appendix)
  build.py        Markdown → HTML → PDF pipeline; runs SQL, numbers figures, builds the contents
  style.css       print stylesheet (A4, running headers, boxes, code, tables)
  cover.html      cover page template
  sql/            the sample database used by every SQL example
  diagrams/       SVG diagram generator (make_diagrams.py) and the generated svg/ files
  fonts/          IBM Plex Sans and Mono (SIL Open Font License)
  scripts/        start_postgres.sh: a local PostgreSQL for the build
```

## Rebuilding the PDF

Requirements: Python 3.10+, PostgreSQL 16 (other recent versions should work, but outputs were verified on
16), and optionally Node.js for the MongoDB syntax check.

```bash
pip install -r handbook/requirements.txt
handbook/scripts/start_postgres.sh          # local server on port 54329 with a "handbook" database
python3 handbook/diagrams/make_diagrams.py  # only needed after changing a diagram
python3 handbook/build.py                   # writes PwC_Modern_Data_Systems_Interview_Handbook.pdf
```

To use an existing server, set `HANDBOOK_PG_DSN`, for example
`HANDBOOK_PG_DSN="host=localhost port=5432 user=postgres dbname=handbook" python3 handbook/build.py`.
**Use a dedicated database:** before loading the sample data, the build runs
`DROP SCHEMA public CASCADE` on the target database, which deletes everything in its `public` schema.

`python3 handbook/build.py --html-only` stops after writing `handbook/build/handbook.html`;
`--no-sql` skips running SQL for quick layout drafts.

## Writing content

The content files are Markdown with a few additions, documented at the top of `handbook/build.py`:

- `::: kind Title` … `:::` for boxes (`explain`, `trap`, `questions`, `practice`, `answers`, `summary`,
  `checklist`, `extension`, `prereq`, `tip` and more);
- `Q:` / `A:` pairs for interview questions;
- ` ```sql run ` blocks (options `keep`, `quiet`, `error`, `plan`, `all`, `max=N`) for executed SQL;
- `[[fig:name | Caption]]` for numbered diagrams;
- `[DEFINITION]`, `[SCENARIO]`, `[TRAP QUESTION]` and similar for coloured labels.
