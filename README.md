# Bit Packing Compression Project

## Description

Ce projet implémente différents algorithmes de compression de données par "bit packing" pour accélérer la transmission d'entiers. L'objectif est de compresser des tableaux d'entiers en utilisant moins de bits par élément, tout en conservant un accès direct aux éléments.

**🆕 NOUVEAU : Interface graphique PyQt5 pour interaction intuitive !**

## Algorithmes Implémentés

### 1. Simple Bit Packing
- **Principe** : Permet aux entiers compressés de s'étendre sur plusieurs entiers consécutifs dans le tableau de sortie
- **Avantages** : Utilisation optimale de l'espace
- **Inconvénients** : Opérations de bits plus complexes pour l'accès

### 2. Aligned Bit Packing
- **Principe** : Garantit que les entiers compressés ne s'étendent jamais sur plusieurs entiers consécutifs
- **Avantages** : Accès plus rapide, opérations simplifiées
- **Inconvénients** : Peut utiliser plus d'espace à cause des contraintes d'alignement

### 3. Overflow Bit Packing
- **Principe** : Gère efficacement les valeurs aberrantes en les stockant dans une zone de débordement séparée
- **Avantages** : Optimal pour les jeux de données avec principalement de petites valeurs et quelques grandes valeurs
- **Inconvénients** : Plus complexe à implémenter

## Structure du Projet

```
PythonProject/
├── main.py           # Point d'entrée principal avec interface CLI
├── bit_packing.py    # Implémentation des algorithmes de compression
├── factory.py        # Factory pattern pour créer les compresseurs
├── benchmark.py      # Suite de benchmarks et mesures de performance
├── gui_interface.py  # 🆕 Interface graphique PyQt5
├── tests.py          # Tests unitaires complets
├── requirements.txt  # 🆕 Dépendances Python (PyQt5)
├── README.md         # Ce fichier
└── rapport.md        # Rapport technique détaillé
```

## Installation et Utilisation

### Prérequis
- Python 3.7+

### Installation

1. **Cloner le projet** :
   ```bash
   git clone <url-du-repository>
   cd PythonProject_SoftwareEngineering
   ```

2. **Créer un environnement virtuel** :
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

### Utilisation Basique (Ligne de Commande)

1. **Démonstration des algorithmes** :
   ```bash
   python main.py --demo
   ```

2. **Mode interactif** :
   ```bash
   python main.py --interactive
   ```

3. **Benchmarks complets** :
   ```bash
   python main.py --benchmark
   ```

4. **Benchmark personnalisé** :
   ```bash
   python main.py --custom-benchmark
   ```

5. **Lister les algorithmes disponibles** :
   ```bash
   python main.py --list-algorithms
   ```

### 🆕 Interface Graphique

#### Lancer l'interface graphique :
```bash
python main.py --gui
```

#### Fonctionnalités de l'interface graphique :

**Onglet "Data Input" :**
- **Saisie manuelle** : Entrer des données directement
- **Chargement de fichier** : Importer des données depuis un fichier texte
- **Génération de données** : Créer des jeux de test avec différentes distributions
- **Aperçu des données** : Visualisation des données chargées

**Onglet "Compression" :**
- **Sélection d'algorithme** : Choisir entre Simple, Aligned, ou Overflow
- **Compression interactive** : Compresser les données avec statistiques en temps réel
- **Test d'accès direct** : Tester l'accès à des éléments spécifiques
- **Affichage des résultats** : Ratios de compression, temps d'exécution

**Onglet "Benchmark" :**
- **Benchmarks personnalisés** : Tester les performances sur vos données
- **Benchmarks par défaut** : Exécuter une suite de tests prédéfinis
- **Tableau de résultats** : Comparaison visuelle des algorithmes

**Onglet "Results" :**
- **Historique complet** : Tous les résultats de tests
- **Sauvegarde** : Exporter les résultats vers un fichier
- **Effacement** : Nettoyer l'historique

### Utilisation Programmatique

```python
from factory import BitPackingFactory, CompressionType

# Créer un compresseur
compressor = BitPackingFactory.create_compressor(CompressionType.SIMPLE)

# Compresser des données
data = [1, 2, 3, 4, 5, 6, 7, 8]
compressed = compressor.compress(data)

# Décompresser
decompressed = compressor.decompress(compressed)

# Accès direct à un élément
value_at_index_3 = compressor.get(3)
```

## 🆕 Avantages de l'Interface Graphique

### Pour les Utilisateurs :
- **Interface intuitive** : Pas besoin de connaître les commandes
- **Visualisation en temps réel** : Voir les résultats immédiatement
- **Tests interactifs** : Expérimenter facilement avec différents paramètres
- **Sauvegarde facile** : Exporter les résultats d'un clic

### Pour l'Apprentissage :
- **Comparaison visuelle** : Voir les différences entre algorithmes
- **Feedback immédiat** : Comprendre l'impact des paramètres
- **Génération de données** : Tester différents types de datasets
- **Historique des tests** : Suivre l'évolution des expériences

### Fonctionnalités Avancées :
- **Traitement asynchrone** : L'interface reste réactive pendant les calculs
- **Gestion d'erreurs** : Messages d'erreur clairs et informatifs
- **Validation d'entrée** : Vérification automatique des données
- **Threading** : Les opérations longues n'bloquent pas l'interface

