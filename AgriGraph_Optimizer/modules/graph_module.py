"""
Graph Intelligence Module
Farmer Network Graph Intelligence using GAT (Graph Attention Networks)

Author: Rajat Pundir (@Rajatpundir7)
Role: Full Stack Developer & Database Architect - GNN Alert Propagation
"""
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import networkx as nx
import numpy as np
import pandas as pd
from torch_geometric.data import Data
from torch_geometric.utils import from_networkx
from torch_geometric.nn import GATConv
from torch_geometric.loader import DataLoader
from sklearn.neighbors import kneighbors_graph


class FarmerGAT(nn.Module):
    """Graph Attention Network for farmer network analysis"""
    def __init__(self, in_channels, hidden_channels, out_channels, heads=4):
        super(FarmerGAT, self).__init__()
        self.conv1 = GATConv(in_channels, hidden_channels, heads=heads, dropout=0.6)
        self.conv2 = GATConv(hidden_channels * heads, out_channels, heads=1, concat=False, dropout=0.6)
    
    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.elu(self.conv1(x, edge_index))
        x = F.elu(self.conv2(x, edge_index))
        return x  # Output embeddings for each node (e.g., risk features)


def build_farmer_graph(csv_path='data/farms.csv', num_nodes=100, device='cpu'):
    """
    Build farmer network graph from CSV data or generate synthetic data
    
    Args:
        csv_path: Path to farm data CSV
        num_nodes: Number of farm nodes if generating synthetic data
        device: Device to place the graph data on
    
    Returns:
        data: PyTorch Geometric Data object
        G: NetworkX graph object
    """
    print(f"[Graph Module] Building farmer graph...")
    
    # Load or generate sample data
    if os.path.exists(csv_path):
        print(f"[Graph Module] Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
    else:
        print(f"[Graph Module] Generating synthetic farm data for {num_nodes} nodes")
        df = pd.DataFrame({
            'id': range(num_nodes),
            'lat': np.random.uniform(40, 42, num_nodes),
            'lon': np.random.uniform(-75, -73, num_nodes),
            'soil_ph': np.random.uniform(5.5, 7.5, num_nodes),
            'crop_type': np.random.randint(0, 5, num_nodes)
        })
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        df.to_csv(csv_path, index=False)
        print(f"[Graph Module] Saved synthetic data to {csv_path}")
    
    # Build NetworkX graph
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_node(row['id'], x=torch.tensor([row['lat'], row['lon'], row['soil_ph'], row['crop_type']], dtype=torch.float))
    
    # Add edges based on proximity (k-nearest neighbors)
    coords = df[['lat', 'lon']].values
    adj = kneighbors_graph(coords, n_neighbors=5, mode='connectivity')
    edges = list(zip(*adj.nonzero()))
    G.add_edges_from(edges)
    
    print(f"[Graph Module] Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Convert to PyTorch Geometric format
    data = from_networkx(G)
    data = data.to(device)
    return data, G


def train_gat(model, data, optimizer, epochs=200, device='cpu'):
    """
    Train the Graph Attention Network
    
    Args:
        model: FarmerGAT model
        data: PyTorch Geometric Data object
        optimizer: Optimizer
        epochs: Number of training epochs
        device: Device to train on
    
    Returns:
        Trained model
    """
    print(f"[Graph Module] Training GAT for {epochs} epochs...")
    model.train()
    loader = DataLoader([data], batch_size=1)
    
    for epoch in range(epochs):
        for batch in loader:
            optimizer.zero_grad()
            out = model(batch)
            # Supervised task: Predict pest risk (using random labels as placeholder)
            labels = torch.rand(out.size(0), out.size(1), device=device)
            loss = F.mse_loss(out, labels)
            loss.backward()
            optimizer.step()
        
        if epoch % 50 == 0:
            print(f"[Graph Module] GAT Epoch {epoch}/{epochs}, Loss: {loss.item():.4f}")
    
    print("[Graph Module] GAT training completed!")
    return model


def get_graph_embeddings(model, data):
    """
    Get node embeddings from trained GAT model
    
    Args:
        model: Trained FarmerGAT model
        data: PyTorch Geometric Data object
    
    Returns:
        Node embeddings tensor
    """
    model.eval()
    with torch.no_grad():
        embeddings = model(data)
    print(f"[Graph Module] Generated embeddings: {embeddings.shape}")
    return embeddings
