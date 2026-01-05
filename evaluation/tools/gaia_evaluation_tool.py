"""
GAIA Evaluation Tool

This tool provides a simple interface for evaluating agents on the GAIA benchmark.
"""

from typing import Dict, Any, Optional, List
import json
import os
from datetime import datetime
from ..benchmarks.gaia import GAIADataset, GAIAEvaluator, GAIAMetrics


class GAIAEvaluationTool:
    """GAIA benchmark evaluation tool"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize GAIA evaluation tool
        
        Args:
            data_dir: Path to the GAIA dataset directory
        """
        self.data_dir = data_dir
        self.evaluator = GAIAEvaluator(data_dir)
        self.results = None
    
    def run(
        self,
        agent: Any,
        level: int = 1,
        max_samples: Optional[int] = None,
        export_results: bool = True,
        generate_report: bool = True,
        output_dir: str = "./gaia_results",
        tolerance: float = 0.0,
        subset: str = "validation"
    ) -> Dict[str, Any]:
        """
        Run GAIA evaluation on the given agent
        
        Args:
            agent: Agent instance with a run() method
            level: GAIA difficulty level (1, 2, or 3)
            max_samples: Maximum number of samples to evaluate (None for all)
            export_results: Whether to export results in GAIA format
            generate_report: Whether to generate evaluation report
            output_dir: Directory to save results
            tolerance: Numeric tolerance for floating point comparisons
            subset: Dataset subset (test or validation)
            
        Returns:
            Dictionary containing evaluation results
        """
        print("\n" + "="*60)
        print("GAIA Evaluation")
        print("="*60)
        print("\n")
        
        print("Configuration:")
        print(f"   Difficulty Level: {level}")
        print(f"   Number of Samples: {max_samples if max_samples else 'All'}")
        print(f"   Dataset: validation")
        print(f"   Output Directory: {output_dir}")
        
        print("\n" + "="*60)
        print("Step 1: Loading GAIA Dataset")
        print("="*60)
        
        # Load dataset for the specified level
        split = f"2023_level{level}"
        print(f"   Loading GAIA dataset: {split}/{subset}")
        self.evaluator.load_dataset(split=split, subset=subset)
        
        # Get dataset statistics
        stats = self.evaluator.get_statistics()
        print(f"✅ GAIA dataset loaded successfully")
        print(f"   Data Source: gaia-benchmark/GAIA")
        print(f"   Split: {subset}")
        print(f"   Level: {level}")
        print(f"   Total Samples: {stats['total_examples']}")
        print(f"   Examples with Files: {stats['examples_with_files']}")
        print(f"   Examples without Files: {stats['examples_without_files']}")
        
        print("\n" + "="*60)
        print("Step 2: Running GAIA Evaluation")
        print("="*60)
        
        # Evaluate agent
        num_samples = min(max_samples, len(self.evaluator.dataset)) if max_samples else len(self.evaluator.dataset)
        print(f"🌟 Starting GAIA evaluation...")
        print(f"   Number of Samples: {num_samples}")
        
        metrics = self.evaluator.evaluate_agent(
            agent=agent,
            tolerance=tolerance,
            max_examples=max_samples
        )
        
        print(f"\n✅ GAIA evaluation completed")
        
        # Calculate additional metrics
        total_samples = len(self.evaluator.predictions)
        exact_matches = sum(metrics['matches'])
        exact_match_rate = exact_matches / total_samples if total_samples > 0 else 0.0
        
        # Calculate partial match (if answer contains correct information)
        partial_matches = self._calculate_partial_matches(
            self.evaluator.predictions,
            self.evaluator.ground_truths
        )
        partial_match_rate = partial_matches / total_samples if total_samples > 0 else 0.0
        
        # Compile results
        self.results = {
            'exact_match_rate': exact_match_rate,
            'partial_match_rate': partial_match_rate,
            'exact_matches': exact_matches,
            'partial_matches': partial_matches,
            'total_samples': total_samples,
            'level': level,
            'metrics': metrics,
            'detailed_results': self.evaluator.get_detailed_results(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Print results
        print("\n" + "="*60)
        print("🎯 Evaluation Results")
        print("="*60)
        self._print_results()
        
        # Export results if requested
        if export_results:
            print("\n" + "="*60)
            print("Step 3: Exporting GAIA Format Results")
            print("="*60)
            self._export_results(output_dir)
        
        # Generate report if requested
        if generate_report:
            print("\n" + "="*60)
            print("Step 4: Generating Evaluation Report")
            print("="*60)
            self._generate_report(output_dir)
        
        print("\n" + "="*60)
        print("🎉 GAIA evaluation process completed")
        print("="*60)
        
        return self.results
    
    def _calculate_partial_matches(
        self,
        predictions: List[Any],
        ground_truths: List[Any]
    ) -> int:
        """
        Calculate partial matches (answers that contain correct information)
        
        Args:
            predictions: List of predictions
            ground_truths: List of ground truths
            
        Returns:
            Number of partial matches
        """
        partial_matches = 0
        
        for pred, gt in zip(predictions, ground_truths):
            pred_str = str(pred).lower()
            gt_str = str(gt).lower()
            
            # Check if prediction contains ground truth (or vice versa)
            if gt_str in pred_str or pred_str in gt_str:
                partial_matches += 1
        
        return partial_matches
    
    def _print_results(self) -> None:
        """Print evaluation results"""
        print("\n" + "=" * 60)
        print("GAIA BENCHMARK EVALUATION RESULTS")
        print("=" * 60)
        print(f"Level: {self.results['level']}")
        print(f"Total samples: {self.results['total_samples']}")
        print(f"Exact matches: {self.results['exact_matches']}")
        print(f"Partial matches: {self.results['partial_matches']}")
        print(f"\nExact match rate: {self.results['exact_match_rate']:.2%}")
        print(f"Partial match rate: {self.results['partial_match_rate']:.2%}")
        print("=" * 60)
    
    def _export_results(self, output_dir: str) -> None:
        """
        Export results in GAIA format
        
        Args:
            output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Create timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export in GAIA OFFICIAL JSONL format
        official_gaia_file = os.path.join(output_dir, f"gaia_level{self.results['level']}_result_{timestamp}.jsonl")
        
        with open(official_gaia_file, 'w', encoding='utf-8') as f:
            for result in self.results['detailed_results']:
                # GAIA official format: task_id, model_answer, reasoning_trace
                gaia_entry = {
                    'task_id': result['task_id'],
                    'model_answer': str(result['prediction']),
                    'reasoning_trace': str(result['prediction'])  # Using prediction as reasoning for now
                }
                f.write(json.dumps(gaia_entry, ensure_ascii=False) + '\n')
        
        # Save detailed results (custom format)
        detailed_file = os.path.join(output_dir, f"gaia_detailed_results_level{self.results['level']}_{timestamp}.json")
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results exported to: {output_dir}")
        print(f"   GAIA official format: {official_gaia_file}")
        print(f"   Detailed results: {detailed_file}")
    
    def _generate_report(self, output_dir: str) -> None:
        """
        Generate evaluation report in markdown format
        
        Args:
            output_dir: Directory to save report
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(output_dir, f"gaia_report_level{self.results['level']}_{timestamp}.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# GAIA Evaluation Report\n\n")
            f.write(f"**Generated at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Evaluation Overview
            f.write("## 📊 Evaluation Overview\n\n")
            f.write(f"- **Difficulty Level**: {self.results['level']}\n")
            f.write(f"- **Total Samples**: {self.results['total_samples']}\n")
            f.write(f"- **Exact Matches**: {self.results['exact_matches']}\n")
            f.write(f"- **Partial Matches**: {self.results['partial_matches']}\n")
            f.write(f"- **Exact Match Rate**: {self.results['exact_match_rate']:.2%}\n")
            f.write(f"- **Partial Match Rate**: {self.results['partial_match_rate']:.2%}\n\n")
            
            # Detailed Metrics
            f.write("## 📈 Detailed Metrics\n\n")
            
            # Level-wise Accuracy
            f.write("### Level-wise Accuracy\n\n")
            level_acc = self.results['metrics'].get('level_accuracy', {})
            for level in [1, 2, 3]:
                if level_acc.get(level) is not None:
                    f.write(f"- **Level {level}**: {level_acc[level]:.2%} exact\n")
            
            # Drop Rates
            drop_rates = self.results['metrics'].get('drop_rates', {})
            if drop_rates:
                f.write("\n### Difficulty Progression Drop Rates\n\n")
                if '1_to_2' in drop_rates:
                    f.write(f"- **Level 1 → 2**: {drop_rates['1_to_2']:.2%}\n")
                if '2_to_3' in drop_rates:
                    f.write(f"- **Level 2 → 3**: {drop_rates['2_to_3']:.2%}\n")
            
            f.write("\n")
            
            # Sample Details
            f.write("## 📝 Sample Details (Top 10)\n\n")
            f.write("| Task ID | Level | Prediction | Ground Truth | Exact Match |\n")
            f.write("|--------|------|------------|--------------|-------------|\n")
            
            for result in self.results['detailed_results'][:10]:
                match_symbol = "✅" if result['match'] else "❌"
                f.write(f"| {result['task_id']} | {result.get('level', 1)} | {result['prediction']} | {result['ground_truth']} | {match_symbol} |\n")
            
            # Accuracy Visualization
            f.write("\n## 📊 Accuracy Visualization\n\n")
            
            # Create simple ASCII bar chart
            exact_percent = int(self.results['exact_match_rate'] * 100)
            partial_percent = int(self.results['partial_match_rate'] * 100)
            
            exact_bar = "█" * exact_percent + "░" * (100 - exact_percent)
            partial_bar = "█" * partial_percent + "░" * (100 - partial_percent)
            
            f.write(f"Exact Match: {exact_bar} {self.results['exact_match_rate']:.2%}\n")
            f.write(f"Partial Match: {partial_bar} {self.results['partial_match_rate']:.2%}\n\n")
            
            # Recommendations
            f.write("## 💡 Recommendations\n\n")
            if self.results['exact_match_rate'] >= 0.8:
                f.write("✅ **Excellent**: Outstanding performance, keep it up.\n")
            elif self.results['exact_match_rate'] >= 0.5:
                f.write("⚠️ **Good**: Average performance, needs improvement.\n")
            else:
                f.write("❌ **Poor**: Poor performance, significant improvement needed.\n")
            
            f.write("\n- 💡 Suggest checking tool usage and multi-step reasoning capabilities.\n")
            f.write("- 💡 Consider optimizing system prompts to ensure output meets GAIA format requirements.\n")
            f.write("- 💡 Enhance ability to handle complex questions.\n\n")
            
            # Raw Results Link
            f.write("## 📁 Result Files\n\n")
            f.write(f"- Detailed Results JSON: [gaia_detailed_results_level{self.results['level']}_{timestamp}.json](gaia_detailed_results_level{self.results['level']}_{timestamp}.json)\n")
            f.write(f"- GAIA Official Format: [gaia_level{self.results['level']}_result_{timestamp}.jsonl](gaia_level{self.results['level']}_result_{timestamp}.jsonl)\n")
        
        print(f"✅ Report generated: {report_file}")
    
    def get_results(self) -> Optional[Dict[str, Any]]:
        """
        Get the last evaluation results
        
        Returns:
            Results dictionary or None if no evaluation has been run
        """
        return self.results
