# PTB Scholar implementation and release plan

1. Backend: verified PDF manifest, page-preserving token chunks, persistent embeddings, filtered retrieval, strict cited answers and explicit abstention.
2. Web: green library dashboard, selected-book downloads in IndexedDB, local chapter reading, cited chat, search, exercise practice and dark mode.
3. Android: Expo application, atomic persistent downloads, missing-file detection, local reading and practice, online AI.
4. Verification: ingestion/retrieval/API tests, storage tests, TypeScript/build checks, browser flows, real-textbook evaluation.
5. Release: Docker persistent volume, backend secrets and exact CORS origins, Vercel web deployment, EAS preview APK.

## Release gates

- Confirm book edition against the students' syllabus. Never silently substitute an old edition or guidebook.
- Review extraction of equations, diagrams and chapter boundaries. Scan-only PDFs need OCR before ingestion.
- Check grounded answers on real exercise questions against a teacher-reviewed answer set.
- Measure memory and latency on the deployment host. Under 2 GB / 3 seconds are targets, not guarantees.
- Rotate keys shared in chat, then configure server secrets. No keys in browser or APK.
- Verify backend health, persistence after restart, browser storage eviction and Android download recovery.
- Deploy only after live-provider and textbook gates pass; do not label fixture tests as textbook validation.
