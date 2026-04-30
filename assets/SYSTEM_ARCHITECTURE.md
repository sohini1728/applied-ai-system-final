# VibeFinder Pro - System Architecture Diagram

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                                │
│            (Taste Profile)                                   │
│  • favorite_genre                                            │
│  • favorite_mood                                             │
│  • target_energy (0.0-1.0)                                   │
│  • likes_acoustic (true/false)                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           SONGS DATABASE                                     │
│      (30 songs × 14 genres)                                  │
│  • id, title, artist, genre, mood                           │
│  • energy, tempo, valence, danceability, acousticness       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         AGENT ORCHESTRATOR                                   │
│     (Multi-Step Reasoning)                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ STEP 1: SCORE (Recommender)                        │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ Input: user_prefs, songs                           │    │
│  │ Algorithm:                                         │    │
│  │  • Genre match: +2.0 pts                          │    │
│  │  • Mood match: +1.0 pt                            │    │
│  │  • Energy similarity: up to +2.0 pts              │    │
│  │  • Acousticness fit: +0-1.0 pts                   │    │
│  │ Output: scored_songs (top 3)                       │    │
│  └─────────────────────────────────────────────────────┘    │
│                      │                                      │
│                      ▼                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ STEP 2: DISCOVER (Retriever - RAG)                 │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ Input: top_song_from_step_1                        │    │
│  │ Algorithm:                                         │    │
│  │  • Compute semantic similarity (6 dimensions)      │    │
│  │  • Genre (exact/related/different)                 │    │
│  │  • Mood (fuzzy matching)                           │    │
│  │  • Energy, tempo, acousticness, valence            │    │
│  │ Output: similar_songs (top 2)                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                      │                                      │
│                      ▼                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ STEP 3: EXPLORE (Retriever - Discovery)            │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ Input: user's favorite_genre                       │    │
│  │ Algorithm:                                         │    │
│  │  • Find adjacent genres (pre-defined graph)        │    │
│  │  • Retrieve songs from those genres                │    │
│  │  • Exclude songs already recommended               │    │
│  │ Output: exploration_songs (top 2)                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                      │                                      │
│                      ▼                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ STEP 4: VALIDATE (Agent Logic)                     │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ Input: all candidates from steps 1-3               │    │
│  │ Actions:                                           │    │
│  │  • Rank all by score (highest first)               │    │
│  │  • Compute confidence: score_quality * 0.4 +       │    │
│  │                       diversity * 0.3 +            │    │
│  │                       match_strength * 0.3         │    │
│  │  • Generate reasoning narrative                    │    │
│  │ Output: final_recommendations (top k)              │    │
│  └─────────────────────────────────────────────────────┘    │
│                      │                                      │
└──────────────────────┼──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         EVALUATION & RELIABILITY TESTING                     │
│            (EvaluationMetrics)                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Metric 1: DIVERSITY                                        │
│  Formula: (unique_genres + unique_artists) / (2 × k)       │
│  Range: 0.0 - 1.0                                           │
│  Measures: Genre/artist variety (prevents filter bubble)    │
│                                                              │
│  Metric 2: RELEVANCE                                        │
│  Formula: (recs_matching_genre_or_mood) / total            │
│  Range: 0.0 - 1.0                                           │
│  Measures: How well system delivers user preferences        │
│                                                              │
│  Metric 3: NOVELTY                                          │
│  Formula: (recs_outside_favorite_genre) / total            │
│  Range: 0.0 - 1.0                                           │
│  Measures: Discovery factor (novelty score)                │
│                                                              │
│  Metric 4: CALIBRATION                                      │
│  Formula: 1.0 - |reported_confidence - actual_quality|    │
│  Range: 0.0 - 1.0                                           │
│  Measures: How well confidence scores match reality         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              OUTPUT                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Top K Recommendations:                                      │
│  • Song title & artist                                      │
│  • Genre & mood                                             │
│  • Score (0-6 scale)                                        │
│  • Source (direct_match/discovery/exploration)             │
│  • Reasons (explicit scoring breakdown)                     │
│                                                              │
│  Confidence Score (0-1 scale)                               │
│  • High confidence: user preferences strongly matched       │
│  • Low confidence: uncertain or limited options             │
│                                                              │
│  Reasoning Narrative                                        │
│  • Explanation of workflow steps                            │
│  • Why recommendations were chosen                          │
│  • How confidence was computed                              │
│                                                              │
│  Evaluation Metrics                                         │
│  • Diversity, Relevance, Novelty, Calibration scores       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

