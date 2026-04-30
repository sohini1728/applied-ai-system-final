"""
Evaluation and reliability testing component.
Measures recommendation quality, diversity, and consistency.
"""

from typing import List, Dict, Any, Tuple
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class EvaluationMetrics:
    """Metrics for assessing recommendation quality."""
    
    def __init__(self):
        self.results = []

    def evaluate_diversity(self, recommendations: List[Dict]) -> float:
        """
        Compute diversity score (0-1).
        Higher = more genre and artist variety.
        """
        if not recommendations:
            return 0.0
        
        genres = set(rec['genre'] for rec in recommendations)
        artists = set(rec['artist'] for rec in recommendations)
        
        # Diversity = (unique_genres + unique_artists) / (2 * total_songs)
        diversity = (len(genres) + len(artists)) / (2 * len(recommendations))
        return min(1.0, diversity)

    def evaluate_relevance(self, recommendations: List[Dict], user_prefs: Dict) -> float:
        """
        Compute relevance score (0-1).
        Higher = more direct matches to stated preferences.
        """
        if not recommendations:
            return 0.0
        
        favorite_genre = user_prefs.get('favorite_genre', '').lower()
        favorite_mood = user_prefs.get('favorite_mood', '').lower()
        
        matches = 0
        for rec in recommendations:
            if rec['genre'].lower() == favorite_genre or rec['mood'].lower() == favorite_mood:
                matches += 1
        
        relevance = matches / len(recommendations)
        return min(1.0, relevance)

    def evaluate_novelty(self, recommendations: List[Dict], user_prefs: Dict) -> float:
        """
        Compute novelty score (0-1).
        Higher = more songs outside user's stated genre (discovery factor).
        """
        if not recommendations:
            return 0.0
        
        favorite_genre = user_prefs.get('favorite_genre', '').lower()
        novel_count = sum(
            1 for rec in recommendations
            if rec['genre'].lower() != favorite_genre
        )
        
        novelty = novel_count / len(recommendations)
        return min(1.0, novelty)

    def evaluate_consistency(self, plan_results: List[Dict]) -> float:
        """
        Evaluate consistency across multiple runs with similar profiles.
        Higher = more stable/consistent recommendations.
        """
        if len(plan_results) < 2:
            return 0.5  # Can't measure consistency with <2 runs
        
        # Compare overlap in recommendations
        first_titles = set(plan_results[0]['titles'])
        overlap_counts = []
        
        for other in plan_results[1:]:
            other_titles = set(other['titles'])
            overlap = len(first_titles.intersection(other_titles))
            overlap_counts.append(overlap / len(first_titles) if first_titles else 0)
        
        consistency = sum(overlap_counts) / len(overlap_counts) if overlap_counts else 0.5
        return min(1.0, consistency)

    def evaluate_confidence_calibration(self, recommendations: List[Dict], confidence: float) -> float:
        """
        Check if reported confidence matches recommendation quality.
        Returns 1.0 if well-calibrated, <1.0 if over/under-confident.
        """
        # Compute actual quality from recommendation scores
        avg_score = sum(rec['score'] for rec in recommendations) / len(recommendations) if recommendations else 0
        actual_quality = min(1.0, avg_score / 6.0)
        
        # Calibration: how close is confidence to actual quality?
        calibration = 1.0 - abs(confidence - actual_quality)
        return max(0.0, calibration)

    def run_full_evaluation(self, agent, test_profiles: List[Dict]) -> Dict[str, Any]:
        """
        Run comprehensive evaluation suite.
        Returns detailed metrics and assessment.
        """
        logger.info(f"Starting full evaluation with {len(test_profiles)} test profiles")
        
        all_recommendations = []
        all_confidences = []
        metrics_by_profile = []
        
        for i, profile in enumerate(test_profiles):
            logger.info(f"Evaluating profile {i+1}: {profile}")
            
            # Generate plan
            plan = agent.plan_recommendations(profile, k=5)
            
            # Evaluate this profile
            diversity = self.evaluate_diversity(plan.recommendations)
            relevance = self.evaluate_relevance(plan.recommendations, profile)
            novelty = self.evaluate_novelty(plan.recommendations, profile)
            calibration = self.evaluate_confidence_calibration(plan.recommendations, plan.confidence)
            
            metrics = {
                'profile': profile,
                'diversity': diversity,
                'relevance': relevance,
                'novelty': novelty,
                'confidence': plan.confidence,
                'calibration': calibration,
                'recommendation_count': len(plan.recommendations),
                'sources': list(set(rec['source'] for rec in plan.recommendations)),
            }
            metrics_by_profile.append(metrics)
            
            all_recommendations.extend(plan.recommendations)
            all_confidences.append(plan.confidence)
            
            logger.info(f"Profile {i+1} metrics: diversity={diversity:.2f}, relevance={relevance:.2f}, novelty={novelty:.2f}")
        
        # Aggregate metrics
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_profiles_tested': len(test_profiles),
            'total_recommendations_generated': len(all_recommendations),
            'average_diversity': sum(m['diversity'] for m in metrics_by_profile) / len(metrics_by_profile),
            'average_relevance': sum(m['relevance'] for m in metrics_by_profile) / len(metrics_by_profile),
            'average_novelty': sum(m['novelty'] for m in metrics_by_profile) / len(metrics_by_profile),
            'average_confidence': sum(all_confidences) / len(all_confidences),
            'average_calibration': sum(m['calibration'] for m in metrics_by_profile) / len(metrics_by_profile),
            'per_profile_metrics': metrics_by_profile,
        }
        
        # Overall assessment
        overall_score = (
            summary['average_relevance'] * 0.4 +
            summary['average_diversity'] * 0.3 +
            summary['average_novelty'] * 0.2 +
            summary['average_calibration'] * 0.1
        )
        summary['overall_quality_score'] = overall_score
        
        self.results.append(summary)
        
        logger.info(f"Evaluation complete. Overall score: {overall_score:.2f}/1.0")
        return summary

    def get_evaluation_summary(self) -> str:
        """Generate human-readable evaluation summary."""
        if not self.results:
            return "No evaluation results available."
        
        latest = self.results[-1]
        
        summary = f"""
RECOMMENDATION SYSTEM EVALUATION SUMMARY
{'='*60}

Test Date: {latest['timestamp']}
Profiles Evaluated: {latest['total_profiles_tested']}
Recommendations Generated: {latest['total_recommendations_generated']}

QUALITY METRICS:
  • Diversity Score:        {latest['average_diversity']:.1%} (variety of genres/artists)
  • Relevance Score:        {latest['average_relevance']:.1%} (matches stated preferences)
  • Novelty Score:          {latest['average_novelty']:.1%} (discovery factor)
  • Confidence Calibration: {latest['average_calibration']:.1%} (confidence accuracy)
  • Overall Quality Score:  {latest['overall_quality_score']:.1%}

KEY FINDINGS:
""".strip()
        
        # Add observations
        if latest['average_relevance'] > 0.8:
            summary += "\n  ✓ System strongly matches user preferences"
        else:
            summary += "\n  ⚠ Consider refining preference matching"
        
        if latest['average_diversity'] > 0.7:
            summary += "\n  ✓ Recommendations show good genre/artist variety"
        else:
            summary += "\n  ⚠ Low diversity - may create filter bubble"
        
        if latest['average_novelty'] > 0.4:
            summary += "\n  ✓ Discovery recommendations help expand taste"
        else:
            summary += "\n  ⚠ Limited discovery - mostly safe recommendations"
        
        if latest['average_calibration'] > 0.75:
            summary += "\n  ✓ Confidence scores are well-calibrated"
        else:
            summary += "\n  ⚠ Confidence scores may be over/under-confident"
        
        summary += f"\n\nRECOMMENDATION: System is {'ready for deployment' if latest['overall_quality_score'] > 0.7 else 'needs improvement'}"
        summary += f"\n{'='*60}"
        
        return summary

    def save_results(self, filepath: str) -> None:
        """Save evaluation results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Evaluation results saved to {filepath}")

    def load_results(self, filepath: str) -> None:
        """Load evaluation results from JSON file."""
        with open(filepath, 'r') as f:
            self.results = json.load(f)
        logger.info(f"Evaluation results loaded from {filepath}")
