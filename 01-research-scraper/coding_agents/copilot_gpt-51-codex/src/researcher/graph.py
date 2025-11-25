from __future__ import annotations

import itertools
import logging
from typing import Iterable, List

import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity

from .config import settings
from .models import GraphEdge, GraphNode, GraphResponse, Paper
from .storage import Storage

logger = logging.getLogger(__name__)


class GraphService:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.graph = nx.Graph()

    def rebuild(self) -> None:
        self.graph.clear()
        papers = list(self.storage.list_papers())
        for paper in papers:
            self.graph.add_node(
                paper.id,
                label=paper.title,
                category=paper.categories[0] if paper.categories else "unknown",
            )
        for left, right in itertools.combinations(papers, 2):
            weight, reason = self._edge_weight(left, right)
            if weight > 0:
                self.graph.add_edge(left.id, right.id, weight=weight, reason=reason)

    def _edge_weight(self, a: Paper, b: Paper) -> tuple[float, str]:
        weight = 0.0
        reasons: list[str] = []
        shared_authors = set(a.authors).intersection(b.authors)
        if shared_authors:
            weight += 0.3
            reasons.append(f"authors:{len(shared_authors)}")
        shared_categories = set(a.categories).intersection(b.categories)
        if shared_categories:
            weight += 0.2
            reasons.append(f"categories:{','.join(shared_categories)}")
        if a.vector and b.vector:
            sim = float(cosine_similarity([a.vector], [b.vector])[0][0])
            if sim >= settings.graph_similarity_threshold:
                weight += sim * 0.5
                reasons.append(f"similarity:{sim:.2f}")
        if not reasons:
            return (0.0, "")
        return (min(weight, 1.0), ";".join(reasons))

    def neighbors(self, paper_id: str, limit: int = 10) -> GraphResponse:
        if not self.graph:
            self.rebuild()
        if paper_id not in self.graph:
            self.rebuild()
        focus_nodes = {paper_id}
        for neighbor in list(self.graph.neighbors(paper_id))[:limit]:
            focus_nodes.add(neighbor)
            for secondary in list(self.graph.neighbors(neighbor))[: limit // 2 or 1]:
                focus_nodes.add(secondary)
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        for node_id in focus_nodes:
            data = self.graph.nodes[node_id]
            nodes.append(
                GraphNode(
                    id=node_id,
                    label=data.get("label", node_id),
                    category=data.get("category", "unknown"),
                )
            )
        for source, target, data in self.graph.edges(data=True):
            if source in focus_nodes and target in focus_nodes:
                edges.append(
                    GraphEdge(
                        source=source,
                        target=target,
                        reason=data.get("reason", ""),
                        weight=float(data.get("weight", 0.0)),
                    )
                )
        return GraphResponse(nodes=nodes, edges=edges)

    def cluster_summary(self) -> dict[str, int]:
        if not self.graph:
            self.rebuild()
        clusters: dict[str, int] = {}
        if self.graph.number_of_nodes() == 0:
            return clusters
        for idx, component in enumerate(nx.connected_components(self.graph), start=1):
            clusters[f"Cluster {idx}"] = len(component)
        return clusters

    def similar_papers(self, paper: Paper, top_k: int = 5) -> list[tuple[Paper, float]]:
        others = [p for p in self.storage.list_papers() if p.id != paper.id and p.vector]
        if not paper.vector or not others:
            return []
        matrix = [p.vector for p in others]
        scores = cosine_similarity([paper.vector], matrix)[0]
        results = sorted(zip(others, scores), key=lambda item: item[1], reverse=True)
        return [(p, float(score)) for p, score in results[:top_k]]

