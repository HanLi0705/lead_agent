"""
GAIA Dataset Loader

This module provides functionality to load and preprocess the GAIA benchmark dataset.
"""

from typing import Dict, List, Any, Optional
from datasets import load_dataset, Dataset
import os


class GAIADataset:
    """GAIA benchmark dataset loader"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize GAIA dataset loader
        
        Args:
            data_dir: Path to the downloaded GAIA dataset. If None, will try to load from default location.
        """
        self.data_dir = data_dir
        self.dataset = None
        self.split = None
        
    def load(self, split: str = "2023_level1", subset: str = "test") -> Dataset:
        """
        Load GAIA dataset
        
        Args:
            split: Dataset split (e.g., "2023_level1", "2023_level2", "2023_level3")
            subset: Dataset subset (e.g., "test", "validation")
            
        Returns:
            Loaded dataset
        """
        if self.data_dir:
            self.dataset = load_dataset(self.data_dir, split, split=subset)
        else:
            # Load directly from HuggingFace
            self.dataset = load_dataset("gaia-benchmark/GAIA", split, split=subset)
        
        self.split = split
        print(f"✅ Loaded {len(self.dataset)} examples from {split}/{subset}")
        return self.dataset
    
    def get_example(self, index: int) -> Dict[str, Any]:
        """
        Get a specific example from the dataset
        
        Args:
            index: Index of the example
            
        Returns:
            Example dictionary
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load() first.")
        
        return self.dataset[index]
    
    def get_file_path(self, example: Dict[str, Any]) -> Optional[str]:
        """
        Get the full file path for an example if it has an associated file
        
        Args:
            example: Example dictionary
            
        Returns:
            Full file path or None
        """
        if 'file_path' in example and example['file_path'] and self.data_dir:
            return os.path.join(self.data_dir, example['file_path'])
        return None
    
    def get_questions(self) -> List[str]:
        """
        Get all questions from the dataset
        
        Returns:
            List of questions
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load() first.")
        
        return [example['Question'] for example in self.dataset]
    
    def get_ground_truths(self) -> List[str]:
        """
        Get all ground truth answers from the dataset
        
        Returns:
            List of ground truth answers
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load() first.")
        
        return [example['Final answer'] for example in self.dataset]
    
    def get_examples_with_files(self) -> List[Dict[str, Any]]:
        """
        Get examples that have associated files
        
        Returns:
            List of examples with files
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load() first.")
        
        return [example for example in self.dataset 
                if 'file_path' in example and example['file_path']]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get dataset statistics
        
        Returns:
            Dictionary with dataset statistics
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load() first.")
        
        total = len(self.dataset)
        with_files = len(self.get_examples_with_files())
        
        # Count by difficulty level if available
        levels = {}
        for example in self.dataset:
            level = example.get('Level', 'unknown')
            levels[level] = levels.get(level, 0) + 1
        
        return {
            'total_examples': total,
            'examples_with_files': with_files,
            'examples_without_files': total - with_files,
            'difficulty_levels': levels,
            'split': self.split
        }
    
    def __len__(self) -> int:
        """Get the number of examples in the dataset"""
        if self.dataset is None:
            return 0
        return len(self.dataset)
    
    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Get an example by index"""
        return self.get_example(index)
