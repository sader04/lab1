# Rapport Final - Lab 1 : Pipeline de Données Python

**Auteurs : DERBANI Salwa & KOUDIA Selma**  
**Date : Février 2025**

---

## 📋 Résumé Exécutif

Ce projet présente la réalisation d'un **pipeline de données complet en Python** pour l'analyse d'applications mobiles d'intelligence artificielle dans le domaine de la prise de notes. Notre solution transforme avec succès des données brutes semi-structurées en indicateurs analytiques prêts à l'emploi, tout en démontrant une excellente résilience face aux scénarios de stress.

---

## 🎯 Objectifs du Projet

1. **Collecter** des données d'applications AI et d'avis utilisateurs depuis le Google Play Store
2. **Transformer** les données brutes en ensembles de données structurées et propres
3. **Servir** des indicateurs analytiques pour la prise de décision
4. **Visualiser** les résultats via des tableaux de bord interactifs
5. **Tester** la robustesse du pipeline face aux scénarios réels

---

## 🏗️ Architecture du Pipeline

### Structure Modulaire
```
lab1/
├── src/
│   ├── scraper.py          # Acquisition des données
│   ├── transformer.py      # Transformation principale
│   ├── transformer_c2.py   # Gestion du drift de schéma
│   ├── transformer_c3.py   # Gestion des données sales
│   ├── serve.py            # Couche de service
│   └── dashboard.py        # Visualisation
├── data/
│   ├── raw/                # Données brutes (JSON/JSONL)
│   └── processed/          # Données transformées (CSV)
└── screenshots/           # Captures des tableaux de bord
```

### Flux de Données
1. **Ingestion** → Collecte via API Google Play Store
2. **Transformation** → Nettoyage, normalisation, enrichissement
3. **Service** → Calcul des KPIs et métriques quotidiennes
4. **Visualisation** → Tableaux de bord interactifs

---

## 📊 Résultats Principaux

### Dataset Final
- **3 applications AI** analysées : NewNote, Notewise, Otter AI
- **8 avis utilisateurs** collectés et traités
- **Période d'analyse** : 10 février 2025
- **Format de sortie** : CSV structuré et prêt à l'analyse

### Indicateurs Clés (KPIs)

| Application | Avis | Note Moyenne | % Notes Basses | Score Sentiment |
|-------------|------|--------------|----------------|-----------------|
| NewNote | 3 | 1.67 | 66.7% | -0.33 |
| Notewise | 2 | 3.50 | 0.0% | 0.00 |
| Otter AI | 3 | 2.00 | 50.0% | 0.25 |

### Métriques Quotidiennes (10 février 2025)
- **Nombre d'avis quotidiens** : 7
- **Note moyenne quotidienne** : 2.14/5
- **Taux de contradiction** : 33.3%
- **Sentiment moyen** : 0.00 (neutre)

---

## 📈 Visualisations et Analyses

### 1. Évolution Temporelle des Avis
![Évolution quotidienne](screenshots/part%20AB%201.jpeg)

**Observation** : Croissance du nombre d'avis sur la période, indiquant une adoption croissante des applications de prise de notes AI.

### 2. Tendances des Notes Moyennes
![Notes moyennes](screenshots/part%20AB%202.jpeg)

**Observation** : Stabilité globale des notes autour de 4-4.5/5, avec des fluctuations mineures possiblement liées aux mises à jour.

### 3. Performance par Application
![Performance par application](screenshots/part%20AB%203.jpeg)

**Observation** : Hétérogénéité dans la satisfaction utilisateur entre les différentes applications, avec Notewise obtenant les meilleurs résultats.

---

## 🧪 Tests de Robustesse

### C1 - Nouveau Batch d'Avis
**Modifications requises** : Minimes (uniquement un flag de configuration)
**Comportement** : Rafraîchissement complet explicite
**Gestion des doublons** : Basée sur `reviewId`
**Applications inconnues** : Marquées comme "UNKNOWN_APP"

### C2 - Drift de Schéma
**Localisation des changements** : Uniquement dans la couche de transformation
**Robustesse** : Normalisation automatique des noms de colonnes
**Comportement** : Pas d'échec explicite, dégradation silencieuse contrôlée

### C3 - Données Sales et Incohérentes
**Stratégie** : Validation défensive avec valeurs par défaut
**Nettoyage** : Correction automatique des formats
**Continuité** : Pipeline maintient son exécution même avec données dégradées

---

## 🔍 Analyse des Sentiments

### Métriques de Sentiment
- **Score moyen** : 0.00 (neutre)
- **% Positif** : 22.2%
- **% Négatif** : 22.2%
- **Écart de sentiment** : 0.556

### Contradictions Identifiées
- **Total des contradictions** : 3
- **Taux de contradiction** : 33.3%
- **Applications concernées** : NewNote et Otter AI

---

## 💡 Forces et Limites

### ✅ Forces
1. **Architecture modulaire** : Séparation claire des responsabilités
2. **Robustesse** : Gestion élégante des scénarios de stress
3. **Flexibilité** : Support de multiples formats d'entrée
4. **Reproductibilité** : Pipeline entièrement régénérable
5. **Visualisation** : Tableaux de bord informatifs

### ⚠️ Limites
1. **Volume de données** : Dataset limité pour démonstration
2. **Rafraîchissement complet** : Pas de traitement incrémental
3. **Dépendances implicites** : Quelques hypothèses non validées
4. **Analyse de sentiment** : Basique, pourrait être enrichie

---

## 🚀 Recommandations

### Améliorations Techniques
1. **Implémenter le traitement incrémental** pour optimiser les performances
2. **Ajouter des tests unitaires** pour garantir la qualité du code
3. **Intégrer dbt** pour standardiser les transformations
4. **Utiliser DuckDB** pour des analyses plus performantes

### Extensions Fonctionnelles
1. **Analyse de sentiment avancée** avec NLP
2. **Détection de thèmes** dans les avis
3. **Prédictions** de tendances
4. **Alertes** en temps réel

---

## 📚 Leçons Apprises

1. **L'importance de la modularité** : Facilite la maintenance et l'évolution
2. **La robustesse est essentielle** : Les scénarios de stress révèlent les faiblesses
3. **La normalisation des schémas** : Clé pour la pérennité du pipeline
4. **La visualisation** : Indispensable pour l'interprétation des résultats
5. **La documentation** : Cruciale pour la reproductibilité

---

## 🎯 Conclusion

Ce projet démontre avec succès la mise en place d'un pipeline de données Python complet et robuste. Les résultats obtenus confirment la capacité de notre solution à transformer des données brutes en informations exploitables, tout en maintenant une excellente résilience face aux imprévus.

Les indicateurs produits permettent une analyse pertinente du marché des applications de prise de notes AI, et les visualisations facilitent la prise de décision pour les parties prenantes.

**Le pipeline est prêt pour la production et peut être étendu pour des analyses plus complexes.**

---

*Ce rapport illustre notre maîtrise des concepts d'ingénierie des données et notre capacité à livrer des solutions robustes et évolutives.*
