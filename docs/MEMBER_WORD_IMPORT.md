# AI-assisted Word member import

## Recommended route

1. Open `/admin/` on the website.
2. Open the bilingual member-update template, copy it into Word and save it as `.docx`.
3. Fill one row or one profile section per person.
4. Use explicit actions: `Add`, `Update`, `Move to alumni`, or `Delete`.
5. Open the GitHub Word-upload issue form and drag the `.docx` into the attachment field.
6. Submit the issue and wait for the workflow to create a pull request.
7. Review the generated report under `imports/reports/` and the changes to `data/members.json`.
8. Merge only after checking all public-facing information.

## Matching and merge rules

The importer matches a person in this order:

1. exact public email address;
2. stable member ID;
3. normalized English or Chinese name.

Incoming non-empty fields update the matched record. Blank fields do not erase existing content. A person missing from the uploaded document remains unchanged. `Move to alumni` changes status and preserves the profile. `Delete` is honored only when explicitly stated.

## Photographs

The importer extracts suitable embedded images to `assets/members/imports/<import-id>/`. The LLM assigns an image only when the Word document clearly associates that image with a person. Confirm every photograph manually in the pull request.

## Privacy

The repository and issue attachments are public. Upload only information approved for public display. Never include patient data, identity documents, private telephone numbers, home addresses, passwords, API keys, confidential reviews or unpublished sensitive research.

For confidential internal rosters, use a private intake repository or a protected server-side upload service instead of public issue attachments.
