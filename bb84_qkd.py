#!/usr/bin/env python3
"""
BB84 Quantum Key Distribution Protocol
Complete implementation with eavesdropping detection
"""

import numpy as np
import hashlib
from typing import List, Tuple, Dict
from dataclasses import dataclass
import time

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Qiskit not available. Using simulation mode.")


@dataclass
class BB84Result:
    """Results from BB84 protocol execution"""
    raw_key: List[int]
    sifted_key: List[int]
    final_key: List[int]
    qber: float
    bases_match_count: int
    key_length: int
    execution_time: float
    eavesdropping_detected: bool
    protocol: str = "BB84"


class BB84Protocol:
    """
    BB84 Protocol Implementation
    
    Alice sends qubits to Bob in random bases.
    Bob measures in random bases.
    They compare bases publicly and keep matching bits.
    QBER (Quantum Bit Error Rate) reveals eavesdropping.
    """
    
    def __init__(self, n_qubits: int = 512, noise_rate: float = 0.0):
        """
        Initialize BB84
        
        Args:
            n_qubits: Number of qubits to generate
            noise_rate: Simulated channel noise (0.0 to 1.0)
        """
        self.n_qubits = n_qubits
        self.noise_rate = noise_rate
        self.simulator = None
        
        if QISKIT_AVAILABLE:
            self.simulator = AerSimulator()
    
    def _create_circuit(self, bit: int, basis: int) -> QuantumCircuit:
        """Create quantum circuit for single qubit"""
        qc = QuantumCircuit(1, 1)
        
        # Encode bit
        if bit == 1:
            qc.x(0)
        
        # Apply basis transformation
        if basis == 1:  # X basis (Hadamard)
            qc.h(0)
            
        return qc
    
    def _simulate_eve(self, qc: QuantumCircuit, bit: int, basis: int) -> QuantumCircuit:
        """Simulate Eve's interception attempt"""
        # Eve chooses random basis
        eve_basis = np.random.randint(0, 2)
        
        # Eve measures
        if eve_basis == 1:
            qc.h(0)
        qc.measure(0, 0)
        
        # Eve resends (simplified: introduce error with 50% probability)
        qc.reset(0)
        if np.random.random() < 0.5:
            # Eve guessed wrong, introduce error
            bit = 1 - bit
        
        # Re-prepare state
        if bit == 1:
            qc.x(0)
        if basis == 1:
            qc.h(0)
            
        return qc
    
    def execute(self, eve_present: bool = False) -> BB84Result:
        """
        Execute full BB84 protocol
        
        Args:
            eve_present: Simulate eavesdropper
            
        Returns:
            BB84Result with all protocol data
        """
        start_time = time.time()
        
        # Step 1: Alice generates random bits and bases
        alice_bits = np.random.randint(0, 2, self.n_qubits)
        alice_bases = np.random.randint(0, 2, self.n_qubits)
        # 0 = Z basis (computational), 1 = X basis (Hadamard)
        
        # Step 2: Bob generates random measurement bases
        bob_bases = np.random.randint(0, 2, self.n_qubits)
        
        # Step 3: Quantum transmission
        bob_results = []
        
        if QISKIT_AVAILABLE and self.simulator:
            # Real quantum simulation
            for i in range(self.n_qubits):
                qc = self._create_circuit(alice_bits[i], alice_bases[i])
                
                # Simulate Eve
                if eve_present:
                    qc = self._simulate_eve(qc, alice_bits[i], alice_bases[i])
                
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
            # Classical simulation (for testing without qiskit)
            bob_results = self._classical_simulation(
                alice_bits, alice_bases, bob_bases, eve_present
            )
        
        bob_results = np.array(bob_results)
        
        # Step 4: Sifting - keep only where bases match
        bases_match = alice_bases == bob_bases
        sifted_key = alice_bits[bases_match]
        bob_sifted = bob_results[bases_match]
        
        # Step 5: Error estimation (QBER calculation)
        # Check 25% of bits publicly
        check_fraction = 0.25
        check_size = int(len(sifted_key) * check_fraction)
        
        if check_size > 0:
            check_indices = np.random.choice(
                len(sifted_key), 
                size=check_size, 
                replace=False
            )
            
            errors = np.sum(sifted_key[check_indices] != bob_sifted[check_indices])
            qber = errors / check_size
            
            # Remove check bits from final key
            mask = np.ones(len(sifted_key), dtype=bool)
            mask[check_indices] = False
            final_key = sifted_key[mask]
        else:
            qber = 0.0
            final_key = sifted_key
        
        # Step 6: Privacy amplification (hash to reduce info leakage)
        final_key_bytes = self._bits_to_bytes(final_key.tolist())
        
        # Use SHA-256 for privacy amplification
        hasher = hashlib.sha256(final_key_bytes)
        amplified_key = list(
            int(b) for b in bin(int(hasher.hexdigest(), 16))[2:].zfill(256)
        )[:len(final_key)]
        
        execution_time = time.time() - start_time
        
        # Eavesdropping detection (threshold: 11%)
        eavesdropping_detected = qber > 0.11
        
        return BB84Result(
            raw_key=alice_bits.tolist(),
            sifted_key=sifted_key.tolist(),
            final_key=amplified_key[:len(final_key)],
            qber=qber,
            bases_match_count=int(np.sum(bases_match)),
            key_length=len(final_key),
            execution_time=execution_time,
            eavesdropping_detected=eavesdropping_detected
        )
    
    def _classical_simulation(self, alice_bits, alice_bases, bob_bases, eve_present):
        """Classical simulation of quantum channel"""
        results = []
        
        for i in range(len(alice_bits)):
            bit = alice_bits[i]
            
            if eve_present:
                # Eve intercepts with 50% probability
                if np.random.random() < 0.5:
                    eve_basis = np.random.randint(0, 2)
                    # If Eve guesses wrong, 50% chance of error
                    if eve_basis != alice_bases[i] and np.random.random() < 0.5:
                        bit = 1 - bit
            
            # Bob's measurement
            if bob_bases[i] == alice_bases[i]:
                # Same basis: correct result
                results.append(bit)
            else:
                # Different basis: random result
                results.append(np.random.randint(0, 2))
        
        return results
    
    def _bits_to_bytes(self, bits: List[int]) -> bytes:
        """Convert bit list to bytes"""
        # Pad to multiple of 8
        while len(bits) % 8 != 0:
            bits.append(0)
        
        byte_array = []
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            byte_array.append(byte)
        
        return bytes(byte_array)
    
    def get_aes_key(self, result: BB84Result, key_size: int = 256) -> bytes:
        """Convert final key to AES-ready key"""
        key_bytes = self._bits_to_bytes(result.final_key)
        
        if key_size == 256:
            hasher = hashlib.sha256(key_bytes)
        elif key_size == 128:
            hasher = hashlib.sha256(key_bytes)
            return hasher.digest()[:16]
        else:
            hasher = hashlib.sha256(key_bytes)
        
        return hasher.digest()


