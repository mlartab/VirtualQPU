import sys
sys.path.insert(0, '/home/lardin/VirtualQPU')

import cirq
from virtualqpu.chip import QPUChip, ChipFactory, QPUBenchmark

print("VirtualQPU loaded successfully")
print("Running first test...\n")

# Design 4 chips
chips = [
    ChipFactory.linear(4, noise=0.001, name="Low-Noise Linear"),
    ChipFactory.linear(4, noise=0.05,  name="High-Noise Linear"),
    ChipFactory.grid(2, 2, noise=0.001, name="Low-Noise Grid"),
    ChipFactory.grid(2, 2, noise=0.05,  name="High-Noise Grid"),
]

# Simple Bell State circuit
q0 = cirq.GridQubit(0, 0)
q1 = cirq.GridQubit(0, 1)

circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1, key='output')
)

print("Circuit:")
print(circuit)
print()

# Run benchmark
benchmark = QPUBenchmark(chips)
results = benchmark.run(circuit, repetitions=1000)
comparison = benchmark.compare(target_state=0)
benchmark.visualize(comparison)