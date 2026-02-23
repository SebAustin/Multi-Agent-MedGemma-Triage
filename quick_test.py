"""
Quick test with 2-3 scenarios to verify the improved accuracy system works.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.workflows.triage_workflow import TriageWorkflow

# Test scenarios
test_cases = [
    {
        "id": "emergency_001",
        "input": "I'm having severe chest pain that started 30 minutes ago. It feels like pressure and it's radiating to my left arm. I'm also sweating and feeling nauseous.",
        "expected": "EMERGENCY"
    },
    {
        "id": "urgent_001",
        "input": "I have a high fever of 103°F that's been going on for 2 days. I also have severe body aches, chills, and a bad headache. I can't keep any food down.",
        "expected": "URGENT"
    },
    {
        "id": "non_urgent_001",
        "input": "I have a mild cold with a runny nose and slight cough that started yesterday. No fever, just feeling a bit under the weather.",
        "expected": "NON-URGENT"
    }
]

def main():
    print("="*80)
    print("QUICK TEST - Improved Accuracy System")
    print("="*80)
    print()
    
    print("Initializing workflow...")
    workflow = TriageWorkflow()
    print("✓ Workflow ready!\n")
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] Testing: {test['id']}")
        print(f"Expected: {test['expected']}")
        
        try:
            result = workflow.run_triage(test['input'])
            actual = result.get('urgency_level', 'UNKNOWN')
            correct = (actual == test['expected'])
            
            # Check red flags
            red_flags = result.get('red_flags', [])
            critical_count = sum(1 for rf in red_flags 
                               if isinstance(rf, dict) and rf.get('type') == 'critical')
            warning_count = sum(1 for rf in red_flags 
                              if isinstance(rf, dict) and rf.get('type') == 'warning')
            
            print(f"Actual: {actual} {'✓' if correct else '✗'}")
            if red_flags:
                print(f"Red flags: {len(red_flags)} (Critical: {critical_count}, Warning: {warning_count})")
                if i == 1:  # Emergency case - show details
                    for rf in red_flags[:3]:  # Show first 3
                        if isinstance(rf, dict):
                            print(f"  - {rf.get('flag')}: {rf.get('severity')} ({rf.get('type')})")
            print()
            
            results.append({
                'id': test['id'],
                'expected': test['expected'],
                'actual': actual,
                'correct': correct,
                'red_flags': len(red_flags),
                'critical': critical_count,
                'warning': warning_count
            })
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            print()
            results.append({
                'id': test['id'],
                'expected': test['expected'],
                'actual': 'ERROR',
                'correct': False,
                'red_flags': 0,
                'critical': 0,
                'warning': 0
            })
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    correct_count = sum(1 for r in results if r['correct'])
    accuracy = (correct_count / len(results)) * 100
    print(f"Accuracy: {correct_count}/{len(results)} = {accuracy:.1f}%")
    print()
    
    for r in results:
        status = "✓" if r['correct'] else "✗"
        print(f"{status} {r['id']}: {r['expected']} -> {r['actual']}")
        if r['red_flags'] > 0:
            print(f"   Flags: {r['critical']} critical, {r['warning']} warning")
    print()
    
    if accuracy >= 66.7:
        print("🎉 LOOKING GOOD! System is working correctly.")
        print("   Ready to run full evaluation.")
    else:
        print("⚠️  Still needs work. Check the output above for issues.")
    
    return results

if __name__ == "__main__":
    main()
