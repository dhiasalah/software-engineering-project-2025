"""
Factory pour créer différents types d'algorithmes de compression bit packing
Author: BEN SALAH Mohamed Dhia

Ce module fournit un pattern Factory pour créer des instances de différents
algorithmes de compression bit packing basés sur un seul paramètre. Cela facilite
la création et le changement d'algorithmes sans modifier le code client.
"""

from enum import Enum
from typing import Union
from bit_packing import BitPackingBase, SimpleBitPacking, AlignedBitPacking, OverflowBitPacking


class CompressionType(Enum):
    """Énumération des types de compression disponibles"""
    SIMPLE = "simple"
    ALIGNED = "aligned"
    OVERFLOW = "overflow"


class BitPackingFactory:
    """
    Classe Factory pour créer des instances de compression bit packing.

    Cette factory permet la création facile de différents algorithmes de compression
    basée sur un seul paramètre, suivant le pattern de conception Factory.
    """

    @staticmethod
    def create_compressor(compression_type: Union[str, CompressionType]) -> BitPackingBase:
        """
        Crée un compresseur bit packing basé sur le type spécifié.

        Args:
            compression_type: Type de compression à créer. Peut être:
                - "simple" ou CompressionType.SIMPLE: Bit packing simple (permet le chevauchement)
                - "aligned" ou CompressionType.ALIGNED: Bit packing aligné (pas de chevauchement)
                - "overflow" ou CompressionType.OVERFLOW: Bit packing avec overflow (gestion des outliers)

        Returns:
            BitPackingBase: Instance de l'algorithme de compression demandé

        Raises:
            ValueError: Si compression_type n'est pas reconnu
        """
        # Convertir la chaîne en enum si nécessaire
        if isinstance(compression_type, str):
            try:
                compression_type = CompressionType(compression_type.lower())
            except ValueError:
                raise ValueError(f"Type de compression inconnu: {compression_type}. "
                               f"Types disponibles: {[t.value for t in CompressionType]}")

        # Créer et retourner le compresseur approprié
        if compression_type == CompressionType.SIMPLE:
            return SimpleBitPacking()
        elif compression_type == CompressionType.ALIGNED:
            return AlignedBitPacking()
        elif compression_type == CompressionType.OVERFLOW:
            return OverflowBitPacking()
        else:
            raise ValueError(f"Type de compression non supporté: {compression_type}")

    @staticmethod
    def get_available_types() -> list:
        """
        Obtient la liste des types de compression disponibles.

        Returns:
            list: Liste des chaînes de types de compression disponibles
        """
        return [compression_type.value for compression_type in CompressionType]

    @staticmethod
    def get_description(compression_type: Union[str, CompressionType]) -> str:
        """
        Obtient la description d'un type de compression.

        Args:
            compression_type: Type de compression à décrire

        Returns:
            str: Description de l'algorithme de compression
        """
        if isinstance(compression_type, str):
            compression_type = CompressionType(compression_type.lower())

        descriptions = {
            CompressionType.SIMPLE:
                "Bit packing simple qui permet aux entiers compressés de s'étendre sur "
                "plusieurs entiers consécutifs dans le tableau de sortie. Le plus efficace "
                "en termes d'espace mais les opérations de bits sont légèrement plus complexes.",

            CompressionType.ALIGNED:
                "Bit packing aligné qui garantit que les entiers compressés ne s'étendent "
                "jamais sur plusieurs entiers consécutifs. Accès plus rapide mais peut "
                "utiliser plus d'espace à cause des contraintes d'alignement.",

            CompressionType.OVERFLOW:
                "Bit packing avec overflow qui gère efficacement les outliers en stockant "
                "les grandes valeurs dans une zone de débordement séparée. Optimal pour les "
                "jeux de données avec principalement de petites valeurs et quelques grandes outliers."
        }

        return descriptions.get(compression_type, "Type de compression inconnu")


# Fonction de commodité pour un accès facile
def create_compressor(compression_type: Union[str, CompressionType]) -> BitPackingBase:
    """
    Fonction de commodité pour créer un compresseur sans instancier la factory.

    Args:
        compression_type: Type de compression à créer

    Returns:
        BitPackingBase: Instance de l'algorithme de compression demandé
    """
    return BitPackingFactory.create_compressor(compression_type)
