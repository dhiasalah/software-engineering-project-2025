"""
Benchmarking module for bit packing compression algorithms.
Author: [Your Name]

This module provides comprehensive benchmarking capabilities to measure
the performance of different compression algorithms and calculate optimal
transmission thresholds.
"""

import time
import statistics
import random
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from bit_packing import BitPackingBase
from factory import BitPackingFactory, CompressionType


@dataclass
class BenchmarkResult:
    """Data class to store benchmark results"""
    compression_time: float
    decompression_time: float
    get_time: float
    compression_ratio: float
    original_size_bits: int
    compressed_size_bits: int
    algorithm_name: str


class DataGenerator:
    """Utility class for generating test datasets with different characteristics"""

    @staticmethod
    def generate_uniform(size: int, max_value: int) -> List[int]:
        """Generate uniformly distributed random integers"""
        return [random.randint(0, max_value) for _ in range(size)]

    @staticmethod
    def generate_power_law(size: int, max_value: int, alpha: float = 2.0) -> List[int]:
        """Generate power-law distributed integers (many small, few large)"""
        data = []
        for _ in range(size):
            # Generate power-law distributed value
            u = random.random()
            value = int((1 - u) ** (-1 / (alpha - 1)) * 10)
            value = min(value, max_value)
            data.append(value)
        return data

    @staticmethod
    def generate_with_outliers(size: int, normal_max: int, outlier_value: int, outlier_ratio: float = 0.05) -> List[int]:
        """Generate data with outliers (good for testing overflow compression)"""
        data = []
        num_outliers = int(size * outlier_ratio)

        for i in range(size):
            if i < num_outliers:
                data.append(outlier_value)
            else:
                data.append(random.randint(0, normal_max))

        random.shuffle(data)
        return data

    @staticmethod
    def generate_sequential(size: int, start: int = 0) -> List[int]:
        """Generate sequential integers"""
        return list(range(start, start + size))


