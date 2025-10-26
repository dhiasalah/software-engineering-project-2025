"""
Tests unitaires pour les algorithmes de compression bit packing
Author: BEN SALAH Mohamed Dhia

Ce module contient des tests pour valider le bon fonctionnement
des algorithmes de compression implémentés. Il vérifie la
correction, l'intégrité des données, et les cas limites.
"""

import unittest
import random
from factory import BitPackingFactory, CompressionType
from bit_packing import SimpleBitPacking, AlignedBitPacking, OverflowBitPacking


class TestBitPackingAlgorithms(unittest.TestCase):
    """Tests pour tous les algorithmes de bit packing"""

    def setUp(self):
        """Préparer les données de test avec différents scénarios"""
        self.test_cases = [
            [],  # Cas vide - teste la gestion des tableaux vides
            [0],  # Un seul élément - cas minimal
            [1, 2, 3, 4, 5],  # Petites valeurs uniformes
            [1, 2, 3, 1024, 4, 5, 2048, 6],  # Avec valeurs aberrantes (outliers)
            [2**power_index for power_index in range(10)],  # Puissances de 2 - teste différents nombres de bits
            [random.randint(0, 1000) for test_case_index in range(100)],  # Données aléatoires réalistes
        ]

    def test_simple_compression(self):
        """Tester la compression simple (permet le chevauchement entre entiers)"""
        compressor = SimpleBitPacking()

        for test_data in self.test_cases:
            with self.subTest(data=test_data):
                # Test compression/décompression - vérifier que les données sont récupérables
                compressed = compressor.compress(test_data.copy())
                decompressed = compressor.decompress(compressed.copy())

                self.assertEqual(decompressed, test_data,
                               f"Échec compression/décompression pour {test_data}")

                # Test accès direct - vérifier que get() retourne les bonnes valeurs
                if test_data:
                    for element_index in range(len(test_data)):
                        self.assertEqual(compressor.get(element_index), test_data[element_index],
                                       f"Échec accès direct à l'index {element_index}")

    def test_aligned_compression(self):
        """Tester la compression alignée (pas de chevauchement entre entiers)"""
        compressor = AlignedBitPacking()

        for test_data in self.test_cases:
            with self.subTest(data=test_data):
                # Vérifier l'intégrité complète du cycle compression-décompression
                compressed = compressor.compress(test_data.copy())
                decompressed = compressor.decompress(compressed.copy())

                self.assertEqual(decompressed, test_data)

                # Vérifier l'accès direct élément par élément
                if test_data:
                    for element_index in range(len(test_data)):
                        self.assertEqual(compressor.get(element_index), test_data[element_index])

    def test_overflow_compression(self):
        """Tester la compression avec débordement (gère les outliers efficacement)"""
        compressor = OverflowBitPacking()

        for test_data in self.test_cases:
            with self.subTest(data=test_data):
                # Tester avec des données qui peuvent contenir des outliers
                compressed = compressor.compress(test_data.copy())
                decompressed = compressor.decompress(compressed.copy())

                self.assertEqual(decompressed, test_data)

                # Vérifier l'accès direct fonctionne même avec la zone de débordement
                if test_data:
                    for element_index in range(len(test_data)):
                        self.assertEqual(compressor.get(element_index), test_data[element_index])

    def test_factory_creation(self):
        """Tester la création via factory (Design Pattern Factory)"""
        for comp_type in CompressionType:
            compressor = BitPackingFactory.create_compressor(comp_type)
            self.assertIsNotNone(compressor)

            # Test avec des données simples pour vérifier que chaque type fonctionne
            test_data = [1, 2, 3, 4, 5]
            compressed = compressor.compress(test_data.copy())
            decompressed = compressor.decompress(compressed.copy())
            self.assertEqual(decompressed, test_data)

    def test_compression_ratios(self):
        """Tester les ratios de compression - vérifier que la compression est efficace"""
        # Générer des données avec petites valeurs (devraient bien se compresser)
        test_data = [random.randint(0, 100) for _ in range(1000)]

        for comp_type in CompressionType:
            compressor = BitPackingFactory.create_compressor(comp_type)
            compressed = compressor.compress(test_data.copy())

            # Calculer les tailles en bits
            original_size = len(test_data) * 32
            compressed_size = len(compressed) * 32
            ratio = original_size / compressed_size if compressed_size > 0 else 0

            # La compression devrait être efficace pour des petites valeurs
            self.assertGreater(ratio, 1.0, f"Pas de compression pour {comp_type.value}")

    def test_edge_cases(self):
        """Tester les cas limites (edge cases)"""
        compressors = [
            BitPackingFactory.create_compressor(CompressionType.SIMPLE),
            BitPackingFactory.create_compressor(CompressionType.ALIGNED),
            BitPackingFactory.create_compressor(CompressionType.OVERFLOW)
        ]

        # Test avec une seule grande valeur (utilise beaucoup de bits)
        test_data = [2**30]
        for compressor in compressors:
            compressed = compressor.compress(test_data.copy())
            decompressed = compressor.decompress(compressed.copy())
            self.assertEqual(decompressed, test_data)
            self.assertEqual(compressor.get(0), test_data[0])

        # Test avec toutes les valeurs identiques (compression optimale)
        test_data = [42] * 100
        for compressor in compressors:
            compressed = compressor.compress(test_data.copy())
            decompressed = compressor.decompress(compressed.copy())
            self.assertEqual(decompressed, test_data)

    def test_index_errors(self):
        """Tester les erreurs d'index - vérifier la gestion des index invalides"""
        test_data = [1, 2, 3, 4, 5]

        for comp_type in CompressionType:
            compressor = BitPackingFactory.create_compressor(comp_type)
            compressor.compress(test_data.copy())

            # Test index valides (devraient fonctionner)
            self.assertEqual(compressor.get(0), 1)
            self.assertEqual(compressor.get(4), 5)

            # Test index invalides (devraient lever IndexError)
            with self.assertRaises(IndexError):
                compressor.get(5)  # Au-delà de la fin
            with self.assertRaises(IndexError):
                compressor.get(-1)  # Index négatif