## Exemples d'Utilisation

### Exemple 1 : Test Rapide via GUI
1. Lancer l'interface : `python main.py --gui`
2. Aller dans "Data Input" → Saisir `1 2 3 4 5 6 7 8`
3. Aller dans "Compression" → Sélectionner "Simple" → Cliquer "Compress Data"
4. Voir les résultats instantanément

### Exemple 2 : Génération et Benchmark
1. Dans "Data Input" → Choisir "with_outliers" → Générer 1000 éléments
2. Dans "Benchmark" → Cliquer "Run Benchmark"
3. Observer la comparaison des algorithmes dans le tableau

### Exemple 3 : Compression Programmatique
```python
from factory import create_compressor

# Données avec de petites valeurs
data = [1, 2, 3, 4, 5, 6, 7, 8]

# Utiliser la compression simple
compressor = create_compressor("simple")
compressed = compressor.compress(data)

print(f"Taille originale: {len(data) * 32} bits")
print(f"Taille compressée: {len(compressed) * 32} bits")
print(f"Ratio de compression: {(len(data) * 32) / (len(compressed) * 32):.2f}x")
```

## Mesures de Performance

Le projet inclut un système de benchmarking complet qui mesure :

- **Temps de compression** : Temps nécessaire pour compresser les données
- **Temps de décompression** : Temps nécessaire pour décompresser les données
- **Temps d'accès direct** : Temps pour accéder à un élément via get()
- **Ratio de compression** : Rapport entre la taille originale et compressée
- **Seuil de latence** : Latence de transmission où la compression devient avantageuse

### 🆕 Interface Graphique :
- **Visualisation en temps réel** des métriques
- **Comparaison graphique** entre algorithmes
- **Historique des performances** avec timestamps
- **Export des résultats** pour analyse ultérieure

### Calcul du Seuil de Transmission

Le programme calcule automatiquement la latence minimale où la compression devient avantageuse selon la formule :

```
Temps sauvé = Temps_transmission_original - Temps_transmission_compressé
Surcharge = Temps_compression + Temps_décompression

Seuil = Surcharge / (Temps_sauvé - Surcharge)
```

## Résultats Typiques

Pour des données uniformes de 10 000 entiers avec des valeurs entre 0 et 1000 :
- **Simple Compression** : Ratio ~2.1x, accès en ~50μs
- **Aligned Compression** : Ratio ~1.8x, accès en ~30μs  
- **Overflow Compression** : Ratio ~2.0x, accès en ~60μs

## Architecture et Design Patterns

### Factory Pattern
Le projet utilise le pattern Factory pour créer les différents types de compresseurs de manière uniforme :

```python
# factory.py implémente BitPackingFactory
compressor = BitPackingFactory.create_compressor("simple")
```

### Strategy Pattern
Les différents algorithmes de compression implémentent une interface commune (`BitPackingBase`) permettant d'interchanger facilement les stratégies.

### Template Method
Les classes de compression utilisent des méthodes communes (`_read_bits`, `_write_bits`) tout en implémentant leurs spécificités propres.

### 🆕 Observer Pattern (GUI)
L'interface graphique utilise le pattern Observer via les signaux PyQt5 pour :
- **Communication asynchrone** entre threads
- **Mise à jour de l'interface** en temps réel
- **Gestion d'événements** utilisateur

## Bonus : Gestion des Nombres Négatifs

### Problème
Les nombres négatifs posent problème car :
1. Ils utilisent la représentation en complément à deux
2. Ils nécessitent toujours 32 bits en représentation standard
3. La compression par bit packing devient inefficace

### Solutions Proposées

1. **Mapping Zig-Zag** : Transformer les nombres signés en non-signés
   ```
   Positif n → 2n
   Négatif -n → 2n-1
   ```

2. **Offset** : Ajouter un offset pour rendre tous les nombres positifs
   ```
   Trouver min(array), puis array[i] = array[i] - min + 1
   ```

3. **Séparation** : Stocker séparément les nombres positifs et négatifs avec un bit de signe

## Tests et Validation

Le projet inclut une validation automatique qui vérifie :
- L'intégrité de la compression/décompression
- La cohérence de l'accès direct via get()
- Les performances relatives des différents algorithmes
- **🆕 Tests d'interface** : Validation GUI avec threading sécurisé

## 🆕 Installation et Configuration

### Installation des Dépendances :
```bash
pip install -r requirements.txt
```

### Vérification de l'Installation :
```bash
python main.py --gui
```

### En cas de Problème PyQt5 :
```bash
# Alternative d'installation
pip install PyQt5-tools
# Ou pour Linux
sudo apt-get install python3-pyqt5
```

## Contribution

Le projet est conçu de manière modulaire pour faciliter l'ajout de nouveaux algorithmes :
1. Hériter de `BitPackingBase`
2. Implémenter `compress()`, `decompress()`, et `get()`
3. Ajouter le nouveau type dans `CompressionType`
4. Mettre à jour la factory
5. **🆕 Les nouveaux algorithmes apparaissent automatiquement dans l'interface graphique**

## Auteur

BEN SALAH Mohamed Dhia  
Projet de Software Engineering 2025
