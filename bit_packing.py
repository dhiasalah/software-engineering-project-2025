"""
BitPacking Implementation for Data Compression
Author: [Your Name]

This module implements bit packing compression for integer arrays with two variants:
1. Simple bit packing (allows splitting across consecutive integers)
2. Aligned bit packing (no splitting across consecutive integers)
3. Overflow bit packing (handles outliers efficiently)
"""

import time
import math
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class BitPackingBase(ABC):
    """Abstract base class for bit packing implementations"""

    def __init__(self):
        self.compressed_data: List[int] = []
        self.original_length: int = 0
        self.bits_per_element: int = 0

    @abstractmethod
    def compress(self, array: List[int]) -> List[int]:
        """Compress an array of integers"""
        pass

    @abstractmethod
    def decompress(self, compressed_array: List[int]) -> List[int]:
        """Decompress and return the original array"""
        pass

    @abstractmethod
    def get(self, index: int) -> int:
        """Get the value at index i from compressed array"""
        pass

    def _calculate_bits_needed(self, array: List[int]) -> int:
        """Calculate minimum bits needed to represent all values"""
        if not array:
            return 0
        max_val = max(array)
        return max_val.bit_length() if max_val > 0 else 1


class SimpleBitPacking(BitPackingBase):
    """
    Simple bit packing that allows compressed integers to span across
    consecutive integers in the output array.
    """

    def compress(self, array: List[int]) -> List[int]:
        """
        Compress array using simple bit packing.
        Compressed integers can span across consecutive output integers.
        """
        if not array:
            return []

        self.original_length = len(array)
        self.bits_per_element = self._calculate_bits_needed(array)

        # Calculate total bits needed
        total_bits = self.original_length * self.bits_per_element
        # Calculate number of 32-bit integers needed
        num_output_ints = (total_bits + 31) // 32

        # Initialize output array
        compressed = [0] * num_output_ints

        # Pack each element
        for i, value in enumerate(array):
            start_bit = i * self.bits_per_element
            self._write_bits(compressed, start_bit, self.bits_per_element, value)

        self.compressed_data = compressed
        return compressed

    def decompress(self, compressed_array: List[int]) -> List[int]:
        """Decompress the array"""
        if not compressed_array:
            return []

        result = []
        for i in range(self.original_length):
            start_bit = i * self.bits_per_element
            value = self._read_bits(compressed_array, start_bit, self.bits_per_element)
            result.append(value)

        return result

    def get(self, index: int) -> int:
        """Get value at index from compressed data"""
        if index < 0 or index >= self.original_length:
            raise IndexError("Index out of range")

        start_bit = index * self.bits_per_element
        return self._read_bits(self.compressed_data, start_bit, self.bits_per_element)

    def _write_bits(self, array: List[int], start_bit: int, num_bits: int, value: int):
        """Write bits to the array starting at start_bit"""
        if num_bits == 0:
            return

        mask = (1 << num_bits) - 1
        value &= mask  # Ensure value fits in num_bits

        int_index = start_bit // 32
        bit_offset = start_bit % 32

        # If the value fits entirely in one integer
        if bit_offset + num_bits <= 32:
            array[int_index] |= (value << bit_offset)
        else:
            # Split across two integers
            bits_in_first = 32 - bit_offset
            bits_in_second = num_bits - bits_in_first

            # Write first part
            first_mask = (1 << bits_in_first) - 1
            array[int_index] |= ((value & first_mask) << bit_offset)

            # Write second part
            if int_index + 1 < len(array):
                array[int_index + 1] |= (value >> bits_in_first)

    def _read_bits(self, array: List[int], start_bit: int, num_bits: int) -> int:
        """Read bits from the array starting at start_bit"""
        if num_bits == 0:
            return 0

        int_index = start_bit // 32
        bit_offset = start_bit % 32

        if int_index >= len(array):
            return 0

        # If the value is entirely in one integer
        if bit_offset + num_bits <= 32:
            mask = (1 << num_bits) - 1
            return (array[int_index] >> bit_offset) & mask
        else:
            # Split across two integers
            bits_in_first = 32 - bit_offset
            bits_in_second = num_bits - bits_in_first

            # Read first part
            first_mask = (1 << bits_in_first) - 1
            first_part = (array[int_index] >> bit_offset) & first_mask

            # Read second part
            if int_index + 1 < len(array):
                second_mask = (1 << bits_in_second) - 1
                second_part = array[int_index + 1] & second_mask
                return first_part | (second_part << bits_in_first)
            else:
                return first_part


