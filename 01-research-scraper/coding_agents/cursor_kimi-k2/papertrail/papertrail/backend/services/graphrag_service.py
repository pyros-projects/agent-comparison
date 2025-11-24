import logging
import networkx as nx
from typing import List, Dict, Any, Tuple
import numpy as np
from ..models.database import db
from ..models.schemas import Relationship
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)

class GraphRAGService:
    """GraphRAG system for paper relationship analysis"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._build_graph()
    
    def _build_graph(self):
        """Build the knowledge graph from database"""
        try:
            # Clear existing graph
            self.graph.clear()
            
            # Add papers as nodes
            papers = db.papers.all()
            for paper in papers:
                self.graph.add_node(
                    paper['id'],
                    title=paper.get('title', ''),
                    authors=paper.get('authors', []),
                    abstract=paper.get('abstract', ''),
                    categories=paper.get('categories', []),
                    published_date=paper.get('published_date', ''),
                    keywords=paper.get('keywords', [])
                )
            
            # Add relationships as edges
            relationships = db.relationships.all()
            for rel in relationships:
                self.graph.add_edge(
                    rel['source_paper_id'],
                    rel['target_paper_id'],
                    relationship_type=rel['relationship_type'],
                    strength=rel['strength'],
                    metadata=rel.get('metadata', {})
                )
            
            logger.info(f"Graph built with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
            
        except Exception as e:
            logger.error(f"Failed to build graph: {e}")
    
    def add_paper_relationships(self, paper_id: str):
        """Add relationships for a new paper"""
        try:
            if paper_id not in self.graph:
                logger.warning(f"Paper {paper_id} not found in graph")
                return
            
            # Find similar papers
            embedding = embedding_service.get_embedding(paper_id)
            if embedding:
                similar_papers = embedding_service.search_similar(embedding, top_k=10)
                for similar in similar_papers:
                    if similar['paper_id'] != paper_id:
                        self._add_relationship(paper_id, similar['paper_id'], 
                                             'semantic_similarity', similar['similarity'])
            
            # Rebuild graph to include new relationships
            self._build_graph()
            
        except Exception as e:
            logger.error(f"Failed to add relationships for paper {paper_id}: {e}")
    
    def _add_relationship(self, source_id: str, target_id: str, rel_type: str, strength: float):
        """Add a relationship to the database"""
        try:
            relationship = Relationship(
                source_paper_id=source_id,
                target_paper_id=target_id,
                relationship_type=rel_type,
                strength=strength
            )
            
            db.relationships.insert(relationship.model_dump())
            logger.debug(f"Added relationship: {source_id} -> {target_id} [{rel_type}]")
            
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
    
    def get_related_papers(self, paper_id: str, relationship_types: List[str] = None) -> List[Dict[str, Any]]:
        """Get papers related to a given paper"""
        try:
            if paper_id not in self.graph:
                return []
            
            related = []
            
            # Get outgoing relationships
            if self.graph.has_node(paper_id):
                for neighbor in self.graph.neighbors(paper_id):
                    edges = self.graph[paper_id][neighbor]
                    for key, edge_data in edges.items():
                        if relationship_types is None or edge_data['relationship_type'] in relationship_types:
                            paper_data = self.graph.nodes[neighbor]
                            related.append({
                                'paper_id': neighbor,
                                'title': paper_data.get('title', ''),
                                'authors': paper_data.get('authors', []),
                                'relationship_type': edge_data['relationship_type'],
                                'strength': edge_data['strength'],
                                'published_date': paper_data.get('published_date', '')
                            })
            
            # Sort by strength
            related.sort(key=lambda x: x['strength'], reverse=True)
            return related
            
        except Exception as e:
            logger.error(f"Failed to get related papers: {e}")
            return []
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        try:
            if not self.graph:
                return {}
            
            stats = {
                'total_papers': len(self.graph.nodes),
                'total_relationships': len(self.graph.edges),
                'relationship_types': {},
                'connected_components': nx.number_weakly_connected_components(self.graph),
                'average_clustering': nx.average_clustering(self.graph.to_undirected())
            }
            
            # Count relationship types
            for _, _, edge_data in self.graph.edges(data=True):
                rel_type = edge_data.get('relationship_type', 'unknown')
                stats['relationship_types'][rel_type] = stats['relationship_types'].get(rel_type, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get graph stats: {e}")
            return {}

# Global GraphRAG service instance
graphrag_service = GraphRAGService()
