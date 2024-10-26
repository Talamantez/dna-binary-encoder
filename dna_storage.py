#!/usr/bin/env python3
"""
DNA Storage System Implementation
-------------------------------
This module provides a proof-of-concept implementation for multi-layer DNA data storage
using various modification techniques.

Requirements:
- Python 3.7+
- numpy (pip install numpy)

To run:
1. Save this file as dna_storage.py
2. Install requirements: pip install numpy
3. Run: python dna_storage.py

The script will demonstrate encoding/decoding example data using multiple storage layers.
"""

import numpy as np
import random
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class ModificationState:
    """Represents the state of a DNA position with multiple modifications"""
    methylated: bool = False
    hydroxymethylated: bool = False
    acetylated: bool = False
    formylated: bool = False

class DNAPosition:
    """Represents a single position in the DNA storage system"""
    def __init__(self, base: str):
        self.base = base
        self.modifications = ModificationState()
        self.backbone = "standard"  # standard, phosphorothioate, or boranophosphate
        self.structure = "B-DNA"    # B-DNA, Z-DNA, or cruciform

    def __str__(self):
        return f"{self.base}[{self._mod_string()}]"

    def _mod_string(self) -> str:
        mods = []
        if self.modifications.methylated:
            mods.append("Me")
        if self.modifications.hydroxymethylated:
            mods.append("hMe")
        if self.modifications.acetylated:
            mods.append("Ac")
        if self.modifications.formylated:
            mods.append("fC")
        return "-".join(mods) if mods else "unmod"


class DNAStorageSystem:
    def __init__(self):
        """Initialize encoding mappings"""
        # Base encoding (2 bits per base)
        self.base_encoding = {
            '00': 'A',
            '01': 'C',
            '10': 'G',
            '11': 'T'
        }
        self.base_decoding = {v: k for k, v in self.base_encoding.items()}

    def encode_to_dna(self, data: str) -> list[DNAPosition]:
        """Convert binary data to DNA sequence with modifications"""
        self.original_length = len(data)
        
        # Process in groups of 4 bits (2 for base, 2 for methylation)
        dna_sequence = []
        for i in range(0, len(data), 4):
            # Get chunks of 4 bits
            chunk = data[i:min(i+4, len(data))]
            if len(chunk) < 4:
                chunk = chunk.ljust(4, '0')
            
            # First 2 bits for base
            base_bits = chunk[:2]
            # Last 2 bits for methylation - if either bit is 1, methylate
            methylation_bits = chunk[2:4]
            is_methylated = '1' in methylation_bits
            
            # Create position
            position = DNAPosition(self.base_encoding[base_bits])
            position.modifications.methylated = is_methylated
            position.backbone = 'standard'
            
            dna_sequence.append(position)
            
        return dna_sequence

    def decode_from_dna(self, dna_sequence: list[DNAPosition]) -> str:
        """Convert DNA sequence back to binary data"""
        binary_data = ""
        
        for i, pos in enumerate(dna_sequence):
            # Get 2 bits from base
            binary_data += self.base_decoding[pos.base]
            
            # Convert methylation back to original bits
            # If there was methylation, the last bits were not 00
            # We'll use 01 for consistency
            binary_data += '01' if pos.modifications.methylated else '00'
        
        # Remove padding if necessary
        if hasattr(self, 'original_length'):
            return binary_data[:self.original_length]
        
        return binary_data

    def _group_bits(self, data: str) -> list[str]:
        """Helper to group bits into groups of 4"""
        groups = []
        for i in range(0, len(data), 4):
            group = data[i:min(i+4, len(data))]
            if len(group) < 4:
                group = group.ljust(4, '0')
            groups.append(group)
        return groups

    def _print_debug_info(self, data: str, dna_sequence: list[DNAPosition], decoded: str) -> None:
        """Helper to print debug information"""
        print(f"\nInput data: {data}")
        print("DNA sequence:")
        for i, pos in enumerate(dna_sequence):
            print(f"  Position {i}: Base={pos.base}, Methylated={pos.modifications.methylated}")
        print(f"Decoded data: {decoded}")
        print(f"Original length: {self.original_length}")

class ErrorCorrection:
    """Simple error correction using repetition code"""

    @staticmethod
    def encode(data: str, repetitions: int = 3) -> str:
        """Encode data with repetition"""
        data = data.strip()
        return "".join(bit * repetitions for bit in data)

    @staticmethod
    def decode(data: str, repetitions: int = 3) -> str:
        """Decode data with majority voting"""
        # Ensure the data length is multiple of repetitions
        if len(data) % repetitions != 0:
            # Remove padding
            data = data[: -(len(data) % repetitions)]

        result = ""
        for i in range(0, len(data), repetitions):
            chunk = data[i : i + repetitions]
            ones = chunk.count("1")
            zeros = chunk.count("0")
            result += "1" if ones > zeros else "0"
        return result

    @staticmethod
    def validate_encoding(original: str, encoded: str, repetitions: int = 3) -> bool:
        """Validate that the encoding is correct"""
        if len(encoded) != len(original) * repetitions:
            return False

        for i, bit in enumerate(original):
            chunk = encoded[i * repetitions : (i + 1) * repetitions]
            if chunk != bit * repetitions:
                return False
        return True

    @staticmethod
    def validate_chunk(chunk: str) -> bool:
        """Validate that a chunk of bits is valid for error correction"""
        return all(b in "01" for b in chunk)


def demo_storage_system():
    """Demonstrate the DNA storage system with example data"""
    # Initialize system
    storage = DNAStorageSystem()
    error_correction = ErrorCorrection()

    # Example data
    original_data = "10110010"
    print(f"\nOriginal data: {original_data}")

    # Add error correction
    encoded_data = error_correction.encode(original_data)
    print(f"Data with error correction: {encoded_data}")

    # Convert to DNA
    dna_sequence = storage.encode_to_dna(encoded_data)

    # Print DNA sequence with modifications
    print("\nDNA Storage representation:")
    for i, pos in enumerate(dna_sequence):
        print(f"Position {i}: {pos}")

    # Decode back to binary
    decoded_data = storage.decode_from_dna(dna_sequence)
    final_data = error_correction.decode(decoded_data)

    print(f"\nDecoded data: {final_data}")
    print(f"Successful recovery: {original_data == final_data}")


if __name__ == "__main__":
    # Run demonstration
    print("DNA Storage System Demonstration")
    print("===============================")
    demo_storage_system()
