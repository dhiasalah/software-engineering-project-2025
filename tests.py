"""
Tests unitaires pour les algorithmes de compression bit packing
Author: [Your Name]

Ce module contient des tests pour valider le bon fonctionnement
des algorithmes de compression implémentés.
"""

import unittest
import random
from factory import BitPackingFactory, CompressionType
from bit_packing import SimpleBitPacking, AlignedBitPacking, OverflowBitPacking


class TestBitPackingAlgorithms(unittest.TestCase):
    """Tests pour tous les algorithmes de bit packing"""

    def setUp(self):
        """Préparer les données de test"""
        self.test_cases = [
            [],  # Cas vide
            [0],  # Un seul élément
            [1, 2, 3, 4, 5],  # Petites valeurs
            [1, 2, 3, 1024, 4, 5, 2048, 6],  # Avec valeurs aberrantes
            [2**i for i in range(10)],  # Puissances de 2
            [random.randint(0, 1000) for _ in range(100)],  # Données aléatoires
        ]

    def test_simple_compression(self):
        """Tester la compression simple"""
        compressor = SimpleBitPacking()

        for test_data in self.test_cases:
            with self.subTest(data=test_data):
                # Test compression/décompression
                compressed = compressor.compress(test_data.copy())
                decompressed = compressor.decompress(compressed.copy())

                self.assertEqual(decompressed, test_data,
                               f"Échec compression/décompression pour {test_data}")

                # Test accès direct
                if test_data:
                    for i in range(len(test_data)):
                        self.assertEqual(compressor.get(i), test_data[i],
                                       f"Échec accès direct à l'index {i}")

    def test_aligned_compression(self):
        """Tester la compression alignée"""
        compressor = AlignedBitPacking()

        for test_data in self.test_cases:
            with self.subTest(data=test_data):
                compressed = compressor.compress(test_data.copy())
                decompressed = compressor.decompress(compressed.copy())

                self.assertEqual(decompressed, test_data)

                if test_data:
                    for i in range(len(test_data)):
                        self.assertEqual(compressor.get(i), test_data[i])

    def test_overflow_compression(self):
        """Tester la compression avec débordement"""
        compressor = OverflowBitPacking()

        for test_data in self.test_cases:
            with self.subTest(data=test_data):
                compressed = compressor.compress(test_data.copy())
                decompressed = compressor.decompress(compressed.copy())

                self.assertEqual(decompressed, test_data)

                if test_data:
                    for i in range(len(test_data)):
                        self.assertEqual(compressor.get(i), test_data[i])

    def test_factory_creation(self):
        """Tester la création via factory"""
        for comp_type in CompressionType:
            compressor = BitPackingFactory.create_compressor(comp_type)
            self.assertIsNotNone(compressor)

            # Test avec des données simples
            test_data = [1, 2, 3, 4, 5]
            compressed = compressor.compress(test_data.copy())
            decompressed = compressor.decompress(compressed.copy())
            self.assertEqual(decompressed, test_data)

    def test_compression_ratios(self):
        """Tester les ratios de compression"""
        test_data = [random.randint(0, 100) for _ in range(1000)]

        for comp_type in CompressionType:
            compressor = BitPackingFactory.create_compressor(comp_type)
            compressed = compressor.compress(test_data.copy())

            original_size = len(test_data) * 32
            compressed_size = len(compressed) * 32
            ratio = original_size / compressed_size if compressed_size > 0 else 0

            # La compression devrait être efficace pour des petites valeurs
            self.assertGreater(ratio, 1.0, f"Pas de compression pour {comp_type.value}")

    def test_edge_cases(self):
        """Tester les cas limites"""
        compressors = [
            BitPackingFactory.create_compressor(CompressionType.SIMPLE),
            BitPackingFactory.create_compressor(CompressionType.ALIGNED),
            BitPackingFactory.create_compressor(CompressionType.OVERFLOW)
        ]

        # Test avec une seule grande valeur
        test_data = [2**30]
        for compressor in compressors:
            compressed = compressor.compress(test_data.copy())
            decompressed = compressor.decompress(compressed.copy())
            self.assertEqual(decompressed, test_data)
            self.assertEqual(compressor.get(0), test_data[0])

        # Test avec toutes les valeurs identiques
        test_data = [42] * 100
        for compressor in compressors:
            compressed = compressor.compress(test_data.copy())
            decompressed = compressor.decompress(compressed.copy())
            self.assertEqual(decompressed, test_data)

    def test_index_errors(self):
        """Tester les erreurs d'index"""
        test_data = [1, 2, 3, 4, 5]

        for comp_type in CompressionType:
            compressor = BitPackingFactory.create_compressor(comp_type)
            compressor.compress(test_data.copy())

            # Test index valide
            self.assertEqual(compressor.get(0), 1)
            self.assertEqual(compressor.get(4), 5)

            # Test index invalide
            with self.assertRaises(IndexError):
                compressor.get(5)
            with self.assertRaises(IndexError):
                compressor.get(-1)


class TestSpecificAlgorithms(unittest.TestCase):
    """Tests spécifiques pour chaque algorithme"""

    def test_simple_vs_aligned(self):
        """Comparer Simple vs Aligned pour des données spécifiques"""
        # Données qui devraient favoriser Simple (utilisation optimale de l'espace)
        test_data = [random.randint(0, 7) for _ in range(1000)]  # 3 bits par élément

        simple = SimpleBitPacking()
        aligned = AlignedBitPacking()

        simple_compressed = simple.compress(test_data.copy())
        aligned_compressed = aligned.compress(test_data.copy())

        # Simple devrait être plus efficace ou égal
        self.assertLessEqual(len(simple_compressed), len(aligned_compressed))

    def test_overflow_efficiency(self):
        """Tester l'efficacité de la compression overflow"""
        # Créer des données avec beaucoup de petites valeurs et quelques grandes
        small_values = [random.randint(0, 15) for _ in range(950)]
        large_values = [random.randint(10000, 100000) for _ in range(50)]
        test_data = small_values + large_values
        random.shuffle(test_data)

        simple = SimpleBitPacking()
        overflow = OverflowBitPacking()

        simple_compressed = simple.compress(test_data.copy())
        overflow_compressed = overflow.compress(test_data.copy())

        # Overflow devrait être plus efficace pour ce type de données
        print(f"Simple: {len(simple_compressed)} entiers")
        print(f"Overflow: {len(overflow_compressed)} entiers")

        # Vérifier que les résultats sont corrects
        simple_decompressed = simple.decompress(simple_compressed.copy())
        overflow_decompressed = overflow.decompress(overflow_compressed.copy())

        self.assertEqual(simple_decompressed, test_data)
        self.assertEqual(overflow_decompressed, test_data)


def run_tests():
    """Exécuter tous les tests"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
