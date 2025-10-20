# Relevance Threshold Tuning Guide

## What is the Relevance Threshold?

The relevance threshold filters search results to only include citations above a certain quality level. This prevents low-quality or irrelevant chunks from appearing in your answers.

**Relevance Score:** A number between 0.0 (completely irrelevant) and 1.0 (perfect match)

## Current Setting

**Default:** `0.3` (30% relevance)

This is a good balance for most use cases - strict enough to filter noise but lenient enough to find relevant information.

## How to Change It

### Option 1: Environment Variable (Recommended)
Edit your `.env` file:
```bash
RELEVANCE_THRESHOLD=0.4  # Adjust as needed
```

### Option 2: Direct Config (For Testing)
Edit `src/config.py`:
```python
RELEVANCE_THRESHOLD = 0.4  # Change this line
```

Then restart your app: `./start.sh`

## Choosing the Right Value

### 🎯 Recommended Values

| Threshold | Description | Use Case |
|-----------|-------------|----------|
| **0.2** | Very lenient | When you want many results, even loosely related |
| **0.3** | Balanced (default) | Good for most questions - filters obvious noise |
| **0.4** | Strict | When you only want highly relevant results |
| **0.5** | Very strict | For very specific queries with precise matches |
| **0.6+** | Extremely strict | May return too few results for complex questions |

### 📊 Examples

#### Threshold: 0.2 (Lenient)
```
Question: "What is a Turing machine?"
Results: 5 citations (relevance: 0.85, 0.72, 0.54, 0.31, 0.23)
✅ Includes borderline relevant results
```

#### Threshold: 0.3 (Default)
```
Question: "What is a Turing machine?"
Results: 4 citations (relevance: 0.85, 0.72, 0.54, 0.31)
✅ Good balance - filters obvious noise
```

#### Threshold: 0.5 (Strict)
```
Question: "What is a Turing machine?"
Results: 2 citations (relevance: 0.85, 0.72)
⚠️  Fewer results, but very high quality
```

## Symptoms & Solutions

### 😕 "I'm not getting enough results"
**Symptom:** Often seeing "No results above relevance threshold"

**Solution:** Lower the threshold
```bash
RELEVANCE_THRESHOLD=0.2  # More lenient
```

### 😤 "I'm getting too many irrelevant results"
**Symptom:** Citations don't seem related to your question

**Solution:** Raise the threshold
```bash
RELEVANCE_THRESHOLD=0.4  # More strict
```

### 🤔 "Results are inconsistent"
**Symptom:** Sometimes good, sometimes bad results

**Solution:** Try subject filtering first (may be more effective)
- Select specific subject in UI sidebar
- This is often more impactful than threshold tuning

## Testing Your Threshold

### 1. Ask a Known Question
```
Question: "What is propositional logic?"
```
Expected: Should find relevant results from Logic book

### 2. Check Reasoning Steps
Look at the reasoning section in UI:
```
📚 Searched course materials and found 3 relevant chunks (threshold: 0.3)
📄 Most relevant: LogicInComputerScience.pdf, Page 42 (relevance: 0.87)
```

### 3. Review Citation Quality
- Are the citations actually relevant to your question?
- If not, raise threshold
- If too few, lower threshold

## Advanced: Per-Query Tuning

Currently, the threshold is global. To add per-query threshold:

1. **Add to API** (`src/api/main.py`):
```python
class QuestionRequest(BaseModel):
    question: str
    use_web_search: bool = True
    subject: Optional[str] = None
    relevance_threshold: Optional[float] = None  # Add this
```

2. **Pass to Agent** (`src/agent/core.py`):
```python
def retrieve_from_course(self, query: str, n_results: int = 5,
                         subject: Optional[str] = None,
                         threshold: Optional[float] = None) -> List[Citation]:
    threshold = threshold or config.RELEVANCE_THRESHOLD
    # ... rest of code
```

3. **Add UI Control** (`src/ui/app.py`):
```python
threshold = st.slider("Relevance Threshold", 0.0, 1.0, 0.3)
```

## Monitoring Threshold Impact

### Log Filtered Results
Check your API logs:
```bash
tail -f logs/api.log | grep "relevant chunks"
```

You'll see lines like:
```
📚 Searched course materials and found 3 relevant chunks (threshold: 0.3)
```

### Compare Settings
Try different thresholds on the same question:
```bash
# Terminal 1
export RELEVANCE_THRESHOLD=0.2
./start.sh

# Ask: "What is a Turing machine?"
# Note number of results

# Terminal 2
export RELEVANCE_THRESHOLD=0.5
./start.sh

# Ask same question
# Compare number and quality of results
```

## Best Practices

### 1. Start with Default (0.3)
Don't change unless you have a specific problem

### 2. Use Subject Filtering First
Subject filtering is often more effective:
- Select "Theory 3" instead of "All Subjects"
- This narrows search space more intelligently

### 3. Adjust Gradually
Change by 0.1 increments:
- 0.3 → 0.4 (if too many irrelevant results)
- 0.3 → 0.2 (if too few results)

### 4. Test with Known Questions
Use questions you know have answers in your PDFs

### 5. Consider Query Type
- **Specific questions** → Higher threshold (0.4-0.5)
- **Broad questions** → Lower threshold (0.2-0.3)

## Troubleshooting

### Q: Threshold doesn't seem to work
**A:** Make sure to restart the app after changing `.env`:
```bash
# Stop current app (Ctrl+C)
./start.sh  # Restart
```

### Q: What's a good starting point for my domain?
**A:**
- **Technical/precise domains** (CS, Math): 0.3-0.4
- **Broad/fuzzy domains** (History, Literature): 0.2-0.3

### Q: Can I see the actual relevance scores?
**A:** Yes! They're shown in the reasoning section and in the citation list

### Q: Should I use threshold or subject filtering?
**A:** **Use both!**
1. First, select the right subject
2. Then, adjust threshold if needed

## Example Workflow

```bash
# 1. Start with defaults
./start.sh

# 2. Ask a question
"What is NP-completeness?"

# 3. Check reasoning steps
"📚 Searched course materials and found 2 relevant chunks (threshold: 0.3)"

# 4. If too few results, lower threshold
# Edit .env: RELEVANCE_THRESHOLD=0.2
# Restart: ./start.sh

# 5. Ask again and verify
"📚 Searched course materials and found 4 relevant chunks (threshold: 0.2)"

# 6. Review quality - are new results helpful?
# If yes, keep new threshold
# If no (too much noise), try 0.25 or revert to 0.3
```

## Summary

- **Default (0.3)** works well for most cases
- **Lower (0.2)** for more results, broader questions
- **Higher (0.4-0.5)** for higher quality, specific questions
- **Use subject filtering** first before tuning threshold
- **Test and iterate** to find your sweet spot

---

**Pro Tip:** The "sweet spot" depends on your PDFs, question types, and personal preference. Experiment! 🎯