class TestSpecificAlgorithms(unittest.TestCase):
    """Tests spécifiques pour comparer les algorithmes entre eux"""

    def test_simple_vs_aligned(self):
        """Comparer Simple vs Aligned - Simple devrait être plus compact"""
        # Données qui nécessitent 3 bits par élément
        test_data = [random.randint(0, 7) for _ in range(1000)]

        simple = SimpleBitPacking()
        aligned = AlignedBitPacking()

        simple_compressed = simple.compress(test_data.copy())
        aligned_compressed = aligned.compress(test_data.copy())

        # Simple devrait être plus efficace ou égal (peut chevaucher)
        self.assertLessEqual(len(simple_compressed), len(aligned_compressed))

    def test_overflow_efficiency(self):
        """Tester l'efficacité de la compression overflow avec beaucoup de petites valeurs"""
        # Créer des données avec 95% de petites valeurs et 5% de grandes valeurs
        small_values = [random.randint(0, 15) for _ in range(950)]
        large_values = [random.randint(10000, 100000) for _ in range(50)]
        test_data = small_values + large_values
        random.shuffle(test_data)  # Mélanger pour simuler des données réalistes

        simple = SimpleBitPacking()
        overflow = OverflowBitPacking()

        simple_compressed = simple.compress(test_data.copy())
        overflow_compressed = overflow.compress(test_data.copy())

        # Afficher les résultats pour le débogage
        print(f"Simple: {len(simple_compressed)} entiers")
        print(f"Overflow: {len(overflow_compressed)} entiers")

        # Vérifier que les deux algorithmes produisent les bonnes données
        simple_decompressed = simple.decompress(simple_compressed.copy())
        overflow_decompressed = overflow.decompress(overflow_compressed.copy())

        self.assertEqual(simple_decompressed, test_data)
        self.assertEqual(overflow_decompressed, test_data)


def run_tests():
    """Exécuter tous les tests avec verbosité pour voir les détails"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
