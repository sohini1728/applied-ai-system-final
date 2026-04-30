"""
Flask web server for VibeFinder Pro
Provides a clean web interface to interact with the recommendation system
"""

from flask import Flask, render_template, request, jsonify
import json
import logging
from src.recommender import load_songs, Recommender, UserProfile
from src.retriever import SimilarityRetriever
from src.agent import Agent
from src.evaluator import EvaluationMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize components once at startup
try:
    songs = load_songs("data/songs.csv")
    recommender = Recommender(songs)
    retriever = SimilarityRetriever(songs)
    agent = Agent(recommender, retriever)
    logger.info("✅ VibeFinder Pro initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize: {e}")
    songs = []


@app.route('/')
def index():
    """Render the main interface"""
    return render_template('index.html')


@app.route('/api/genres')
def get_genres():
    """Get list of available genres"""
    genres = sorted(set(song.genre for song in songs))
    return jsonify(genres)


@app.route('/api/moods')
def get_moods():
    """Get list of available moods"""
    moods = sorted(set(song.mood for song in songs))
    return jsonify(moods)


@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """
    Get recommendations based on user preferences
    Expected JSON:
    {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": false
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_prefs = {
            "favorite_genre": data.get("favorite_genre", "pop").lower(),
            "favorite_mood": data.get("favorite_mood", "happy").lower(),
            "target_energy": float(data.get("target_energy", 0.5)),
            "likes_acoustic": bool(data.get("likes_acoustic", False)),
        }
        
        # Generate plan
        plan = agent.plan_recommendations(user_prefs, k=5)
        
        # Format response
        response = {
            "userProfile": user_prefs,
            "confidence": round(plan.confidence, 3),
            "workflowSteps": plan.steps,
            "recommendations": [
                {
                    "title": rec["title"],
                    "artist": rec["artist"],
                    "genre": rec["genre"],
                    "mood": rec["mood"],
                    "energy": rec.get("energy", 0),
                    "score": round(rec["score"], 2),
                    "source": rec["source"],
                    "reasons": rec["reasons"],
                }
                for rec in plan.recommendations
            ],
            "reasoning": plan.reasoning,
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/evaluate', methods=['POST'])
def evaluate_system():
    """
    Run evaluation on multiple test profiles
    """
    try:
        test_profiles = [
            {
                "favorite_genre": "pop",
                "favorite_mood": "happy",
                "target_energy": 0.8,
                "likes_acoustic": False,
            },
            {
                "favorite_genre": "lofi",
                "favorite_mood": "chill",
                "target_energy": 0.35,
                "likes_acoustic": True,
            },
            {
                "favorite_genre": "rock",
                "favorite_mood": "intense",
                "target_energy": 0.9,
                "likes_acoustic": False,
            },
            {
                "favorite_genre": "jazz",
                "favorite_mood": "relaxed",
                "target_energy": 0.45,
                "likes_acoustic": True,
            },
        ]
        
        evaluator = EvaluationMetrics()
        results = evaluator.run_full_evaluation(agent, test_profiles)
        
        return jsonify({
            "status": "success",
            "timestamp": results["timestamp"],
            "profilesTested": results["total_profiles_tested"],
            "metricsAveraged": {
                "diversity": round(results["average_diversity"], 3),
                "relevance": round(results["average_relevance"], 3),
                "novelty": round(results["average_novelty"], 3),
                "calibration": round(results["average_calibration"], 3),
            },
            "overallScore": round(results["overall_quality_score"], 3),
            "summary": evaluator.get_evaluation_summary(),
        })
    
    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/test-data')
def get_test_data():
    """Get sample test profiles"""
    return jsonify({
        "profiles": [
            {
                "name": "Pop/Happy Lover",
                "genre": "pop",
                "mood": "happy",
                "energy": 0.8,
                "acoustic": False,
            },
            {
                "name": "Chill Lofi Vibes",
                "genre": "lofi",
                "mood": "chill",
                "energy": 0.35,
                "acoustic": True,
            },
            {
                "name": "Intense Rock Fan",
                "genre": "rock",
                "mood": "intense",
                "energy": 0.9,
                "acoustic": False,
            },
            {
                "name": "Relaxed Jazz Enthusiast",
                "genre": "jazz",
                "mood": "relaxed",
                "energy": 0.45,
                "acoustic": True,
            },
        ]
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "songsLoaded": len(songs),
        "genres": len(set(song.genre for song in songs)),
    })


if __name__ == '__main__':
    logger.info("🎵 Starting VibeFinder Pro Web Server")
    logger.info("📱 Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
