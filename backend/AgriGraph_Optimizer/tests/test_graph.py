"""
Test Script for Graph Module
Tests the farmer network graph construction and GAT training
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.optim as optim
from config import DEVICE, GRAPH_CONFIG, DATA_PATH
from modules.graph_module import FarmerGAT, build_farmer_graph, train_gat, get_graph_embeddings


def test_graph_module():
    """Test graph intelligence module"""
    print("=" * 80)
    print("Testing Graph Intelligence Module")
    print("=" * 80)
    
    # Test 1: Build graph
    print("\n[Test 1] Building farmer network graph...")
    try:
        graph_data, graph_nx = build_farmer_graph(
            csv_path=DATA_PATH,
            num_nodes=GRAPH_CONFIG['num_nodes'],
            device=DEVICE
        )
        print(f"✓ Graph built successfully")
        print(f"  - Number of nodes: {graph_nx.number_of_nodes()}")
        print(f"  - Number of edges: {graph_nx.number_of_edges()}")
        print(f"  - Node features shape: {graph_data.x.shape}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 2: Initialize GAT model
    print("\n[Test 2] Initializing GAT model...")
    try:
        gat_model = FarmerGAT(
            in_channels=GRAPH_CONFIG['in_channels'],
            hidden_channels=GRAPH_CONFIG['hidden_channels'],
            out_channels=GRAPH_CONFIG['out_channels'],
            heads=GRAPH_CONFIG['heads']
        ).to(DEVICE)
        print(f"✓ GAT model initialized successfully")
        print(f"  - Parameters: {sum(p.numel() for p in gat_model.parameters())}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 3: Forward pass
    print("\n[Test 3] Testing forward pass...")
    try:
        output = gat_model(graph_data)
        print(f"✓ Forward pass successful")
        print(f"  - Output shape: {output.shape}")
        print(f"  - Output range: [{output.min().item():.3f}, {output.max().item():.3f}]")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 4: Train for a few epochs
    print("\n[Test 4] Training GAT (5 epochs)...")
    try:
        optimizer = optim.Adam(gat_model.parameters(), lr=GRAPH_CONFIG['learning_rate'])
        gat_model = train_gat(gat_model, graph_data, optimizer, epochs=5, device=DEVICE)
        print(f"✓ Training successful")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 5: Get embeddings
    print("\n[Test 5] Extracting node embeddings...")
    try:
        embeddings = get_graph_embeddings(gat_model, graph_data)
        print(f"✓ Embeddings extracted successfully")
        print(f"  - Shape: {embeddings.shape}")
        print(f"  - Sample embedding: {embeddings[0].cpu().numpy()}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✓ All Graph Module tests passed!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_graph_module()
    sys.exit(0 if success else 1)