class AlignedBitPacking(BitPackingBase):
    """
    Aligned bit packing that ensures compressed integers don't span
    across consecutive integers in the output array.
    """

    def compress(self, array: List[int]) -> List[int]:
        """
        Compress array using aligned bit packing.
        Compressed integers never span across consecutive output integers.
        """
        if not array:
            return []

        self.original_length = len(array)
        self.bits_per_element = self._calculate_bits_needed(array)

        # Calculate how many elements fit in one 32-bit integer
        elements_per_int = 32 // self.bits_per_element if self.bits_per_element > 0 else 32

        # Calculate number of output integers needed
        num_output_ints = (self.original_length + elements_per_int - 1) // elements_per_int

        # Initialize output array
        compressed = [0] * num_output_ints

        # Pack elements
        for i, value in enumerate(array):
            output_index = i // elements_per_int
            element_index = i % elements_per_int
            bit_offset = element_index * self.bits_per_element

            compressed[output_index] |= (value << bit_offset)

        self.compressed_data = compressed
        return compressed

    def decompress(self, compressed_array: List[int]) -> List[int]:
        """Decompress the array"""
        if not compressed_array:
            return []

        result = []
        elements_per_int = 32 // self.bits_per_element if self.bits_per_element > 0 else 32
        mask = (1 << self.bits_per_element) - 1

        for i in range(self.original_length):
            output_index = i // elements_per_int
            element_index = i % elements_per_int
            bit_offset = element_index * self.bits_per_element

            if output_index < len(compressed_array):
                value = (compressed_array[output_index] >> bit_offset) & mask
                result.append(value)
            else:
                result.append(0)

        return result

    def get(self, index: int) -> int:
        """Get value at index from compressed data"""
        if index < 0 or index >= self.original_length:
            raise IndexError("Index out of range")

        elements_per_int = 32 // self.bits_per_element if self.bits_per_element > 0 else 32
        output_index = index // elements_per_int
        element_index = index % elements_per_int
        bit_offset = element_index * self.bits_per_element
        mask = (1 << self.bits_per_element) - 1

        if output_index < len(self.compressed_data):
            return (self.compressed_data[output_index] >> bit_offset) & mask
        else:
            return 0


