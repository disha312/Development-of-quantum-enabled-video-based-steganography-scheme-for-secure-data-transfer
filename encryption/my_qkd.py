#!/usr/bin/env python3

"""
MY QKD MODULE - BB84 Quantum Key Distribution
Your part of the project: Generate quantum-secure keys
"""

import numpy as np
import hashlib
import time

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    QISKIT_AVAILABLE = True
    print("Qiskit loaded - using quantum simulation")

except ImportError:
    QISKIT_AVAILABLE = False
    print("Qiskit not found - using classical simulation mode")


class MyQKD:

    def __init__(self, n_qubits=512):

        self.n_qubits = n_qubits
        self.simulator = None

        if QISKIT_AVAILABLE:
            self.simulator = AerSimulator()
            print(f"Quantum simulator ready for {n_qubits} qubits")


    def generate_key(self, detect_eavesdropping=True):

        print("\n" + "=" * 60)
        print("GENERATING QUANTUM KEY")
        print("=" * 60)

        start_time = time.time()

        # Step 1: Alice generates random bits and bases
        alice_bits = np.random.randint(0, 2, self.n_qubits)
        alice_bases = np.random.randint(0, 2, self.n_qubits)

        # Step 2: Bob generates random measurement bases
        bob_bases = np.random.randint(0, 2, self.n_qubits)

        # Step 3: Quantum transmission
        bob_results = self._quantum_channel(
            alice_bits,
            alice_bases,
            bob_bases
        )

        # Step 4: Sifting
        matching_bases = alice_bases == bob_bases

        sifted_key = alice_bits[matching_bases]
        bob_sifted = bob_results[matching_bases]

        print(f"Raw bits: {len(alice_bits)}")
        print(f"After sifting: {len(sifted_key)}")

        # Step 5: Eavesdropping detection
        qber, final_key = self._check_eavesdropping(
            sifted_key,
            bob_sifted
        )

        print(
            f"QBER: {qber:.4f} "
            f"({qber * 100:.2f}%)"
        )

        eavesdropping_detected = qber > 0.11

        if eavesdropping_detected:
            print("EAVESDROPPING DETECTED!")
        else:
            print("No eavesdropping detected.")

        # Step 6: Privacy amplification
        final_key_bytes = self._bits_to_bytes(final_key)

        hashed_key = hashlib.sha256(
            final_key_bytes
        ).digest()

        execution_time = time.time() - start_time

        return {
            "key_bits": final_key.tolist(),
            "key_bytes": hashed_key,
            "key_hex": hashed_key.hex(),
            "qber": qber,
            "eavesdropping_detected":
                eavesdropping_detected,
            "secure":
                not eavesdropping_detected
        }


    def _quantum_channel(
        self,
        alice_bits,
        alice_bases,
        bob_bases
    ):

        bob_results = []

        if QISKIT_AVAILABLE and self.simulator:

            for i in range(self.n_qubits):

                qc = QuantumCircuit(1, 1)

                # Encode bit
                if alice_bits[i] == 1:
                    qc.x(0)

                # Alice basis
                if alice_bases[i] == 1:
                    qc.h(0)

                # Bob basis
                if bob_bases[i] == 1:
                    qc.h(0)

                # Measurement
                qc.measure(0, 0)

                job = self.simulator.run(
                    qc,
                    shots=1
                )

                result = job.result()
                counts = result.get_counts()

                bit = int(list(counts.keys())[0])

                bob_results.append(bit)

        else:

            for i in range(len(alice_bits)):

                if bob_bases[i] == alice_bases[i]:

                    bob_results.append(
                        alice_bits[i]
                    )

                else:

                    bob_results.append(
                        np.random.randint(0, 2)
                    )

        return np.array(bob_results)


    def _check_eavesdropping(
        self,
        sifted_key,
        bob_sifted
    ):

        check_size = max(
            1,
            len(sifted_key) // 4
        )

        check_indices = np.random.choice(
            len(sifted_key),
            check_size,
            replace=False
        )

        errors = np.sum(
            sifted_key[check_indices]
            != bob_sifted[check_indices]
        )

        qber = errors / check_size

        # Remove checked bits
        mask = np.ones(
            len(sifted_key),
            dtype=bool
        )

        mask[check_indices] = False

        final_key = sifted_key[mask]

        return qber, final_key


    def _bits_to_bytes(self, bits):

        bits = bits.tolist()

        while len(bits) % 8 != 0:
            bits.append(0)

        byte_array = []

        for i in range(0, len(bits), 8):

            byte = 0

            for j in range(8):
                byte = (
                    byte << 1
                ) | bits[i + j]

            byte_array.append(byte)

        return bytes(byte_array)


    def get_aes_key(
        self,
        result_dict,
        key_size=256
    ):

        if key_size == 256:

            return result_dict["key_bytes"][:32]

        elif key_size == 128:

            return result_dict["key_bytes"][:16]

        else:

            return result_dict["key_bytes"]


def main():

    print("\n" + "=" * 60)
    print("MY QUANTUM KEY DISTRIBUTION PROJECT")
    print("BB84 Protocol Implementation")
    print("=" * 60)

    qkd = MyQKD(n_qubits=256)

    result = qkd.generate_key(
        detect_eavesdropping=False
    )

    print("\nRESULTS:")
    print(
        "Key:",
        result["key_hex"][:32],
        "..."
    )

    print(
        "Total bits:",
        len(result["key_bits"])
    )

    print(
        "Secure:",
        result["secure"]
    )

    print(
        "QBER:",
        result["qber"]
    )

    # Generate AES-256 key
    aes_key = qkd.get_aes_key(
        result,
        key_size=256
    )

    print("\nAES-256 KEY:")
    print(aes_key.hex())

    print(
        "Length:",
        len(aes_key),
        "bytes"
    )

    # Save key
    with open(
        "quantum_key.bin",
        "wb"
    ) as f:

        f.write(aes_key)

    print(
        "Key saved to quantum_key.bin"
    )


if __name__ == "__main__":
    main()