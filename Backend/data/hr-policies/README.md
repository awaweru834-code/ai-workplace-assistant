# HR Policy Documents

Place your HR policy PDF files in this directory.

After adding PDFs, run the ingestion script from the `Backend/` folder:

```bash
python ingest.py
```

Each PDF will be:
1. Parsed into text pages
2. Split into overlapping chunks (~500 words each)
3. Embedded via Pinecone's hosted `multilingual-e5-large` model
4. Upserted into your Pinecone `hr-policies` index

The `source` metadata stored with each chunk will be the PDF filename (e.g. `employee-handbook.pdf`),
which is what the HR Policy Librarian cites when answering questions.
