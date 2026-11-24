# Verified textbook import

`data/books/manifest.json` is the review record. Keep science-stream and technical-stream editions separate. The official catalogue's link label is not sufficient: inspect the actual cover and contents.

For scanned books, prepare `filename.pages.json` alongside the PDF using an OCR tool. Schema: an object mapping 1-based PDF page numbers to extracted text, e.g. `{"5":"Chapter text..."}`. Include `ocr_sha256` in the manifest to bind the reviewed sidecar to the import. The pipeline validates it before use and removes recurring publisher watermarks before testing text availability. Review every chapter boundary and formula before publishing; OCR cannot reliably reconstruct all equations.

Calculate hashes with `Get-FileHash -Algorithm SHA256`. Use lowercase SHA-256 values in the manifest. Restart the backend after changes. Do not set an edition to verified just to bypass ingestion safeguards.

PDFs, extracted study content and OCR sidecars are excluded from Git. The science-stream Class 9/10 Physics and Chemistry PDFs have been checked for cover/contents; the TECH Physics candidate is excluded. Machine OCR is marked `text_origin: machine_transcribed` and used for retrieval only; online answers also receive original page images. This does not certify full OCR accuracy. Maths currently indexes only two visually reviewed pages.

Private study sidecars (`{book}.study.json`) bind curated topics/questions/solutions to the original PDF SHA-256. Their hash is stored as `study_sha256`. Checked Maths Exercise 1.1 material can be reproduced with `build_math_ex11.py`; the first six checked Chemistry answers are provided by `build_chemistry14_solutions.py`. AI batch drafts from `generate_math_solutions.py` remain `needs_review` and are never published automatically.
