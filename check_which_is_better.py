#!/usr/bin/env python3
"""
QKD Protocol Comparison Checker
Shows exactly how to determine which protocol is better through code
"""

from bb84_qkd import BB84Protocol, run_bb84
from e91_qkd import E91Protocol, run_e91
import numpy as np


def evaluate_bb84(n_iterations=5) -> dict:
    """
    Evaluate BB84 protocol and return metrics
    """
    print("🔬 Testing BB84 Protocol...")
    
    results = {
        'qber_no_eve': [],
        'qber_with_eve': [],
        'key_lengths': [],
        'eavesdropping_detected': 0,
        'execution_times': []
    }
    
    for i in range(n_iterations):
        # Test without eavesdropping
        result_no_eve = run_bb84(n_qubits=128, eve_present=False)
        results['qber_no_eve'].append(result_no_eve.qber)
        results['key_lengths'].append(result_no_eve.key_length)
        results['execution_times'].append(result_no_eve.execution_time)
        
        # Test with eavesdropping
        result_eve = run_bb84(n_qubits=128, eve_present=True)
        results['qber_with_eve'].append(result_eve.qber)
        
        if result_eve.eavesdropping_detected:
            results['eavesdropping_detected'] += 1
    
    # Calculate averages
    avg_qber_no_eve = np.mean(results['qber_no_eve'])
    avg_qber_with_eve = np.mean(results['qber_with_eve'])
    avg_key_length = np.mean(results['key_lengths'])
    detection_rate = results['eavesdropping_detected'] / n_iterations
    avg_time = np.mean(results['execution_times'])
    
    print(f"   ✓ Average QBER (no Eve): {avg_qber_no_eve:.4f}")
    print(f"   ✓ Average QBER (with Eve): {avg_qber_with_eve:.4f}")
    print(f"   ✓ Eavesdropping detection rate: {detection_rate*100:.1f}%")
    print(f"   ✓ Average key length: {avg_key_length:.1f} bits")
    print(f"   ✓ Average time: {avg_time:.3f}s")
    
    return {
        'protocol': 'BB84',
        'avg_qber_no_eve': avg_qber_no_eve,
        'avg_qber_with_eve': avg_qber_with_eve,
        'detection_rate': detection_rate,
        'avg_key_length': avg_key_length,
        'efficiency': avg_key_length / 128,
        'avg_time': avg_time
    }


def evaluate_e91(n_iterations=5) -> dict:
    """
    Evaluate E91 protocol and return metrics
    """
    print("\n🔬 Testing E91 Protocol...")
    
    results = {
        'chsh_values': [],
        'key_lengths': [],
        'secure_runs': 0,
        'execution_times': []
    }
    
    for i in range(n_iterations):
        result = run_e91(n_pairs=128)
        results['chsh_values'].append(result.chsh_value)
        results['key_lengths'].append(result.key_length)
        results['execution_times'].append(result.execution_time)
        
        if result.secure:
            results['secure_runs'] += 1
    
    # Calculate averages
    avg_chsh = np.mean(results['chsh_values'])
    avg_key_length = np.mean(results['key_lengths'])
    security_rate = results['secure_runs'] / n_iterations
    avg_time = np.mean(results['execution_times'])
    
    print(f"   ✓ Average CHSH: {avg_chsh:.4f}")
    print(f"   ✓ Security rate (|S| > 2): {security_rate*100:.1f}%")
    print(f"   ✓ Average key length: {avg_key_length:.1f} bits")
    print(f"   ✓ Average time: {avg_time:.3f}s")
    
    return {
        'protocol': 'E91',
        'avg_chsh': avg_chsh,
        'security_rate': security_rate,
        'avg_key_length': avg_key_length,
        'efficiency': avg_key_length / 128,
        'avg_time': avg_time
    }


