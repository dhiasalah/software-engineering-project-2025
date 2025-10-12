"""
Main entry point for the Bit Packing Compression Project
Author: BEN SALAH Mohamed Dhia

Ce module est le point d'entrée principal pour tester et utiliser les algorithmes
de compression bit packing. Il offre une interface en ligne de commande et une
interface graphique pour une utilisation interactive.
"""

import sys
import argparse
from typing import List
from factory import BitPackingFactory, CompressionType
from benchmark import BenchmarkSuite, DataGenerator, run_default_benchmarks


def start_gui():
    """Démarre l'interface graphique PyQt5 pour une utilisation interactive"""
    print("=== DÉMARRAGE DE L'INTERFACE GRAPHIQUE ===")
    print("Lancement de l'interface graphique pour tester")
    print("interactivement les algorithmes de compression.")
    print()

    try:
        # Import ici pour éviter les problèmes si PyQt5 n'est pas installé
        import gui_interface
        gui_interface.main()
    except ImportError:
        print("PyQt5 est requis pour lancer l'interface graphique.")
        print("Installez les dépendances avec: pip install -r requirements.txt")
    except Exception as e:
        print(f"Échec du démarrage de l'interface: {e}")


def demonstrate_algorithms():
    """
    Démontre les trois algorithmes de compression avec des exemples.
    Affiche les ratios de compression et vérifie l'intégrité des données.
    """
    print("=== DÉMONSTRATION DES ALGORITHMES DE COMPRESSION BIT PACKING ===\n")

    # Exemples de données avec différentes caractéristiques
    examples = {
        "Petites valeurs": [1, 2, 3, 4, 5, 6, 7, 8],
        "Valeurs mixtes": [1, 2, 3, 1024, 4, 5, 2048, 6],
        "Puissances de 2": [1, 2, 4, 8, 16, 32, 64, 128]
    }

    for example_name, data in examples.items():
        print(f"Exemple: {example_name}")
        print(f"Données originales: {data}")
        print(f"Taille des données: {len(data)} entiers = {len(data) * 32} bits = {len(data) * 4} octets\n")

        # Tester chaque algorithme
        for comp_type in CompressionType:
            compressor = BitPackingFactory.create_compressor(comp_type)

            # Compresser les données
            compressed = compressor.compress(data.copy())

            # Décompresser pour vérifier l'intégrité
            decompressed = compressor.decompress(compressed.copy())

            # Tester l'accès aléatoire (méthode get)
            test_index = len(data) // 2
            direct_value = compressor.get(test_index)

            # Calculer le ratio de compression
            original_size = len(data) * 32
            compressed_size = len(compressed) * 32
            ratio = original_size / compressed_size if compressed_size > 0 else 0

            print(f"  {comp_type.value.capitalize()} Compression:")
            print(f"    Taille compressée: {len(compressed)} entiers = {compressed_size} bits = {compressed_size // 8} octets")
            print(f"    Ratio de compression: {ratio:.2f}x")
            print(f"    Vérification: {'✓ SUCCÈS' if decompressed == data else '✗ ÉCHEC'}")
            print(f"    Test accès aléatoire (index {test_index}): {direct_value} {'✓' if direct_value == data[test_index] else '✗'}")

            # Afficher les valeurs overflow si applicable
            if comp_type == CompressionType.OVERFLOW and hasattr(compressor, 'overflow_data'):
                print(f"    Valeurs en overflow: {compressor.overflow_data}")

            print()

        print("-" * 60 + "\n")


