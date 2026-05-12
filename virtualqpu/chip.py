# VirtualQPU — Virtual Quantum Processing Unit
# Author:  mlartab (github.com/mlartab)
# License: MIT
# Created: May 2026
#
# Original work. First open source quantum chip design
# simulator built on Google Cirq.
#
# You may use, modify, and distribute this code freely
# under the MIT License. Attribution appreciated.
# =======================================================

# virtualqpu/chip.py
# The heart of VirtualQPU
# You design a chip. You define its qubits and connections.
# The framework handles the rest.

import cirq
import cirq_google
import qsimcirq
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import time

@dataclass
class QPUChip:
    """
    A designable quantum chip.
    
    You define:
      - How many qubits
      - Which qubits connect to which
      - How noisy the chip is
      - The chip's name
    
    VirtualQPU handles:
      - Building the Cirq device
      - Applying the noise model
      - Running circuits
      - Benchmarking performance
    """
    
    name: str
    qubits: List[cirq.GridQubit]
    connections: List[Tuple[cirq.GridQubit, cirq.GridQubit]]
    noise_level: float = 0.01
    description: str = ""
    topology: str = ""
    
    def __post_init__(self):
        self.qubit_count = len(self.qubits)
        self.connection_count = len(self.connections)
        self._build_noise_model()
    
    def _build_noise_model(self):
        """Build a noise model from the noise level parameter."""
        self.noise_model = cirq.ConstantQubitNoiseModel(
            cirq.depolarize(self.noise_level)
        )
    
    def is_connected(self, q1, q2):
        """Check if two qubits are directly connected on this chip."""
        return (q1, q2) in self.connections or (q2, q1) in self.connections
    
    def validate_circuit(self, circuit):
        """
        Check if a circuit can run on this chip.
        Returns list of problems found.
        """
        problems = []
        for moment in circuit:
            for op in moment.operations:
                if len(op.qubits) == 2:
                    q1, q2 = op.qubits
                    if not self.is_connected(q1, q2):
                        problems.append(
                            f"Gate between {q1} and {q2} not allowed — not connected on {self.name}"
                        )
                for q in op.qubits:
                    if q not in self.qubits:
                        problems.append(
                            f"Qubit {q} does not exist on {self.name}"
                        )
        return problems
    
    def run(self, circuit, repetitions=1000):
        """Run a circuit on this chip with its noise model."""
        problems = self.validate_circuit(circuit)
        if problems:
            print(f"Circuit validation failed on {self.name}:")
            for p in problems:
                print(f"  - {p}")
            return None
        
        noisy_circuit = circuit.with_noise(self.noise_model)
        simulator = cirq.DensityMatrixSimulator(noise=self.noise_model)
        start = time.time()
        result = simulator.run(circuit, repetitions=repetitions)
        elapsed = time.time() - start
        
        return {
            'chip': self.name,
            'result': result,
            'time_seconds': elapsed,
            'repetitions': repetitions,
            'noise_level': self.noise_level,
        }
    
    def info(self):
        print(f"\nChip: {self.name}")
        print(f"  Description:  {self.description}")
        print(f"  Qubits:       {self.qubit_count}")
        print(f"  Connections:  {self.connection_count}")
        print(f"  Noise level:  {self.noise_level:.4f} ({self.noise_level*100:.2f}%)")
        print(f"  Topology:     {self._topology_type()}")
    
    def _topology_type(self):
        if hasattr(self, "topology"):
            return self.topology
        ratio = self.connection_count / self.qubit_count
        if ratio < 0.85:
            return "Sparse linear"
        elif ratio < 1.1:
            return "Linear chain"
        elif ratio < 2.0:
            return "Grid mesh"
        else:
            return "Dense mesh"


# ================================================================
# CHIP FACTORY
# Pre-built chip designs you can use immediately
# ================================================================

class ChipFactory:
    """
    Ready-made chip designs.
    Use these or design your own.
    """
    
    @staticmethod
    def linear(n_qubits, noise=0.01, name=None):
        """
        Linear chain: each qubit connects to the next.
        Simple. Like a wire.
        q0 - q1 - q2 - q3 - ...
        """
        qubits = [cirq.GridQubit(0, i) for i in range(n_qubits)]
        connections = [(qubits[i], qubits[i+1]) for i in range(n_qubits-1)]
        return QPUChip(
            name=name or f"Linear-{n_qubits}Q",
            qubits=qubits,
            connections=connections,
            noise_level=noise,
            description=f"{n_qubits}-qubit linear chain", topology="Linear chain"
        )
    
    @staticmethod
    def grid(rows, cols, noise=0.01, name=None):
        """
        2D grid: each qubit connects to neighbors.
        Like Google's real hardware.
        q(0,0) - q(0,1) - q(0,2)
           |        |        |
        q(1,0) - q(1,1) - q(1,2)
        """
        qubits = [cirq.GridQubit(r, c) for r in range(rows) for c in range(cols)]
        connections = []
        for r in range(rows):
            for c in range(cols):
                if c + 1 < cols:
                    connections.append((cirq.GridQubit(r, c), cirq.GridQubit(r, c+1)))
                if r + 1 < rows:
                    connections.append((cirq.GridQubit(r, c), cirq.GridQubit(r+1, c)))
        return QPUChip(
            name=name or f"Grid-{rows}x{cols}",
            qubits=qubits,
            connections=connections,
            noise_level=noise,
            description=f"{rows}x{cols} grid topology", topology="Grid mesh"
        )
    
    @staticmethod
    def star(n_outer, noise=0.01, name=None):
        """
        Star topology: one central qubit connects to all others.
        Central qubit is the hub.
        """
        center = cirq.GridQubit(0, 0)
        outer = [cirq.GridQubit(1, i) for i in range(n_outer)]
        connections = [(center, q) for q in outer]
        return QPUChip(
            name=name or f"Star-{n_outer+1}Q",
            qubits=[center] + outer,
            connections=connections,
            noise_level=noise,
            description=f"Star topology — 1 hub + {n_outer} outer qubits"
        )
    
    @staticmethod
    def ring(n_qubits, noise=0.01, name=None):
        """
        Ring topology: each qubit connects to next, last connects to first.
        q0 - q1 - q2 - q3 - q0
        """
        qubits = [cirq.GridQubit(0, i) for i in range(n_qubits)]
        connections = [(qubits[i], qubits[(i+1) % n_qubits]) for i in range(n_qubits)]
        return QPUChip(
            name=name or f"Ring-{n_qubits}Q",
            qubits=qubits,
            connections=connections,
            noise_level=noise,
            description=f"{n_qubits}-qubit ring", topology="Ring"
        )


