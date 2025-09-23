# Rapport du Projet : Compression de Données par Bit Packing

**Auteur :** BEN SALAH Mohamed Dhia
**Date :** 23 septembre 2025  
**Cours :** Software Engineering  

## 1. Introduction et Problématique

### 1.1 Contexte
La transmission de tableaux d'entiers constitue l'un des problèmes centraux d'Internet. Ce projet étudie différents modes de transmission basés sur la compression d'entiers pour réduire le nombre d'entiers à transmettre, puis les décompresser après transmission.

### 1.2 Objectifs
- Implémenter une méthode de compression qui ne perd pas l'accès direct aux éléments
- Développer trois variantes d'algorithmes de bit packing
- Mesurer et analyser les performances de chaque algorithme
- Calculer les seuils de latence où la compression devient avantageuse

## 2. Solution Technique

### 2.1 Principe du Bit Packing
Le bit packing consiste à utiliser le nombre minimal de bits nécessaires pour représenter chaque élément. Si chaque élément peut être représenté avec k bits, alors on peut créer une représentation globale utilisant n*k bits au lieu de 32n bits avec des entiers conventionnels.

### 2.2 Algorithmes Implémentés

#### 2.2.1 Simple Bit Packing
- **Principe** : Permet aux entiers compressés de s'étendre sur plusieurs entiers consécutifs dans le tableau de sortie
- **Avantages** : Utilisation optimale de l'espace, meilleur ratio de compression
- **Inconvénients** : Opérations de bits plus complexes

**Exemple** : Pour 6 éléments nécessitant 12 bits chacun :
- Le 1er élément : bits 1-12 du 1er entier de sortie
- Le 2ème élément : bits 13-24 du 1er entier de sortie  
- Le 3ème élément : bits 25-32 du 1er entier + bits 1-4 du 2ème entier
- Et ainsi de suite...

#### 2.2.2 Aligned Bit Packing
- **Principe** : Garantit que les entiers compressés ne s'étendent jamais sur plusieurs entiers consécutifs
- **Avantages** : Accès plus rapide, opérations simplifiées
- **Inconvénients** : Peut gaspiller de l'espace à cause des contraintes d'alignement

**Exemple** : Pour 6 éléments nécessitant 12 bits chacun :
- Le 1er élément : bits 1-12 du 1er entier de sortie
- Le 2ème élément : bits 13-24 du 1er entier de sortie
- Le 3ème élément : bits 1-12 du 2ème entier de sortie
- Et ainsi de suite...

#### 2.2.3 Overflow Bit Packing
- **Principe** : Gère efficacement les valeurs aberrantes en les stockant dans une zone de débordement séparée
- **Avantages** : Optimal pour les datasets avec principalement de petites valeurs et quelques grandes valeurs
- **Inconvénients** : Plus complexe à implémenter

**Exemple** : Pour encoder [1, 2, 3, 1024, 4, 5, 2048] :
- Utiliser 3 bits pour les valeurs normales et 1 bit pour indiquer le débordement
- Représentation : 0-1, 0-2, 0-3, 1-0, 0-4, 0-5, 1-1, [1024, 2048]

## 3. Architecture et Design Patterns

### 3.1 Factory Pattern
Le projet utilise le pattern Factory (`BitPackingFactory`) pour créer les différents types de compresseurs de manière uniforme :

```python
compressor = BitPackingFactory.create_compressor(CompressionType.SIMPLE)
```

### 3.2 Strategy Pattern
Les différents algorithmes implémentent une interface commune (`BitPackingBase`) permettant d'interchanger facilement les stratégies de compression.

### 3.3 Template Method
Les classes de compression partagent des méthodes communes (`_read_bits`, `_write_bits`) tout en implémentant leurs spécificités propres.

## 4. Résultats et Analyse

### 4.1 Ratios de Compression Obtenus

| Dataset | Simple | Aligned | Overflow |
|---------|--------|---------|----------|
| Small Uniform (1K) | 3.19x | 2.99x | 3.19x |
| Large Uniform (10K) | 3.20x | 3.00x | 3.20x |
| Power Law | 2.29x | 2.00x | 2.29x |
| With Outliers | 1.88x | 1.00x | **2.91x** |
| Sequential | 2.46x | 2.00x | 2.46x |
| Mixed Small | 8.00x | 8.00x | 8.00x |

### 4.2 Temps d'Exécution