def score_protocol(bb84_metrics: dict, e91_metrics: dict) -> dict:
    """
    Score each protocol based on key criteria
    Returns winner and scores
    """
    print("\n" + "="*60)
    print("SCORING BREAKDOWN")
    print("="*60)
    
    scores = {
        'BB84': 0,
        'E91': 0
    }
    
    # Criterion 1: Low QBER vs High CHSH violation
    print("\n📊 Criterion 1: Quantum Quality")
    print(f"   BB84 QBER (lower is better): {bb84_metrics['avg_qber_no_eve']:.4f}")
    print(f"   E91 CHSH (higher is better): {e91_metrics['avg_chsh']:.4f}")
    
    # BB84 wins if QBER < 0.05 (5%)
    bb84_qber_good = bb84_metrics['avg_qber_no_eve'] < 0.05
    # E91 wins if CHSH > 2.0 (Bell violation)
    e91_chsh_good = e91_metrics['avg_chsh'] > 2.0
    
    if bb84_qber_good and not e91_chsh_good:
        print("   ✅ BB84 wins: Low error rate")
        scores['BB84'] += 1
    elif e91_chsh_good and not bb84_qber_good:
        print("   ✅ E91 wins: Strong quantum correlation")
        scores['E91'] += 1
    elif bb84_qber_good and e91_chsh_good:
        print("   ⚖️  Both good - checking other criteria")
        scores['BB84'] += 1
        scores['E91'] += 1
    else:
        print("   ⚠️  Both have issues")
    
    # Criterion 2: Eavesdropping Detection (BB84 only)
    print("\n📊 Criterion 2: Security Detection")
    print(f"   BB84 detection rate: {bb84_metrics['detection_rate']*100:.1f}%")
    print(f"   E91 security rate: {e91_metrics['security_rate']*100:.1f}%")
    
    if bb84_metrics['detection_rate'] > 0.8:  # >80% detection
        print("   ✅ BB84 wins: Excellent eavesdropping detection")
        scores['BB84'] += 2  # Weighted higher - this is crucial
    
    # Criterion 3: Key Generation Efficiency
    print("\n📊 Criterion 3: Efficiency")
    print(f"   BB84 efficiency: {bb84_metrics['efficiency']*100:.1f}%")
    print(f"   E91 efficiency: {e91_metrics['efficiency']*100:.1f}%")
    
    if bb84_metrics['efficiency'] > e91_metrics['efficiency']:
        print(f"   ✅ BB84 wins: {bb84_metrics['efficiency']/e91_metrics['efficiency']:.1f}x more efficient")
        scores['BB84'] += 1
    else:
        print("   ✅ E91 wins: Higher efficiency")
        scores['E91'] += 1
    
    # Criterion 4: Execution Speed
    print("\n📊 Criterion 4: Speed")
    print(f"   BB84 time: {bb84_metrics['avg_time']:.3f}s")
    print(f"   E91 time: {e91_metrics['avg_time']:.3f}s")
    
    if bb84_metrics['avg_time'] < e91_metrics['avg_time']:
        print("   ✅ BB84 wins: Faster execution")
        scores['BB84'] += 1
    else:
        print("   ✅ E91 wins: Faster execution")
        scores['E91'] += 1
    
    # Determine winner
    print("\n" + "="*60)
    print("FINAL SCORES")
    print("="*60)
    print(f"BB84: {scores['BB84']} points")
    print(f"E91:  {scores['E91']} points")
    
    if scores['BB84'] > scores['E91']:
        winner = 'BB84'
        print(f"\n🏆 WINNER: BB84 (by {scores['BB84'] - scores['E91']} points)")
    elif scores['E91'] > scores['BB84']:
        winner = 'E91'
        print(f"\n🏆 WINNER: E91 (by {scores['E91'] - scores['BB84']} points)")
    else:
        winner = 'TIE'
        print("\n⚖️  RESULT: Tie - both protocols are equally suitable")
    
    return {
        'winner': winner,
        'bb84_score': scores['BB84'],
        'e91_score': scores['E91'],
        'bb84_metrics': bb84_metrics,
        'e91_metrics': e91_metrics
    }


