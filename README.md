# PTB Scholar

An offline-first class 9 and 10 study companion for Punjab Board students.

## How students use it

Choose a subject → download its verified textbook once → read chapters, search saved passages, and practice without internet. If device files or browser storage are deleted, download again. An internet connection is needed for new AI explanations. Textbook passages are explicitly distinguished from generated explanations; every supported AI response includes page sources.

Whole-book downloads and separate chapter packs are supported. Each chapter pack contains its original PDF pages, available text, a portable local LSA vector index, and any checked solutions. Packs can be opened offline or deleted independently. PDF page references preserve original book numbering; the reader adjusts chapter-file offsets. Expo OTA checks download compatible updates quietly for the next launch; native changes require a new APK.

Current content coverage: Class 10 Chemistry has native text, 174 transcribed questions and 6 checked worked solutions. Class 9 Physics/Chemistry and Class 10 Physics use machine OCR for retrieval and original page images for online answers; OCR is not fully reviewed. Maths has 12 chapter boundaries, only two reviewed pages and 17 checked Exercise 1.1 subparts. No whole-book completeness or zero-error claim is made.

Roman Urdu questions are normalized for retrieval; explanations always use simple English. Offline practice quizzes shuffle saved exercise questions and reveal only checked solutions. New AI answers require the backend; offline excerpts and previously saved answers do not.

Named online profiles use server-verified study codes stored as salted scrypt hashes. Ayesha and Huzaifa are configured locally; the remaining two profiles can be added with `backend/tools/set_profile.py`. Deployment requires transferring the hash configuration as a secret. Offline books are device-local and shared on that device; progress belongs to the last selected profile and does not sync between devices. Sessions expire after seven days or a backend restart.

## Run locally

Backend (Python 3.12):

```powershell
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env: add a fresh Gemini key and supported model.
.venv/Scripts/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Web (Node 22+):

```powershell
cd web
npm ci
Copy-Item .env.local.example .env.local
npm run dev
```

Android:

```powershell
cd mobile
npm ci
Copy-Item .env.example .env
# Use your computer's LAN IP, not localhost, on a physical phone.
npx expo start
```

Use HTTPS for deployed APIs. Only the backend receives `GEMINI_API_KEY`; client environment variables contain the public API address. Session tokens are stored in session storage on web and SecureStore on Android; study codes are not persisted on clients. Rotate API credentials shared in chat before production. Add profiles using `python tools/set_profile.py ayesha Ayesha` from the backend environment; it prompts for the code without exposing it in CLI arguments.

## Lightweight and semantic retrieval

Default `RETRIEVAL_MODE=lexical` ranks verified textbook chunks on the CPU with term frequency and inverse document frequency; no embedding runtime is loaded. This reduces server cost and startup latency. Device search uses saved textbook text and needs no backend. Local search is keyword-based and cannot understand every paraphrase.

For optional semantic retrieval, install `backend/requirements-semantic.txt`, set `RETRIEVAL_MODE=semantic`, and use `Dockerfile.semantic`. MiniLM embeddings run locally and ChromaDB persists under `DATA_DIR/chroma_db`. Chunks are 220 model tokens with 30 overlap, below MiniLM's 256-token limit. A single worker shares the model. Memory and latency must be measured with real books on the actual host.

Gemini 1.5 Flash and the old `google-generativeai` SDK were replaced by a configurable model and `google-genai`. Verify current model access and free-tier quotas in your Google account; neither cost nor response time is guaranteed.

## Textbooks and accuracy

Source catalogue: https://pectaa.edu.pk/curriculum-compliance/

Verified Physics and Maths PDFs are locally available in **reading-only mode**. Their text is scanned, so AI/search/prep remain unavailable until extraction is reviewed. Chemistry is awaiting the correct science-stream PDF. Put the correct English-medium **science-stream 2026–27** PDFs in `backend/data/books/`. For each book in `manifest.json`, record its edition, official source URL, SHA-256, and reviewed chapter boundaries using **1-based PDF page numbers**, not printed page labels. Remove `reader_only` only after reviewed OCR, topics and exercises are prepared.

Example chapter record:

```json
{
  "number": 12,
  "title": "Waves",
  "start_page": 35,
  "topics": [{"id":"12.1","title":"Wave motion","page_number":36,"key_points":["A reviewed textbook definition."]}],
  "exercises": [{"id":"12.q1","text":"Exact reviewed exercise text.","page_number":47}]
}
```

The numbers above illustrate the schema and are not actual page mappings. Never invent chapter/topic/exercise content. PDFs are ignored in Git. Startup validates hashes, prepares chapter bundles, and rebuilds changed vector records. Scanned PDFs need an OCR sidecar and review before ingestion. See `backend/tools/README.md`.

Citation validation proves cited source numbers exist; it does **not** prove the AI's interpretation is correct. Use the real-book evaluation set in `evaluation/` before releasing the tutor. Inspect original pages for tables, superscripts, equations and diagrams. Training/fine-tuning is not currently implemented or necessary for the first RAG release.

## Checks

```powershell
cd backend
.venv/Scripts/python -m pytest -q
cd ../web
npm test
npm run typecheck
npm run build
cd ../mobile
npm run typecheck
npx expo-doctor
npm run export
```

Backend tests use generated PDF fixtures and fake AI responses. Passing them does not certify textbook accuracy or provider connectivity. Browser shell caching requires a production build and HTTPS (or localhost); browser storage can be evicted. Android keeps books in its document directory; app uninstall or data clearing removes them. Web SHA-256 verification reads the PDF into memory. Android uses native MD5 checks for transfer corruption to avoid loading large PDFs into the JavaScript heap; the server verifies source SHA-256 and deployments require HTTPS.

## Deploy

See [DEPLOYMENT.md](DEPLOYMENT.md) and [PLAN.md](PLAN.md) for deployment settings and release gates. No production deployment or APK should be described as complete until host and EAS results confirm success.
