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
from typing import Dict, List, Tuple
import random
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
    """Main class for DNA-based data storage"""
    
    def __init__(self):
        self.base_encoding = {
            '00': 'A', '01': 'C',
            '10': 'G', '11': 'T'
        }
        self.modification_encoding = {
            '00': ModificationState(),
            '01': ModificationState(methylated=True),
            '10': ModificationState(hydroxymethylated=True),
            '11': ModificationState(formylated=True)
        }
        self.backbone_encoding = {
            '0': 'standard',
            '1': 'phosphorothioate'
        }

    def encode_to_dna(self, data: str) -> List[DNAPosition]:
        """Convert binary data to DNA sequence with modifications"""
        # Ensure data length is multiple of 2
        if len(data) % 2 != 0:
            data += '0'

        dna_sequence = []
        
        # Process 2 bits at a time for base encoding
        for i in range(0, len(data)-3, 4):
            base_bits = data[i:i+2]
            mod_bits = data[i+2:i+4]
            
            # Create DNA position
            position = DNAPosition(self.base_encoding[base_bits])
            position.modifications = self.modification_encoding[mod_bits]
            position.backbone = self.backbone_encoding[str(random.randint(0, 1))]
            
            dna_sequence.append(position)
            
        return dna_sequence

    def decode_from_dna(self, dna_sequence: List[DNAPosition]) -> str:
        """Convert DNA sequence back to binary data"""
        binary_data = ""
        
        for pos in dna_sequence:
            # Decode base
            for bits, base in self.base_encoding.items():
                if base == pos.base:
                    binary_data += bits
            
            # Decode modifications
            for bits, mods in self.modification_encoding.items():
                if (mods.methylated == pos.modifications.methylated and
                    mods.hydroxymethylated == pos.modifications.hydroxymethylated and
                    mods.formylated == pos.modifications.formylated):
                    binary_data += bits
                    
        return binary_data

class ErrorCorrection:
    """Simple error correction using repetition code"""
    
    @staticmethod
    def encode(data: str, repetitions: int = 3) -> str:
        """Encode data with repetition"""
        return ''.join(bit * repetitions for bit in data)
    
    @staticmethod
    def decode(data: str, repetitions: int = 3) -> str:
        """Decode data with majority voting"""
        result = ""
        for i in range(0, len(data), repetitions):
            chunk = data[i:i+repetitions]
            ones = chunk.count('1')
            zeros = chunk.count('0')
            result += '1' if ones > zeros else '0'
        return result

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