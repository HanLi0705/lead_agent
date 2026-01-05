"""
Quasi Exact Match Algorithm for GAIA Evaluation

This module implements the quasi-exact matching algorithm used in GAIA benchmark evaluation.
"""

import re
import json
from typing import Any, Union


def normalize_string(s: str) -> str:
    """
    Normalize a string for comparison
    
    Args:
        s: Input string
        
    Returns:
        Normalized string
    """
    # Convert to lowercase
    s = s.lower()
    
    # Remove articles (a, an, the) at the beginning
    s = re.sub(r'\b(a|an|the)\b\s*', '', s)
    
    # Remove extra whitespace
    s = re.sub(r'\s+', ' ', s)
    
    # Strip leading/trailing whitespace
    s = s.strip()
    
    # Remove common punctuation at the end
    s = re.sub(r'[.,!?;:]+$', '', s)
    
    return s


def normalize_number(value: Union[str, int, float]) -> str:
    """
    Normalize a numeric value for comparison
    
    Args:
        value: Numeric value (string, int, or float)
        
    Returns:
        Normalized string representation
    """
    if isinstance(value, (int, float)):
        return str(value)
    
    # Remove currency symbols ($, €, £, etc.)
    value = re.sub(r'[$€£¥₹₽]', '', value)
    
    # Remove percentage sign
    value = re.sub(r'%', '', value)
    
    # Remove commas from numbers (e.g., "1,234" -> "1234")
    value = re.sub(r',', '', value)
    
    # Try to parse as float
    try:
        num = float(value)
        # If it's an integer, return without decimal
        if num == int(num):
            return str(int(num))
        return str(num)
    except ValueError:
        return normalize_string(value)


def extract_number(s: str) -> Union[float, None]:
    """
    Extract the first number from a string
    
    Args:
        s: Input string
        
    Returns:
        Extracted number or None
    """
    # Try to find a number in the string
    match = re.search(r'-?\d+\.?\d*', s)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def normalize_list(value: str) -> str:
    """
    Normalize a list string for comparison
    
    Args:
        value: Input list string (e.g., "Paris, London, Berlin")
        
    Returns:
        Normalized list string (e.g., "berlin,london,paris")
    """
    # Split by comma
    items = [item.strip() for item in value.split(',')]
    
    # Normalize each item
    normalized_items = [normalize_string(item) for item in items]
    
    # Sort alphabetically
    normalized_items.sort()
    
    # Join with comma
    return ','.join(normalized_items)


def quasi_exact_match(
    prediction: Any, 
    ground_truth: Any, 
    tolerance: float = 0.0
) -> bool:
    """
    Perform quasi-exact match between prediction and ground truth
    
    This is the main evaluation metric used in GAIA benchmark. It handles:
    - String matching with normalization
    - Numeric matching with optional tolerance
    - List/set matching
    - JSON/dict matching
    
    Args:
        prediction: Predicted answer
        ground_truth: Ground truth answer
        tolerance: Numeric tolerance for floating point comparisons
        
    Returns:
        True if prediction matches ground truth, False otherwise
    """
    # Handle None values
    if prediction is None and ground_truth is None:
        return True
    if prediction is None or ground_truth is None:
        return False
    
    # Handle numeric types
    if isinstance(prediction, (int, float)) and isinstance(ground_truth, (int, float)):
        return abs(prediction - ground_truth) <= tolerance
    
    # Handle string types
    if isinstance(prediction, str) and isinstance(ground_truth, str):
        # Try numeric comparison first
        pred_num = extract_number(prediction)
        gt_num = extract_number(ground_truth)
        
        if pred_num is not None and gt_num is not None:
            return abs(pred_num - gt_num) <= tolerance
        
        # Check if both strings look like lists (contain commas)
        pred_has_comma = ',' in prediction
        gt_has_comma = ',' in ground_truth
        
        if pred_has_comma and gt_has_comma:
            # Both look like lists, use list normalization
            return normalize_list(prediction) == normalize_list(ground_truth)
        
        # Otherwise do string comparison
        return normalize_string(prediction) == normalize_string(ground_truth)
    
    # Handle mixed string/numeric types
    if isinstance(prediction, str) and isinstance(ground_truth, (int, float)):
        pred_num = extract_number(prediction)
        if pred_num is not None:
            return abs(pred_num - ground_truth) <= tolerance
        return normalize_string(prediction) == normalize_string(str(ground_truth))
    
    if isinstance(prediction, (int, float)) and isinstance(ground_truth, str):
        gt_num = extract_number(ground_truth)
        if gt_num is not None:
            return abs(prediction - gt_num) <= tolerance
        return normalize_string(str(prediction)) == normalize_string(ground_truth)
    
    # Handle list/set types
    if isinstance(prediction, (list, set)) and isinstance(ground_truth, (list, set)):
        # Convert to lists for consistent processing
        pred_list = list(prediction) if isinstance(prediction, set) else prediction
        gt_list = list(ground_truth) if isinstance(ground_truth, set) else ground_truth
        
        # Normalize each element
        pred_normalized = [normalize_string(str(item)) for item in pred_list]
        gt_normalized = [normalize_string(str(item)) for item in gt_list]
        
        # Sort and compare
        pred_normalized.sort()
        gt_normalized.sort()
        
        return pred_normalized == gt_normalized
    
    # Handle dict types
    if isinstance(prediction, dict) and isinstance(ground_truth, dict):
        return json.dumps(prediction, sort_keys=True) == json.dumps(ground_truth, sort_keys=True)
    
    # Default: convert to string and compare
    return normalize_string(str(prediction)) == normalize_string(str(ground_truth))


def batch_quasi_exact_match(
    predictions: list, 
    ground_truths: list, 
    tolerance: float = 0.0
) -> list[bool]:
    """
    Perform batch quasi-exact matching
    
    Args:
        predictions: List of predictions
        ground_truths: List of ground truths
        tolerance: Numeric tolerance for floating point comparisons
        
    Returns:
        List of boolean match results
    """
    if len(predictions) != len(ground_truths):
        raise ValueError("Predictions and ground truths must have the same length")
    
    return [
        quasi_exact_match(pred, gt, tolerance)
        for pred, gt in zip(predictions, ground_truths)
    ]
