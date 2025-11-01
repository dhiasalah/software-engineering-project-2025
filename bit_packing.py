"""
Implémentation des algorithmes de compression BitPacking pour tableaux d'entiers
Author: BEN SALAH Mohamed Dhia

Ce module implémente la compression bit packing pour les tableaux d'entiers avec trois variantes:
1. Simple bit packing (permet le découpage sur plusieurs entiers consécutifs)
2. Aligned bit packing (pas de découpage sur plusieurs entiers consécutifs)
3. Overflow bit packing (gère les outliers efficacement dans une zone séparée)

Chaque algorithme compresse les données en utilisant le nombre minimum de bits nécessaire
pour représenter chaque valeur, réduisant ainsi la taille de transmission.
"""

import math
from abc import ABC, abstractmethod
from typing import List


class BitPackingBase(ABC):
    """Classe de base abstraite pour toutes les implémentations de bit packing"""

    def __init__(self):
        """Initialise les attributs communs à tous les compresseurs"""
        self.compressed_data: List[int] = []  # Données compressées
        self.original_length: int = 0  # Longueur du tableau original
        self.bits_per_element: int = 0  # Nombre de bits par élément

    @abstractmethod
    def compress(self, array: List[int]) -> List[int]:
        """
        Compresse un tableau d'entiers.

        Args:
            array: Tableau d'entiers à compresser

        Returns:
            List[int]: Tableau compressé
        """
        pass

    @abstractmethod
    def decompress(self, compressed_array: List[int]) -> List[int]:
        """
        Décompresse et retourne le tableau original.

        Args:
            compressed_array: Tableau compressé

        Returns:
            List[int]: Tableau décompressé original
        """
        pass

    @abstractmethod
    def get(self, index: int) -> int:
        """
        Obtient la valeur à l'index i depuis le tableau compressé.
        Permet un accès direct sans décompression complète.

        Args:
            index: Index de l'élément à récupérer

        Returns:
            int: Valeur à l'index spécifié

        Raises:
            IndexError: Si l'index est hors limites
        """
        pass

    def _calculate_bits_needed(self, array: List[int]) -> int:
        """
        Calcule le nombre minimum de bits nécessaires pour représenter toutes les valeurs.

        Args:
            array: Tableau d'entiers à analyser

        Returns:
            int: Nombre de bits minimum nécessaires
        """
        if not array:
            return 0

        min_val = min(array)
        max_val = max(array)

        # Si on a des nombres négatifs, on doit décaler toutes les valeurs
        if min_val < 0:
            # Décaler de sorte que la valeur minimale devient 0
            range_val = max_val - min_val
        else:
            range_val = max_val

        # bit_length() retourne le nombre de bits nécessaires pour représenter le nombre
        return range_val.bit_length() if range_val > 0 else 1