class OverflowBitPacking(BitPackingBase):
    """
    Bit packing with overflow area for handling outliers efficiently.
    Uses a special value to indicate that the actual value is in overflow area.
    """

    def __init__(self):
        super().__init__()
        self.overflow_data: List[int] = []
        self.overflow_bits: int = 0
        self.main_bits: int = 0
        self.has_overflow_bit: bool = False
        self.threshold_value: int = 0

    def compress(self, array: List[int]) -> List[int]:
        """
        Compress array using overflow bit packing.
        Outliers are stored in a separate overflow area.
        """
        if not array:
            return []

        self.original_length = len(array)

        # Analyze the data to determine optimal bit allocation
        self._analyze_overflow_strategy(array)

        # Separate main values and overflow values
        main_values = []
        self.overflow_data = []
        overflow_map = {}

        for value in array:
            if self._needs_overflow(value):
                if value not in overflow_map:
                    overflow_map[value] = len(self.overflow_data)
                    self.overflow_data.append(value)
                # Use overflow indicator + position
                encoded_value = (1 << self.main_bits) | overflow_map[value]
                main_values.append(encoded_value)
            else:
                # Direct encoding
                main_values.append(value)

        # Compress main values using simple bit packing
        total_bits_per_element = self.main_bits + (1 if self.has_overflow_bit else 0)
        total_bits = len(main_values) * total_bits_per_element
        num_output_ints = (total_bits + 31) // 32

        compressed = [0] * num_output_ints

        for i, value in enumerate(main_values):
            start_bit = i * total_bits_per_element
            self._write_bits(compressed, start_bit, total_bits_per_element, value)

        # Append overflow data
        compressed.extend(self.overflow_data)

        self.compressed_data = compressed
        return compressed

    def _analyze_overflow_strategy(self, array: List[int]):
        """Analyze values to determine optimal overflow strategy"""
        if not array:
            self.has_overflow_bit = False
            self.main_bits = 1
            self.overflow_bits = 0
            self.threshold_value = 0
            return

        sorted_values = sorted(set(array))

        if len(sorted_values) <= 1:
            # Simple case: all values are the same or empty
            self.has_overflow_bit = False
            self.main_bits = self._calculate_bits_needed(array)
            self.overflow_bits = 0
            self.threshold_value = max(array) if array else 0
            return

        # For simplicity, use a threshold-based approach
        # Values requiring more than 75% of max bits go to overflow
        max_bits = max(sorted_values).bit_length()
        threshold_bits = max(3, int(max_bits * 0.6))
        self.threshold_value = (1 << threshold_bits) - 1

        overflow_values = [v for v in sorted_values if v > self.threshold_value]

        if len(overflow_values) > 0 and len(overflow_values) < len(sorted_values) * 0.3:
            self.has_overflow_bit = True
            self.main_bits = threshold_bits
            self.overflow_bits = math.ceil(math.log2(len(overflow_values) + 1)) if len(overflow_values) > 1 else 1
        else:
            self.has_overflow_bit = False
            self.main_bits = max_bits
            self.overflow_bits = 0

    def _needs_overflow(self, value: int) -> bool:
        """Check if value needs to go to overflow area"""
        return self.has_overflow_bit and value > self.threshold_value

    def decompress(self, compressed_array: List[int]) -> List[int]:
        """Decompress the array"""
        if not compressed_array:
            return []

        # Split compressed data and overflow data
        total_bits_per_element = self.main_bits + (1 if self.has_overflow_bit else 0)
        total_bits = self.original_length * total_bits_per_element
        num_main_ints = (total_bits + 31) // 32

        main_compressed = compressed_array[:num_main_ints]
        overflow_data = compressed_array[num_main_ints:]

        result = []
        overflow_mask = 1 << self.main_bits if self.has_overflow_bit else 0
        value_mask = (1 << self.main_bits) - 1

        for i in range(self.original_length):
            start_bit = i * total_bits_per_element
            encoded_value = self._read_bits(main_compressed, start_bit, total_bits_per_element)

            if self.has_overflow_bit and (encoded_value & overflow_mask):
                # This is an overflow reference
                overflow_index = encoded_value & value_mask
                if overflow_index < len(overflow_data):
                    actual_value = overflow_data[overflow_index]
                    result.append(actual_value)
                else:
                    result.append(0)
            else:
                # Direct value
                result.append(encoded_value & value_mask)

        return result

    def get(self, index: int) -> int:
        """Get value at index from compressed data"""
        if index < 0 or index >= self.original_length:
            raise IndexError("Index out of range")

        total_bits_per_element = self.main_bits + (1 if self.has_overflow_bit else 0)
        total_bits = self.original_length * total_bits_per_element
        num_main_ints = (total_bits + 31) // 32

        start_bit = index * total_bits_per_element
        encoded_value = self._read_bits(self.compressed_data[:num_main_ints], start_bit, total_bits_per_element)

        overflow_mask = 1 << self.main_bits if self.has_overflow_bit else 0
        value_mask = (1 << self.main_bits) - 1

        if self.has_overflow_bit and (encoded_value & overflow_mask):
            # This is an overflow reference
            overflow_index = encoded_value & value_mask
            overflow_start = num_main_ints
            if overflow_start + overflow_index < len(self.compressed_data):
                return self.compressed_data[overflow_start + overflow_index]
            else:
                return 0
        else:
            # Direct value
            return encoded_value & value_mask

    def _write_bits(self, array: List[int], start_bit: int, num_bits: int, value: int):
        """Write bits to the array starting at start_bit"""
        if num_bits == 0:
            return

        mask = (1 << num_bits) - 1
        value &= mask

        int_index = start_bit // 32
        bit_offset = start_bit % 32

        if int_index >= len(array):
            return

        if bit_offset + num_bits <= 32:
            array[int_index] |= (value << bit_offset)
        else:
            bits_in_first = 32 - bit_offset
            first_mask = (1 << bits_in_first) - 1
            array[int_index] |= ((value & first_mask) << bit_offset)
            if int_index + 1 < len(array):
                array[int_index + 1] |= (value >> bits_in_first)

    def _read_bits(self, array: List[int], start_bit: int, num_bits: int) -> int:
        """Read bits from the array starting at start_bit"""
        if num_bits == 0:
            return 0

        int_index = start_bit // 32
        bit_offset = start_bit % 32

        if int_index >= len(array):
            return 0

        if bit_offset + num_bits <= 32:
            mask = (1 << num_bits) - 1
            return (array[int_index] >> bit_offset) & mask
        else:
            bits_in_first = 32 - bit_offset
            bits_in_second = num_bits - bits_in_first

            first_mask = (1 << bits_in_first) - 1
            first_part = (array[int_index] >> bit_offset) & first_mask

            if int_index + 1 < len(array):
                second_mask = (1 << bits_in_second) - 1
                second_part = array[int_index + 1] & second_mask
                return first_part | (second_part << bits_in_first)
            else:
                return first_part