# ================================================================
# BENCHMARKER
# Run the same algorithm on multiple chips
# Compare performance automatically
# ================================================================

class QPUBenchmark:
    """
    Run the same circuit on multiple chips.
    Compare: accuracy, speed, noise sensitivity.
    """
    
    def __init__(self, chips: List[QPUChip]):
        self.chips = chips
        self.results = {}
    
    def run(self, circuit, repetitions=1000):
        print("=" * 55)
        print("VIRTUAQPU BENCHMARK")
        print(f"Circuit depth: {len(circuit)}")
        print(f"Repetitions:   {repetitions}")
        print("=" * 55)
        
        for chip in self.chips:
            chip.info()
            result = chip.run(circuit, repetitions=repetitions)
            if result:
                self.results[chip.name] = result
                print(f"  Completed in {result['time_seconds']:.3f}s")
        
        return self.results
    
    def compare(self, key='result', target_state=0):
        """
        Compare how accurately each chip found the target state.
        target_state: the measurement outcome you expected (0 = truth)
        """
        print("\n" + "=" * 55)
        print("BENCHMARK RESULTS")
        print("=" * 55)
        
        comparison = {}
        for chip_name, data in self.results.items():
            counts = data['result'].histogram(key='output')
            total = sum(counts.values())
            target_count = counts.get(target_state, 0)
            accuracy = target_count / total
            comparison[chip_name] = {
                'accuracy': accuracy,
                'time': data['time_seconds'],
                'noise': data['noise_level'],
                'counts': counts
            }
            print(f"\n  {chip_name}")
            print(f"    Target state accuracy: {accuracy*100:.1f}%")
            print(f"    Simulation time:       {data['time_seconds']:.3f}s")
            print(f"    Noise level:           {data['noise_level']*100:.2f}%")
        
        return comparison
    
    def visualize(self, comparison):
        """Generate comparison charts across all chips."""
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.patch.set_facecolor('#0a0a2e')
        
        names = list(comparison.keys())
        accuracies = [comparison[n]['accuracy'] * 100 for n in names]
        times = [comparison[n]['time'] * 1000 for n in names]
        noises = [comparison[n]['noise'] * 100 for n in names]
        
        colors = ['#00d4ff', '#a855f7', '#ff6b35', '#00ff88', '#ffd700'][:len(names)]
        
        for ax in axes:
            ax.set_facecolor('#0a0a2e')
            for spine in ax.spines.values():
                spine.set_edgecolor('#00d4ff')
            ax.tick_params(colors='white')
        
        # Accuracy chart
        bars = axes[0].bar(names, accuracies, color=colors,
                           edgecolor='white', linewidth=0.5)
        axes[0].set_title('Target State Accuracy\nby Chip Design',
                          color='white', fontsize=11)
        axes[0].set_ylabel('Accuracy %', color='white')
        axes[0].set_ylim(0, 100)
        axes[0].tick_params(axis='x', rotation=15)
        for bar, val in zip(bars, accuracies):
            axes[0].text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 1,
                        f'{val:.1f}%', ha='center',
                        color='white', fontsize=9)
        
        # Speed chart
        bars2 = axes[1].bar(names, times, color=colors,
                            edgecolor='white', linewidth=0.5)
        axes[1].set_title('Simulation Speed\nby Chip Design',
                          color='white', fontsize=11)
        axes[1].set_ylabel('Time (ms)', color='white')
        axes[1].tick_params(axis='x', rotation=15)
        for bar, val in zip(bars2, times):
            axes[1].text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 1,
                        f'{val:.0f}ms', ha='center',
                        color='white', fontsize=9)
        
        # Noise comparison
        bars3 = axes[2].bar(names, noises, color=colors,
                            edgecolor='white', linewidth=0.5)
        axes[2].set_title('Noise Level\nby Chip Design',
                          color='white', fontsize=11)
        axes[2].set_ylabel('Noise %', color='white')
        axes[2].tick_params(axis='x', rotation=15)
        for bar, val in zip(bars3, noises):
            axes[2].text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 0.001,
                        f'{val:.2f}%', ha='center',
                        color='white', fontsize=9)
        
        plt.suptitle('VirtualQPU — Chip Design Benchmark Comparison\n'
                     'Same algorithm. Different chip topologies. Different results.',
                     color='white', fontsize=11, y=1.02)
        plt.tight_layout()
        plt.savefig('virtualqpu_benchmark.png', dpi=200,
                    bbox_inches='tight', facecolor='#0a0a2e')
        plt.show()
        print("\nSaved as virtualqpu_benchmark.png")