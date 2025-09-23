from __future__ import annotations
from ast import List
import numpy as np
from typing import Dict, Any
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import os


class PerformancePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            "complexity_score",
            "join_count",
            "subquery_count",
            "aggregation_count",
            "table_count",
            "estimated_rows",
        ]

    def extract_features(self, analysis: Dict[str, Any]) -> np.array:
        features = [
            analysis.get("complexity_score", 1.0),
            analysis.get("joins", 0),
            analysis.get("subqueries", 0),
            analysis.get("aggregations", 0),
            len(analysis.get("tables", [])),
            analysis.get("estimated_rows", 1000),
        ]
        return np.array(features).reshape(1, -1)

    def train(self, training_data: List[Dict]):
        if len(training_data) < 10:
            # Use synthetic data for initial training
            training_data = self._generate_synthetic_data()

        X = []
        y = []

        for data in training_data:
            features = self.extract_features(data["analysis"])
            X.append(features.flatten())
            y.append(data["execution_time"])

        X = np.array(X)
        y = np.array(y)

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True

    def predict(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        if not self.is_trained:
            self.train([])  # Train with synthetic data

        features = self.extract_features(analysis)
        features_scaled = self.scaler.transform(features)

        predicted_time = self.model.predict(features_scaled)[0]
        confidence = self._calculate_confidence(features_scaled)

        return {
            "predicted_time": max(0.01, predicted_time),  # Minimum 0.01s
            "confidence": confidence,
            "performance_category": self._categorize_performance(predicted_time),
        }

    def _generate_synthetic_data(self) -> List[Dict]:
        """Generate synthetic training data for initial model"""
        synthetic_data = []
        np.random.seed(42)

        for _ in range(100):
            complexity = np.random.uniform(1, 20)
            joins = np.random.poisson(2)
            subqueries = np.random.poisson(1)
            aggregations = np.random.poisson(1)
            tables = np.random.randint(1, 6)
            rows = np.random.randint(100, 10000)

            # Simulate execution time based on complexity
            base_time = 0.1
            execution_time = base_time * (
                complexity * 0.1
                + joins * 0.2
                + subqueries * 0.5
                + aggregations * 0.3
                + tables * 0.1
                + (rows / 1000) * 0.05
            ) + np.random.normal(0, 0.1)

            execution_time = max(0.01, execution_time)

            synthetic_data.append(
                {
                    "analysis": {
                        "complexity_score": complexity,
                        "joins": joins,
                        "subqueries": subqueries,
                        "aggregations": aggregations,
                        "tables": [f"table_{i}" for i in range(tables)],
                        "estimated_rows": rows,
                    },
                    "execution_time": execution_time,
                }
            )

        return synthetic_data

    def _calculate_confidence(self, features_scaled: np.array) -> float:
        # Simple confidence calculation based on feature values
        feature_variance = np.var(features_scaled)
        confidence = max(0.5, min(0.95, 1 - feature_variance))
        return confidence

    def _categorize_performance(self, predicted_time: float) -> str:
        if predicted_time < 0.1:
            return "Excellent"
        elif predicted_time < 0.5:
            return "Good"
        elif predicted_time < 2.0:
            return "Average"
        elif predicted_time < 5.0:
            return "Slow"
        else:
            return "Very Slow"
