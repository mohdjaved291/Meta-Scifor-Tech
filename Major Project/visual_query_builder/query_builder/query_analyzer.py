from __future__ import annotations
import sqlparse
import hashlib
import re
from typing import Dict, List, Any
import time


class QueryAnalyzer:
    def __init__(self):
        self.performance_weights = {
            "select": 1.0,
            "join": 2.5,
            "where": 1.2,
            "group_by": 2.0,
            "order_by": 1.5,
            "subquery": 3.0,
            "aggregate": 2.2,
        }

    def analyze_query(self, sql: str) -> Dict[str, Any]:
        parsed = sqlparse.parse(sql)[0]
        analysis = {
            "complexity_score": self._calculate_complexity(parsed),
            "operations": self._extract_operations(parsed),
            "tables": self._extract_tables(parsed),
            "joins": self._count_joins(parsed),
            "subqueries": self._count_subqueries(parsed),
            "aggregations": self._count_aggregations(parsed),
            "estimated_rows": self._estimate_rows(parsed),
            "optimization_suggestions": [],
        }

        analysis["optimization_suggestions"] = self._generate_suggestions(analysis)
        return analysis

    def _calculate_complexity(self, parsed) -> float:
        score = 1.0
        sql_lower = str(parsed).lower()

        # Count operations and apply weights
        for operation, weight in self.performance_weights.items():
            if operation == "join":
                count = len(re.findall(r"\bjoin\b", sql_lower))
            elif operation == "subquery":
                count = sql_lower.count("(select")
            elif operation == "aggregate":
                count = len(re.findall(r"\b(count|sum|avg|max|min)\b", sql_lower))
            else:
                count = sql_lower.count(operation.replace("_", " "))

            score += count * weight

        return round(score, 2)

    def _extract_operations(self, parsed) -> List[str]:
        operations = []
        sql_lower = str(parsed).lower()

        if "select" in sql_lower:
            operations.append("SELECT")
        if "join" in sql_lower:
            operations.append("JOIN")
        if "where" in sql_lower:
            operations.append("WHERE")
        if "group by" in sql_lower:
            operations.append("GROUP BY")
        if "order by" in sql_lower:
            operations.append("ORDER BY")
        if "having" in sql_lower:
            operations.append("HAVING")

        return operations

    def _extract_tables(self, parsed) -> List[str]:
        tables = []
        sql = str(parsed).lower()

        # Simple table extraction (can be improved with proper parsing)
        from_match = re.search(r"from\s+(\w+)", sql)
        if from_match:
            tables.append(from_match.group(1))

        join_matches = re.findall(r"join\s+(\w+)", sql)
        tables.extend(join_matches)

        return list(set(tables))

    def _count_joins(self, parsed) -> int:
        return len(re.findall(r"\bjoin\b", str(parsed).lower()))

    def _count_subqueries(self, parsed) -> int:
        return str(parsed).lower().count("(select")

    def _count_aggregations(self, parsed) -> int:
        sql_lower = str(parsed).lower()
        return len(re.findall(r"\b(count|sum|avg|max|min)\b", sql_lower))

    def _estimate_rows(self, parsed) -> int:
        # Simplified row estimation based on query complexity
        base_rows = 1000
        complexity_multiplier = self._calculate_complexity(parsed)
        return int(base_rows * complexity_multiplier)

    def _generate_suggestions(self, analysis: Dict) -> List[str]:
        suggestions = []

        if analysis["joins"] > 3:
            suggestions.append("Consider breaking complex joins into smaller queries")

        if analysis["subqueries"] > 2:
            suggestions.append("Review subqueries - consider using JOINs instead")

        if analysis["complexity_score"] > 10:
            suggestions.append("High complexity query - consider indexing key columns")

        if analysis["aggregations"] > 0 and "GROUP BY" not in analysis["operations"]:
            suggestions.append("Add GROUP BY clause when using aggregate functions")

        return suggestions
