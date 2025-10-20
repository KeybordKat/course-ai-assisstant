# Subject-Based Organization Setup

## How to Organize Your PDFs by Subject

### Step 1: Create Subject Folders

Organize your PDFs into subject folders inside `data/pdfs/`:

```
data/pdfs/
├── theory/
│   ├── Languages & Theory of Computation Introduction 4th Ed.pdf
│   └── combined_problems_solutions_week01.pdf
├── logic/
│   ├── LogicInComputerScience copy.pdf
│   └── combined_problems_solutions_week02.pdf
└── algorithms/
    └── algorithms_textbook.pdf
```

### Step 2: Re-ingest Documents

After organizing into folders, run:
```bash
python scripts/ingest_documents.py
```

The system will automatically tag each document with its subject based on the folder name.

### Step 3: Use Subject Filter in UI

In the UI sidebar, you can now:
- Select "All Subjects" to search everything
- Select a specific subject to only search those documents

## Current Subjects Detected

The system will auto-detect subjects based on your folder structure.

## Benefits

- **Faster searches**: Only search relevant documents
- **Better accuracy**: Agent focuses on the right course material
- **Organized**: Keep different courses separate
