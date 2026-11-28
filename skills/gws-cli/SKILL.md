---
name: gws-cli
description: >-
  Use the Google Workspace CLI (`gws`) to work with Drive, Gmail, Calendar,
  Sheets, Docs, and other Workspace APIs. Apply when a user asks to perform a
  Workspace task through gws, construct a gws command, or troubleshoot its
  authentication and API requests.
---

# Google Workspace CLI

Use the installed `gws` command to make Google Workspace API requests. The CLI
is community maintained and is not an officially supported Google product.

## Workflow

1. Check `gws --help` and the relevant service help or `gws schema SERVICE.RESOURCE.METHOD`
   when command shape, parameters, or request body are uncertain. The CLI
   accepts URL/query parameters through `--params '<JSON>'` and request bodies
   through `--json '<JSON>'`.
2. Check authentication with `gws auth status` if a request reports missing or
   invalid credentials. `gws auth login` starts OAuth sign-in; let the user
   complete any browser consent. Never request or expose tokens or credential
   files in chat.
3. Inspect the requested operation and its effects before running it. Reading
   data is distinct from sending mail, changing sharing, deleting files, or
   modifying Workspace records. Confirm the target and material details with
   the user before consequential writes when they have not specified them.
4. Run the narrowest command that fulfills the request. Use `--format table`,
   `yaml`, or `csv` when useful; use `--page-all` for paginated results and set
   a reasonable `--page-limit` when the result could be large.
5. Report what happened and surface API errors. Exit codes: 1 API error, 2
   authentication error, 3 invalid arguments, 4 schema discovery error, 5
   internal error.

## Command patterns

```sh
gws drive files list --params '{"pageSize": 10}'
gws drive files get --params '{"fileId": "FILE_ID"}'
gws sheets spreadsheets get --params '{"spreadsheetId": "SHEET_ID"}'
gws gmail users messages list --params '{"userId": "me"}'
gws schema drive.files.list
```

Avoid putting sensitive values directly in shell commands where they may be
saved in shell history or logs. Prefer supported environment variables for
credentials, and do not print `gws auth export` output.
