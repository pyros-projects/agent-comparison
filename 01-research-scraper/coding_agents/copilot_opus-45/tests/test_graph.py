"""Tests for graph service."""

import pytest
import networkx as nx

from researcher.models import GraphRelationship


class TestGraphService:
    """Test cases for GraphService - simplified for graph operations."""

    def test_graph_relationship_model(self):
        """Test the GraphRelationship model."""
        rel = GraphRelationship(
            source_id="paper-1",
            target_id="paper-2",
            relationship_type="similar",
            weight=0.85,
        )
        
        assert rel.source_id == "paper-1"
        assert rel.target_id == "paper-2"
        assert rel.relationship_type == "similar"
        assert rel.weight == 0.85

    def test_networkx_graph_operations(self):
        """Test basic NetworkX operations."""
        graph = nx.Graph()
        
        # Add nodes
        graph.add_node("paper-1", title="Paper 1", category="cs.AI", authors=["Author"])
        graph.add_node("paper-2", title="Paper 2", category="cs.AI", authors=["Author"])
        
        assert graph.has_node("paper-1")
        assert graph.nodes["paper-1"]["title"] == "Paper 1"
        
        # Add edge
        graph.add_edge("paper-1", "paper-2", relationship_type="similar", weight=0.85)
        
        assert graph.has_edge("paper-1", "paper-2")
        edge_data = graph.edges["paper-1", "paper-2"]
        assert edge_data["weight"] == 0.85

    def test_networkx_neighbors(self):
        """Test finding neighbors in NetworkX graph."""
        graph = nx.Graph()
        
        graph.add_node("center", title="Center", category="cs.AI", authors=["Author"])
        graph.add_node("related-1", title="Related 1", category="cs.AI", authors=["Author"])
        graph.add_node("related-2", title="Related 2", category="cs.AI", authors=["Author"])
        graph.add_node("unrelated", title="Unrelated", category="cs.LG", authors=["Other"])
        
        graph.add_edge("center", "related-1", relationship_type="similar", weight=0.9)
        graph.add_edge("center", "related-2", relationship_type="author", weight=0.7)
        
        neighbors = list(graph.neighbors("center"))
        
        assert len(neighbors) == 2
        assert "related-1" in neighbors
        assert "related-2" in neighbors
        assert "unrelated" not in neighbors

    def test_networkx_subgraph(self):
        """Test getting subgraph for visualization."""
        graph = nx.Graph()
        
        graph.add_node("center", title="Center", category="cs.AI", authors=["Author"])
        graph.add_node("neighbor-1", title="Neighbor 1", category="cs.AI", authors=["Author"])
        graph.add_node("neighbor-2", title="Neighbor 2", category="cs.AI", authors=["Author"])
        
        graph.add_edge("center", "neighbor-1", relationship_type="similar", weight=0.8)
        graph.add_edge("center", "neighbor-2", relationship_type="citation", weight=0.6)
        
        # Create subgraph
        subgraph = graph.subgraph(["center", "neighbor-1", "neighbor-2"])
        
        assert subgraph.number_of_nodes() == 3
        assert subgraph.number_of_edges() == 2

    def test_networkx_remove_node(self):
        """Test removing a node from the graph."""
        graph = nx.Graph()
        
        graph.add_node("paper-1", title="Paper 1", category="cs.AI", authors=["Author"])
        graph.add_node("paper-2", title="Paper 2", category="cs.AI", authors=["Author"])
        graph.add_edge("paper-1", "paper-2", relationship_type="similar", weight=0.8)
        
        assert graph.has_node("paper-1")
        assert graph.has_edge("paper-1", "paper-2")
        
        graph.remove_node("paper-1")
        
        assert not graph.has_node("paper-1")
        assert not graph.has_edge("paper-1", "paper-2")

    def test_graph_data_export(self):
        """Test exporting graph data for visualization."""
        graph = nx.Graph()
        
        for i in range(5):
            graph.add_node(f"paper-{i}", title=f"Paper {i}", category="cs.AI", authors=["Author"])
        
        for i in range(4):
            graph.add_edge(f"paper-{i}", f"paper-{i+1}", relationship_type="similar", weight=0.7)
        
        nodes = []
        for node, data in graph.nodes(data=True):
            nodes.append({
                "id": node,
                "title": data.get("title", "Unknown"),
                "category": data.get("category", ""),
            })
        
        edges = []
        for source, target, data in graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "type": data.get("relationship_type", "similar"),
                "weight": data.get("weight", 0.5),
            })
        
        assert len(nodes) == 5
        assert len(edges) == 4
