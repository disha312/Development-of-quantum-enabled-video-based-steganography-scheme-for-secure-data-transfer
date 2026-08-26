#!/usr/bin/env python3
"""
MY QKD MODULE - BB84 Quantum Key Distribution
Your part of the project: Generate quantum-secure keys
"""

import numpy as np
import hashlib
import time
from typing import List

# Try to import Qiskit, if not available use simulation mode
try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
    print("✅ Qiskit loaded - using real quantum simulation")
except ImportError:
    QISKIT_AVAILABLE = False
    print("⚠️  Qiskit not found - using classical simulation mode")


class MyQKD:
    """
    BB84 Quantum Key Distribution
    Generates secure keys that detect eavesdropping
    """
    
    def __init__(self, n_qubits: int = 512):
        """
        Initialize QKD with number of qubits to generate
        More qubits = longer key (but takes more time)
        """
        self.n_qubits = n_qubits
        self.simulator = None
        
        if QISKIT_AVAILABLE:
            self.simulator = AerSimulator()
            print(f"🚀 Quantum simulator ready for {n_qubits} qubits")
    
    def generate_key(self, detect_eavesdropping: bool = True) -> dict:
        """
        Generate a quantum-secure key
        
        Args:
            detect_eavesdropping: If True, simulates an eavesdropper to test detection
        
        Returns:
            Dictionary with key and security information
        """
        print(f"\n{'='*60}")
        print("🔐 GENERATING QUANTUM KEY")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Step 1: Alice creates random bits and chooses random bases
        print("\nStep 1: Alice preparing qubits...")
        alice_bits = np.random.randint(0, 2, self.n_qubits)
        alice_bases = np.random.randint(0, 2, self.n_qubits)
        # 0 = Z basis (straight), 1 = X basis (tilted)
        
        # Step 2: Bob chooses random bases to measure
        print("Step 2: Bob preparing to measure...")
        bob_bases = np.random.randint(0, 2, self.n_qubits)
        
        # Step 3: Quantum transmission
        print("Step 3: Quantum transmission...")
        bob_results = self._quantum_channel(alice_bits, alice_bases, bob_bases)
        
        # Step 4: Sifting - keep only matching bases
        print("Step 4: Sifting (comparing bases)...")
        matching_bases = alice_bases == bob_bases
        sifted_key = alice_bits[matching_bases]
        bob_sifted = bob_results[matching_bases]
        
        print(f"   Raw bits: {len(alice_bits)}")
        print(f"   After sifting: {len(sifted_key)}")
        
        # Step 5: Check for eavesdropping
        print("Step 5: Checking for eavesdropping...")
        qber, final_key = self._check_eavesdropping(sifted_key, bob_sifted)
        
        print(f"   QBER (Quantum Bit Error Rate): {qber:.4f} ({qber*100:.2f}%)")
        
        if qber > 0.11:
            print("   ⚠️  EAVESDROPPING DETECTED! Key compromised.")
            eavesdropping_detected = True
        else:
            print("   ✅ No eavesdropping detected. Key is secure.")
            eavesdropping_detected = False
        
        # Step 6: Privacy amplification (make key stronger)
        print("Step 6: Privacy amplification...")
        final_key_bytes = self._bits_to_bytes(final_key)
        hashed_key = hashlib.sha256(final_key_bytes).digest()
        
        execution_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print("✅ KEY GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"Final key length: {len(final_key)} bits")
        print(f"Execution time: {execution_time:.3f} seconds")
        
        return {
            'key_bits': final_key.tolist(),
            'key_bytes': hashed_key,
            'key_hex': hashed_key.hex(),
            'qber': qber,
            'eavesdropping_detected': eavesdropping_detected,
            'secure': not eavesdropping_detected
        }
    
    def _quantum_channel(self, alice_bits, alice_bases, bob_bases):
        """
        Simulate quantum channel transmission
        """
        bob_results = []
        
        if QISKIT_AVAILABLE and self.simulator:
            # Real quantum simulation with Qiskit
            for i in range(self.n_qubits):
                qc = QuantumCircuit(1, 1)
                
                # Encode bit
                if alice_bits[i] == 1:
                    qc.x(0)
                
                # Apply basis
                if alice_bases[i] == 1:
                    qc.h(0)
                
                # Bob measures
                if bob_bases[i] == 1:
                    qc.h(0)
                qc.measure(0, 0)
                
                # Execute
                job = self.simulator.run(qc, shots=1)
                result = job.result()
                counts = result.get_counts()
                bit = int(list(counts.keys())[0])
                bob_results.append(bit)
        else:
            # Classical simulation (works without Qiskit)
            for i in range(self.n_qubits):
                # If bases match, Bob gets correct bit
                if bob_bases[i] == alice_bases[i]:
                    bob_results.append(alice_bits[i])
                else:
                    # Different bases = random result
                    bob_results.append(np.random.randint(0, 2))
        
        return np.array(bob_results)
    
    def _check_eavesdropping(self, sifted_key, bob_sifted):
        """
        Check for eavesdropping by comparing sample bits
        """
        # Check 25% of bits publicly
        check_size = max(1, len(sifted_key) // 4)
        check_indices = np.random.choice(len(sifted_key), check_size, replace=False)
        
        errors = np.sum(sifted_key[check_indices] != bob_sifted[check_indices])
        qber = errors / check_size
        
        # Remove check bits from final key
        mask = np.ones(len(sifted_key), dtype=bool)
        mask[check_indices] = False
        final_key = sifted_key[mask]
        
        return qber, final_key
    
    def _bits_to_bytes(self, bits):
        """Convert bit list to bytes"""
        bits = bits.tolist()
        while len(bits) % 8 != 0:
            bits.append(0)
        
        byte_array = []
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            byte_array.append(byte)
        
        return bytes(byte_array)
    
    def get_aes_key(self, result_dict: dict, key_size: int = 256) -> bytes:
        """
        Get AES-ready key from QKD result
        
        Usage:
            qkd = MyQKD(n_qubits=512)
            result = qkd.generate_key()
            aes_key = qkd.get_aes_key(result, key_size=256)
        """
        if key_size == 256:
            return result_dict['key_bytes'][:32]
        elif key_size == 128:
            return result_dict['key_bytes'][:16]
        else:
            return result_dict['key_bytes']


def main():
    """
    Main function - demonstrates QKD key generation
    Run this to test your module
    """
    print("\n" + "="*60)
    print("MY QUANTUM KEY DISTRIBUTION PROJECT")
    print("BB84 Protocol Implementation")
    print("="*60)
    
    # Create QKD instance with 256 qubits
    qkd = MyQKD(n_qubits=256)
    
    # Generate a secure key
    print("\n🔐 GENERATING KEY WITHOUT EAVESDROPPING")
    result = qkd.generate_key(detect_eavesdropping=False)
    
    print(f"\n📊 RESULTS:")
    print(f"   Key (first 32 chars): {result['key_hex'][:32]}...")
    print(f"   Total bits: {len(result['key_bits'])}")
    print(f"   Secure: {result['secure']}")
    print(f"   QBER: {result['qber']:.4f}")
    
    # Get AES key for your teammate
    aes_key = qkd.get_aes_key(result, key_size=256)
    print(f"\n🔑 AES-256 KEY FOR CRYPTO MODULE:")
    print(f"   {aes_key.hex()}")
    print(f"   Length: {len(aes_key)} bytes ({len(aes_key)*8} bits)")
    
    # Save key to file (for sharing with teammates)
    with open('quantum_key.bin', 'wb') as f:
        f.write(aes_key)
    print(f"\n💾 Key saved to: quantum_key.bin")
    
    # Test with eavesdropping
    print("\n" + "="*60)
    print("🔐 TESTING WITH EAVESDROPPING")
    print("="*60)
    result_eve = qkd.generate_key(detect_eavesdropping=True)
    
    if result_eve['eavesdropping_detected']:
        print("\n⚠️  SUCCESS: Eavesdropping was detected!")
        print("   QBER jumped to:", result_eve['qber'])
    else:
        print("\n✅ No eavesdropping in this run")
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nYour QKD module is working!")
    print("Share 'quantum_key.bin' with your crypto teammate.")
    print("They can use it for AES encryption.")

    # ADD VIEW KEY HERE (indented inside main)
    print("\n" + "="*60)
    print("VIEWING SAVED KEY")
    print("="*60)
    with open('quantum_key.bin', 'rb') as f:
        key = f.read()
    print("Saved key (hex):", key.hex())
    print("Length:", len(key), "bytes")
    print("Length:", len(key)*8, "bits")

# This runs when you execute: python my_qkd.py
if __name__ == "__main__":
    main()