class SimpleBitPacking(BitPackingBase):
    """
    Bit packing simple qui permet aux entiers compressés de s'étendre sur
    plusieurs entiers consécutifs dans le tableau de sortie.

    Exemple: Si on compresse avec 12 bits par élément, le 3ème élément peut
    s'étendre sur les bits 25-32 du premier entier ET les bits 1-4 du second.
    C'est le plus efficace en termes d'espace.
    """

    def compress(self, array: List[int]) -> List[int]:
        """
        Compresse le tableau en utilisant le bit packing simple.
        Les entiers compressés peuvent s'étendre sur plusieurs entiers de sortie consécutifs.

        Args:
            array: Tableau d'entiers positifs à compresser

        Returns:
            List[int]: Tableau compressé avec utilisation optimale de l'espace
        """
        if not array:
            return []

        self.original_length = len(array)
        self.bits_per_element = self._calculate_bits_needed(array)

        # Calculer le nombre total de bits nécessaires
        total_bits = self.original_length * self.bits_per_element
        # Calculer le nombre d'entiers 32-bit nécessaires
        num_output_ints = (total_bits + 31) // 32

        # Initialiser le tableau de sortie avec des zéros
        compressed = [0] * num_output_ints

        # Empaqueter chaque élément dans le tableau compressé
        for element_index, value in enumerate(array):
            start_bit = element_index * self.bits_per_element
            self._write_bits(compressed, start_bit, self.bits_per_element, value)

        self.compressed_data = compressed
        return compressed

    def decompress(self, compressed_array: List[int]) -> List[int]:
        """
        Décompresse le tableau en extrayant chaque valeur.

        Args:
            compressed_array: Tableau compressé à décompresser

        Returns:
            List[int]: Tableau original reconstitué
        """
        if not compressed_array:
            return []

        result = []
        for element_index in range(self.original_length):
            start_bit = element_index * self.bits_per_element
            value = self._read_bits(compressed_array, start_bit, self.bits_per_element)
            result.append(value)

        return result

    def get(self, index: int) -> int:
        """
        Accès direct à un élément sans décompression complète.

        Args:
            index: Index de l'élément (0-based)

        Returns:
            int: Valeur à cet index

        Raises:
            IndexError: Si index est hors limites
        """
        if index < 0 or index >= self.original_length:
            raise IndexError("Index hors limites")

        start_bit = index * self.bits_per_element
        return self._read_bits(self.compressed_data, start_bit, self.bits_per_element)

    def _write_bits(self, array: List[int], start_bit: int, num_bits: int, value: int):
        """
        Écrit des bits dans le tableau en commençant à start_bit.
        Peut s'étendre sur deux entiers consécutifs si nécessaire.

        Args:
            array: Tableau où écrire
            start_bit: Position du bit de départ (0-based)
            num_bits: Nombre de bits à écrire
            value: Valeur à écrire
        """
        if num_bits == 0:
            return

        # Créer un masque pour garantir que la valeur tient dans num_bits
        mask = (1 << num_bits) - 1
        value &= mask  # Appliquer le masque

        # Calculer dans quel entier 32-bit on écrit et à quel offset
        int_index = start_bit // 32
        bit_offset = start_bit % 32

        # Si la valeur tient entièrement dans un seul entier
        if bit_offset + num_bits <= 32:
            array[int_index] |= (value << bit_offset)
        else:
            # Cas où on doit découper la valeur sur deux entiers
            bits_in_first = 32 - bit_offset  # Bits qu'on peut mettre dans le premier
            bits_in_second = num_bits - bits_in_first  # Reste à mettre dans le second

            # Écrire la première partie (bits de poids faible)
            first_mask = (1 << bits_in_first) - 1
            array[int_index] |= ((value & first_mask) << bit_offset)

            # Écrire la seconde partie (bits de poids fort) si possible
            if int_index + 1 < len(array):
                array[int_index + 1] |= (value >> bits_in_first)

    def _read_bits(self, array: List[int], start_bit: int, num_bits: int) -> int:
        """
        Lit des bits depuis le tableau en commençant à start_bit.
        Peut lire depuis deux entiers consécutifs si nécessaire.

        Args:
            array: Tableau depuis lequel lire
            start_bit: Position du bit de départ (0-based)
            num_bits: Nombre de bits à lire

        Returns:
            int: Valeur lue
        """
        if num_bits == 0:
            return 0

        # Calculer l'index de l'entier et l'offset du bit
        int_index = start_bit // 32
        bit_offset = start_bit % 32

        if int_index >= len(array):
            return 0

        # Si la valeur est entièrement dans un seul entier
        if bit_offset + num_bits <= 32:
            mask = (1 << num_bits) - 1
            return (array[int_index] >> bit_offset) & mask
        else:
            # Cas où la valeur est découpée sur deux entiers
            bits_in_first = 32 - bit_offset
            bits_in_second = num_bits - bits_in_first

            # Lire la première partie
            first_mask = (1 << bits_in_first) - 1
            first_part = (array[int_index] >> bit_offset) & first_mask

            # Lire la seconde partie si possible
            if int_index + 1 < len(array):
                second_mask = (1 << bits_in_second) - 1
                second_part = array[int_index + 1] & second_mask
                return first_part | (second_part << bits_in_first)
            else:
                return first_part


