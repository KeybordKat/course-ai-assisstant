# Document Upload Guide

## 📤 How to Upload PDFs via UI

### Quick Start

1. **Open the app**: `./start.sh`
2. **Go to sidebar** → Click "📤 Upload Documents"
3. **Click "➕ Add PDFs"** to expand the upload section
4. **Choose subject** (existing or create new)
5. **Upload PDF**
6. **Click "🔄 Process New Documents"**
7. **Restart app** to load new documents

---

## Step-by-Step Guide

### Step 1: Choose Subject

**Option A: Use Existing Subject**
- Select "Existing Subject" radio button
- Choose from dropdown (e.g., "Theory 3")

**Option B: Create New Subject**
- Select "New Subject" radio button
- Enter name (e.g., "Algorithms", "Theory 4", "Machine Learning")
- Subject name will become a folder: `data/pdfs/Your Subject Name/`

### Step 2: Upload PDF

1. Click "Choose PDF file" button
2. Select your PDF from your computer
3. Click "📤 Upload PDF" button

**Result:**
```
✅ File uploaded successfully to subject 'Your Subject'
💡 Click 'Process New Documents' below to add to database
```

### Step 3: Process Documents

After uploading one or more PDFs:

1. Click "🔄 Process New Documents" button
2. Wait (2-10 minutes depending on PDF size)
3. You'll see:
   ```
   ✅ Documents processed successfully!
   ⚠️ Please restart the app to load new documents
   Ctrl+C in terminal, then: ./start.sh
   ```

### Step 4: Restart App

1. Go to terminal where app is running
2. Press `Ctrl+C`
3. Run `./start.sh` again
4. New subject will now appear in dropdown!

---

## Examples

### Example 1: Add to Existing Subject

```
1. Expand "➕ Add PDFs"
2. Select: Existing Subject → "Theory 3"
3. Upload: "new_textbook.pdf"
4. Click: Upload PDF
5. Click: Process New Documents (wait...)
6. Restart app
```

### Example 2: Create New Subject

```
1. Expand "➕ Add PDFs"
2. Select: New Subject
3. Type: "Algorithms"
4. Upload: "algorithms_textbook.pdf"
5. Click: Upload PDF
6. Click: Process New Documents (wait...)
7. Restart app
8. "Algorithms" now appears in subject dropdown!
```

### Example 3: Bulk Upload

```
1. Upload first PDF → Success
2. Upload second PDF → Success
3. Upload third PDF → Success
4. Click "Process New Documents" ONCE (processes all)
5. Restart app
```

---

## File Organization

After uploading, your PDFs are organized like this:

```
data/pdfs/
├── Theory 3/
│   ├── existing_file1.pdf
│   ├── existing_file2.pdf
│   └── new_file.pdf          ← Just uploaded
└── Algorithms/               ← New subject
    └── algorithms_book.pdf   ← Just uploaded
```

---

## Troubleshooting

### "File already exists"
**Error:** `File 'textbook.pdf' already exists in subject 'Theory 3'`

**Solution:**
- Rename your file before uploading, or
- File already in database - no need to upload again

### Upload button doesn't work
**Cause:** Missing subject name or file

**Solution:**
- Make sure you entered a subject name
- Make sure you selected a PDF file

### "Ingestion failed"
**Possible causes:**
1. PDF is corrupted or password-protected
2. File is too large (>500 pages may take very long)
3. Disk space issues

**Solution:**
- Check the error message
- Try with a smaller/simpler PDF first
- Check `logs/api.log` for details

### New subject doesn't appear
**Cause:** Forgot to restart app

**Solution:**
- After processing, you MUST restart: `Ctrl+C` then `./start.sh`

### Processing takes forever
**Normal:** Large PDFs (200+ pages) can take 5-10 minutes

**If stuck >15 minutes:**
1. Check terminal for errors
2. Try restarting app
3. Check if PDF is valid

---

## Behind the Scenes

### What Happens When You Upload:

1. **Upload** → PDF saved to `data/pdfs/[subject]/[filename].pdf`
2. **Process** → Runs `python scripts/ingest_documents.py`
   - Extracts text from PDF
   - Splits into chunks
   - Generates embeddings
   - Stores in vector database
3. **Restart** → Agent reloads, sees new documents

### File Validation

- ✅ Only PDF files accepted
- ✅ Duplicate detection (won't overwrite)
- ✅ Subject folders created automatically

---

## Tips & Best Practices

### 📁 Subject Organization

**Good subject names:**
- "Theory 3" (clear, numbered)
- "Algorithms" (specific topic)
- "Machine Learning 2024" (with date)

**Avoid:**
- "Misc" (too vague)
- "Temp" (not descriptive)
- Very long names

### 📄 PDF Quality

**Best results:**
- Text-based PDFs (not scanned images)
- Clear formatting
- Reasonable file size (<50MB)

**May have issues:**
- Scanned PDFs without OCR
- Password-protected PDFs
- Very large files (>100MB)

### ⏱️ Processing Time

Expected processing times:
- Small PDF (10 pages): ~30 seconds
- Medium PDF (100 pages): ~2-3 minutes
- Large PDF (500 pages): ~5-10 minutes

### 🔄 When to Process

**Process documents:**
- After uploading one or more PDFs
- Not needed after every single upload
- Can batch multiple uploads then process once

**Don't need to process:**
- If just asking questions
- If documents already in database

---

## Alternative: Terminal Upload

If UI upload isn't working, you can still use terminal:

```bash
# 1. Copy PDF to subject folder
cp ~/Downloads/textbook.pdf data/pdfs/"Theory 3"/

# 2. Run ingestion
python scripts/ingest_documents.py

# 3. Restart app
./start.sh
```

---

## API Endpoints (Advanced)

### Upload Endpoint
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/file.pdf" \
  -F "subject=Theory 3"
```

### Ingest Endpoint
```bash
curl -X POST "http://localhost:8000/api/ingest"
```

### Check Subjects
```bash
curl http://localhost:8000/api/subjects
```

---

## FAQ

**Q: Can I upload multiple files at once?**
A: Currently one at a time, but you can upload several, then process all at once.

**Q: What file formats are supported?**
A: Only PDF files currently.

**Q: Can I delete uploaded files?**
A: Not via UI yet. Use terminal: `rm data/pdfs/"Subject Name"/file.pdf`

**Q: How do I rename a subject?**
A: Rename the folder: `mv data/pdfs/"Old Name" data/pdfs/"New Name"`, then re-ingest.

**Q: Can I upload from URL?**
A: Not yet - download the PDF first, then upload.

**Q: Is there a file size limit?**
A: No hard limit, but very large files (>100MB) may be slow or cause issues.

---

## Summary

1. **Upload** = Add PDF to folder
2. **Process** = Add to searchable database
3. **Restart** = Load new documents

**The UI makes this easy!** 🎉

Just click → Upload → Process → Restart!