| Algorithme | Compression (ms) | Décompression (ms) | Accès Direct (μs) |
|------------|------------------|--------------------|--------------------|
| Simple | 0.4-4.9 | 0.4-4.3 | 0.3-0.8 |
| Aligned | 0.2-1.9 | 0.2-1.9 | 0.3-0.7 |
| Overflow | 0.6-5.9 | 0.4-12.9 | 1.4-8.7 |

### 4.3 Seuils de Transmission

Le calcul du seuil de latence où la compression devient avantageuse suit la formule :

```
Temps_sauvé = Temps_transmission_original - Temps_transmission_compressé
Surcharge = Temps_compression + Temps_décompression
Seuil = Surcharge / (Temps_sauvé - Surcharge)
```

**Résultats typiques** (dataset Mixed Small à 1 Mbps) :
- Simple : 22.3 ms de latence
- Aligned : 13.1 ms de latence  
- Overflow : 28.7 ms de latence

## 5. Choix de Conception et Justifications

### 5.1 Choix du Langage
Python a été choisi pour sa simplicité de développement et ses capacités de manipulation de bits, permettant un prototypage rapide des algorithmes.

### 5.2 Structure Modulaire
Le projet est organisé en modules séparés :
- `bit_packing.py` : Implémentations des algorithmes
- `factory.py` : Factory pattern pour la création d'objets
- `benchmark.py` : Suite de benchmarks et mesures
- `main.py` : Interface utilisateur et point d'entrée

### 5.3 Gestion des Cas Limites
- **Tableaux vides** : Retour de tableaux vides
- **Valeurs nulles** : Gestion spéciale pour éviter les erreurs de bits
- **Index invalides** : Levée d'exceptions `IndexError`
- **Débordements** : Vérifications de limites dans toutes les opérations

## 6. Validation et Tests

### 6.1 Tests Unitaires
Le projet inclut une suite complète de tests unitaires couvrant :
- Intégrité compression/décompression
- Cohérence de l'accès direct via `get()`
- Gestion des erreurs d'index
- Cas limites (tableaux vides, grandes valeurs)

### 6.2 Benchmarks
Les benchmarks évaluent :
- Différents types de données (uniformes, power-law, avec outliers)
- Performances temporelles (compression, décompression, accès)
- Ratios de compression
- Seuils de transmission optimaux

## 7. Bonus : Gestion des Nombres Négatifs

### 7.1 Problème
Les nombres négatifs posent des défis spécifiques :
- Utilisation de la représentation en complément à deux
- Nécessité de 32 bits complets en représentation standard
- Inefficacité du bit packing traditionnel

### 7.2 Solutions Proposées

#### 7.2.1 Mapping Zig-Zag
Transformation des nombres signés en non-signés :
```
Positif n → 2n
Négatif -n → 2n-1
```

#### 7.2.2 Méthode par Offset
Ajout d'un offset pour rendre tous les nombres positifs :
```
Trouver min(array), puis array[i] = array[i] - min + 1
```

#### 7.2.3 Séparation par Signe
Stockage séparé des nombres positifs et négatifs avec un bit de signe.

## 8. Conclusion et Perspectives

### 8.1 Résultats Obtenus
- **Simple Bit Packing** : Meilleur ratio de compression général
- **Aligned Bit Packing** : Meilleur compromis performance/compression
- **Overflow Bit Packing** : Excellente performance sur données avec outliers

### 8.2 Recommandations d'Utilisation
- **Données uniformes** : Utiliser Simple ou Aligned selon les contraintes de performance
- **Données avec outliers** : Utiliser Overflow pour une compression optimale
- **Applications temps réel** : Privilégier Aligned pour sa rapidité d'accès

### 8.3 Améliorations Futures
- Implémentation de la gestion des nombres négatifs
- Optimisation des opérations de bits pour de meilleures performances
- Algorithmes adaptatifs qui choisissent automatiquement la meilleure stratégie
- Support pour d'autres types de données (nombres flottants, caractères)

## 9. Annexes

### 9.1 Instructions d'Installation et d'Utilisation
Voir le fichier README.md pour les instructions détaillées.

### 9.2 Code Source
Le code source complet est disponible dans le repository GitHub avec tous les fichiers documentés.

### 9.3 Résultats de Benchmarks Détaillés
Les résultats complets des benchmarks sont sauvegardés dans le fichier `benchmark_report.txt`.