class AlignedBitPacking(BitPackingBase):
    """
    Bit packing aligné qui garantit que les entiers compressés ne s'étendent
    jamais sur plusieurs entiers consécutifs dans le tableau de sortie.

    Exemple: Si on compresse avec 12 bits par élément, on peut mettre 2 éléments
    (24 bits) dans un entier 32-bit, et le 3ème élément commence au début du
    prochain entier. C'est plus simple et rapide mais peut gaspiller de l'espace.
    """

    def __init__(self):
        """Initialise le compresseur avec support des nombres négatifs"""
        super().__init__()
        self.min_value = 0  # Stocke la valeur minimale pour l'offset

    def compress(self, array: List[int]) -> List[int]:
        """
        Compresse le tableau en utilisant le bit packing aligné.
        Les entiers compressés ne s'étendent jamais sur plusieurs entiers de sortie.

        Args:
            array: Tableau d'entiers (positifs, négatifs, ou mixtes) à compresser

        Returns:
            List[int]: Tableau compressé avec alignement
        """
        if not array:
            return []

        self.original_length = len(array)

        # Calculer la valeur minimale pour l'offset
        self.min_value = min(array)

        # Appliquer le décalage pour tous les nombres
        shifted_array = [value - self.min_value for value in array]

        self.bits_per_element = self._calculate_bits_needed(shifted_array)

        # Calculer combien d'éléments peuvent tenir dans un entier 32-bit
        elements_per_int = 32 // self.bits_per_element if self.bits_per_element > 0 else 32

        # Calculer le nombre d'entiers de sortie nécessaires
        num_output_ints = (self.original_length + elements_per_int - 1) // elements_per_int

        # Initialiser le tableau de sortie
        compressed = [0] * num_output_ints

        # Empaqueter les éléments sans chevauchement
        for i, value in enumerate(shifted_array):
            output_index = i // elements_per_int  # Dans quel entier on écrit
            element_index = i % elements_per_int  # Position dans cet entier
            bit_offset = element_index * self.bits_per_element  # Offset en bits

            compressed[output_index] |= (value << bit_offset)

        # Stocker l'offset au début du tableau compressé
        result = [self.min_value] + compressed
        self.compressed_data = result
        return result

    def decompress(self, compressed_array: List[int]) -> List[int]:
        """
        Décompresse le tableau aligné en appliquant l'offset inverse.

        Args:
            compressed_array: Tableau compressé à décompresser

        Returns:
            List[int]: Tableau original reconstitué
        """
        if not compressed_array or len(compressed_array) < 2:
            return []

        # Extraire l'offset du début du tableau
        self.min_value = compressed_array[0]
        actual_compressed = compressed_array[1:]

        result = []
        elements_per_int = 32 // self.bits_per_element if self.bits_per_element > 0 else 32
        mask = (1 << self.bits_per_element) - 1

        for i in range(self.original_length):
            output_index = i // elements_per_int
            element_index = i % elements_per_int
            bit_offset = element_index * self.bits_per_element

            if output_index < len(actual_compressed):
                value = (actual_compressed[output_index] >> bit_offset) & mask
                # Appliquer l'offset inverse
                result.append(value + self.min_value)
            else:
                result.append(0)

        return result

    def get(self, index: int) -> int:
        """
        Accès direct à un élément sans décompression complète.
        Plus rapide que SimpleBitPacking car pas de chevauchement.

        Args:
            index: Index de l'élément (0-based)

        Returns:
            int: Valeur à cet index

        Raises:
            IndexError: Si index est hors limites
        """
        if index < 0 or index >= self.original_length:
            raise IndexError("Index hors limites")

        elements_per_int = 32 // self.bits_per_element if self.bits_per_element > 0 else 32
        output_index = index // elements_per_int
        element_index = index % elements_per_int
        bit_offset = element_index * self.bits_per_element
        mask = (1 << self.bits_per_element) - 1

        # Ignorer le premier élément qui contient l'offset
        actual_compressed = self.compressed_data[1:]

        if output_index < len(actual_compressed):
            value = (actual_compressed[output_index] >> bit_offset) & mask
            # Appliquer l'offset inverse
            return value + self.min_value
        else:
            return 0


