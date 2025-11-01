#!/usr/bin/env python3
"""Test to verify negative numbers extraction after compression"""

from bit_packing import OffsetBitPacking, ZigZagBitPacking, SignSeparationBitPacking

def test_offset_extraction():
    print("=" * 70)
    print("Testing OffsetBitPacking - Extraction of Negative Numbers")
    print("=" * 70)

    # Test data with negative numbers
    data = [-10, -5, 0, 5, 10, 15, -20, 100]
    print(f"Original data: {data}")

    compressor = OffsetBitPacking()
    compressed = compressor.compress(data.copy())
    print(f"Compressed successfully (size: {len(compressed)} integers)")

    # Test decompression
    decompressed = compressor.decompress(compressed)
    print(f"Decompressed data: {decompressed}")
    match = data == decompressed
    print(f"Decompression integrity: {'✓ PASS' if match else '✗ FAIL'}")

    # Test random access (extraction)
    print("\nTesting random access (extraction):")
    all_pass = True
    for i in range(len(data)):
        value = compressor.get(i)
        expected = data[i]
        status = "✓" if value == expected else "✗"
        if value != expected:
            all_pass = False
        print(f"  Index {i}: Got {value:4d}, Expected {expected:4d} {status}")

    print(f"\nRandom access: {'✓ ALL PASS' if all_pass else '✗ SOME FAILED'}")
    print()

def test_zigzag_extraction():
    print("=" * 70)
    print("Testing ZigZagBitPacking - Extraction of Negative Numbers")
    print("=" * 70)

    data = [-10, -5, 0, 5, 10, 15, -20, 100]
    print(f"Original data: {data}")

    compressor = ZigZagBitPacking()
    compressed = compressor.compress(data.copy())
    print(f"Compressed successfully (size: {len(compressed)} integers)")

    decompressed = compressor.decompress(compressed)
    print(f"Decompressed data: {decompressed}")
    match = data == decompressed
    print(f"Decompression integrity: {'✓ PASS' if match else '✗ FAIL'}")

    print("\nTesting random access (extraction):")
    all_pass = True
    for i in range(len(data)):
        value = compressor.get(i)
        expected = data[i]
        status = "✓" if value == expected else "✗"
        if value != expected:
            all_pass = False
        print(f"  Index {i}: Got {value:4d}, Expected {expected:4d} {status}")

    print(f"\nRandom access: {'✓ ALL PASS' if all_pass else '✗ SOME FAILED'}")
    print()

def test_sign_separation_extraction():
    print("=" * 70)
    print("Testing SignSeparationBitPacking - Extraction of Negative Numbers")
    print("=" * 70)

    data = [-10, -5, 0, 5, 10, 15, -20, 100]
    print(f"Original data: {data}")

    compressor = SignSeparationBitPacking()
    compressed = compressor.compress(data.copy())
    print(f"Compressed successfully (size: {len(compressed)} integers)")

    decompressed = compressor.decompress(compressed)
    print(f"Decompressed data: {decompressed}")
    match = data == decompressed
    print(f"Decompression integrity: {'✓ PASS' if match else '✗ FAIL'}")

    print("\nTesting random access (extraction):")
    all_pass = True
    for i in range(len(data)):
        value = compressor.get(i)
        expected = data[i]
        status = "✓" if value == expected else "✗"
        if value != expected:
            all_pass = False
        print(f"  Index {i}: Got {value:4d}, Expected {expected:4d} {status}")

    print(f"\nRandom access: {'✓ ALL PASS' if all_pass else '✗ SOME FAILED'}")
    print()

if __name__ == "__main__":
    try:
        test_offset_extraction()
        test_zigzag_extraction()
        test_sign_separation_extraction()
        print("=" * 70)
        print("All tests completed!")
        print("=" * 70)
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

