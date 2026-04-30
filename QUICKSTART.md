# 🚀 Quick Start: VibeFinder Pro Web Interface

## Installation & Launch (2 minutes)

```bash
cd ~/applied-ai-system-final

# Make run script executable
chmod +x run.sh

# Start the web server (installs dependencies automatically)
./run.sh
```

You'll see:
```
🎵 Starting VibeFinder Pro Web Server...
📱 Open http://localhost:5000 in your browser
```

## Using the Web Interface

### 1. **Input Your Music Taste** (Left Panel)
- Select your **favorite genre** (pop, rock, lofi, jazz, etc.)
- Choose your **favorite mood** (happy, chill, intense, relaxed, etc.)
- Adjust **energy level** slider (0 = chill, 1 = energetic)
- Check "I prefer acoustic music" if applicable
- Click **"Get Recommendations"**

### 2. **View Recommendations** (Right Panel)
The system shows:
- **Confidence Score** - How confident is the AI? (0-100%)
- **AI Workflow** - 4 observable steps the agent took:
  1. **Score** - Found direct matches via recommender
  2. **Discover** - Retrieved similar songs via RAG retriever
  3. **Explore** - Explored adjacent genres for discovery
  4. **Validate** - Computed final scores and confidence

- **5 Recommendation Cards**:
  - Song title, artist, genre, mood, energy
  - Score (0-1 scale)
  - Source: "Direct Match", "RAG Retrieval", or "Exploration"
  - Reasons explaining why this song matches your preferences

- **AI Reasoning** - Natural language explanation of the overall recommendation strategy

### 3. **Run System Evaluation**
Scroll to "System Evaluation" section and click **"Run Full Evaluation"** to see:
- **Diversity** (0-100%): Genre/artist variety in recommendations
- **Relevance** (0-100%): How well recs match your preferences
- **Novelty** (0-100%): Discovery factor outside your stated genre
- **Calibration** (0-100%): How well confidence scores match actual quality
- **Overall Score** (0-100%): Aggregate system quality

### 4. **Quick Test Profiles**
Use the preset buttons in the left panel to instantly test different profiles:
- **Pop/Happy** - High energy, positive mood
- **Lofi/Chill** - Low energy, relaxing
- **Rock/Intense** - Maximum energy, intensity

---

## Architecture Overview

### Components Working Together:

1. **Recommender** (src/recommender.py)
   - Loads 30 songs from CSV
   - Scores songs based on genre, mood, energy, acousticness

2. **RAG Retriever** (src/retriever.py)
   - Computes semantic similarity across 6 dimensions
   - Enables discovery beyond exact matches
   - Caches computations for efficiency

3. **Agent** (src/agent.py)
   - Orchestrates 4-step planning workflow
   - Combines recommender + retriever
   - Computes confidence scores
   - Generates reasoning narratives

4. **Evaluator** (src/evaluator.py)
   - Measures reliability across 4 metrics
   - Tests on multiple user profiles
   - Aggregates results with overall score

---

## What's Being Demonstrated

This web interface showcases **VibeFinder Pro**, an applied AI system featuring:

✅ **RAG (Retrieval-Augmented Generation)**
- 6-dimensional semantic similarity (genre 25%, mood 20%, energy 20%, tempo 15%, acousticness 10%, valence 10%)
- Enables discovery beyond exact matching

✅ **Agentic Workflow**
- Multi-step planning with observable reasoning
- Step 1: Direct preference matching
- Step 2: Semantic similarity retrieval
- Step 3: Adjacent genre exploration
- Step 4: Confidence scoring & validation

✅ **Reliability Testing**
- Diversity measurement (genre/artist variety)
- Relevance measurement (preference matching)
- Novelty measurement (discovery factor)
- Calibration measurement (confidence accuracy)

---

## Troubleshooting

**"Address already in use"?**
```bash
# Change port in app.py line ~150: app.run(debug=True, port=5001)
# Or kill existing process:
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**Port not responding?**
```bash
# Make sure Flask is installed:
pip install flask flask-cors

# Run directly:
python3 app.py
```

**No genres/moods showing?**
```bash
# Ensure data file exists:
ls -la data/songs.csv
# If missing, regenerate from README instructions
```

---

## Full Documentation

- **README.md** - Complete system documentation with architecture diagrams
- **model_card.md** - Detailed AI ethics, biases, and evaluation metrics
- **LOOM_RECORDING_SCRIPT.md** - Recording instructions for video demo
- **GitHub Repository** - https://github.com/sohini1728/applied-ai-system-final

---

**Ready to see it in action?** Run `./run.sh` and open http://localhost:5000! 🎵