def interactive_mode():
    """
    Mode interactif pour tester avec des données personnalisées.
    Permet à l'utilisateur d'entrer des données et de choisir l'algorithme.
    """
    print("=== MODE INTERACTIF ===")
    print("Entrez des entiers séparés par des espaces (ou 'quit' pour quitter):")

    while True:
        try:
            user_input = input("\nDonnées: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            # Analyser l'entrée utilisateur
            data = [int(x) for x in user_input.split()]

            if not data:
                print("Veuillez entrer au moins un entier.")
                continue

            print(f"\nTest avec les données: {data}")

            # Demander le type de compression
            print("Types de compression disponibles:")
            for i, comp_type in enumerate(CompressionType, 1):
                description = BitPackingFactory.get_description(comp_type)
                print(f"{i}. {comp_type.value.capitalize()}: {description[:80]}...")

            choice = input("Choisissez le type de compression (1-3): ").strip()

            try:
                comp_types = list(CompressionType)
                comp_type = comp_types[int(choice) - 1]
            except (ValueError, IndexError):
                print("Choix invalide. Utilisation de la compression Simple.")
                comp_type = CompressionType.SIMPLE

            # Tester l'algorithme choisi
            compressor = BitPackingFactory.create_compressor(comp_type)
            compressed = compressor.compress(data.copy())
            decompressed = compressor.decompress(compressed.copy())

            print(f"\nRésultats pour la compression {comp_type.value.capitalize()}:")
            print(f"Original: {data}")
            print(f"Taille compressée: {len(compressed)} entiers")
            print(f"Décompressé: {decompressed}")
            print(f"Vérification: {'✓ SUCCÈS' if decompressed == data else '✗ ÉCHEC'}")

            # Afficher les détails de compression
            original_bits = len(data) * 32
            compressed_bits = len(compressed) * 32
            ratio = original_bits / compressed_bits if compressed_bits > 0 else 0
            print(f"Ratio de compression: {ratio:.2f}x")
            print(f"Espace économisé: {original_bits - compressed_bits} bits ({(original_bits - compressed_bits) / 8:.1f} octets)")

        except ValueError:
            print("Veuillez entrer des entiers valides.")
        except KeyboardInterrupt:
            break

    print("\nFermeture du mode interactif.")


def run_benchmarks():
    """
    Exécute des benchmarks complets sur différents types de données.
    Mesure les performances et génère un rapport détaillé.
    """
    print("=== EXÉCUTION DES BENCHMARKS COMPLETS ===")
    print("Cela peut prendre quelques minutes...\n")

    # Exécuter les benchmarks
    results = run_default_benchmarks()

    # Générer et afficher le rapport
    benchmark_suite = BenchmarkSuite()
    report = benchmark_suite.generate_report(results)
    print(report)

    # Sauvegarder dans un fichier
    with open("benchmark_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    print("Rapport détaillé sauvegardé dans 'benchmark_report.txt'")


def run_custom_benchmark():
    """
    Exécute un benchmark sur des données personnalisées.
    Permet à l'utilisateur de spécifier la taille et le type de données.
    """
    print("=== BENCHMARK PERSONNALISÉ ===")

    try:
        size = int(input("Entrez la taille des données: "))
        max_value = int(input("Entrez la valeur maximale: "))

        print("Options de génération de données:")
        print("1. Distribution uniforme")
        print("2. Distribution en loi de puissance (beaucoup de petites, peu de grandes)")
        print("3. Avec outliers (valeurs aberrantes)")
        print("4. Séquentielle")

        choice = input("Choisissez une option (1-4): ").strip()

        # Générer les données selon le choix
        if choice == "1":
            data = DataGenerator.generate_uniform(size, max_value)
            data_name = f"Uniforme({size}, max={max_value})"
        elif choice == "2":
            data = DataGenerator.generate_power_law(size, max_value)
            data_name = f"LoiPuissance({size}, max={max_value})"
        elif choice == "3":
            outlier_value = int(input("Entrez la valeur aberrante: "))
            data = DataGenerator.generate_with_outliers(size, max_value, outlier_value)
            data_name = f"AvecOutliers({size}, max={max_value}, outlier={outlier_value})"
        elif choice == "4":
            data = DataGenerator.generate_sequential(size)
            data_name = f"Séquentielle({size})"
        else:
            print("Choix invalide. Utilisation de la distribution uniforme.")
            data = DataGenerator.generate_uniform(size, max_value)
            data_name = f"Uniforme({size}, max={max_value})"

        print(f"\nGénéré {data_name}")
        print(f"Échantillon de données: {data[:10]}{'...' if len(data) > 10 else ''}")

        # Exécuter le benchmark
        datasets = {data_name: data}
        benchmark_suite = BenchmarkSuite(num_iterations=20)
        results = benchmark_suite.run_comprehensive_benchmark(datasets)

        # Afficher les résultats
        report = benchmark_suite.generate_report(results)
        print(report)

    except ValueError:
        print("Entrée invalide. Veuillez entrer des nombres valides.")
    except KeyboardInterrupt:
        print("\nBenchmark annulé.")


def main():
    """Fonction principale avec interface en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Bit Packing Compression - Compression de données pour accélérer la transmission",
        epilog="Exemples:\n"
               "  python main.py --demo                 # Lancer la démonstration\n"
               "  python main.py --interactive          # Mode interactif\n"
               "  python main.py --benchmark            # Benchmarks complets\n"
               "  python main.py --custom-benchmark     # Benchmark personnalisé\n"
               "  python main.py --gui                  # Lancer l'interface graphique\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--demo", action="store_true",
                       help="Lancer une démonstration des algorithmes")
    parser.add_argument("--interactive", action="store_true",
                       help="Démarrer le mode interactif")
    parser.add_argument("--benchmark", action="store_true",
                       help="Exécuter des benchmarks complets")
    parser.add_argument("--custom-benchmark", action="store_true",
                       help="Exécuter un benchmark personnalisé")
    parser.add_argument("--list-algorithms", action="store_true",
                       help="Lister les algorithmes de compression disponibles")
    parser.add_argument("--gui", action="store_true",
                       help="Lancer l'interface graphique")

    args = parser.parse_args()

    # Si aucun argument fourni, afficher l'aide et lancer la démo
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "="*60)
        print("Lancement de la démonstration car aucun argument n'a été fourni...")
        print("="*60 + "\n")
        demonstrate_algorithms()
        return

    # Traiter les arguments
    if args.list_algorithms:
        print("Algorithmes de compression disponibles:")
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

    if args.gui:
        start_gui()


if __name__ == "__main__":
    main()