```
src/
├── recommender.py (Core Scoring)
│   ├── Song (dataclass)
│   ├── UserProfile (dataclass)
│   ├── Recommender (class)
│   │   ├── recommend() → List[Tuple[Song, score, reasons]]
│   │   └── _score_song() → Tuple[score, reasons]
│   └── load_songs() → List[Song]
│
├── retriever.py (RAG Semantic Similarity)
│   ├── SimilarityRetriever (class)
│   │   ├── compute_similarity() → float (0-1)
│   │   ├── _mood_similarity() → float (fuzzy matching)
│   │   ├── retrieve_similar() → List[Tuple[Song, similarity]]
│   │   └── retrieve_by_exploration() → List[Song]
│   └── [Similarity Cache]
│
├── agent.py (Multi-Step Reasoning)
│   ├── Agent (class)
│   │   ├── plan_recommendations() → RecommendationPlan
│   │   ├── _find_adjacent_genres() → List[str]
│   │   ├── _compute_confidence() → float
│   │   ├── _create_reasoning_narrative() → str
│   │   └── get_execution_log() → List[Dict]
│   └── RecommendationPlan (dataclass)
│
├── evaluator.py (Reliability Testing)
│   ├── EvaluationMetrics (class)
│   │   ├── evaluate_diversity() → float
│   │   ├── evaluate_relevance() → float
│   │   ├── evaluate_novelty() → float
│   │   ├── evaluate_confidence_calibration() → float
│   │   ├── run_full_evaluation() → Dict
│   │   ├── get_evaluation_summary() → str
│   │   ├── save_results() → None
│   │   └── load_results() → None
│   └── [Results JSON]
│
└── main.py (Orchestrator)
    ├── run_demo() → None
    ├── print_recommendation_results() → None
    └── [Logging & Error Handling]

tests/
└── test_recommender.py (15+ Tests)
    ├── TestRecommender (4 tests)
    ├── TestRetriever (3 tests)
    ├── TestAgent (2 tests)
    └── TestEvaluator (5+ tests)

data/
└── songs.csv (30 songs, 14 genres)

assets/
└── [System diagram, screenshots]
```

---

## Data Types

### Song
```python
@dataclass
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float (0-1)
    tempo_bpm: float
    valence: float (0-1, positivity)
    danceability: float (0-1)
    acousticness: float (0-1)
```

### UserProfile
```python
@dataclass
class UserProfile:
    favorite_genre: str
    favorite_mood: str
    target_energy: float (0-1)
    likes_acoustic: bool
```

### RecommendationPlan
```python
@dataclass
class RecommendationPlan:
    user_profile: Dict
    steps: List[str]  # Workflow steps executed
    recommendations: List[Dict]  # Final recs with scores
    confidence: float (0-1)
    reasoning: str  # Narrative explanation
```

---

## Key Design Patterns

### 1. **Modular Component Design**
- Each component (recommender, retriever, agent, evaluator) is independent
- Can test/modify one without affecting others
- Easy to swap implementations (e.g., different similarity metric)

### 2. **Multi-Step Agentic Workflow**
- Step 1: Score (direct matches)
- Step 2: Discover (semantic similarity)
- Step 3: Explore (adjacent genres)
- Step 4: Validate (rank & confidence)
- Each step is observable and debuggable

### 3. **Interpretability First**
- Every recommendation includes reasoning (why chosen)
- Scoring breakdown shows contribution of each factor
- Confidence score quantifies uncertainty
- Execution log records all steps

### 4. **Comprehensive Evaluation**
- Measures diversity (variety), relevance (preference match), novelty (discovery), calibration (confidence quality)
- Not just accuracy (unmeasurable without ground truth)
- Enables continuous improvement

---

## Execution Flow

### Example: Pop/Happy Lover (energy 0.8, acoustic: false)

```
INPUT: {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": false}
                                              │
                                              ▼
STEP 1: SCORE all 30 songs
  • "Sunrise City" (pop, happy, 0.85 energy): 2.0 + 1.0 + 1.9 + 0.1 = 5.78 ✓ Top
  • "Neon City Lights" (pop, happy, 0.80 energy): 2.0 + 1.0 + 2.0 + 0.1 = 5.10
  • "Energetic Pop" (pop, happy, 0.85 energy): 2.0 + 1.0 + 1.9 + 0.1 = 5.00
  → Return top 3 direct matches
                                              │
                                              ▼
STEP 2: DISCOVER similar to "Sunrise City" (pop, happy, 0.85, 0.1 acoustic)
  • Compute similarity to all other songs:
    - "Rooftop Lights" (indie pop, happy, 0.72, 0.35 acoustic): 0.82 ✓
    - "Dance Floor Groove" (dance, happy, 0.88, 0.08 acoustic): 0.71
  → Return top 2 similar songs
                                              │
                                              ▼
STEP 3: EXPLORE adjacent genres
  • Adjacent to "pop": indie pop, electronic, dance
  • Retrieve 2 non-pop songs from these genres
  → "Dance Floor Groove" + one other
                                              │
                                              ▼
STEP 4: VALIDATE & RANK
  • Combine all candidates: 3 (direct) + 2 (discover) + 2 (explore) = 7 candidates
  • Rank by score:
    1. "Sunrise City" - 5.78 [direct_match]
    2. "Neon City Lights" - 5.62 [direct_match]
    3. "Energetic Pop" - 5.51 [direct_match]
    4. "Rooftop Lights" - 4.12 [discovery]
    5. "Dance Floor Groove" - 3.94 [exploration]
  • Compute confidence: 87.2%
    (score_quality: 5.6/6.0=0.93, diversity: 0.80, match_strength: 0.80)
  • Generate narrative
                                              │
                                              ▼
EVALUATION:
  • Diversity: 0.85 (4 genres, 4 artists in top 5)
  • Relevance: 1.00 (all 5 match genre or mood)
  • Novelty: 0.40 (2/5 outside favorite "pop" genre)
  • Calibration: 0.92 (confidence close to quality)
                                              │
                                              ▼
OUTPUT: 5 recommendations + confidence + reasoning + metrics
```

---

This architecture enables:
✅ **Interpretability** - Every decision explained
✅ **Modularity** - Swap components independently
✅ **Testability** - Each step can be tested
✅ **Reliability** - Comprehensive evaluation
✅ **Extensibility** - Easy to add features
