"""
Run evaluation of the triage system with improved accuracy.
"""
import sys
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.workflows.triage_workflow import TriageWorkflow
from src.utils.logger import logger

def load_test_scenarios():
    """Load test scenarios from JSON file."""
    scenarios_file = Path(__file__).parent / "data" / "test_scenarios.json"
    
    with open(scenarios_file, 'r') as f:
        data = json.load(f)
    
    return data["test_scenarios"]

def run_evaluation(workflow, scenarios):
    """Run evaluation on all test scenarios."""
    results = []
    
    print(f"\n{'='*80}")
    print(f"Running evaluation on {len(scenarios)} scenarios...")
    print(f"{'='*80}\n")
    
    for i, scenario in enumerate(scenarios, 1):
        scenario_id = scenario['id']
        category = scenario['category']
        patient_input = scenario['patient_input']
        expected_urgency = scenario['expected_urgency']
        
        print(f"\n[{i}/{len(scenarios)}] Testing: {scenario_id} ({category})")
        print(f"Expected: {expected_urgency}")
        
        try:
            # Run triage
            result = workflow.run_triage(patient_input)
            
            actual_urgency = result.get('urgency_level', 'UNKNOWN')
            correct = (actual_urgency == expected_urgency)
            
            # Extract red flag info
            red_flags_data = result.get('red_flags', [])
            num_red_flags = len(red_flags_data) if red_flags_data else 0
            
            # Get severity info if available
            critical_flags = sum(1 for rf in red_flags_data 
                               if isinstance(rf, dict) and 
                               (rf.get('severity') == 'critical' or rf.get('type') == 'critical'))
            warning_flags = sum(1 for rf in red_flags_data 
                              if isinstance(rf, dict) and 
                              rf.get('type') == 'warning')
            
            print(f"Actual: {actual_urgency} {'✓' if correct else '✗'}")
            if red_flags_data:
                print(f"Red flags: {num_red_flags} (Critical: {critical_flags}, Warning: {warning_flags})")
            
            results.append({
                'scenario_id': scenario_id,
                'category': category,
                'expected_urgency': expected_urgency,
                'actual_urgency': actual_urgency,
                'correct': correct,
                'time_sensitive': result.get('time_sensitive', False),
                'red_flags': num_red_flags,
                'critical_flags': critical_flags,
                'warning_flags': warning_flags,
                'care_setting': result.get('care_setting', ''),
                'needs_more_info': result.get('needs_more_info', False),
                'success': True,
                'error': ''
            })
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            logger.error(f"Error processing {scenario_id}: {e}")
            results.append({
                'scenario_id': scenario_id,
                'category': category,
                'expected_urgency': expected_urgency,
                'actual_urgency': 'ERROR',
                'correct': False,
                'time_sensitive': False,
                'red_flags': 0,
                'critical_flags': 0,
                'warning_flags': 0,
                'care_setting': '',
                'needs_more_info': False,
                'success': False,
                'error': str(e)
            })
    
    return pd.DataFrame(results)

def calculate_metrics(df):
    """Calculate performance metrics."""
    metrics = {}
    
    # Overall accuracy
    metrics['overall_accuracy'] = (df['correct'].sum() / len(df)) * 100
    
    # Accuracy by category
    for category in df['category'].unique():
        category_df = df[df['category'] == category]
        accuracy = (category_df['correct'].sum() / len(category_df)) * 100
        metrics[f'{category.lower()}_accuracy'] = accuracy
    
    # Red flag detection (for emergency cases)
    emergency_df = df[df['expected_urgency'] == 'EMERGENCY']
    if len(emergency_df) > 0:
        # Check if critical flags were detected for emergency cases
        detected = emergency_df['critical_flags'].sum()
        total = len(emergency_df)
        metrics['critical_flag_detection_rate'] = (detected / total) * 100
    
    # Success rate
    metrics['success_rate'] = (df['success'].sum() / len(df)) * 100
    
    return metrics

def print_results(df, metrics):
    """Print evaluation results."""
    print(f"\n{'='*80}")
    print("EVALUATION RESULTS")
    print(f"{'='*80}\n")
    
    print("Performance Metrics:")
    print(f"  Overall Accuracy: {metrics['overall_accuracy']:.2f}%")
    print(f"  Success Rate: {metrics['success_rate']:.2f}%")
    
    print("\nAccuracy by Category:")
    for key, value in metrics.items():
        if '_accuracy' in key and key != 'overall_accuracy':
            category = key.replace('_accuracy', '').upper()
            print(f"  {category}: {value:.2f}%")
    
    if 'critical_flag_detection_rate' in metrics:
        print(f"\nCritical Flag Detection Rate: {metrics['critical_flag_detection_rate']:.2f}%")
    
    print("\nDetailed Results by Scenario:")
    print(df[['scenario_id', 'expected_urgency', 'actual_urgency', 'correct', 
              'critical_flags', 'warning_flags']].to_string(index=False))
    
    # Confusion matrix
    print("\n\nConfusion Matrix:")
    confusion = pd.crosstab(
        df['expected_urgency'], 
        df['actual_urgency'],
        rownames=['Expected'],
        colnames=['Actual'],
        margins=True
    )
    print(confusion)

def save_results(df, metrics):
    """Save results to files."""
    output_dir = Path(__file__).parent / "data"
    
    # Save detailed results
    results_file = output_dir / "evaluation_results_improved.csv"
    df.to_csv(results_file, index=False)
    print(f"\n✓ Saved detailed results to: {results_file}")
    
    # Save metrics summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'metrics': metrics,
        'total_scenarios': int(len(df)),
        'successful_runs': int(df['success'].sum())
    }
    
    summary_file = output_dir / "evaluation_summary_improved.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved metrics summary to: {summary_file}")

def main():
    """Main evaluation function."""
    print("="*80)
    print("MedGemma AI Triage System - Improved Accuracy Evaluation")
    print("="*80)
    
    # Load scenarios
    print("\nLoading test scenarios...")
    scenarios = load_test_scenarios()
    print(f"✓ Loaded {len(scenarios)} test scenarios")
    
    # Initialize workflow
    print("\nInitializing triage workflow (this may take a few minutes)...")
    workflow = TriageWorkflow()
    print("✓ Workflow initialized")
    
    # Run evaluation
    df = run_evaluation(workflow, scenarios)
    
    # Calculate metrics
    metrics = calculate_metrics(df)
    
    # Print results
    print_results(df, metrics)
    
    # Save results
    save_results(df, metrics)
    
    # Check if target accuracy achieved
    target_accuracy = 70.0
    if metrics['overall_accuracy'] >= target_accuracy:
        print(f"\n{'='*80}")
        print(f"🎉 SUCCESS! Target accuracy of {target_accuracy}% achieved!")
        print(f"Overall Accuracy: {metrics['overall_accuracy']:.2f}%")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print(f"⚠️  Target accuracy of {target_accuracy}% not yet achieved.")
        print(f"Current Accuracy: {metrics['overall_accuracy']:.2f}%")
        print(f"Gap: {target_accuracy - metrics['overall_accuracy']:.2f}%")
        print(f"{'='*80}")
    
    return metrics

if __name__ == "__main__":
    main()