class OverflowBitPacking(BitPackingBase):
    """
    Bit packing avec zone de débordement pour gérer efficacement les outliers.

    Utilise une valeur spéciale pour indiquer que la valeur réelle est stockée
    dans une zone de débordement séparée. Optimal quand on a beaucoup de petites
    valeurs et quelques très grandes valeurs (outliers).

    Exemple: [1, 2, 3, 1024, 4, 5] → encode 1,2,3,4,5 avec 3 bits + 1 bit overflow,
    et stocke 1024 dans une zone séparée avec une référence.
    """

    def __init__(self):
        """Initialise le compresseur avec overflow"""
        super().__init__()
        self.overflow_data: List[int] = []  # Zone de débordement pour les outliers
        self.overflow_bits: int = 0  # Bits pour indexer dans overflow
        self.main_bits: int = 0  # Bits pour les valeurs normales
        self.has_overflow_bit: bool = False  # Si on utilise un bit d'overflow
        self.threshold_value: int = 0  # Seuil pour décider si une valeur va en overflow

    def compress(self, array: List[int]) -> List[int]:
        """
        Compresse le tableau en utilisant le bit packing avec overflow.
        Les outliers sont stockés dans une zone de débordement séparée.

        Args:
            array: Tableau d'entiers positifs à compresser

        Returns:
            List[int]: Tableau compressé suivi de la zone d'overflow
        """
        if not array:
            return []

        self.original_length = len(array)

        # Analyser les données pour déterminer la stratégie d'overflow optimale
        self._analyze_overflow_strategy(array)

        # Séparer les valeurs normales et les valeurs overflow
        main_values = []
        self.overflow_data = []
        overflow_map = {}  # Mapping valeur -> index dans overflow

        for value in array:
            if self._needs_overflow(value):
                # Cette valeur doit aller en overflow
                if value not in overflow_map:
                    # Nouvelle valeur overflow, l'ajouter
                    overflow_map[value] = len(self.overflow_data)
                    self.overflow_data.append(value)
                # Encoder avec le bit d'overflow + position dans overflow
                encoded_value = (1 << self.main_bits) | overflow_map[value]
                main_values.append(encoded_value)
            else:
                # Encodage direct
                main_values.append(value)

        # Compresser les valeurs principales en utilisant simple bit packing
        total_bits_per_element = self.main_bits + (1 if self.has_overflow_bit else 0)
        total_bits = len(main_values) * total_bits_per_element
        num_output_ints = (total_bits + 31) // 32

        compressed = [0] * num_output_ints

        for i, value in enumerate(main_values):
            start_bit = i * total_bits_per_element
            self._write_bits(compressed, start_bit, total_bits_per_element, value)

        # Ajouter les données overflow à la fin
        compressed.extend(self.overflow_data)

        self.compressed_data = compressed
        return compressed

    def _analyze_overflow_strategy(self, array: List[int]):
        """
        Analyse les valeurs pour déterminer la stratégie d'overflow optimale.
        Décide combien de bits utiliser pour les valeurs normales et si on
        doit utiliser une zone d'overflow.

        Args:
            array: Tableau à analyser
        """
        if not array:
            self.has_overflow_bit = False
            self.main_bits = 1
            self.overflow_bits = 0
            self.threshold_value = 0
            return

        sorted_values = sorted(set(array))

        if len(sorted_values) <= 1:
            # Cas simple: toutes les valeurs sont identiques
            self.has_overflow_bit = False
            self.main_bits = self._calculate_bits_needed(array)
            self.overflow_bits = 0
            self.threshold_value = max(array) if array else 0
            return

        # Stratégie basée sur un seuil
        # Les valeurs nécessitant plus de 60% des bits max vont en overflow
        max_bits = max(sorted_values).bit_length()
        threshold_bits = max(3, int(max_bits * 0.6))
        self.threshold_value = (1 << threshold_bits) - 1

        overflow_values = [v for v in sorted_values if v > self.threshold_value]

        # Utiliser overflow seulement si < 30% des valeurs uniques sont des outliers
        if len(overflow_values) > 0 and len(overflow_values) < len(sorted_values) * 0.3:
            self.has_overflow_bit = True
            self.main_bits = threshold_bits
            self.overflow_bits = math.ceil(math.log2(len(overflow_values) + 1)) if len(overflow_values) > 1 else 1
        else:
            # Pas assez d'outliers pour justifier l'overflow
            self.has_overflow_bit = False
            self.main_bits = max_bits
            self.overflow_bits = 0

    def _needs_overflow(self, value: int) -> bool:
        """
        Vérifie si une valeur doit aller dans la zone d'overflow.

        Args:
            value: Valeur à vérifier

        Returns:
            bool: True si la valeur dépasse le seuil
        """
        return self.has_overflow_bit and value > self.threshold_value

    def decompress(self, compressed_array: List[int]) -> List[int]:
        """
        Décompresse le tableau avec gestion de l'overflow.

        Args:
            compressed_array: Tableau compressé incluant la zone d'overflow

        Returns:
            List[int]: Tableau original reconstitué
        """
        if not compressed_array:
            return []

        # Séparer les données compressées et les données overflow
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
                # Ceci est une référence overflow
                overflow_index = encoded_value & value_mask
                if overflow_index < len(overflow_data):
                    actual_value = overflow_data[overflow_index]
                    result.append(actual_value)
                else:
                    result.append(0)
            else:
                # Valeur directe
                result.append(encoded_value & value_mask)

        return result

    def get(self, index: int) -> int:
        """
        Accès direct à un élément avec gestion de l'overflow.

        Args:
            index: Index de l'élément (0-based)

        Returns:
            int: Valeur à cet index

        Raises:
            IndexError: Si index est négatif ou >= longueur originale
        """
        if index < 0 or index >= self.original_length:
            raise IndexError("Index hors limites")

        total_bits_per_element = self.main_bits + (1 if self.has_overflow_bit else 0)
        total_bits = self.original_length * total_bits_per_element
        num_main_ints = (total_bits + 31) // 32

        start_bit = index * total_bits_per_element
        encoded_value = self._read_bits(self.compressed_data[:num_main_ints], start_bit, total_bits_per_element)

        overflow_mask = 1 << self.main_bits if self.has_overflow_bit else 0
        value_mask = (1 << self.main_bits) - 1

        if self.has_overflow_bit and (encoded_value & overflow_mask):
            # Référence overflow - récupérer depuis la zone overflow
            overflow_index = encoded_value & value_mask
            overflow_start = num_main_ints
            if overflow_start + overflow_index < len(self.compressed_data):
                return self.compressed_data[overflow_start + overflow_index]
            else:
                return 0
        else:
            # Valeur directe
            return encoded_value & value_mask

    def _write_bits(self, array: List[int], start_bit: int, num_bits: int, value: int):
        """Écrit des bits - implémentation identique à SimpleBitPacking"""
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
        """Lit des bits - implémentation identique à SimpleBitPacking"""
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


