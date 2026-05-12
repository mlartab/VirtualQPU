# VirtualQPU

Open source quantum chip design simulator built on Google Cirq.

Design your own quantum chips in software.
Define qubit count, topology, and noise level.
Run real quantum circuits on your designed chip.
Benchmark performance across different chip designs.

---

## The Idea

Everyone uses quantum frameworks to run algorithms.
Nobody uses them to simulate the hardware itself as a designable object.

VirtualQPU lets you:
  - Design chips with different topologies (linear, grid, star, ring)
  - Set noise levels based on real hardware benchmarks
  - Run any quantum circuit on your designed chip
  - Compare results across chip designs automatically

---

## Quick Start

pip install cirq matplotlib numpy

from virtualqpu.chip import ChipFactory, QPUBenchmark
import cirq

chips = [
    ChipFactory.linear(4, noise=0.001, name="Clean Chip"),
    ChipFactory.linear(4, noise=0.05,  name="Noisy Chip"),
    ChipFactory.grid(2, 2, noise=0.001, name="Clean Grid"),
    ChipFactory.grid(2, 2, noise=0.05,  name="Noisy Grid"),
]

q0, q1 = cirq.GridQubit(0,0), cirq.GridQubit(0,1)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1, key='output')
)

benchmark = QPUBenchmark(chips)
results = benchmark.run(circuit, repetitions=1000)
benchmark.compare(target_state=0)
benchmark.visualize(results)

---

## Available Chip Topologies

ChipFactory.linear(n, noise)        -- linear chain
ChipFactory.grid(rows, cols, noise) -- 2D grid
ChipFactory.star(n, noise)          -- hub and spoke
ChipFactory.ring(n, noise)          -- circular

---

## Noise Presets

from virtualqpu.noise import NoisePreset

NoisePreset.PERFECT     = 0.0000  -- theoretical only
NoisePreset.RESEARCH    = 0.0005  -- best current hardware
NoisePreset.GOOD        = 0.0010  -- solid near-term hardware
NoisePreset.MODERATE    = 0.0100  -- average hardware
NoisePreset.NOISY       = 0.0500  -- early quantum hardware
NoisePreset.VERY_NOISY  = 0.1000  -- proof of concept

---

## Benchmark Results

Bell State circuit on 4 chip designs:

Chip               Accuracy   Noise     Topology
Low-Noise Linear   51.4%      0.10%     Linear chain
High-Noise Linear  43.0%      5.00%     Linear chain
Low-Noise Grid     49.1%      0.10%     Grid mesh
High-Noise Grid    42.8%      5.00%     Grid mesh

The 8% accuracy gap between clean and noisy chips
is quantum decoherence measured and designed by hand.

---

## Project Structure

VirtualQPU/
  virtualqpu/
    chip.py     -- QPUChip, ChipFactory, QPUBenchmark
    runner.py   -- QPURunner for single chip runs
    noise.py    -- NoisePreset constants
    __init__.py -- package exports
  test_chip.py  -- benchmark demo
  README.md

---

## Built With

Google Cirq
Python 3.12
WSL Ubuntu on a Dell laptop with 8GB RAM

---

## What is Next

- Custom noise per qubit (not just per chip)
- Visual chip layout designer
- Circuit optimizer per topology
- Export and import chip specs as JSON
- pip installable package

---

## Author

Built from curiosity.
No physics degree. No CS degree.
Just someone who wanted to see if it was possible.

It was.