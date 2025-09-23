"""
Factory for creating different types of bit packing compression algorithms.
Author: [Your Name]

This module provides a factory pattern for creating instances of different
bit packing compression algorithms based on a single parameter.
"""

from enum import Enum
from typing import Union
from bit_packing import BitPackingBase, SimpleBitPacking, AlignedBitPacking, OverflowBitPacking


class CompressionType(Enum):
    """Enumeration of available compression types"""
    SIMPLE = "simple"
    ALIGNED = "aligned"
    OVERFLOW = "overflow"


class BitPackingFactory:
    """
    Factory class for creating bit packing compression instances.

    This factory allows easy creation of different compression algorithms
    based on a single parameter, following the Factory design pattern.
    """

    @staticmethod
    def create_compressor(compression_type: Union[str, CompressionType]) -> BitPackingBase:
        """
        Create a bit packing compressor based on the specified type.

        Args:
            compression_type: Type of compression to create. Can be:
                - "simple" or CompressionType.SIMPLE: Simple bit packing (allows spanning)
                - "aligned" or CompressionType.ALIGNED: Aligned bit packing (no spanning)
                - "overflow" or CompressionType.OVERFLOW: Overflow bit packing (with outlier handling)

        Returns:
            BitPackingBase: Instance of the requested compression algorithm

        Raises:
            ValueError: If compression_type is not recognized
        """

        # Convert string to enum if necessary
        if isinstance(compression_type, str):
            try:
                compression_type = CompressionType(compression_type.lower())
            except ValueError:
                raise ValueError(f"Unknown compression type: {compression_type}. "
                               f"Available types: {[t.value for t in CompressionType]}")

        # Create and return the appropriate compressor
        if compression_type == CompressionType.SIMPLE:
            return SimpleBitPacking()
        elif compression_type == CompressionType.ALIGNED:
            return AlignedBitPacking()
        elif compression_type == CompressionType.OVERFLOW:
            return OverflowBitPacking()
        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")

    @staticmethod
    def get_available_types() -> list:
        """
        Get list of available compression types.

        Returns:
            list: List of available compression type strings
        """
        return [compression_type.value for compression_type in CompressionType]

    @staticmethod
    def get_description(compression_type: Union[str, CompressionType]) -> str:
        """
        Get description of a compression type.

        Args:
            compression_type: Type of compression to describe

        Returns:
            str: Description of the compression algorithm
        """

        if isinstance(compression_type, str):
            compression_type = CompressionType(compression_type.lower())

        descriptions = {
            CompressionType.SIMPLE:
                "Simple bit packing that allows compressed integers to span across "
                "consecutive integers in the output array. Most space-efficient but "
                "slightly more complex bit operations.",

            CompressionType.ALIGNED:
                "Aligned bit packing that ensures compressed integers never span "
                "across consecutive integers. Faster access but may use more space "
                "due to alignment constraints.",

            CompressionType.OVERFLOW:
                "Overflow bit packing that handles outliers efficiently by storing "
                "large values in a separate overflow area. Optimal for datasets with "
                "mostly small values and few large outliers."
        }

        return descriptions.get(compression_type, "Unknown compression type")


# Convenience function for easy access
def create_compressor(compression_type: Union[str, CompressionType]) -> BitPackingBase:
    """
    Convenience function to create a compressor without instantiating the factory.

    Args:
        compression_type: Type of compression to create

    Returns:
        BitPackingBase: Instance of the requested compression algorithm
    """
    return BitPackingFactory.create_compressor(compression_type)
