# PTB Scholar implementation and release plan

1. Backend: verified PDF manifest, page-preserving token chunks, persistent embeddings, filtered retrieval, strict cited answers and explicit abstention.
2. Web: green library dashboard, selected-book downloads in IndexedDB, local chapter reading, cited chat, search, exercise practice and dark mode.
3. Android: Expo application, atomic persistent downloads, missing-file detection, local reading and practice, online AI.
4. Verification: ingestion/retrieval/API tests, storage tests, TypeScript/build checks, browser flows, real-textbook evaluation.
5. Release: Docker persistent volume, backend secrets and exact CORS origins, Vercel web deployment, EAS preview APK.

## Verified checkpoint — 25 November 2026

- Source committed and pushed to the requested GitHub repository. First clean GitHub Actions run passed.
- Backend: 62 tests pass. Web: 7 tests and production build pass. Mobile: 14 pure offline tests, strict TypeScript, native config introspection and Android bundle export pass.
- Dependency audits after compatible updates: no known vulnerabilities in web/mobile at this checkpoint.
- Live sign-in works for both named profiles. Roman Urdu input receives simple English answers. Book-scoped sources, exact stored page text and original-page rendering are wired.
- Five PDFs are installed locally: Class 10 Physics/Chemistry/Maths and Class 9 Physics/Chemistry. Full Class 9 science OCR drafts are complete. Machine OCR is explicitly unreviewed; online science answers inspect original page images. Maths has only two reviewed text pages and 17 checked Exercise 1.1 subparts. Six Chemistry Chapter 14 short-question solutions were checked against original pages and saved with source references.
- Chapter APIs and web/mobile storage support independent, checksum-verified chapter PDFs, original-page offsets, offline opening and deletion. Existing PDFs are reused when only study data changes.
- Backend observed RSS 124 MB / peak 134 MB during local smoke checks; this is not a deployment stress-test guarantee.
- Expo APK build `0cd334a5-2307-4882-9d28-35d273cbd7db` finished successfully. APK saved at `C:\Users\Admin\Downloads\PTB-Scholar-2026-11-25.apk` (100,793,826 bytes); ZIP integrity and required Android files pass. SHA-256: `96d5ad47686814d7f1d24952fef4202f0004ec46ef6376ebfef56c200199f96c`.
- Preview OTA update group `e0dc4279-44f1-47b6-aa58-18170d7c96a1` was published. Its runtime `6412dce5d181bbc58dbcf3c115764baeccfd6c5d` exactly matches the native build fingerprint. Updates download quietly and apply at next launch.

## Remaining work

- Complete and independently verify every exercise solution across all five books. Chemistry has 174 transcribed questions and 6 checked worked solutions; science OCR has not been fully proofread.
- Add a teacher-reviewed real-book evaluation set. Source/citation validation and fixture tests do not certify every answer.
- Install and test on actual student phones. Browser automation was unavailable in this session, so do not claim full visual/end-to-end UI verification.
- Deploy an HTTPS backend and production web host. Current APK configuration is same-Wi-Fi testing at `192.168.1.7:8000`; outside that network new AI answers cannot reach it.

## Release gates

- Confirm book edition against the students' syllabus. Never silently substitute an old edition or guidebook.
- Review extraction of equations, diagrams and chapter boundaries. Scan-only PDFs need OCR before ingestion.
- Check grounded answers on real exercise questions against a teacher-reviewed answer set.
- Measure memory and latency on the deployment host. Under 2 GB / 3 seconds are targets, not guarantees.
- Rotate keys shared in chat, then configure server secrets. No keys in browser or APK.
- Verify backend health, persistence after restart, browser storage eviction and Android download recovery.
- Deploy only after live-provider and textbook gates pass; do not label fixture tests as textbook validation.
