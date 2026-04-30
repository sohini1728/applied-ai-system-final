# 🎬 Quick Reference: Recording Your Loom Video

## 30-Second Setup

```bash
cd ~/applied-ai-system-final
chmod +x run.sh
./run.sh
# Wait for: "* Running on http://localhost:5000"
```

Then:
1. Open http://localhost:5000 in browser
2. Go to https://www.loom.com and hit "Start recording" 
3. Select "Record desktop"
4. Follow the 7 sections below

---

## The 7 Sections (8 minutes total)

### Section A (1 min): Setup
```bash
cd ~/applied-ai-system-final
clear
echo "=== VibeFinder Pro: AI-Powered Music Recommender ==="
echo "Extended from Module 3 with RAG, Agentic Workflow & Reliability Testing"
echo ""
ls -la src/ tests/ data/
```
**Say:** "This is VibeFinder Pro... [read from LOOM_RECORDING_SCRIPT.md]"

### Section B (30 sec): Start Server
- Show the `./run.sh` running and terminal output
- **Say:** "Now I'm launching the Flask web server..."

### Section C (2 min): Pop/Happy Profile
- Browser to http://localhost:5000
- Click "Pop/Happy" button
- **Pause and highlight:**
  - Confidence score
  - 4-step workflow
  - 5 recommendation cards
  - Reasons & sources
  - AI narrative
- **Say:** "When I clicked Pop/Happy... [read from script]"

### Section D (1 min): Lofi/Chill Profile
- Click "Lofi/Chill" button
- Show different recommendations
- Point out lower confidence
- **Say:** "Now with Lofi/Chill... [read from script]"

### Section E (1.5 min): Evaluation
- Scroll down to "System Evaluation"
- Click "Run Full Evaluation"
- Wait for metrics (10-15 sec)
- Show the 5 metric cards
- Read the summary
- **Say:** "Running the evaluation... [read from script]"

### Section F (1.5 min): Code & Docs
- Back to terminal
- `cat src/agent.py | head -60`
- `head -40 README.md`
- **Say:** "The core AI logic... [read from script]"

### Section G (30 sec): Summary
- Back to browser
- Show GitHub link at bottom
- Final remarks
- **Say:** "VibeFinder Pro demonstrates... [read from script]"

---

## Copy-Paste Commands

**Terminal setup:**
```bash
cd ~/applied-ai-system-final
clear
echo "=== VibeFinder Pro: AI-Powered Music Recommender ==="
echo "Extended from Module 3 with RAG, Agentic Workflow & Reliability Testing"
echo ""
ls -la src/ tests/ data/
```

**Show agent code:**
```bash
cat src/agent.py | head -60
```

**Show README:**
```bash
head -40 README.md
```

---

## What NOT to Do

❌ Don't rush through sections
❌ Don't interrupt the system mid-output
❌ Don't forget to speak/explain
❌ Don't have the browser zoomed too small
❌ Don't have terminal text too small

---

## What TO Do

✅ Speak clearly and confidently
✅ Let each section fully load/complete
✅ Point out the key elements (workflow, confidence, metrics)
✅ Show code that demonstrates the AI logic
✅ Keep terminal/browser zoomed for readability

---

## After Recording

1. Loom will process (1-5 min)
2. Click "Share" 
3. Copy the link (https://www.loom.com/share/xxxxx)
4. Edit README.md - find "Video Walkthrough" section
5. Add your link
6. `git add README.md && git commit -m "Add Loom video" && git push`

Done! 🎉

---

## Pro Tips

- **Practice once** without recording first
- **Speak like you're explaining to a friend** - not robotic
- **Don't worry about perfection** - graders care about content
- **Test audio** before recording (click "Test Speaker")
- **Good lighting** makes screen easier to read
- **Keep talking** - silence can make video seem slow

---

## If Something Goes Wrong

**Web server won't start?**
- `pip install flask flask-cors`
- Try port 5001: edit app.py line 150: `app.run(debug=True, port=5001)`

**Browser won't load?**
- Try incognito window
- Hard refresh: Cmd+Shift+R
- Check terminal shows "Running on..."

**Evaluation takes too long?**
- Just show terminal output instead
- Or skip to code section
- Evaluation is meant to show reliability - terminal demo also works

**Need to re-record?**
- No problem! Delete the first Loom
- Record a new one
- Only add the final link to README

---

## You Got This! 🎵

The web frontend makes this look great. Just follow the script, speak clearly, and let the system do its thing. Your graders will be impressed!

Questions? Check LOOM_RECORDING_SCRIPT.md for detailed script with exact things to say.
