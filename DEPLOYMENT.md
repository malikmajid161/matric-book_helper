# Deployment runbook

## Backend: Render / Railway

1. Connect this repository and choose `backend` as the service root, `Dockerfile` as the Docker build. The default image is lightweight. Use `Dockerfile.semantic` only with a measured memory budget.
2. Configure server secrets: `GEMINI_API_KEY`, a currently accessible `GEMINI_MODEL`, `STUDENT_PROFILES_JSON` (salted hashes from local configuration), and optional `STUDY_ACCESS_CODE`. Do not publish student codes or hashes in Git.
3. Set `CORS_ORIGINS` to the exact Vercel production origin and any allowed preview origins, comma-separated. Do not use wildcard origins for private access codes.
4. Provision persistent storage for `DATA_DIR`. Copy `books/manifest.json`, verified PDFs and OCR sidecars to it. A mount hides bundled files at the same path, so populate it explicitly before restart.
5. Use one worker. Confirm `/health` returns `ready`, `books_ready: 3`, and `ai_configured: true`. `ready` alone means service initialization succeeded, not that textbooks are available.
6. Ask real textbook questions, check citations, restart the service, and verify persisted books/indexes. Measure peak memory and cold/warm latency.

Free-tier sleep, quotas and disk availability vary. Confirm these in the chosen account before provisioning. Do not assume persistent disk is free.

## Web: Vercel

Connect the GitHub repository, set root directory `web`, framework Next.js, and `NEXT_PUBLIC_API_URL` to the HTTPS backend address. Set Node 22 or newer. Build command `npm run build`. No LLM keys belong in Vercel client variables.

Verify downloads, saved-book reload, offline shell refresh, local search, four profile checklists, storage deletion/redownload, dark mode and narrow-screen layout. Configure the final Vercel origin in backend CORS.

## APK: Expo EAS

Authenticate with your Expo account, set `EXPO_PUBLIC_API_URL` in the preview EAS environment, initialize the EAS project, then:

```powershell
cd mobile
npx eas-cli build --platform android --profile preview
```

Install the resulting APK on the students' actual phones. Test first download, airplane-mode read/search/practice, failed download retry, missing files, low-storage behavior and new AI answers after reconnecting. EAS export success is not an APK build or a device test.

## Release status

Hosting sign-in, verified science-stream PDFs/OCR, rotated Gemini key, real-book evaluation, and APK device validation are required before release. The checked-in configuration alone does not deploy services.
