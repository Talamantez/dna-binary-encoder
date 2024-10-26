import unittest
from dna_storage import (
    DNAStorageSystem,
    ErrorCorrection,
    DNAPosition,
    ModificationState,
)


class TestErrorCorrection(unittest.TestCase):
    def setUp(self):
        self.error_correction = ErrorCorrection()

    def test_encode_basic(self):
        """Test basic encoding functionality"""
        test_cases = [
            ("101", "111000111"),
            ("0101", "000111000111"),
            ("1", "111"),
            ("0", "000"),
            ("11", "111111"),
        ]
        for input_data, expected in test_cases:
            with self.subTest(input_data=input_data):
                result = self.error_correction.encode(input_data)
                self.assertEqual(result, expected)
                # Verify encoding pattern
                self.assertTrue(
                    self.error_correction.validate_encoding(input_data, result),
                    f"Invalid encoding pattern for {input_data}:\n" +
                    f"Expected: {expected}\n" +
                    f"Got: {result}"
                )
                # Verify each chunk is valid
                for i in range(0, len(result), 3):
                    chunk = result[i:i+3]
                    self.assertTrue(
                        self.error_correction.validate_chunk(chunk),
                        f"Invalid chunk {chunk} in encoded result for {input_data}"
                    )

    def test_decode_basic(self):
        """Test basic decoding functionality"""
        test_cases = [
            ("111000111", "101"),
            ("000111000111", "0101"),
            ("111", "1"),
            ("000", "0"),
            ("111111", "11"),
        ]
        for input_data, expected in test_cases:
            with self.subTest(input_data=input_data):
                result = self.error_correction.decode(input_data)
                self.assertEqual(result, expected)

    def test_error_correction_capability(self):
        """Test that single bit errors are corrected"""
        test_cases = [
            ("110000111", "101"),  # One error in first triplet
            ("111000110", "101"),  # One error in last triplet
            ("111000011", "101"),  # One error in middle triplet
        ]
        for input_data, expected in test_cases:
            with self.subTest(input_data=input_data):
                result = self.error_correction.decode(input_data)
                self.assertEqual(result, expected)

    def test_encode_decode_roundtrip(self):
        """Test that encoding followed by decoding returns original data"""
        test_cases = ["101", "0101", "1", "0", "11", "0101010"]
        for test_data in test_cases:
            with self.subTest(test_data=test_data):
                encoded = self.error_correction.encode(test_data)
                decoded = self.error_correction.decode(encoded)
                self.assertEqual(test_data, decoded)


class TestDNAStorageSystem(unittest.TestCase):
    def setUp(self):
        self.storage_system = DNAStorageSystem()
        self.error_correction = ErrorCorrection()

    def test_base_encoding(self):
        """Test basic DNA base encoding"""
        test_cases = {
            "00": "A",
            "01": "C",
            "10": "G",
            "11": "T",
        }
        for bits, base in test_cases.items():
            with self.subTest(bits=bits):
                sequence = self.storage_system.encode_to_dna(bits + "00")
                self.assertEqual(sequence[0].base, base)

    def test_modification_encoding(self):
        """Test modification state encoding"""
        test_cases = [
            ("0000", False),   # A, no methylation
            ("0001", True),    # A with methylation
            ("0100", False),   # C, no methylation
            ("0101", True),    # C with methylation
            ("1100", False),   # T, no methylation
            ("1101", True),    # T with methylation
        ]
        for bits, should_be_methylated in test_cases:
            with self.subTest(bits=bits):
                sequence = self.storage_system.encode_to_dna(bits)
                self.assertEqual(
                    sequence[0].modifications.methylated,
                    should_be_methylated,
                    f"Methylation state incorrect for bits {bits}"
                )

    def test_encode_decode_roundtrip(self):
        """Test that encoding followed by decoding preserves data"""
        test_cases = [
            "0000",      # Single base, no modifications
            "0001",      # Single base with methylation
            "00010001",  # Two bases
            "01010101"   # Multiple bases
        ]
        for test_data in test_cases:
            with self.subTest(test_data=test_data):
                dna_sequence = self.storage_system.encode_to_dna(test_data)
                decoded = self.storage_system.decode_from_dna(dna_sequence)
                
                # Compare only up to original length
                self.assertEqual(
                    test_data,
                    decoded[:len(test_data)],
                    f"Roundtrip failed for {test_data}"
                )

    def test_methylation_patterns(self):
        """Test that methylation patterns are preserved"""
        test_cases = [
            ("0001", True),    # Should be methylated
            ("0000", False),   # Should not be methylated
            ("0101", True),    # Should be methylated
            ("0100", False)    # Should not be methylated
        ]
        
        for input_data, should_be_methylated in test_cases:
            with self.subTest(input_data=input_data):
                dna_sequence = self.storage_system.encode_to_dna(input_data)
                
                # Verify initial methylation
                self.assertEqual(
                    dna_sequence[0].modifications.methylated,
                    should_be_methylated,
                    f"Wrong initial methylation for {input_data}"
                )
                
                # Test roundtrip preservation
                decoded = self.storage_system.decode_from_dna(dna_sequence)
                new_sequence = self.storage_system.encode_to_dna(decoded[:len(input_data)])
                
                self.assertEqual(
                    new_sequence[0].modifications.methylated,
                    should_be_methylated,
                    f"Methylation not preserved for {input_data}"
                )


    def test_error_correction_roundtrip(self):
        """Test full roundtrip with error correction"""
        test_cases = [
            "1100",   # Simple case
            "0101",   # Alternating bits
            "1010",   # Different alternating bits
            "0000",   # All zeros
            "1111"    # All ones
        ]
        for test_data in test_cases:
            with self.subTest(test_data=test_data):
                # Add error correction
                encoded = self.error_correction.encode(test_data)
                print(f"\nTest data: {test_data}")
                print(f"With error correction: {encoded}")
                
                # Convert to DNA
                dna_sequence = self.storage_system.encode_to_dna(encoded)
                dna_str = [f"{p.base}{'*' if p.modifications.methylated else ''}" 
                        for p in dna_sequence]
                print(f"DNA sequence: {dna_str}")
                
                # Convert back
                decoded = self.storage_system.decode_from_dna(dna_sequence)
                print(f"Decoded binary: {decoded}")
                
                # Apply error correction
                final = self.error_correction.decode(decoded[:len(encoded)])
                print(f"Final result: {final}")
                
                self.assertEqual(
                    test_data,
                    final,
                    f"Error correction roundtrip failed for {test_data}"
                )
                
def run_tests():
    unittest.main(argv=[""], verbosity=2)


if __name__ == "__main__":
    run_tests()
