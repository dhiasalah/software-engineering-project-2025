"""
Module de benchmarking pour les algorithmes de compression bit packing
Author: BEN SALAH Mohamed Dhia

Ce module fournit des capacités de benchmarking complètes pour mesurer
les performances des différents algorithmes de compression et calculer les
seuils de transmission optimaux où la compression devient avantageuse.
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
    """Classe de données pour stocker les résultats de benchmark"""
    compression_time: float  # Temps moyen de compression en secondes
    decompression_time: float  # Temps moyen de décompression en secondes
    get_time: float  # Temps moyen d'accès direct en secondes
    compression_ratio: float  # Ratio de compression (taille_originale / taille_compressée)
    original_size_bits: int  # Taille originale en bits
    compressed_size_bits: int  # Taille compressée en bits
    algorithm_name: str  # Nom de l'algorithme testé


class DataGenerator:
    """Classe utilitaire pour générer des jeux de données de test avec différentes caractéristiques"""

    @staticmethod
    def generate_uniform(size: int, max_value: int) -> List[int]:
        """
        Génère des entiers distribués uniformément.

        Args:
            size: Nombre d'éléments à générer
            max_value: Valeur maximale (inclusive)

        Returns:
            List[int]: Liste d'entiers aléatoires uniformément distribués
        """
        return [random.randint(0, max_value) for _ in range(size)]

    @staticmethod
    def generate_power_law(size: int, max_value: int, alpha: float = 2.0) -> List[int]:
        """
        Génère des entiers suivant une distribution en loi de puissance.
        Simule des données réelles où beaucoup de petites valeurs et peu de grandes.

        Args:
            size: Nombre d'éléments à générer
            max_value: Valeur maximale (inclusive)
            alpha: Exposant de la loi de puissance (>1, typiquement 2.0)

        Returns:
            List[int]: Liste d'entiers suivant une loi de puissance
        """
        data = []
        for _ in range(size):
            # Générer une valeur suivant une loi de puissance
            u = random.random()
            value = int((1 - u) ** (-1 / (alpha - 1)) * 10)
            value = min(value, max_value)  # Limiter à max_value
            data.append(value)
        return data

    @staticmethod
    def generate_with_outliers(size: int, normal_max: int, outlier_value: int, outlier_ratio: float = 0.05) -> List[int]:
        """
        Génère des données avec des outliers (valeurs aberrantes).
        Utile pour tester la compression overflow.

        Args:
            size: Nombre total d'éléments
            normal_max: Valeur max pour les valeurs normales
            outlier_value: Valeur des outliers (typiquement beaucoup plus grande)
            outlier_ratio: Proportion d'outliers (0.05 = 5%)

        Returns:
            List[int]: Liste avec majoritairement des petites valeurs et quelques outliers
        """
        data = []
        num_outliers = int(size * outlier_ratio)

        # Générer les outliers et les valeurs normales
        for i in range(size):
            if i < num_outliers:
                data.append(outlier_value)
            else:
                data.append(random.randint(0, normal_max))

        # Mélanger pour distribuer les outliers aléatoirement
        random.shuffle(data)
        return data

    @staticmethod
    def generate_sequential(size: int, start: int = 0) -> List[int]:
        """
        Génère des entiers séquentiels.

        Args:
            size: Nombre d'éléments
            start: Valeur de départ

        Returns:
            List[int]: Liste séquentielle [start, start+1, start+2, ...]
        """
        return list(range(start, start + size))


class BenchmarkSuite:
    """Suite de benchmarking complète pour les algorithmes bit packing"""

    def __init__(self, num_iterations: int = 100):
        """
        Initialise la suite de benchmark.

        Args:
            num_iterations: Nombre d'itérations pour les mesures de timing
                           (plus élevé = plus précis mais plus lent)
        """
        self.num_iterations = num_iterations
        self.results: Dict[str, List[BenchmarkResult]] = {}

    def benchmark_algorithm(self,
                          algorithm: BitPackingBase,
                          data: List[int],
                          algorithm_name: str) -> BenchmarkResult:
        """
        Benchmark un seul algorithme sur des données données.
        Mesure les temps de compression, décompression et accès direct.

        Args:
            algorithm: L'algorithme de compression à tester
            data: Données de test
            algorithm_name: Nom pour les rapports

        Returns:
            BenchmarkResult: Résultats complets du benchmark
        """
        # Mesurer le temps de compression sur plusieurs itérations
        compression_times = []
        for _ in range(self.num_iterations):
            start_time = time.perf_counter()
            compressed = algorithm.compress(data.copy())
            end_time = time.perf_counter()
            compression_times.append(end_time - start_time)

        # Utiliser la dernière compression pour les tests suivants
        compressed = algorithm.compress(data.copy())

        # Mesurer le temps de décompression
        decompression_times = []
        for _ in range(self.num_iterations):
            start_time = time.perf_counter()
            decompressed = algorithm.decompress(compressed.copy())
            end_time = time.perf_counter()
            decompression_times.append(end_time - start_time)

        # Mesurer le temps d'accès aléatoire (opération get)
        get_times = []
        # Préparer des indices de test aléatoires
        test_indices = [random.randint(0, len(data) - 1) for _ in range(min(100, len(data)))]

        # Mesurer avec moins d'itérations car get() est rapide
        for _ in range(self.num_iterations // 10):
            start_time = time.perf_counter()
            for idx in test_indices:
                _ = algorithm.get(idx)
            end_time = time.perf_counter()
            # Diviser par le nombre d'accès pour obtenir le temps moyen par accès
            get_times.append((end_time - start_time) / len(test_indices))

        # Calculer les métriques de compression
        original_size_bits = len(data) * 32  # En assumant des entiers 32-bit
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
        Exécute des benchmarks complets sur plusieurs jeux de données et algorithmes.

        Args:
            datasets: Dictionnaire mappant noms de datasets -> tableaux de données

        Returns:
            Dict: Dictionnaire imbriqué avec résultats [dataset][algorithme] = BenchmarkResult
        """
        results = {}
        # Créer les trois algorithmes à tester
        algorithms = {
            "Simple": BitPackingFactory.create_compressor(CompressionType.SIMPLE),
            "Aligned": BitPackingFactory.create_compressor(CompressionType.ALIGNED),
            "Overflow": BitPackingFactory.create_compressor(CompressionType.OVERFLOW)
        }

        for dataset_name, data in datasets.items():
            print(f"Benchmarking du dataset: {dataset_name} (taille: {len(data)})")
            results[dataset_name] = {}

            for algo_name, algorithm in algorithms.items():
                print(f"  Test de l'algorithme {algo_name}...")
                try:
                    result = self.benchmark_algorithm(algorithm, data, algo_name)
                    results[dataset_name][algo_name] = result
                    print(f"    Ratio de compression: {result.compression_ratio:.2f}")
                except Exception as e:
                    print(f"    Erreur lors du test de {algo_name}: {e}")

        return results

    def calculate_transmission_threshold(self,
                                       benchmark_result: BenchmarkResult,
                                       transmission_speed_mbps: float) -> float:
        """
        Calcule le seuil de latence où la compression devient avantageuse.

        La compression est bénéfique quand:
        temps_transmission_original - temps_transmission_compressée > temps_compression + temps_décompression

        Args:
            benchmark_result: Résultats du benchmarking
            transmission_speed_mbps: Vitesse de transmission en Mbps (mégabits par seconde)

        Returns:
            float: Seuil de latence en secondes (ou inf si jamais bénéfique)
        """
        # Convertir la vitesse de transmission en bits par seconde
        transmission_speed_bps = transmission_speed_mbps * 1_000_000

        # Calculer les temps de transmission
        original_transmission_time = benchmark_result.original_size_bits / transmission_speed_bps
        compressed_transmission_time = benchmark_result.compressed_size_bits / transmission_speed_bps

        # Calculer le surcoût de traitement
        processing_overhead = benchmark_result.compression_time + benchmark_result.decompression_time

        # Calculer le temps économisé par la compression
        time_saved = original_transmission_time - compressed_transmission_time

        # Si le surcoût > temps économisé, la compression n'est jamais bénéfique
        if time_saved <= processing_overhead:
            return float('inf')  # Jamais bénéfique

        # Retourner la latence où les bénéfices commencent
        return processing_overhead / (time_saved - processing_overhead) if time_saved > processing_overhead else 0

    def generate_report(self, results: Dict[str, Dict[str, BenchmarkResult]]) -> str:
        """
        Génère un rapport de benchmark complet et lisible.

        Args:
            results: Résultats de benchmark depuis run_comprehensive_benchmark

        Returns:
            str: Rapport formaté prêt à afficher ou sauvegarder
        """
        report = []
        report.append("=== RAPPORT DE BENCHMARK - COMPRESSION BIT PACKING ===\n")

        for dataset_name, dataset_results in results.items():
            report.append(f"Dataset: {dataset_name}")
            report.append("-" * 50)

            # Trier les algorithmes par ratio de compression (meilleur d'abord)
            sorted_results = sorted(dataset_results.items(),
                                  key=lambda x: x[1].compression_ratio,
                                  reverse=True)

            for algo_name, result in sorted_results:
                report.append(f"\nAlgorithme: {algo_name}")
                report.append(f"  Ratio de compression: {result.compression_ratio:.3f}x")
                report.append(f"  Temps de compression: {result.compression_time*1000:.3f} ms")
                report.append(f"  Temps de décompression: {result.decompression_time*1000:.3f} ms")
                report.append(f"  Temps d'accès aléatoire: {result.get_time*1000000:.3f} μs")
                report.append(f"  Taille originale: {result.original_size_bits/8:.0f} octets")
                report.append(f"  Taille compressée: {result.compressed_size_bits/8:.0f} octets")

                # Calculer les seuils de transmission pour différentes vitesses
                for speed in [1, 10, 100, 1000]:  # Mbps
                    threshold = self.calculate_transmission_threshold(result, speed)
                    if threshold == float('inf'):
                        report.append(f"  Seuil à {speed} Mbps: Jamais bénéfique")
                    else:
                        report.append(f"  Seuil à {speed} Mbps: {threshold*1000:.3f} ms de latence")

            report.append("\n" + "="*70 + "\n")

        return "\n".join(report)


