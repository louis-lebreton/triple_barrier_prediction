# 📈 Projet de Finance Quantitative – Genetic Algorithm-Optimized Triple Barrier Labeling for Bitcoin Trading Based on GBMs Stacking Prediction

## 📝 Description  
Ce projet explore l'application d'une méthode de labeling **Triple Barrier** introduite en 2018 par Marcos Lopez de Prado. Celle-ci est optimisée à l'aide d'un **Algorithme Génétique** pour maximiser les performances financières.
Le labeling est appliqué aux données **Bitcoin**, générant trois catégories de signaux : Buy, Hold et Sell.
Une fois l'ensemble de données labélisées construit, j'utilise un modèle de classification pour prédire les signaux à partir de données agrégées. En intégrant
des variables macroéconomiques, des scores de sentiment déduits des tweets à l'aide d'un
modèle BERTweet et des mesures spécifiques au Bitcoin, j'utilise un
modèle de **Stacking** combinant **3 GBMs (XGBoost, Light-GBM, CatBoost)** avec un meta-classifier **Softmax**. Les hyperparamètres de ces modèles sont optimisés via **optimisation Bayésienne**.
Les décisions de trading dérivées de ces prédictions sont évaluées à l'aide de métriques de performance financière telles que le **profit**, **le maximum drawdown** et le **Sharpe ratio**,
et sont comparées à des approches d'investissement plus traditionnelles telles que le simple Hold et le DCA (Dollars Cost Averaging).

## 📂 Contenu du projet  

### 🔹 **Notebooks Jupyter**  
- **`df_builder.ipynb`** : Construction des datasets d'entraînement et de test à partir des données disponibles.  
- **`predict.ipynb`** :  
  - Entraînement du modèle de prédiction  
  - Génération des prévisions  
  - Évaluation de la stratégie de trading  

### 🔹 **Script FastAPI**  
- **`main.py`** : Implémente une API basée sur **FastAPI** pour exposer le modèle et permettre des interactions externes.  

## 🚀 Installation & Exécution  
### 📌 Prérequis  
- Python 3.8+  
- Jupyter Notebook  
- FastAPI  
- pip ou conda pour la gestion des packages  

### 📥 Installation des dépendances  
Exécutez la commande suivante pour installer les dépendances nécessaires :  
```bash
pip install -r requirements.txt