class ZigZagBitPacking(SimpleBitPacking):
    """
    Bit packing avec codage ZigZag pour gérer les entiers signés.

    Le codage ZigZag permet de représenter les entiers signés de manière à ce que
    les valeurs négatives aient également une petite représentation binaire.
    Parfait pour les données où les valeurs positives et négatives sont également probables.

    Exemple: [1, -1, 2, -2] pourrait être codé comme [2, 1, 3, 0] avec 2 bits par élément.
    """

    @staticmethod
    def _zigzag_encode(value: int) -> int:
        """Encode un entier signé en non-signé avec Zig-Zag."""
        return (value << 1) ^ (value >> 31)

    @staticmethod
    def _zigzag_decode(value: int) -> int:
        """Decode un entier non-signé en signé avec Zig-Zag inverse."""
        return (value >> 1) ^ (-(value & 1))

    def compress(self, array: List[int]) -> List[int]:
        """
        Compresse le tableau en utilisant le bit packing avec codage ZigZag.

        Args:
            array: Tableau d'entiers (positifs et négatifs) à compresser

        Returns:
            List[int]: Tableau compressé avec codage ZigZag
        """
        if not array:
            return []

        # Appliquer le codage ZigZag
        zigzag_encoded = [self._zigzag_encode(value) for value in array]

        # Utiliser le bit packing simple sur les données ZigZag codées
        return super().compress(zigzag_encoded)

    def decompress(self, compressed_array: List[int]) -> List[int]:
        """
        Décompresse le tableau en appliquant le décodage ZigZag inverse.

        Args:
            compressed_array: Tableau compressé à décompresser

        Returns:
            List[int]: Tableau original (avec signes restaurés)
        """
        if not compressed_array:
            return []

        # Utiliser le décompressage simple
        zigzag_decoded = super().decompress(compressed_array)

        # Appliquer le décodage ZigZag inverse
        return [self._zigzag_decode(value) for value in zigzag_decoded]

    def get(self, index: int) -> int:
        """
        Accès direct à un élément compressé avec codage ZigZag.

        Args:
            index: Index de l'élément (0-based)

        Returns:
            int: Valeur à cet index (avec signe)

        Raises:
            IndexError: Si index est hors limites
        """
        if index < 0 or index >= self.original_length:
            raise IndexError("Index hors limites")

        # Lire la valeur compressée via la classe parente
        encoded_value = super().get(index)

        # Appliquer le décodage ZigZag inverse
        return self._zigzag_decode(encoded_value)
