"""
Main entry point for the Bit Packing Compression Project
Author: [Your Name]

This is the main interface for testing and using the bit packing compression algorithms.
It provides both a command-line interface and programmatic examples.
"""

import sys
import argparse
from typing import List
from factory import BitPackingFactory, CompressionType
from benchmark import BenchmarkSuite, DataGenerator, run_default_benchmarks


def demonstrate_algorithms():
    """Demonstrate all three compression algorithms with example data"""

    print("=== BIT PACKING COMPRESSION DEMONSTRATION ===\n")

    # Example data with different characteristics
    examples = {
        "Small values": [1, 2, 3, 4, 5, 6, 7, 8],
        "Mixed values": [1, 2, 3, 1024, 4, 5, 2048, 6],
        "Power of 2": [1, 2, 4, 8, 16, 32, 64, 128]
    }

    for example_name, data in examples.items():
        print(f"Example: {example_name}")
        print(f"Original data: {data}")
        print(f"Data size: {len(data)} integers = {len(data) * 32} bits = {len(data) * 4} bytes\n")

        # Test each algorithm
        for comp_type in CompressionType:
            compressor = BitPackingFactory.create_compressor(comp_type)

            # Compress
            compressed = compressor.compress(data.copy())

            # Decompress to verify
            decompressed = compressor.decompress(compressed.copy())

            # Test random access
            test_index = len(data) // 2
            direct_value = compressor.get(test_index)

            # Calculate compression ratio
            original_size = len(data) * 32
            compressed_size = len(compressed) * 32
            ratio = original_size / compressed_size if compressed_size > 0 else 0

            print(f"  {comp_type.value.capitalize()} Compression:")
            print(f"    Compressed size: {len(compressed)} integers = {compressed_size} bits = {compressed_size // 8} bytes")
            print(f"    Compression ratio: {ratio:.2f}x")
            print(f"    Verification: {'✓ PASS' if decompressed == data else '✗ FAIL'}")
            print(f"    Random access test (index {test_index}): {direct_value} {'✓' if direct_value == data[test_index] else '✗'}")

            if comp_type == CompressionType.OVERFLOW and hasattr(compressor, 'overflow_data'):
                print(f"    Overflow values: {compressor.overflow_data}")

            print()

        print("-" * 60 + "\n")


