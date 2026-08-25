#!/usr/bin/env python3
"""
QKD Protocol Comparison Demo
Compares BB84 vs E91 across multiple metrics
"""

import time
import numpy as np
from typing import List, Dict
import sys

# Import both protocols
from bb84_qkd import BB84Protocol, run_bb84
from e91_qkd import E91Protocol, run_e91


class QKDComparison:
    """Compare BB84 and E91 protocols"""
    
    def __init__(self, n_iterations: int = 10):
        self.n_iterations = n_iterations
        self.results = {
            'bb84': [],
            'bb84_eve': [],
            'e91': []
        }
    
    def run_comparison(self, n_qubits: int = 256):
        """Run full comparison"""
        print("=" * 70)
        print("QUANTUM KEY DISTRIBUTION PROTOCOL COMPARISON")
        print("BB84 vs E91")
        print("=" * 70)
        
        print(f"\nRunning {self.n_iterations} iterations with {n_qubits} qubits/pairs...")
        print("-" * 70)
        
        for i in range(self.n_iterations):
            print(f"\nIteration {i+1}/{self.n_iterations}")
            
            # BB84 without Eve
            bb84_result = run_bb84(n_qubits=n_qubits, eve_present=False)
            self.results['bb84'].append(bb84_result)
            
            # BB84 with Eve
            bb84_eve = run_bb84(n_qubits=n_qubits, eve_present=True)
            self.results['bb84_eve'].append(bb84_eve)
            
            # E91
            e91_result = run_e91(n_pairs=n_qubits)
            self.results['e91'].append(e91_result)
            
            print(f"  BB84 QBER: {bb84_result.qber:.4f} | "
                  f"E91 CHSH: {e91_result.chsh_value:.3f}")
        
        self._print_statistics()
        self._print_recommendation()
    
    def _print_statistics(self):
        """Print comparison statistics"""
        print("\n" + "=" * 70)
        print("STATISTICAL COMPARISON")
        print("=" * 70)
        
        # BB84 Stats
        bb84_qbers = [r.qber for r in self.results['bb84']]
        bb84_times = [r.execution_time for r in self.results['bb84']]
        bb84_keylen = [r.key_length for r in self.results['bb84']]
        
        bb84_eve_qbers = [r.qber for r in self.results['bb84_eve']]
        bb84_eve_detected = sum(1 for r in self.results['bb84_eve'] if r.eavesdropping_detected)
        
        # E91 Stats
        e91_chsh = [r.chsh_value for r in self.results['e91']]
        e91_times = [r.execution_time for r in self.results['e91']]
        e91_keylen = [r.key_length for r in self.results['e91']]
        e91_secure = sum(1 for r in self.results['e91'] if r.secure)
        
        print("\n📊 BB84 Protocol (No Eavesdropping)")
        print(f"   Average QBER: {np.mean(bb84_qbers):.4f} (±{np.std(bb84_qbers):.4f})")
        print(f"   Average key length: {np.mean(bb84_keylen):.0f} bits")
        print(f"   Average time: {np.mean(bb84_times):.3f}s")
        print(f"   Efficiency: {np.mean(bb84_keylen)/256*100:.1f}%")
        
        print("\n📊 BB84 Protocol (With Eavesdropping)")
        print(f"   Average QBER: {np.mean(bb84_eve_qbers):.4f} (±{np.std(bb84_eve_qbers):.4f})")
        print(f"   Eavesdropping detected: {bb84_eve_detected}/{self.n_iterations} "
              f"({bb84_eve_detected/self.n_iterations*100:.0f}%)")
        print(f"   Detection threshold: 11%")
        
        print("\n📊 E91 Protocol")
        print(f"   Average CHSH: {np.mean(e91_chsh):.4f} (±{np.std(e91_chsh):.4f})")
        print(f"   Theoretical max: 2.828")
        print(f"   Average key length: {np.mean(e91_keylen):.0f} bits")
        print(f"   Average time: {np.mean(e91_times):.3f}s")
        print(f"   Secure runs: {e91_secure}/{self.n_iterations} "
              f"({e91_secure/self.n_iterations*100:.0f}%)")
        print(f"   Efficiency: {np.mean(e91_keylen)/256*100:.1f}%")
    
    def _print_recommendation(self):
        """Print recommendation"""
        print("\n" + "=" * 70)
        print("RECOMMENDATION")
        print("=" * 70)
        
        print("""
🏆 BEST CHOICE: BB84

Advantages:
✓ Simpler to implement and understand
✓ Faster execution (prepare-and-measure)
✓ Direct QBER metric for eavesdropping detection
✓ More mature, extensively tested in literature
✓ Higher key generation efficiency

When to use E91:
• When you need the strongest theoretical security proof
• When entanglement sources are readily available
• For demonstrating Bell inequality violation

For your project: BB84 is recommended as the primary protocol
with E91 as the comparative alternative.
        """)
    
    def generate_report_data(self) -> Dict:
        """Generate data for your project report"""
        return {
            'bb84_avg_qber': np.mean([r.qber for r in self.results['bb84']]),
            'bb84_eve_detection_rate': sum(1 for r in self.results['bb84_eve'] 
                                             if r.eavesdropping_detected) / self.n_iterations,
            'e91_avg_chsh': np.mean([r.chsh_value for r in self.results['e91']]),
            'e91_security_rate': sum(1 for r in self.results['e91'] 
                                     if r.secure) / self.n_iterations,
            'bb84_efficiency': np.mean([r.key_length for r in self.results['bb84']]) / 256,
            'e91_efficiency': np.mean([r.key_length for r in self.results['e91']]) / 256,
        }


def demo_single_run():
    """Demonstrate single run of both protocols"""
    print("=" * 70)
    print("SINGLE RUN DEMONSTRATION")
    print("=" * 70)
    
    print("\n🔐 BB84 Protocol (No Eavesdropping)")
    print("-" * 40)
    bb84 = run_bb84(n_qubits=64, eve_present=False)
    print(f"Raw bits: {len(bb84.raw_key)}")
    print(f"After sifting: {len(bb84.sifted_key)}")
    print(f"Final key: {bb84.key_length} bits")
    print(f"QBER: {bb84.qber:.4f}")
    print(f"Sample key: {''.join(str(b) for b in bb84.final_key[:16])}...")
    
    print("\n🔐 BB84 Protocol (With Eavesdropping)")
    print("-" * 40)
    bb84_eve = run_bb84(n_qubits=64, eve_present=True)
    print(f"QBER: {bb84_eve.qber:.4f}")
    print(f"Eavesdropping detected: {bb84_eve.eavesdropping_detected}")
    
    print("\n🔐 E91 Protocol (Entanglement-based)")
    print("-" * 40)
    e91 = run_e91(n_pairs=64)
    print(f"Key length: {e91.key_length} bits")
    print(f"CHSH value: {e91.chsh_value:.4f}")
    print(f"Secure (|S| > 2): {e91.secure}")
    print(f"Sample key: {''.join(str(b) for b in e91.alice_key[:16])}...")


if __name__ == "__main__":
    # First show single run demo
    demo_single_run()
    
    print("\n" + "=" * 70)
    input("\nPress Enter to run statistical comparison...")
    
    # Then run statistical comparison
    comparison = QKDComparison(n_iterations=10)
    comparison.run_comparison(n_qubits=256)
    
    # Generate report data
    print("\n" + "=" * 70)
    print("DATA FOR YOUR REPORT")
    print("=" * 70)
    report_data = comparison.generate_report_data()
    for key, value in report_data.items():
        print(f"{key}: {value:.4f}")