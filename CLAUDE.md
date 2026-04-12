# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BD Bagarre is a comic book library server that parses comic metadata from two sources (Calibre OPF files and ComicRack CBZ files) and serves them via a FastAPI REST API with an OPDS feed for catalog navigation.

## Commands

### Running the server

```bash
uvicorn bd_bagarre.mongodb_server:main --host 0.0.0.0 --port 5000
```

The active server backend is `mongodb_server.py` (the `couchdb_server.py` is the older backend).

### Required environment variables

- `MONGODB_PASSWORD` — MongoDB Atlas password
- `MONGODB_URL` — MongoDB Atlas cluster URL
- `MONGODB_USER` — defaults to `bd_bagarre` if unset

### Running tests

```bash
pytest test/
```

Run a single test:

```bash
pytest test/test_parser.py::test_parse_comicrack_xml
```

### Docker

```bash
docker build -t bd_bagarre .
docker run -e MONGODB_PASSWORD=... -e MONGODB_URL=... -p 5000:5000 bd_bagarre
```

## Architecture

### Two parallel backends

- **`mongodb_server.py`** — active backend; uses PyMongo connected to MongoDB Atlas. Defines FastAPI routes and includes the OPDS feed router from `feed.py`.
- **`couchdb_server.py`** — older backend; uses IBM Cloudant SDK connected to CouchDB. Configured via `CLOUDANT_*` environment variables.

Both backends share the same scanning logic: `recurse_scan()` walks a library path, dispatching CBZ files to `create_document_from_comicrack()` and `metadata.opf` files to `create_document_from_calibre()`. Scans run in a `ProcessPoolExecutor` (8 workers) triggered via `GET /scan`.

### Parsers

- **`comicrack_parser.py`** — primary parser. Reads `ComicInfo.xml` from inside a `.cbz` zip file. Returns a `ComicInfo` TypedDict (snake_case keys) plus raw bytes of the front cover image. PascalCase XML keys are converted to snake_case via regex.
- **`calibre_parser.py`** — reads Calibre `metadata.opf` (XML) from a book directory, extracts authors/publisher/tags/language using `apischema` deserialization into SQLAlchemy models.
- **`parser.py`** — filename-pattern-based fallback parser; extracts series, number, and title from filename using regex patterns like `"<series> T<number>"`.

### OPDS feed (`feed.py`)

Implements an OPDS 1.2 Atom feed at `/opds-comics/`. The `Atom1Feed` subclass overrides `add_root_elements` and `add_item_elements` to produce OPDS-compliant XML with the required namespaces (`dcterms`, `pse`, `opds`, `opensearch`). Routes: `/opds-comics/` (root navigation), `/opds-comics/all`, `/opds-comics/folders`, `/opds-comics/latest`, `/opds-comics/random`.

### SQLAlchemy models (legacy, used by calibre_parser)

- `database.py` — declarative `Base` with a custom `__init_subclass__` that automatically generates `apischema` dataclass models from SQLAlchemy columns. The `GUID` type handles UUID portability between SQLite and PostgreSQL.
- `model/` — `Resource` mixin (id, state, creation/update/deletion timestamps), `Book` with rich metadata fields, `Author` with role subclasses (`Writer`, `Penciller`, etc.), `Publisher`, `BookFile`.

### Test structure

Tests use `pytest` with a `db_session` autouse fixture (in `conftest.py`) that creates and tears down a SQLite database for each test function. Several tests are marked `@pytest.mark.skip` (calibre parser and filename parser tests are not yet passing).
