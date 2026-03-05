# AgriGraph Optimizer

An integrated machine learning system for agricultural optimization combining **Graph Neural Networks**, **Generative Adversarial Networks**, and **Reinforcement Learning** to optimize pesticide and fertilizer dosages.

## 🌟 Features

- **Graph Intelligence**: Uses Graph Attention Networks (GAT) to model farmer networks and spatial relationships
- **Synthetic Scenario Generation**: Employs WGAN-GP to generate realistic pest and climate scenarios
- **Optimal Dosage Recommendation**: Leverages PPO (Proximal Policy Optimization) to recommend optimal pesticide and fertilizer dosages

## 📁 Project Structure

```
AgriGraph_Optimizer/
├── config.py                 # Configuration settings for all modules
├── main.py                   # Main integration script
├── requirements.txt          # Python dependencies
├── modules/                  # Core modules
│   ├── __init__.py
│   ├── graph_module.py      # Graph Intelligence (GAT)
│   ├── gan_module.py        # Synthetic scenario generation (WGAN-GP)
│   └── rl_module.py         # RL optimization (PPO)
├── tests/                    # Test scripts for each module
│   ├── test_graph.py
│   ├── test_gan.py
│   └── test_rl.py
├── data/                     # Data directory
│   └── farms.csv            # Farm data (auto-generated if missing)
└── outputs/                  # Output directory
    ├── graph_embeddings.pt
    ├── synthetic_scenarios.npy
    ├── actor_model.pt
    ├── critic_model.pt
    └── *.png                # Visualizations
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- CUDA (optional, for GPU support)

### Step 1: Clone or Navigate to Project
```powershell
cd "C:\Users\kulde\IIT DELHI\AgriGraph_Optimizer"
```

### Step 2: Install Dependencies
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install torch-geometric
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.0.0+cu118.html
pip install -r requirements.txt
```

**Note**: Adjust CUDA version (cu118) based on your system. Use CPU version if no GPU:
```powershell
pip install torch torchvision torchaudio
```

## 🧪 Testing Individual Modules

Test each component separately before running the full pipeline:

### Test Graph Module (GAT)
```powershell
python tests/test_graph.py
```
**Expected Output**: Graph construction, GAT training, and embedding generation

### Test GAN Module (WGAN-GP)
```powershell
python tests/test_gan.py
```
**Expected Output**: Synthetic scenario generation and visualization

### Test RL Module (PPO)
```powershell
python tests/test_rl.py
```
**Expected Output**: Environment interaction and agent training

## 🎯 Running the Full System

Run the integrated pipeline:
```powershell
python main.py
```

### What Happens:
1. **Step 1**: Builds farmer network graph and trains GAT (200 epochs)
2. **Step 2**: Generates synthetic pest/climate scenarios using WGAN-GP (5000 epochs)
3. **Step 3**: Trains PPO agent for optimal dosage recommendations (1000 epochs)
4. **Step 4**: Demonstrates inference with sample recommendations

### Expected Runtime:
- **CPU**: 30-60 minutes
- **GPU**: 10-20 minutes

## ⚙️ Configuration

Edit `config.py` to customize hyperparameters:

```python
# Graph Module
GRAPH_CONFIG = {
    'num_nodes': 100,           # Number of farm nodes
    'gat_epochs': 200,          # GAT training epochs
    'learning_rate': 0.01,
    # ...
}

# GAN Module
GAN_CONFIG = {
    'epochs': 5000,             # WGAN training epochs
    'batch_size': 64,
    # ...
}

# RL Module
RL_CONFIG = {
    'epochs': 1000,             # PPO training epochs
    'batch_size': 32,
    # ...
}
```

## 📊 Outputs

All outputs are saved to the `outputs/` directory:

- **graph_embeddings.pt**: Trained node embeddings from GAT
- **synthetic_scenarios.npy**: Generated pest/climate scenarios
- **actor_model.pt**: Trained PPO actor (policy network)
- **critic_model.pt**: Trained PPO critic (value network)
- **sample_scenario.png**: Visualization of synthetic scenario
- **test_*.png**: Test visualizations

## 🔍 Understanding the Output

### Inference Example:
```
Test 1:
  Initial Crop Health: 0.500
  Weather Conditions:
    - Temperature: 0.123
    - Rainfall: -0.456
    - Pest Level: 0.789
  Farm Network Embeddings: [0.234, -0.567]
  ✓ Recommended Dosages:
    - Pesticide: 0.678 (0-1 scale)
    - Fertilizer: 0.432 (0-1 scale)
```

**Interpretation**:
- Higher pest level → Higher pesticide recommendation
- Lower rainfall → Moderate fertilizer recommendation
- Network embeddings influence neighbor effects

## 📈 Customizing with Real Data

Replace synthetic data with real farm data:

1. **Farm Data**: Create `data/farms.csv` with columns:
   - `id`: Farm identifier
   - `lat`: Latitude
   - `lon`: Longitude
   - `soil_ph`: Soil pH level
   - `crop_type`: Crop type (integer encoded)

2. **Climate Data**: Modify `gan_module.py` → `generate_real_data()` to load historical weather and pest data

## 🐛 Troubleshooting

### Issue: "No module named 'torch_geometric'"
**Solution**: Install PyTorch Geometric properly:
```powershell
pip install torch-geometric
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.0.0+cu118.html
```

### Issue: Out of memory (GPU)
**Solution**: Reduce batch sizes in `config.py`:
```python
GAN_CONFIG['batch_size'] = 32  # Reduce from 64
RL_CONFIG['batch_size'] = 16   # Reduce from 32
```

### Issue: Training takes too long
**Solution**: Reduce epochs for testing:
```python
GRAPH_CONFIG['gat_epochs'] = 50    # Reduce from 200
GAN_CONFIG['epochs'] = 1000        # Reduce from 5000
RL_CONFIG['epochs'] = 200          # Reduce from 1000
```

## 📚 Technical Details

### Graph Intelligence (GAT)
- Multi-head attention mechanism (4 heads)
- K-nearest neighbors for edge construction (k=5)
- ELU activation for better gradient flow

### GAN (WGAN-GP)
- Wasserstein distance with gradient penalty
- Critic iterations: 5 per generator update
- Feature dimensions: Temperature, Rainfall, Pest Level, Climate Anomaly

### RL (PPO)
- Actor-Critic architecture
- Generalized Advantage Estimation (GAE)
- Continuous action space [0, 1] for dosages

## 🤝 Next Steps

1. **Fine-tune hyperparameters** in `config.py` based on your data
2. **Add real farm data** to `data/` directory
3. **Extend features**: Add soil moisture, crop variety, seasonal patterns
4. **Deploy**: Integrate with farming management systems
5. **Validate**: Compare recommendations with expert agronomists

## 📄 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- PyTorch Geometric for graph neural networks
- OpenAI Gym for RL environment
- PyTorch for deep learning framework

---

**Questions or Issues?** Check the test outputs first, then review configuration settings.
