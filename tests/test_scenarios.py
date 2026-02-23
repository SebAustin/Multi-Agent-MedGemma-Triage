"""
Test the system with predefined scenarios.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.triage_workflow import TriageWorkflow
from src.utils.logger import logger


def load_test_scenarios() -> list[Dict[str, Any]]:
    """Load test scenarios from JSON file."""
    scenarios_file = Path(__file__).parent.parent / "data" / "test_scenarios.json"
    
    with open(scenarios_file, 'r') as f:
        data = json.load(f)
    
    return data["test_scenarios"]


def evaluate_scenario(workflow: TriageWorkflow, scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a single test scenario.
    
    Returns dict with results and evaluation metrics.
    """
    scenario_id = scenario["id"]
    patient_input = scenario["patient_input"]
    expected_urgency = scenario["expected_urgency"]
    
    logger.info(f"Testing scenario: {scenario_id}")
    
    try:
        # Run triage
        result = workflow.run_triage(patient_input)
        
        if result.get("error"):
            return {
                "scenario_id": scenario_id,
                "success": False,
                "error": result["error"]
            }
        
        # Extract results
        actual_urgency = result.get("urgency_level", "")
        actual_care = result.get("care_setting", "")
        detected_red_flags = result.get("red_flags", [])
        
        # Evaluate correctness
        urgency_correct = actual_urgency == expected_urgency
        
        # Check if red flags were properly detected
        expected_red_flags = set(scenario.get("red_flags", []))
        detected_red_flags_set = set(detected_red_flags)
        
        red_flags_detected = len(expected_red_flags & detected_red_flags_set) > 0 if expected_red_flags else True
        
        return {
            "scenario_id": scenario_id,
            "category": scenario["category"],
            "success": True,
            "urgency_correct": urgency_correct,
            "expected_urgency": expected_urgency,
            "actual_urgency": actual_urgency,
            "expected_care": scenario["expected_care"],
            "actual_care": actual_care,
            "red_flags_detected": red_flags_detected,
            "expected_red_flags": list(expected_red_flags),
            "detected_red_flags": detected_red_flags,
            "report_length": len(result.get("formatted_report", "")),
            "time_sensitive": result.get("time_sensitive", False)
        }
        
    except Exception as e:
        logger.error(f"Error testing scenario {scenario_id}: {e}")
        return {
            "scenario_id": scenario_id,
            "success": False,
            "error": str(e)
        }


def run_evaluation():
    """Run evaluation on all test scenarios."""
    print("=" * 70)
    print("MedGemma AI Triage System - Scenario Evaluation")
    print("=" * 70)
    print()
    
    # Load scenarios
    scenarios = load_test_scenarios()
    print(f"Loaded {len(scenarios)} test scenarios")
    print()
    
    # Initialize workflow
    print("Initializing triage workflow...")
    try:
        workflow = TriageWorkflow()
        print("✓ Workflow initialized")
    except Exception as e:
        print(f"✗ Failed to initialize workflow: {e}")
        return
    
    print()
    print("=" * 70)
    print()
    
    # Run evaluation
    results = []
    for i, scenario in enumerate(scenarios, 1):
        print(f"[{i}/{len(scenarios)}] Testing: {scenario['description']}")
        result = evaluate_scenario(workflow, scenario)
        results.append(result)
        
        if result["success"]:
            status = "✓" if result["urgency_correct"] else "✗"
            print(f"  {status} Expected: {result['expected_urgency']}, Got: {result['actual_urgency']}")
        else:
            print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
        print()
    
    # Calculate metrics
    print("=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70)
    print()
    
    successful_tests = [r for r in results if r["success"]]
    total_tests = len(results)
    successful_count = len(successful_tests)
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful Runs: {successful_count} ({successful_count/total_tests*100:.1f}%)")
    print()
    
    if successful_tests:
        correct_urgency = sum(1 for r in successful_tests if r["urgency_correct"])
        print(f"Urgency Classification Accuracy: {correct_urgency}/{successful_count} ({correct_urgency/successful_count*100:.1f}%)")
        
        # Breakdown by category
        categories = {}
        for result in successful_tests:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "correct": 0}
            categories[cat]["total"] += 1
            if result["urgency_correct"]:
                categories[cat]["correct"] += 1
        
        print()
        print("Accuracy by Category:")
        for cat, stats in categories.items():
            accuracy = stats["correct"] / stats["total"] * 100
            print(f"  {cat}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
        
        # Red flag detection
        red_flag_tests = [r for r in successful_tests if r.get("expected_red_flags")]
        if red_flag_tests:
            red_flags_correct = sum(1 for r in red_flag_tests if r["red_flags_detected"])
            print()
            print(f"Red Flag Detection: {red_flags_correct}/{len(red_flag_tests)} ({red_flags_correct/len(red_flag_tests)*100:.1f}%)")
    
    print()
    print("=" * 70)
    
    # Save results
    results_file = Path(__file__).parent.parent / "data" / "evaluation_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "successful_runs": successful_count,
                "accuracy": correct_urgency / successful_count if successful_tests else 0
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    run_evaluation()