class BenchmarkSuite:
    """Comprehensive benchmarking suite for bit packing algorithms"""

    def __init__(self, num_iterations: int = 100):
        """
        Initialize benchmark suite.

        Args:
            num_iterations: Number of iterations for timing measurements
        """
        self.num_iterations = num_iterations
        self.results: Dict[str, List[BenchmarkResult]] = {}

    def benchmark_algorithm(self,
                          algorithm: BitPackingBase,
                          data: List[int],
                          algorithm_name: str) -> BenchmarkResult:
        """
        Benchmark a single algorithm on given data.

        Args:
            algorithm: The compression algorithm to test
            data: Test data
            algorithm_name: Name for reporting

        Returns:
            BenchmarkResult: Comprehensive benchmark results
        """

        # Measure compression time
        compression_times = []
        for _ in range(self.num_iterations):
            start_time = time.perf_counter()
            compressed = algorithm.compress(data.copy())
            end_time = time.perf_counter()
            compression_times.append(end_time - start_time)

        # Use the last compression for further tests
        compressed = algorithm.compress(data.copy())

        # Measure decompression time
        decompression_times = []
        for _ in range(self.num_iterations):
            start_time = time.perf_counter()
            decompressed = algorithm.decompress(compressed.copy())
            end_time = time.perf_counter()
            decompression_times.append(end_time - start_time)

        # Measure random access time (get operation)
        get_times = []
        test_indices = [random.randint(0, len(data) - 1) for _ in range(min(100, len(data)))]

        for _ in range(self.num_iterations // 10):  # Less iterations for get operations
            start_time = time.perf_counter()
            for idx in test_indices:
                _ = algorithm.get(idx)
            end_time = time.perf_counter()
            get_times.append((end_time - start_time) / len(test_indices))

        # Calculate compression metrics
        original_size_bits = len(data) * 32  # Assuming 32-bit integers
        compressed_size_bits = len(compressed) * 32
        compression_ratio = original_size_bits / compressed_size_bits if compressed_size_bits > 0 else 0

        return BenchmarkResult(
            compression_time=statistics.mean(compression_times),
            decompression_time=statistics.mean(decompression_times),
            get_time=statistics.mean(get_times),
            compression_ratio=compression_ratio,
            original_size_bits=original_size_bits,
            compressed_size_bits=compressed_size_bits,
            algorithm_name=algorithm_name
        )

    def run_comprehensive_benchmark(self, datasets: Dict[str, List[int]]) -> Dict[str, Dict[str, BenchmarkResult]]:
        """
        Run comprehensive benchmarks on multiple datasets and algorithms.

        Args:
            datasets: Dictionary mapping dataset names to data arrays

        Returns:
            Dict: Nested dictionary with results [dataset][algorithm] = BenchmarkResult
        """

        results = {}
        algorithms = {
            "Simple": BitPackingFactory.create_compressor(CompressionType.SIMPLE),
            "Aligned": BitPackingFactory.create_compressor(CompressionType.ALIGNED),
            "Overflow": BitPackingFactory.create_compressor(CompressionType.OVERFLOW)
        }

        for dataset_name, data in datasets.items():
            print(f"Benchmarking dataset: {dataset_name} (size: {len(data)})")
            results[dataset_name] = {}

            for algo_name, algorithm in algorithms.items():
                print(f"  Testing {algo_name} algorithm...")
                try:
                    result = self.benchmark_algorithm(algorithm, data, algo_name)
                    results[dataset_name][algo_name] = result
                    print(f"    Compression ratio: {result.compression_ratio:.2f}")
                except Exception as e:
                    print(f"    Error testing {algo_name}: {e}")

        return results

    def calculate_transmission_threshold(self,
                                       benchmark_result: BenchmarkResult,
                                       transmission_speed_mbps: float) -> float:
        """
        Calculate the latency threshold where compression becomes worthwhile.

        Args:
            benchmark_result: Results from benchmarking
            transmission_speed_mbps: Transmission speed in Mbps

        Returns:
            float: Latency threshold in seconds
        """

        # Convert transmission speed to bits per second
        transmission_speed_bps = transmission_speed_mbps * 1_000_000

        # Calculate transmission times
        original_transmission_time = benchmark_result.original_size_bits / transmission_speed_bps
        compressed_transmission_time = benchmark_result.compressed_size_bits / transmission_speed_bps

        # Calculate processing overhead
        processing_overhead = benchmark_result.compression_time + benchmark_result.decompression_time

        # Calculate time saved by compression
        time_saved = original_transmission_time - compressed_transmission_time

        # Threshold latency where compression becomes beneficial
        # If processing_overhead > time_saved, compression is not beneficial at any latency
        if time_saved <= processing_overhead:
            return float('inf')  # Never beneficial

        # Return the latency where benefits start
        return processing_overhead / (time_saved - processing_overhead) if time_saved > processing_overhead else 0

    def generate_report(self, results: Dict[str, Dict[str, BenchmarkResult]]) -> str:
        """
        Generate a comprehensive benchmark report.

        Args:
            results: Benchmark results from run_comprehensive_benchmark

        Returns:
            str: Formatted report
        """

        report = []
        report.append("=== BIT PACKING COMPRESSION BENCHMARK REPORT ===\n")

        for dataset_name, dataset_results in results.items():
            report.append(f"Dataset: {dataset_name}")
            report.append("-" * 50)

            # Sort algorithms by compression ratio
            sorted_results = sorted(dataset_results.items(),
                                  key=lambda x: x[1].compression_ratio,
                                  reverse=True)

            for algo_name, result in sorted_results:
                report.append(f"\nAlgorithm: {algo_name}")
                report.append(f"  Compression Ratio: {result.compression_ratio:.3f}x")
                report.append(f"  Compression Time: {result.compression_time*1000:.3f} ms")
                report.append(f"  Decompression Time: {result.decompression_time*1000:.3f} ms")
                report.append(f"  Random Access Time: {result.get_time*1000000:.3f} μs")
                report.append(f"  Original Size: {result.original_size_bits/8:.0f} bytes")
                report.append(f"  Compressed Size: {result.compressed_size_bits/8:.0f} bytes")

                # Calculate transmission thresholds for different speeds
                for speed in [1, 10, 100, 1000]:  # Mbps
                    threshold = self.calculate_transmission_threshold(result, speed)
                    if threshold == float('inf'):
                        report.append(f"  Threshold at {speed} Mbps: Never beneficial")
                    else:
                        report.append(f"  Threshold at {speed} Mbps: {threshold*1000:.3f} ms latency")

            report.append("\n" + "="*70 + "\n")

        return "\n".join(report)


def run_default_benchmarks() -> Dict[str, Dict[str, BenchmarkResult]]:
    """
    Run a set of default benchmarks with various data patterns.

    Returns:
        Dict: Benchmark results
    """

    print("Generating test datasets...")

    # Generate test datasets
    datasets = {
        "Small Uniform (1K)": DataGenerator.generate_uniform(1000, 1000),
        "Large Uniform (10K)": DataGenerator.generate_uniform(10000, 1000),
        "Power Law": DataGenerator.generate_power_law(5000, 10000),
        "With Outliers": DataGenerator.generate_with_outliers(5000, 100, 100000),
        "Sequential": DataGenerator.generate_sequential(5000),
        "Mixed Small": DataGenerator.generate_uniform(10000, 15),  # Good for alignment
    }

    # Run benchmarks
    benchmark_suite = BenchmarkSuite(num_iterations=50)
    results = benchmark_suite.run_comprehensive_benchmark(datasets)

    return results


if __name__ == "__main__":
    # Run default benchmarks if script is executed directly
    results = run_default_benchmarks()

    benchmark_suite = BenchmarkSuite()
    report = benchmark_suite.generate_report(results)
    print(report)

    # Save report to file
    with open("benchmark_report.txt", "w") as f:
        f.write(report)