def interactive_mode():
    """Interactive mode for testing custom data"""

    print("=== INTERACTIVE MODE ===")
    print("Enter integers separated by spaces (or 'quit' to exit):")

    while True:
        try:
            user_input = input("\nData: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            # Parse input
            data = [int(x) for x in user_input.split()]

            if not data:
                print("Please enter at least one integer.")
                continue

            print(f"\nTesting with data: {data}")

            # Ask for compression type
            print("Available compression types:")
            for i, comp_type in enumerate(CompressionType, 1):
                description = BitPackingFactory.get_description(comp_type)
                print(f"{i}. {comp_type.value.capitalize()}: {description[:80]}...")

            choice = input("Choose compression type (1-3): ").strip()

            try:
                comp_types = list(CompressionType)
                comp_type = comp_types[int(choice) - 1]
            except (ValueError, IndexError):
                print("Invalid choice. Using Simple compression.")
                comp_type = CompressionType.SIMPLE

            # Test the chosen algorithm
            compressor = BitPackingFactory.create_compressor(comp_type)
            compressed = compressor.compress(data.copy())
            decompressed = compressor.decompress(compressed.copy())

            print(f"\nResults for {comp_type.value.capitalize()} compression:")
            print(f"Original: {data}")
            print(f"Compressed size: {len(compressed)} integers")
            print(f"Decompressed: {decompressed}")
            print(f"Verification: {'✓ PASS' if decompressed == data else '✗ FAIL'}")

            # Show compression details
            original_bits = len(data) * 32
            compressed_bits = len(compressed) * 32
            ratio = original_bits / compressed_bits if compressed_bits > 0 else 0
            print(f"Compression ratio: {ratio:.2f}x")
            print(f"Space saved: {original_bits - compressed_bits} bits ({(original_bits - compressed_bits) / 8:.1f} bytes)")

        except ValueError:
            print("Please enter valid integers.")
        except KeyboardInterrupt:
            break

    print("\nExiting interactive mode.")


def run_benchmarks():
    """Run comprehensive benchmarks"""

    print("=== RUNNING COMPREHENSIVE BENCHMARKS ===")
    print("This may take a few minutes...\n")

    # Run benchmarks
    results = run_default_benchmarks()

    # Generate and display report
    benchmark_suite = BenchmarkSuite()
    report = benchmark_suite.generate_report(results)
    print(report)

    # Save to file
    with open("benchmark_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    print("Detailed report saved to 'benchmark_report.txt'")


def run_custom_benchmark():
    """Run benchmark on custom data"""

    print("=== CUSTOM BENCHMARK ===")

    try:
        size = int(input("Enter data size: "))
        max_value = int(input("Enter maximum value: "))

        print("Data generation options:")
        print("1. Uniform distribution")
        print("2. Power law distribution (many small, few large)")
        print("3. With outliers")
        print("4. Sequential")

        choice = input("Choose option (1-4): ").strip()

        if choice == "1":
            data = DataGenerator.generate_uniform(size, max_value)
            data_name = f"Uniform({size}, max={max_value})"
        elif choice == "2":
            data = DataGenerator.generate_power_law(size, max_value)
            data_name = f"PowerLaw({size}, max={max_value})"
        elif choice == "3":
            outlier_value = int(input("Enter outlier value: "))
            data = DataGenerator.generate_with_outliers(size, max_value, outlier_value)
            data_name = f"WithOutliers({size}, max={max_value}, outlier={outlier_value})"
        elif choice == "4":
            data = DataGenerator.generate_sequential(size)
            data_name = f"Sequential({size})"
        else:
            print("Invalid choice. Using uniform distribution.")
            data = DataGenerator.generate_uniform(size, max_value)
            data_name = f"Uniform({size}, max={max_value})"

        print(f"\nGenerated {data_name}")
        print(f"Sample data: {data[:10]}{'...' if len(data) > 10 else ''}")

        # Run benchmark
        datasets = {data_name: data}
        benchmark_suite = BenchmarkSuite(num_iterations=20)
        results = benchmark_suite.run_comprehensive_benchmark(datasets)

        # Display results
        report = benchmark_suite.generate_report(results)
        print(report)

    except ValueError:
        print("Invalid input. Please enter valid numbers.")
    except KeyboardInterrupt:
        print("\nBenchmark cancelled.")


def main():
    """Main function with command-line interface"""

    parser = argparse.ArgumentParser(
        description="Bit Packing Compression - Data Compression for Speed Up Transmission",
        epilog="Examples:\n"
               "  python main.py --demo                 # Run demonstration\n"
               "  python main.py --interactive          # Interactive testing\n"
               "  python main.py --benchmark            # Run full benchmarks\n"
               "  python main.py --custom-benchmark     # Custom benchmark\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--demo", action="store_true",
                       help="Run algorithm demonstration")
    parser.add_argument("--interactive", action="store_true",
                       help="Start interactive mode")
    parser.add_argument("--benchmark", action="store_true",
                       help="Run comprehensive benchmarks")
    parser.add_argument("--custom-benchmark", action="store_true",
                       help="Run custom benchmark")
    parser.add_argument("--list-algorithms", action="store_true",
                       help="List available compression algorithms")

    args = parser.parse_args()

    # If no arguments provided, show help and run demo
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "="*60)
        print("Running demonstration since no arguments were provided...")
        print("="*60 + "\n")
        demonstrate_algorithms()
        return

    # Handle arguments
    if args.list_algorithms:
        print("Available Compression Algorithms:")
        for comp_type in CompressionType:
            description = BitPackingFactory.get_description(comp_type)
            print(f"\n{comp_type.value.upper()}:")
            print(f"  {description}")

    if args.demo:
        demonstrate_algorithms()

    if args.interactive:
        interactive_mode()

    if args.benchmark:
        run_benchmarks()

    if args.custom_benchmark:
        run_custom_benchmark()


if __name__ == "__main__":
    main()
