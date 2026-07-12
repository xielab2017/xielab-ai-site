# Xie Lab Editorial Console

The Editorial Console at `/admin/` is the section-by-section management interface for the public Xie Lab website.

## Architecture

GitHub Pages serves the public website and the browser-based console. Because GitHub Pages is static hosting, the protected write layer is implemented through authorized GitHub issues, GitHub Actions and review pull requests:

```text
Editorial Console form
        ↓
structured [CMS] GitHub issue
        ↓
owner/member/collaborator authorization check
        ↓
optional OpenRouter bilingual editing
        ↓
collection-specific merge / archive / delete
        ↓
full data validation + audit report
        ↓
review pull request
        ↓
merge → GitHub Pages deployment
```

No repository token or OpenRouter key is exposed to browser JavaScript.

## Managed sections

- Homepage: laboratory name, tagline, introduction and synchronization settings.
- Contact: public email, address, GitHub, Scholar and PubMed links.
- Openings: bilingual recruitment text.
- Members: roles, groups, status, biographies, interests, education, links, photos and alumni transitions.
- Research: bilingual research directions and card ordering.
- Publications: bibliographic metadata, DOI/PMID, citation metadata and bilingual summaries.
- Patents: titles, inventors, numbers, status, dates, links and summaries.
- News: dates, bilingual headlines, descriptions, links and images.
- Tools: names, URLs, bilingual descriptions, status and ordering.

## Routine use

1. Open `https://www.xielab.net/admin/` or the GitHub Pages preview URL ending in `/admin/`.
2. Select a content module in the left navigation.
3. Choose a record or create a new one.
4. Complete the structured fields.
5. Leave **Use OpenRouter AI** enabled when bilingual translation or scientific wording improvement is useful.
6. Add an editorial note describing the source and reason for the update.
7. Click **Submit for review**.
8. Submit the prefilled GitHub issue.
9. Review the automatically generated pull request and audit report.
10. Merge the pull request to publish.

The console never directly publishes a browser edit. This protects the public website from accidental or unauthorized changes.

## Word member import

For multiple members or long biographies, use **Upload Word file**. The dedicated workflow extracts paragraphs, tables and suitable images, calls OpenRouter, matches existing profiles and creates a review pull request. Omitted members are not deleted. Alumni transitions are applied only when explicitly stated.

## Required repository settings

Under **Settings → Actions → General → Workflow permissions**:

- enable **Read and write permissions**;
- enable **Allow GitHub Actions to create and approve pull requests**.

Under **Settings → Secrets and variables → Actions**:

- `OPENROUTER_API_KEY`: optional for deterministic form updates, required for AI bilingual assistance and Word imports;
- `OPENROUTER_MODEL`: repository variable, such as `openai/gpt-4.1-mini`;
- optional PubMed, Scholar and other research-output synchronization credentials documented in the main README.

## Security model

- The console page can be viewed publicly, but only issues created by a repository owner, member or collaborator trigger the write workflow.
- Every write is restricted to an allowlisted file under `data/`.
- Submitted JSON is parsed deterministically and validated.
- AI may edit only section-specific narrative fields. Identifiers, names, dates, emails, publication metadata and URLs remain controlled by the human-authored form.
- Every change has an issue, audit report, commit and pull request history.
