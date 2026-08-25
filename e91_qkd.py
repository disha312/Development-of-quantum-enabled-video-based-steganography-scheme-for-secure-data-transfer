#!/usr/bin/env python3
"""
E91 Quantum Key Distribution Protocol
Entanglement-based QKD using Bell inequality violation
"""

import numpy as np
import hashlib
from typing import List, Tuple, Dict
from dataclasses import dataclass
import time

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Qiskit not available. Using simulation mode.")


@dataclass
class E91Result:
    """Results from E91 protocol execution"""
    alice_key: List[int]
    bob_key: List[int]
    matching_bits: int
    chsh_value: float
    key_length: int
    execution_time: float
    secure: bool
    protocol: str = "E91"


class E91Protocol:
    """
    E91 Protocol Implementation (Ekert 1991)
    
    Uses entangled Bell pairs distributed to Alice and Bob.
    Security proven via violation of Bell's inequality (CHSH).
    """
    
    def __init__(self, n_pairs: int = 256):
        """
        Initialize E91
        
        Args:
            n_pairs: Number of entangled pairs to generate
        """
        self.n_pairs = n_pairs
        self.simulator = None
        
        if QISKIT_AVAILABLE:
            self.simulator = AerSimulator()
    
    def _create_bell_pair(self) -> QuantumCircuit:
        """Create Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2"""
        qc = QuantumCircuit(2, 2)
        qc.h(0)        # Hadamard on first qubit
        qc.cx(0, 1)    # CNOT to entangle
        return qc
    
    def _measure_in_basis(self, qc: QuantumCircuit, 
                         alice_basis: int, bob_basis: int) -> Tuple[int, int]:
        """Measure both qubits in specified bases"""
        
        # Alice's measurement basis
        # 0 = Z (0°), 1 = X (45°), 2 = rotated (-22.5°)
        if alice_basis == 1:
            qc.ry(-np.pi/2, 0)  # Rotate to X basis
        elif alice_basis == 2:
            qc.ry(-np.pi/4, 0)  # Rotate to -22.5°
        
        # Bob's measurement basis
        # 0 = Z (0°), 1 = rotated (22.5°), 2 = X (45°)
        if bob_basis == 1:
            qc.ry(np.pi/4, 1)   # Rotate to 22.5°
        elif bob_basis == 2:
            qc.ry(-np.pi/2, 1)  # Rotate to X basis
        
        qc.measure([0, 1], [0, 1])
        
        # Execute
        if self.simulator:
            job = self.simulator.run(qc, shots=1)
            result = job.result()
            counts = result.get_counts()
            bits = list(counts.keys())[0]
            return int(bits[1]), int(bits[0])  # Alice, Bob
        else:
            # Classical simulation
            return self._classical_bell_measurement(alice_basis, bob_basis)
    
    def _classical_bell_measurement(self, a_basis: int, b_basis: int) -> Tuple[int, int]:
        """Classical simulation of Bell pair measurement"""
        # In Bell state |Φ+⟩, measurements are perfectly correlated in Z basis
        # In other bases, correlations follow quantum mechanics
        
        # Generate correlated random bits
        alice_bit = np.random.randint(0, 2)
        
        # Correlation depends on basis angle difference
        angle_diff = 0
        if a_basis == 0 and b_basis == 0:
            angle_diff = 0           # Both Z
        elif a_basis == 2 and b_basis == 2:
            angle_diff = 0           # Both X
        elif (a_basis == 0 and b_basis == 2) or (a_basis == 2 and b_basis == 0):
            angle_diff = np.pi/4      # Z vs X
        elif a_basis == 2 and b_basis == 1:
            angle_diff = np.pi/8     # X vs 22.5°
        elif a_basis == 1 and b_basis == 2:
            angle_diff = np.pi/8     # 45° vs X
        elif a_basis == 1 and b_basis == 1:
            angle_diff = np.pi/4     # 45° vs 22.5°
        
        # Quantum correlation: cos²(θ) for same, sin²(θ) for different
        same_prob = np.cos(angle_diff) ** 2
        
        if np.random.random() < same_prob:
            bob_bit = alice_bit
        else:
            bob_bit = 1 - alice_bit
        
        return alice_bit, bob_bit
    
    def execute(self) -> E91Result:
        """
        Execute full E91 protocol
        
        Returns:
            E91Result with all protocol data
        """
        start_time = time.time()
        
        # Measurement bases for CHSH inequality
        # Alice: a=0° (Z), a'=45° (X)
        # Bob: b=22.5°, b'=-22.5°
        
        alice_bases = np.random.choice([0, 1, 2], self.n_pairs)  # 0=Z, 1=45°, 2=-22.5°
        bob_bases = np.random.choice([0, 1, 2], self.n_pairs)    # 0=Z, 1=22.5°, 2=X
        
        alice_results = []
        bob_results = []
        
        # Generate and measure entangled pairs
        for i in range(self.n_pairs):
            if self.simulator:
                qc = self._create_bell_pair()
                a_bit, b_bit = self._measure_in_basis(
                    qc, alice_bases[i], bob_bases[i]
                )
            else:
                a_bit, b_bit = self._classical_bell_measurement(
                    alice_bases[i], bob_bases[i]
                )
            
            alice_results.append(a_bit)
            bob_results.append(b_bit)
        
        alice_results = np.array(alice_results)
        bob_results = np.array(bob_results)
        
        # Calculate CHSH inequality
        chsh_value = self._calculate_chsh(
            alice_results, bob_results, 
            alice_bases, bob_bases
        )
        
        # Key generation: use specific basis combinations
        # Alice's Z (0) and Bob's X (2) for key
        key_mask = (alice_bases == 0) & (bob_bases == 2)
        
        alice_key = alice_results[key_mask]
        bob_key = bob_results[key_mask]
        
        # Verify keys match (they should due to entanglement)
        matching = np.sum(alice_key == bob_key)
        
        execution_time = time.time() - start_time
        
        # Security check: CHSH > 2 indicates entanglement (quantum correlation)
        # Maximum violation is 2√2 ≈ 2.828
        secure = abs(chsh_value) > 2.0
        
        return E91Result(
            alice_key=alice_key.tolist(),
            bob_key=bob_key.tolist(),
            matching_bits=int(matching),
            chsh_value=chsh_value,
            key_length=len(alice_key),
            execution_time=execution_time,
            secure=secure
        )
    
    def _calculate_chsh(self, a_results, b_results, a_bases, b_bases) -> float:
        """
        Calculate CHSH inequality value
        S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
        
        where E is correlation function
        """
        # Define basis combinations for CHSH
        # a=0 (Z), a'=1 (45°)
        # b=1 (22.5°), b'=2 (X)
        
        def correlation(a_res, b_res, a_bas, b_bas, a_val, b_val):
            """Calculate correlation for specific basis combination"""
            mask = (a_bas == a_val) & (b_bas == b_val)
            if np.sum(mask) == 0:
                return 0
            
            a_sub = a_res[mask]
            b_sub = b_res[mask]
            
            # Correlation: +1 if same, -1 if different
            same = np.sum(a_sub == b_sub)
            diff = np.sum(a_sub != b_sub)
            total = len(a_sub)
            
            return (same - diff) / total if total > 0 else 0
        
        # E(a,b) where a=Z(0), b=22.5°(1)
        E_ab = correlation(a_results, b_results, a_bases, b_bases, 0, 1)
        
        # E(a,b') where a=Z(0), b'=X(2)
        E_abp = correlation(a_results, b_results, a_bases, b_bases, 0, 2)
        
        # E(a',b) where a'=45°(1), b=22.5°(1)
        E_apb = correlation(a_results, b_results, a_bases, b_bases, 1, 1)
        
        # E(a',b') where a'=45°(1), b'=X(2)
        E_apbp = correlation(a_results, b_results, a_bases, b_bases, 1, 2)
        
        # CHSH value
        S = E_ab - E_abp + E_apb + E_apbp
        
        return S
    
    def get_aes_key(self, result: E91Result, key_size: int = 256) -> bytes:
        """Convert E91 key to AES-ready key"""
        key_bytes = self._bits_to_bytes(result.alice_key)
        
        if key_size == 256:
            hasher = hashlib.sha256(key_bytes)
        elif key_size == 128:
            hasher = hashlib.sha256(key_bytes)
            return hasher.digest()[:16]
        else:
            hasher = hashlib.sha256(key_bytes)
        
        return hasher.digest()
    
    def _bits_to_bytes(self, bits: List[int]) -> bytes:
        """Convert bit list to bytes"""
        while len(bits) % 8 != 0:
            bits.append(0)
        
        byte_array = []
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            byte_array.append(byte)
        
        return bytes(byte_array)


# Quick usage function
def run_e91(n_pairs: int = 256) -> E91Result:
    """Quick E91 execution"""
    protocol = E91Protocol(n_pairs=n_pairs)
    return protocol.execute()


if __name__ == "__main__":
    print("=" * 60)
    print("E91 QKD Protocol Demo")
    print("=" * 60)
    
    result = run_e91(n_pairs=256)
    
    print(f"\nKey length: {result.key_length} bits")
    print(f"Matching bits: {result.matching_bits}")
    print(f"CHSH value: {result.chsh_value:.4f}")
    print(f"Secure (|S| > 2): {result.secure}")
    print(f"Execution time: {result.execution_time:.3f}s")
    
    # Generate AES key
    aes_key = E91Protocol().get_aes_key(result, key_size=256)
    print(f"\nAES-256 Key (hex): {aes_key.hex()[:32]}...")