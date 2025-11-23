"""GraphRAG - Knowledge graph for paper relationships."""

import networkx as nx
from typing import List, Dict, Any, Tuple

from researcher.models import PaperRelationship, Paper
from researcher.database import db
from researcher.embeddings import embedding_service
from researcher.logger import setup_logger

logger = setup_logger(__name__)


class GraphRAGService:
    """Knowledge graph service for paper relationships."""
    
    def __init__(self):
        """Initialize graph service."""
        self.graph = nx.Graph()
        self._load_graph()
    
    def _load_graph(self):
        """Load graph from database."""
        logger.info("Loading knowledge graph from database")
        
        # Add nodes (papers)
        papers = db.get_all_papers()
        for paper in papers:
            self.graph.add_node(
                paper.id,
                title=paper.title,
                authors=[a.name for a in paper.authors],
                categories=paper.categories
            )
        
        # Add edges (relationships)
        relationships = db.get_all_relationships()
        for rel in relationships:
            self.graph.add_edge(
                rel.source_id,
                rel.target_id,
                type=rel.relationship_type,
                weight=rel.weight
            )
        
        logger.info(f"Loaded graph: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
    
    def build_relationships(self, paper: Paper):
        """Build relationships for a new paper.
        
        Args:
            paper: Paper to build relationships for
        """
        logger.info(f"Building relationships for: {paper.title}")
        
        # Add paper node
        self.graph.add_node(
            paper.id,
            title=paper.title,
            authors=[a.name for a in paper.authors],
            categories=paper.categories
        )
        
        all_papers = db.get_all_papers()
        
        # Find shared authors
        for other_paper in all_papers:
            if other_paper.id == paper.id:
                continue
            
            shared_authors = self._find_shared_authors(paper, other_paper)
            if shared_authors:
                self._add_relationship(
                    paper.id,
                    other_paper.id,
                    "shared_author",
                    len(shared_authors) / max(len(paper.authors), len(other_paper.authors)),
                    {"shared_authors": shared_authors}
                )
        
        # Find topic similarity using embeddings
        paper_embedding = db.get_embedding(paper.id)
        if paper_embedding:
            all_embeddings = db.get_all_embeddings()
            
            for other_embedding in all_embeddings:
                if other_embedding.paper_id == paper.id:
                    continue
                
                similarity = embedding_service.compute_similarity(
                    paper_embedding.embedding,
                    other_embedding.embedding
                )
                
                # Add edge if similarity is high enough
                if similarity > 0.7:
                    self._add_relationship(
                        paper.id,
                        other_embedding.paper_id,
                        "topic_similarity",
                        similarity
                    )
        
        logger.info(f"Built relationships for {paper.title}")
    
    def _find_shared_authors(self, paper1: Paper, paper2: Paper) -> List[str]:
        """Find authors shared between two papers."""
        authors1 = {a.name.lower() for a in paper1.authors}
        authors2 = {a.name.lower() for a in paper2.authors}
        return list(authors1 & authors2)
    
    def _add_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        weight: float,
        metadata: Dict[str, Any] = None
    ):
        """Add a relationship to the graph and database."""
        # Add to graph
        self.graph.add_edge(source_id, target_id, type=rel_type, weight=weight)
        
        # Save to database
        relationship = PaperRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=rel_type,
            weight=weight,
            metadata=metadata
        )
        db.insert_relationship(relationship)
    
    def get_related_papers(self, paper_id: str, max_results: int = 10) -> List[Tuple[str, float, str]]:
        """Get papers related to a given paper.
        
        Args:
            paper_id: Paper ID
            max_results: Maximum number of results
            
        Returns:
            List of (paper_id, weight, relationship_type) tuples
        """
        if paper_id not in self.graph:
            logger.warning(f"Paper {paper_id} not in graph")
            return []
        
        # Get all neighbors
        neighbors = []
        for neighbor in self.graph.neighbors(paper_id):
            edge_data = self.graph.get_edge_data(paper_id, neighbor)
            neighbors.append((
                neighbor,
                edge_data.get('weight', 1.0),
                edge_data.get('type', 'unknown')
            ))
        
        # Sort by weight
        neighbors.sort(key=lambda x: x[1], reverse=True)
        
        return neighbors[:max_results]
    
    def get_graph_data(self, paper_id: str, depth: int = 1) -> Dict[str, Any]:
        """Get graph data for visualization.
        
        Args:
            paper_id: Central paper ID
            depth: Graph depth (levels of relationships)
            
        Returns:
            Dictionary with nodes and edges for visualization
        """
        if paper_id not in self.graph:
            return {"nodes": [], "edges": []}
        
        # Get subgraph using BFS
        nodes_to_include = {paper_id}
        current_level = {paper_id}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                neighbors = set(self.graph.neighbors(node))
                next_level.update(neighbors)
            nodes_to_include.update(next_level)
            current_level = next_level
        
        # Build nodes list
        nodes = []
        for node_id in nodes_to_include:
            node_data = self.graph.nodes[node_id]
            nodes.append({
                "id": node_id,
                "title": node_data.get("title", "Unknown"),
                "is_center": node_id == paper_id
            })
        
        # Build edges list
        edges = []
        for source, target in self.graph.edges():
            if source in nodes_to_include and target in nodes_to_include:
                edge_data = self.graph.get_edge_data(source, target)
                edges.append({
                    "source": source,
                    "target": target,
                    "type": edge_data.get("type", "unknown"),
                    "weight": edge_data.get("weight", 1.0)
                })
        
        return {"nodes": nodes, "edges": edges}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "avg_degree": sum(dict(self.graph.degree()).values()) / max(self.graph.number_of_nodes(), 1)
        }


# Global graph service instance
graph_service = GraphRAGService()