# Quick usage function
def run_bb84(n_qubits: int = 512, eve_present: bool = False) -> BB84Result:
    """Quick BB84 execution"""
    protocol = BB84Protocol(n_qubits=n_qubits)
    return protocol.execute(eve_present=eve_present)


if __name__ == "__main__":
    print("=" * 60)
    print("BB84 QKD Protocol Demo")
    print("=" * 60)
    
    # Test without eavesdropping
    print("\n--- Without Eavesdropping ---")
    result = run_bb84(n_qubits=256, eve_present=False)
    print(f"Raw key length: {len(result.raw_key)} bits")
    print(f"Sifted key length: {len(result.sifted_key)} bits")
    print(f"Final key length: {result.key_length} bits")
    print(f"QBER: {result.qber:.4f} ({result.qber*100:.2f}%)")
    print(f"Eavesdropping detected: {result.eavesdropping_detected}")
    print(f"Execution time: {result.execution_time:.3f}s")
    
    # Test with eavesdropping
    print("\n--- With Eavesdropping (Eve present) ---")
    result_eve = run_bb84(n_qubits=256, eve_present=True)
    print(f"QBER: {result_eve.qber:.4f} ({result_eve.qber*100:.2f}%)")
    print(f"Eavesdropping detected: {result_eve.eavesdropping_detected}")
    
    # Generate AES key
    aes_key = BB84Protocol().get_aes_key(result, key_size=256)
    print(f"\nAES-256 Key (hex): {aes_key.hex()[:32]}...")