def run_default_benchmarks() -> Dict[str, Dict[str, BenchmarkResult]]:
    """
    Exécute un ensemble de benchmarks par défaut avec différents patterns de données.
    Utile pour tester rapidement les performances sur des cas d'usage typiques.

    Returns:
        Dict: Résultats des benchmarks
    """
    print("Génération des jeux de données de test...")

    # Générer des datasets de test variés
    datasets = {
        "Uniforme Petit (1K)": DataGenerator.generate_uniform(1000, 1000),
        "Uniforme Grand (10K)": DataGenerator.generate_uniform(10000, 1000),
        "Loi de Puissance": DataGenerator.generate_power_law(5000, 10000),
        "Avec Outliers": DataGenerator.generate_with_outliers(5000, 100, 100000),
        "Séquentiel": DataGenerator.generate_sequential(5000),
        "Petites Valeurs": DataGenerator.generate_uniform(10000, 15),  # Bon pour l'alignement
    }

    # Exécuter les benchmarks
    benchmark_suite = BenchmarkSuite(num_iterations=50)
    results = benchmark_suite.run_comprehensive_benchmark(datasets)

    return results


if __name__ == "__main__":
    # Exécuter les benchmarks par défaut si le script est lancé directement
    results = run_default_benchmarks()

    benchmark_suite = BenchmarkSuite()
    report = benchmark_suite.generate_report(results)
    print(report)

    # Sauvegarder le rapport dans un fichier
    with open("benchmark_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
