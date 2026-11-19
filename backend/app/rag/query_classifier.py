import re
from typing import Dict, Any, List

class QueryClassifier:
    def __init__(self):
        self.code_keywords = {
            "function", "class", "method", "code", "implementation", "syntax",
            "import", "def", "defined", "definition", "signature", "return",
            "endpoint", "controller", "repository", "git", "commit", "diff",
            "branch", "pr", "pull request",
        }
        self.incident_keywords = {
            "incident", "outage", "timeout", "exception", "error", "crash",
            "failure", "postmortem", "alert", "severity", "root cause", "rca",
        }
        self.dependency_keywords = {
            "depend", "depends", "dependency", "caller", "call", "architecture",
            "topology", "upstream", "downstream", "blast radius", "service",
        }
        self.doc_keywords = {
            "runbook", "guide", "documentation", "doc", "readme", "how to",
            "setup", "configure", "step", "manual", "policy",
        }

        self.known_entities = [
            "payment-service", "auth-service", "api-gateway", "data-pipeline",
            "postgres-cluster", "redis-cluster", "stripe", "inc_demo_001",
        ]

    def analyze(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower()
        words = set(re.findall(r"[a-z0-9_\-]+", q_lower))

        code_score = len(words.intersection(self.code_keywords))
        incident_score = len(words.intersection(self.incident_keywords))
        dependency_score = len(words.intersection(self.dependency_keywords))
        doc_score = len(words.intersection(self.doc_keywords))

        # Discovered entities
        extracted_entities = []
        for ent in self.known_entities:
            if ent in q_lower or ent.replace("-", " ") in q_lower:
                extracted_entities.append(ent)

        # Primary intent classification
        scores = {
            "code": code_score,
            "incident": incident_score,
            "dependency": dependency_score,
            "documentation": doc_score,
        }
        max_type = max(scores, key=scores.get)
        max_score = scores[max_type]

        if max_score == 0:
            intent = "hybrid"
        else:
            tied = [k for k, v in scores.items() if v == max_score]
            if len(tied) > 1:
                intent = "hybrid"
            else:
                intent = max_type

        return {
            "query": query,
            "intent": intent,
            "intentScores": scores,
            "extractedEntities": extracted_entities,
            "suggestedSourceType": "code" if intent == "code" else ("runbook" if intent == "documentation" else None),
        }

# Singleton instance
query_classifier = QueryClassifier()
