# VirtualQPU — Virtual Quantum Processing Unit
# Author:  mlartab (github.com/mlartab)
# License: MIT
# Created: May 2026
# =======================================================

# virtualqpu/noise.py
# Noise presets for VirtualQPU
# Use these when designing your chips

import cirq

class NoisePreset:
    """
    Ready-made noise levels based on real quantum hardware.
    
    PERFECT:      no noise - theoretical only, does not exist in reality
    RESEARCH:     best current superconducting hardware
    GOOD:         solid near-term hardware
    NOISY:        early quantum hardware level
    VERY_NOISY:   proof of concept hardware
    """
    
    PERFECT    = 0.0000
    RESEARCH   = 0.0005
    GOOD       = 0.0010
    MODERATE   = 0.0100
    NOISY      = 0.0500
    VERY_NOISY = 0.1000

    @staticmethod
    def describe(noise_level):
        if noise_level == 0:
            return "Perfect (theoretical)"
        elif noise_level <= 0.001:
            return "Research grade"
        elif noise_level <= 0.01:
            return "Good hardware"
        elif noise_level <= 0.05:
            return "Noisy hardware"
        else:
            return "Very noisy hardware"

    @staticmethod
    def build(noise_level):
        """Build a Cirq noise model from a noise level float."""
        if noise_level == 0:
            return cirq.NO_NOISE
        return cirq.ConstantQubitNoiseModel(
            cirq.depolarize(noise_level)
        )