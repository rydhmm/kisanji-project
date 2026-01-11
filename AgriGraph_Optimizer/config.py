"""Configuration file for AgriGraph Optimizer"""
import torch

# Device configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Graph Module Config
GRAPH_CONFIG = {
    'num_nodes': 50,
    'in_channels': 4,
    'hidden_channels': 16,
    'out_channels': 2,
    'heads': 4,
    'gat_epochs': 50,
    'learning_rate': 0.01,
    'k_neighbors': 5
}

# GAN Module Config
GAN_CONFIG = {
    'z_dim': 100,
    'seq_len': 30,
    'feature_dim': 4,
    'epochs': 500,
    'batch_size': 64,
    'critic_iters': 5,
    'lambda_gp': 10,
    'lr': 2e-4,
    'beta1': 0.5,
    'beta2': 0.9,
    'num_real_samples': 500,
    'num_synthetic_samples': 200
}

# RL Module Config
RL_CONFIG = {
    'state_dim': 6,
    'action_dim': 2,
    'epochs': 200,
    'batch_size': 32,
    'gamma': 0.99,
    'lam': 0.95,
    'clip': 0.2,
    'lr_actor': 3e-4,
    'lr_critic': 3e-4,
    'ppo_epochs': 10
}

# File paths
DATA_PATH = 'data/farms.csv'
OUTPUT_PATH = 'outputs/'
