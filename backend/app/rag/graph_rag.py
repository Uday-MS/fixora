import os
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("fixora.rag.graph")

class GraphRAGService:
    def __init__(self):
        self.neo4j_uri = getattr(settings, "NEO4J_URI", None) or os.getenv("NEO4J_URI")
        self.neo4j_user = getattr(settings, "NEO4J_USER", None) or os.getenv("NEO4J_USER")
        self.neo4j_password = getattr(settings, "NEO4J_PASSWORD", None) or os.getenv("NEO4J_PASSWORD")
        self.is_remote: bool = False
        self._driver = self._init_driver()
        self._local_graph: Dict[str, Dict[str, Any]] = {}
        self._init_graph()

    def _init_driver(self):
        if self.neo4j_uri and str(self.neo4j_uri).strip():
            try:
                from neo4j import GraphDatabase
                auth = (self.neo4j_user, self.neo4j_password) if (self.neo4j_user and self.neo4j_password) else None
                driver = GraphDatabase.driver(self.neo4j_uri, auth=auth)
                driver.verify_connectivity()
                self.is_remote = True
                logger.info("Connected to remote Neo4j graph database at %s", self.neo4j_uri)
                return driver
            except Exception as e:
                logger.warning(
                    "Remote Neo4j unavailable (%s). Falling back to in-memory topology graph.",
                    str(e),
                )
        else:
            logger.info("NEO4J_URI not configured. Using in-memory topology graph fallback.")

        self.is_remote = False
        return None

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "connected (remote)" if self.is_remote else "in-memory (fallback active)",
            "persistent": self.is_remote,
            "mode": "remote" if self.is_remote else "in-memory",
            "description": (
                "Hosted Neo4j Graph Database"
                if self.is_remote
                else "Local in-memory software topology (ephemeral GraphRAG fallback)"
            ),
        }

    def _init_graph(self):
        """
        Initialize the graph model with benchmark software topology:
        Projects, Repositories, Services, Dependencies, Commits, and Incidents.
        """
        # Node structures
        self._nodes: Dict[str, Dict[str, Any]] = {
            "proj_demo_001": {"type": "Project", "name": "Acme Core Platform"},
            "repo_payment": {"type": "Repository", "name": "payment-service", "project": "proj_demo_001"},
            "repo_auth": {"type": "Repository", "name": "auth-service", "project": "proj_demo_001"},
            "repo_gateway": {"type": "Repository", "name": "api-gateway", "project": "proj_demo_001"},
            "service_payment": {"type": "Service", "name": "payment-service", "tier": "backend", "runtime": "go"},
            "service_auth": {"type": "Service", "name": "auth-service", "tier": "backend", "runtime": "python"},
            "service_gateway": {"type": "Service", "name": "api-gateway", "tier": "gateway", "runtime": "typescript"},
            "service_db": {"type": "Database", "name": "postgres-cluster", "tier": "storage"},
            "service_redis": {"type": "Cache", "name": "redis-cluster", "tier": "cache"},
            "commit_c48a": {"type": "Commit", "sha": "c48a92f", "message": "Optimize connection pool keep-alive timeout"},
            "inc_demo_001": {"type": "Incident", "id": "inc_demo_001", "title": "Payment Gateway Timeout Surge", "severity": "CRITICAL"},
        }

        # Directed Edges: (source, rel, target)
        self._edges: List[Dict[str, str]] = [
            {"source": "proj_demo_001", "rel": "CONTAINS_REPO", "target": "repo_payment"},
            {"source": "proj_demo_001", "rel": "CONTAINS_REPO", "target": "repo_auth"},
            {"source": "proj_demo_001", "rel": "CONTAINS_REPO", "target": "repo_gateway"},
            {"source": "repo_payment", "rel": "PROVIDES_SERVICE", "target": "service_payment"},
            {"source": "repo_auth", "rel": "PROVIDES_SERVICE", "target": "service_auth"},
            {"source": "repo_gateway", "rel": "PROVIDES_SERVICE", "target": "service_gateway"},
            {"source": "service_gateway", "rel": "DEPENDS_ON", "target": "service_auth"},
            {"source": "service_gateway", "rel": "DEPENDS_ON", "target": "service_payment"},
            {"source": "service_payment", "rel": "DEPENDS_ON", "target": "service_db"},
            {"source": "service_payment", "rel": "DEPENDS_ON", "target": "service_redis"},
            {"source": "service_auth", "rel": "DEPENDS_ON", "target": "service_redis"},
            {"source": "repo_payment", "rel": "HAS_COMMIT", "target": "commit_c48a"},
            {"source": "inc_demo_001", "rel": "AFFECTED_SERVICE", "target": "service_payment"},
            {"source": "inc_demo_001", "rel": "LINKED_COMMIT", "target": "commit_c48a"},
        ]

    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any]):
        self._nodes[node_id] = {"type": node_type, **properties}

    def add_edge(self, source_id: str, rel: str, target_id: str):
        self._edges.append({"source": source_id, "rel": rel, "target": target_id})

    def get_service_dependencies(self, service_name: str) -> Dict[str, Any]:
        """
        Find downstream dependencies and upstream callers for a service.
        """
        s_id = f"service_{service_name.replace('-service', '').replace('-', '_')}"
        if s_id not in self._nodes:
            # Look up by name
            for k, v in self._nodes.items():
                if v.get("name") == service_name:
                    s_id = k
                    break

        downstream = []
        upstream = []

        for edge in self._edges:
            if edge["source"] == s_id and edge["rel"] == "DEPENDS_ON":
                target_node = self._nodes.get(edge["target"], {})
                downstream.append(target_node.get("name", edge["target"]))
            elif edge["target"] == s_id and edge["rel"] == "DEPENDS_ON":
                source_node = self._nodes.get(edge["source"], {})
                upstream.append(source_node.get("name", edge["source"]))

        return {
            "service": service_name,
            "downstreamDependencies": downstream,
            "upstreamCallers": upstream,
            "dependencyCount": len(downstream),
            "blastRadiusCount": len(upstream),
        }

    def get_incident_blast_radius(self, incident_id: str) -> Dict[str, Any]:
        """
        Query graph path: Incident -> Affected Service -> Upstream Callers -> Linked Commit.
        """
        affected_services = []
        linked_commits = []

        for edge in self._edges:
            if edge["source"] == incident_id:
                if edge["rel"] == "AFFECTED_SERVICE":
                    s_node = self._nodes.get(edge["target"], {})
                    affected_services.append(s_node.get("name", edge["target"]))
                elif edge["rel"] == "LINKED_COMMIT":
                    c_node = self._nodes.get(edge["target"], {})
                    linked_commits.append(c_node.get("sha", edge["target"]))

        # For affected services, find callers
        impacted_callers = []
        for s in affected_services:
            deps = self.get_service_dependencies(s)
            impacted_callers.extend(deps.get("upstreamCallers", []))

        return {
            "incidentId": incident_id,
            "affectedServices": affected_services,
            "linkedCommits": linked_commits,
            "impactedCallers": list(set(impacted_callers)),
        }

    def query_graph_context(self, entities: List[str]) -> List[str]:
        """
        Generate natural language GraphRAG context lines for entities mentioned in query.
        """
        context_lines = []
        for entity in entities:
            clean_e = entity.lower().strip()
            # Check services
            for node_id, data in self._nodes.items():
                node_name = data.get("name", "").lower()
                if clean_e in node_name:
                    deps = self.get_service_dependencies(data.get("name"))
                    if deps["downstreamDependencies"]:
                        context_lines.append(
                            f"[GraphRAG] Service '{data.get('name')}' directly depends on: {', '.join(deps['downstreamDependencies'])}"
                        )
                    if deps["upstreamCallers"]:
                        context_lines.append(
                            f"[GraphRAG] Upstream services calling '{data.get('name')}': {', '.join(deps['upstreamCallers'])}"
                        )

            # Check incidents
            if "inc" in clean_e or "incident" in clean_e:
                for edge in self._edges:
                    if edge["rel"] == "AFFECTED_SERVICE" and edge["source"] in clean_e:
                        s_name = self._nodes.get(edge["target"], {}).get("name")
                        context_lines.append(f"[GraphRAG] Incident '{edge['source']}' affected service '{s_name}'")

        return context_lines

# Singleton instance
graph_rag = GraphRAGService()
graph_rag_service = graph_rag
