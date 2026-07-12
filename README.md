# Xie Lab AI Website v0.3 — Editorial Console + AI CMS

> Section-by-section editorial management, Word-to-website member updates, AI-assisted bilingual content, publication/patent synchronization and review-first deployment.

A bilingual, data-driven research-group website rebuilt from the legacy structure of `xielab.net`. The repository supports GitHub Pages deployment, PubMed synchronization, optional Google Scholar metadata, patent discovery, OpenRouter translation and AI-assisted Word imports for lab-member updates.

## Website architecture

- `index.html` and `assets/` — responsive bilingual website.
- `data/` — structured content collections; routine content updates do not require HTML editing.
- `admin/` — full Editorial Console for homepage, contact, openings, members, research, publications, patents, news and tools.
- `scripts/` — publication, patent, translation, legacy migration and Word-member import pipelines.
- `.github/workflows/` — Pages deployment, scheduled research-output sync, Word import, AI issue intake and validation.
- `templates/` — bilingual Word template for team updates.

## v0.3 Editorial Console

Open `/admin/` on the deployed website for a complete section-by-section management interface. Each module provides structured bilingual forms, record search/filtering, add/edit controls, member-to-alumni transitions, deletion requests, browser drafts and JSON preview.

A console submission creates a deterministic `[CMS]` GitHub issue. The authorized workflow then:

1. verifies that the issue author is a repository owner, member or collaborator;
2. parses the allowlisted collection and JSON record;
3. optionally calls OpenRouter only for approved narrative and bilingual fields;
4. protects names, identifiers, dates, emails, publication metadata and URLs from AI rewriting;
5. applies collection-specific merging, archiving or deletion;
6. validates the complete content dataset;
7. creates an audit report and review pull request;
8. publishes only after the pull request is merged.

See [Editorial Console guide](docs/EDITORIAL_CONSOLE.md).

## Existing AI CMS update routes

The site now has three practical maintenance routes:

1. **Member Word import:** upload a `.docx`; OpenRouter extracts bilingual profiles and creates a review pull request.
2. **Quick content issue:** paste news, project, tool, publication or patent details into the GitHub form; AI structures the record and creates a review pull request.
3. **Scheduled research-output sync:** PubMed, optional Scholar metadata, patents and translations run from GitHub Actions.

Open `/admin/` on the deployed website to access all three routes. No API key is exposed to the browser.

## First deployment

1. Open **Settings → Pages** and select **GitHub Actions** as the deployment source.
2. Open **Settings → Actions → General → Workflow permissions**:
   - enable **Read and write permissions**;
   - enable **Allow GitHub Actions to create and approve pull requests**.
3. Run **Deploy site to GitHub Pages** from the Actions tab.
4. Preview the GitHub Pages URL before switching `www.xielab.net` DNS.

`CNAME` is already set to `www.xielab.net`. Keep the legacy server available until page content, images, links and domain routing have been verified.

## API configuration

Open **Settings → Secrets and variables → Actions**.

### Actions secrets

- `OPENROUTER_API_KEY` — required for Word member import and automatic bilingual translation.
- `NCBI_API_KEY` — optional; increases the PubMed E-utilities request allowance.
- `SERPAPI_API_KEY` — optional Google Scholar adapter. Google Scholar does not provide an official public API.
- `SCHOLAR_AUTHOR_ID` — Google Scholar profile identifier used by the optional adapter.

### Repository variable

- `OPENROUTER_MODEL` — for example `openai/gpt-4.1-mini`. Choose a model that supports structured outputs.

Never place API keys in HTML, JavaScript or files under `data/`.

## Fast member updates from Word

Open the deployed **AI Content Studio** at `/admin/`, or use the repository issue form:

**Issues → New issue → Upload a Word file to update lab members**

Workflow:

1. Download `templates/member-update-template.html`, or prepare another `.docx` containing biographies or a roster table.
2. Drag the Word file into the GitHub form and submit the issue.
3. The workflow extracts paragraphs, tables and suitable images.
4. OpenRouter converts the document into the bilingual member schema.
5. Deterministic code matches existing people by email, then bilingual name.
6. New and revised records are merged. Missing names are not removed.
7. Alumni or deletion actions are applied only when explicitly stated.
8. A validation report and review pull request are generated.
9. Review names, roles, status, public emails, links and photographs; merge the pull request to publish.

The issue-triggered workflow only runs for repository owners, members and collaborators. Because this repository and its issue attachments are public, Word files must contain only website-ready public information. See [Word member import guide](docs/MEMBER_WORD_IMPORT.md).

A manual document-URL import is also available under **Actions → Import lab members from Word**.

## Member data schema

`data/members.json` stores one record per person. Important fields include:

```json
{
  "id": "jane-doe",
  "name_en": "Jane Doe",
  "name_zh": "张三",
  "role_en": "PhD Student",
  "role_zh": "博士研究生",
  "group": "phd",
  "status": "current",
  "order": 30,
  "bio_en": "...",
  "bio_zh": "...",
  "research_interests_en": ["..."],
  "research_interests_zh": ["..."],
  "email": "public-email@example.edu",
  "photo": "assets/members/jane-doe.jpg"
}
```

Allowed groups: `principal-investigator`, `faculty`, `research-scientist`, `postdoc`, `phd`, `master`, `undergraduate`, `staff`, `visitor`, and `alumni`.

## Publication, Scholar and patent synchronization

The **Sync publications patents and translations** workflow runs every Monday and can also be started manually. It:

1. queries PubMed using `data/site.json` search expressions;
2. merges optional Google Scholar records and citation counts;
3. discovers patent candidates using configured inventor aliases;
4. translates missing bilingual fields with OpenRouter;
5. validates and commits changed data;
6. triggers Pages deployment.

PubMed records are treated as the primary biomedical source. Scholar and patent results require human review because third-party layouts, author ambiguity and namesakes can produce imperfect matches.

## Quick JSON updates

The `/admin/` Editorial Console presents schema-aware forms for every public section and submits review-first update requests. A JSON preview remains available for audit and advanced editing.

The standard **Website content update** issue form collects news, publication, patent, project and tool changes. An authorized issue triggers OpenRouter extraction, deterministic collection merging, validation and a review pull request. Use the dedicated Word workflow for member rosters and biographies.

## Local preview and validation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/validate_content.py
python -m http.server 8080
```

Open `http://localhost:8080`.

## Recovering legacy content

On a machine that can reach the old host:

```bash
python scripts/import_legacy_site.py --base http://www.xielab.net/
```

The crawler writes a non-destructive archive under `legacy_archive/`. Review and migrate historical biographies, photographs, news and complete publication records into `data/*.json`.

## Security and editorial controls

- API keys remain in GitHub Actions secrets and are never sent to browsers.
- Word import creates a review pull request rather than publishing directly.
- User-supplied text is treated as untrusted data, not executable code.
- The importer accepts `.docx` only, enforces a 25 MB limit and validates the package.
- Automatically discovered publications and patents should be checked for namesakes.
- Do not upload confidential, patient-related, unpublished or personally sensitive material to a public repository.
