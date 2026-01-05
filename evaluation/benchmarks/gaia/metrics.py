"""
GAIA Evaluation Metrics

This module provides metrics for evaluating GAIA benchmark performance.
"""

from typing import List, Dict, Any
from .quasi_exact_match import quasi_exact_match, batch_quasi_exact_match


class GAIAMetrics:
    """GAIA benchmark metrics calculator"""
    
    @staticmethod
    def accuracy(matches: List[bool]) -> float:
        """
        Calculate accuracy (percentage of correct predictions)
        
        Args:
            matches: List of boolean match results
            
        Returns:
            Accuracy score (0-1)
        """
        if not matches:
            return 0.0
        return sum(matches) / len(matches)
    
    @staticmethod
    def exact_match(predictions: List[Any], ground_truths: List[Any]) -> float:
        """
        Calculate exact match accuracy using quasi-exact matching
        
        Args:
            predictions: List of predictions
            ground_truths: List of ground truths
            
        Returns:
            Exact match accuracy (0-1)
        """
        matches = batch_quasi_exact_match(predictions, ground_truths)
        return GAIAMetrics.accuracy(matches)
    
    @staticmethod
    def calculate_metrics(
        predictions: List[Any], 
        ground_truths: List[Any],
        levels: List[int] = None,
        tolerance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive metrics for GAIA evaluation
        
        Args:
            predictions: List of predictions
            ground_truths: List of ground truths
            levels: Optional list of difficulty levels for each example
            tolerance: Numeric tolerance for floating point comparisons
            
        Returns:
            Dictionary containing various metrics
        """
        if len(predictions) != len(ground_truths):
            raise ValueError("Predictions and ground truths must have the same length")
        
        if levels and len(predictions) != len(levels):
            raise ValueError("Levels must have the same length as predictions")
        
        matches = batch_quasi_exact_match(predictions, ground_truths, tolerance)
        
        total = len(predictions)
        correct = sum(matches)
        incorrect = total - correct
        
        metrics = {
            'total': total,
            'correct': correct,
            'incorrect': incorrect,
            'exact_match_rate': correct / total if total > 0 else 0.0,
            'matches': matches,
            'tolerance': tolerance
        }
        
        # Calculate level-wise accuracy if levels are provided
        if levels:
            level_accuracy = {}
            for level in [1, 2, 3]:
                level_indices = [i for i, l in enumerate(levels) if l == level]
                if level_indices:
                    level_matches = [matches[i] for i in level_indices]
                    level_accuracy[level] = sum(level_matches) / len(level_matches)
                else:
                    level_accuracy[level] = None
            
            metrics['level_accuracy'] = level_accuracy
            
            # Calculate difficulty progression drop rates
            drop_rates = {}
            if level_accuracy[1] is not None and level_accuracy[2] is not None and level_accuracy[1] > 0:
                drop_rates['1_to_2'] = (level_accuracy[1] - level_accuracy[2]) / level_accuracy[1]
            
            if level_accuracy[2] is not None and level_accuracy[3] is not None and level_accuracy[2] > 0:
                drop_rates['2_to_3'] = (level_accuracy[2] - level_accuracy[3]) / level_accuracy[2]
            
            metrics['drop_rates'] = drop_rates
        
        return metrics
    
    @staticmethod
    def format_metrics(metrics: Dict[str, Any]) -> str:
        """
        Format metrics for display
        
        Args:
            metrics: Metrics dictionary from calculate_metrics()
            
        Returns:
            Formatted string
        """
        lines = [
            "=" * 60,
            "GAIA Benchmark Evaluation Results",
            "=" * 60,
            f"Total examples: {metrics['total']}",
            f"Correct: {metrics['correct']}",
            f"Incorrect: {metrics['incorrect']}",
            f"Accuracy: {metrics['accuracy']:.2%}",
            "=" * 60
        ]
        return "\n".join(lines)
    
    @staticmethod
    def get_detailed_results(
        predictions: List[Any], 
        ground_truths: List[Any],
        questions: List[Any] = None,
        tolerance: float = 0.0,
        task_ids: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get detailed results for each example
        
        Args:
            predictions: List of predictions
            ground_truths: List of ground truths
            questions: Optional list of questions (can be strings or full example dicts)
            tolerance: Numeric tolerance for floating point comparisons
            task_ids: Optional list of task IDs
            
        Returns:
            List of detailed result dictionaries
        """
        # Handle partial evaluation - only evaluate the predictions we have
        num_predictions = len(predictions)
        # Ensure ground_truths is a sliceable sequence
        try:
            ground_truths_subset = ground_truths[:num_predictions]
        except (TypeError, AttributeError):
            raise ValueError("ground_truths must be a sliceable sequence (list, tuple, etc.)")
        # Ensure questions is a sliceable sequence before slicing
        # Check if it's a list, tuple, or other sequence type that supports slicing
        questions_subset = None
        if questions:
            # Check if it's a sliceable type (list, tuple, etc.) but not a dict
            if hasattr(questions, '__getitem__') and hasattr(questions, '__len__') and not isinstance(questions, (dict, set)):
                try:
                    questions_subset = questions[:num_predictions]
                except (TypeError, AttributeError):
                    # If slicing fails, just use None
                    pass
        # Apply the same slice protection to task_ids
        task_ids_subset = None
        if task_ids:
            if hasattr(task_ids, '__getitem__') and hasattr(task_ids, '__len__') and not isinstance(task_ids, (dict, set)):
                try:
                    task_ids_subset = task_ids[:num_predictions]
                except (TypeError, AttributeError):
                    pass
        
        if len(predictions) != len(ground_truths_subset):
            raise ValueError("Predictions and ground truths must have the same length")
        
        results = []
        for i, (pred, gt) in enumerate(zip(predictions, ground_truths_subset)):
            match = quasi_exact_match(pred, gt, tolerance)
            
            result = {
                'index': i,
                'task_id': task_ids_subset[i] if task_ids_subset else f"example_{i+1}",
                'prediction': pred,
                'ground_truth': gt,
                'match': match
            }
            
            if questions_subset:
                question_item = questions_subset[i]
                if isinstance(question_item, dict):
                    # Full example dict
                    result['question'] = question_item.get('Question', '')
                    result['level'] = question_item.get('Level', 1)
                    result['file_name'] = question_item.get('file_name', '')
                else:
                    # Just the question string
                    result['question'] = question_item
            
            results.append(result)
        
        return results
