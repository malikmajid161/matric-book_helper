# Verified textbook import

`data/books/manifest.json` is the review record. Keep science-stream and technical-stream editions separate. The official catalogue's link label is not sufficient: inspect the actual cover and contents.

For scanned books, prepare `filename.pages.json` alongside the PDF using an OCR tool. Schema: an object mapping 1-based PDF page numbers to extracted text, e.g. `{"5":"Chapter text..."}`. Include `ocr_sha256` in the manifest to bind the reviewed sidecar to the import. The pipeline validates it before use and removes recurring publisher watermarks before testing text availability. Review every chapter boundary and formula before publishing; OCR cannot reliably reconstruct all equations.

Calculate hashes with `Get-FileHash -Algorithm SHA256`. Use lowercase SHA-256 values in the manifest. Restart the backend after changes. Do not set an edition to verified just to bypass ingestion safeguards.

The downloaded local candidates are excluded from Git. Physics labelled EM was found to be TECH. Maths EM is scanned. The alternate standard Physics link needs inspection after download. No candidate has been approved for AI use yet.
