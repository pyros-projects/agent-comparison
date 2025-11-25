"""Knowledge graph service using NetworkX."""

import logging
from typing import Optional
import networkx as nx
import numpy as np

from researcher.models import Paper, GraphRelationship
from researcher.services.database import get_database
from researcher.services.embedding import get_embedding_service

logger = logging.getLogger("papertrail.graph")


class GraphService:
    """Knowledge graph service for paper relationships."""

    _instance: Optional["GraphService"] = None

    def __new__(cls) -> "GraphService":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize graph service."""
        if self._initialized:
            return

        logger.info("Initializing knowledge graph")
        self.graph = nx.Graph()
        self._initialized = True
        self._load_graph()

    def _load_graph(self) -> None:
        """Load graph from database."""
        db = get_database()
        
        # Add all papers as nodes
        papers = db.get_all_papers(limit=10000)
        for paper in papers:
            self.graph.add_node(
                paper.id,
                title=paper.title,
                category=paper.primary_category,
                authors=paper.authors,
            )
        
        # Add all relationships as edges
        relationships = db.get_all_relationships()
        for rel in relationships:
            self.graph.add_edge(
                rel.source_id,
                rel.target_id,
                relationship_type=rel.relationship_type,
                weight=rel.weight,
                metadata=rel.metadata,
            )
        
        logger.info(
            f"Loaded graph with {self.graph.number_of_nodes()} nodes "
            f"and {self.graph.number_of_edges()} edges"
        )

    def add_paper(self, paper: Paper) -> None:
        """Add a paper to the graph."""
        logger.debug(f"Adding paper to graph: {paper.id}")
        self.graph.add_node(
            paper.id,
            title=paper.title,
            category=paper.primary_category,
            authors=paper.authors,
        )

    def add_relationship(self, rel: GraphRelationship) -> None:
        """Add a relationship to the graph."""
        logger.debug(
            f"Adding relationship: {rel.source_id} -> {rel.target_id} ({rel.relationship_type})"
        )
        self.graph.add_edge(
            rel.source_id,
            rel.target_id,
            relationship_type=rel.relationship_type,
            weight=rel.weight,
            metadata=rel.metadata,
        )
        
        # Also persist to database
        db = get_database()
        if not db.relationship_exists(rel.source_id, rel.target_id, rel.relationship_type):
            db.add_relationship(rel)

    def get_related_papers(
        self,
        paper_id: str,
        max_depth: int = 2,
        max_papers: int = 20,
    ) -> list[dict]:
        """Get papers related to a given paper."""
        if paper_id not in self.graph:
            return []

        related = []
        visited = {paper_id}
        
        # BFS to find related papers
        current_level = [paper_id]
        depth = 0
        
        while current_level and depth < max_depth and len(related) < max_papers:
            next_level = []
            for node in current_level:
                for neighbor in self.graph.neighbors(node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        edge_data = self.graph.get_edge_data(node, neighbor)
                        related.append({
                            "paper_id": neighbor,
                            "relationship_type": edge_data.get("relationship_type", "similar"),
                            "weight": edge_data.get("weight", 0.5),
                            "depth": depth + 1,
                            **self.graph.nodes[neighbor],
                        })
                        next_level.append(neighbor)
            current_level = next_level
            depth += 1
        
        # Sort by weight descending
        related.sort(key=lambda x: x.get("weight", 0), reverse=True)
        return related[:max_papers]

    def find_author_connections(self, paper_id: str) -> list[dict]:
        """Find papers by the same authors."""
        if paper_id not in self.graph:
            return []

        paper_authors = set(self.graph.nodes[paper_id].get("authors", []))
        if not paper_authors:
            return []

        connections = []
        for node, data in self.graph.nodes(data=True):
            if node == paper_id:
                continue
            node_authors = set(data.get("authors", []))
            shared = paper_authors & node_authors
            if shared:
                connections.append({
                    "paper_id": node,
                    "shared_authors": list(shared),
                    "title": data.get("title", ""),
                })
        
        return connections

    def find_category_papers(self, paper_id: str, limit: int = 10) -> list[dict]:
        """Find papers in the same category."""
        if paper_id not in self.graph:
            return []

        category = self.graph.nodes[paper_id].get("category", "")
        if not category:
            return []

        same_category = []
        for node, data in self.graph.nodes(data=True):
            if node == paper_id:
                continue
            if data.get("category") == category:
                same_category.append({
                    "paper_id": node,
                    "title": data.get("title", ""),
                    "category": category,
                })
        
        return same_category[:limit]

    def get_graph_data(self, paper_id: Optional[str] = None) -> dict:
        """Get graph data for visualization."""
        if paper_id:
            # Get subgraph around paper
            related = self.get_related_papers(paper_id, max_depth=2, max_papers=30)
            node_ids = {paper_id} | {r["paper_id"] for r in related}
            subgraph = self.graph.subgraph(node_ids)
        else:
            subgraph = self.graph

        nodes = []
        for node, data in subgraph.nodes(data=True):
            nodes.append({
                "id": node,
                "title": data.get("title", "Unknown"),
                "category": data.get("category", ""),
                "is_center": node == paper_id,
            })

        edges = []
        for source, target, data in subgraph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "type": data.get("relationship_type", "similar"),
                "weight": data.get("weight", 0.5),
            })

        return {"nodes": nodes, "edges": edges}

    def get_topic_clusters(self) -> list[dict]:
        """Get topic clusters using community detection."""
        if self.graph.number_of_nodes() < 2:
            return []

        try:
            # Use Louvain community detection
            import networkx.algorithms.community as nx_comm
            
            communities = nx_comm.louvain_communities(self.graph)
            
            clusters = []
            for i, community in enumerate(communities):
                papers_in_cluster = []
                categories = {}
                
                for node in community:
                    data = self.graph.nodes[node]
                    papers_in_cluster.append({
                        "id": node,
                        "title": data.get("title", ""),
                    })
                    cat = data.get("category", "unknown")
                    categories[cat] = categories.get(cat, 0) + 1
                
                # Determine main category
                main_category = max(categories.items(), key=lambda x: x[1])[0] if categories else "unknown"
                
                clusters.append({
                    "id": i,
                    "main_category": main_category,
                    "paper_count": len(community),
                    "papers": papers_in_cluster[:10],  # Top 10 papers
                    "categories": categories,
                })
            
            return clusters
        except Exception as e:
            logger.error(f"Error detecting communities: {e}")
            return []

    def rebuild_graph(self) -> None:
        """Rebuild the graph from database."""
        logger.info("Rebuilding knowledge graph")
        self.graph.clear()
        self._load_graph()


# Singleton instance
def get_graph_service() -> GraphService:
    """Get the graph service instance."""
    return GraphService()
