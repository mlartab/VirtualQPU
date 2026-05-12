# VirtualQPU — Virtual Quantum Processing Unit
# Author:  mlartab (github.com/mlartab)
# License: MIT
# Created: May 2026
# =======================================================

# virtualqpu/runner.py
# Simple interface to run any circuit on any chip

import cirq
from virtualqpu.chip import QPUChip

class QPURunner:
    """
    Run a circuit on a chip and get clean results back.
    Simpler interface than QPUBenchmark for single runs.
    """

    def __init__(self, chip: QPUChip):
        self.chip = chip
        print(f"Runner ready on chip: {chip.name}")

    def run(self, circuit, repetitions=1000, key='output'):
        """Run a circuit and return histogram of results."""
        result = self.chip.run(circuit, repetitions=repetitions)
        if result is None:
            return None
        counts = result['result'].histogram(key=key)
        return {
            'chip': self.chip.name,
            'counts': counts,
            'repetitions': repetitions,
            'time': result['time_seconds'],
        }

    def print_result(self, result, key='output'):
        """Print results in readable format."""
        if result is None:
            print("No result — circuit validation failed.")
            return
        print(f"\nResults on {result['chip']}:")
        print(f"  Repetitions: {result['repetitions']}")
        print(f"  Time:        {result['time']*1000:.1f}ms")
        print(f"  Counts:")
        total = sum(result['counts'].values())
        for state, count in sorted(result['counts'].items()):
            pct = count / total * 100
            bar = '#' * int(pct / 2)
            print(f"    State {state}: {count:5d} ({pct:.1f}%) {bar}")