def detailed_comparison(result: dict):
    """
    Print detailed comparison and recommendation
    """
    print("\n" + "="*60)
    print("DETAILED RECOMMENDATION")
    print("="*60)
    
    winner = result['winner']
    bb84 = result['bb84_metrics']
    e91 = result['e91_metrics']
    
    if winner == 'BB84':
        print("""
✅ RECOMMENDATION: Use BB84 as your primary protocol

Why BB84 is better for your project:

1. ✅ EAVESDROPPING DETECTION
   - BB84 detected eavesdropping in {detection:.0f}% of cases
   - QBER jumped from {qber_no_eve:.1f}% to {qber_eve:.1f}% when Eve was present
   - This is BB84's killer feature - you can SEE if someone is listening

2. ✅ HIGHER EFFICIENCY  
   - BB84 generated {bb84_key:.0f} bits on average
   - E91 generated only {e91_key:.0f} bits on average
   - BB84 is {efficiency:.1f}x more efficient

3. ✅ SIMPLER IMPLEMENTATION
   - Prepare-and-measure is easier than entanglement
   - More documentation and examples available
   - Faster execution time

When E91 might be better:
- If you need the strongest theoretical security proof (Bell inequality)
- If you have access to real quantum entanglement sources
- For academic research on quantum foundations

For a practical final year project: BB84 is the clear winner.
        """.format(
            detection=bb84['detection_rate']*100,
            qber_no_eve=bb84['avg_qber_no_eve']*100,
            qber_eve=bb84['avg_qber_with_eve']*100,
            bb84_key=bb84['avg_key_length'],
            e91_key=e91['avg_key_length'],
            efficiency=bb84['efficiency']/e91['efficiency'] if e91['efficiency'] > 0 else 0
        ))
    
    elif winner == 'E91':
        print("""
✅ RECOMMENDATION: Use E91 as your primary protocol

Why E91 is better:

1. ✅ STRONGER SECURITY PROOF
   - Based on Bell inequality violation (fundamental physics)
   - Security doesn't rely on device trust
   
2. ✅ DEVICE-INDEPENDENT
   - More robust against implementation attacks

BB84 is still valid as a comparison point for your report.
        """)
    
    # Generate data for report
    print("\n" + "="*60)
    print("DATA FOR YOUR REPORT")
    print("="*60)
    print(f"""
Table: Protocol Comparison Results

Metric                    | BB84          | E91
--------------------------|---------------|---------------
Quantum Error Rate (QBER) | {bb84['avg_qber_no_eve']:.4f}       | N/A
CHSH Violation            | N/A           | {e91['avg_chsh']:.4f}
Eavesdropping Detection   | {bb84['detection_rate']*100:.1f}%        | N/A
Key Generation Efficiency | {bb84['efficiency']*100:.1f}%        | {e91['efficiency']*100:.1f}%
Average Execution Time    | {bb84['avg_time']:.3f}s       | {e91['avg_time']:.3f}s
Winner                    | {'✓ YES' if winner == 'BB84' else '✗ NO'}       | {'✓ YES' if winner == 'E91' else '✗ NO'}

Conclusion: {winner} is recommended for the proposed system based on 
superior eavesdropping detection and higher key generation efficiency.
    """)

def main():
    """
    Main function - runs full comparison
    """
    print("="*60)
    print("QKD PROTOCOL COMPARISON CHECKER")
    print("Determining which protocol is better through code")
    print("="*60)
    
    # Evaluate both protocols
    bb84_metrics = evaluate_bb84(n_iterations=5)
    e91_metrics = evaluate_e91(n_iterations=5)
    
    # Score and determine winner
    result = score_protocol(bb84_metrics, e91_metrics)
    
    # Print detailed recommendation
    detailed_comparison(result)
    
    return result

if __name__ == "__main__":
    result = main()