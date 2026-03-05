"""
AgriGraph Optimizer - Main Integration Script
Integrates Graph Intelligence, GANs, and RL for agricultural optimization

Author: Rajat Pundir (@Rajatpundir7)
Role: Full Stack Developer & Database Architect - GNN Alert System
"""
import os
import torch
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from config import DEVICE, GRAPH_CONFIG, GAN_CONFIG, RL_CONFIG, DATA_PATH, OUTPUT_PATH

# Import modules
from modules.graph_module import (
    FarmerGAT, build_farmer_graph, train_gat, get_graph_embeddings
)
from modules.gan_module import (
    Generator, Critic, generate_real_data, train_wgan, generate_synthetic_scenarios
)
from modules.rl_module import (
    AgriEnv, Actor, Critic as RLCritic, train_ppo, get_optimal_action
)


def main():
    """Main execution pipeline"""
    print("=" * 80)
    print("AgriGraph Optimizer - Integrated System")
    print("=" * 80)
    print(f"Device: {DEVICE}")
    print()
    
    # ========== STEP 1: Graph Intelligence ==========
    print("\n" + "=" * 80)
    print("STEP 1: Building Farmer Network Graph with GAT")
    print("=" * 80)
    
    graph_data, graph_nx = build_farmer_graph(
        csv_path=DATA_PATH,
        num_nodes=GRAPH_CONFIG['num_nodes'],
        device=DEVICE
    )
    
    gat_model = FarmerGAT(
        in_channels=GRAPH_CONFIG['in_channels'],
        hidden_channels=GRAPH_CONFIG['hidden_channels'],
        out_channels=GRAPH_CONFIG['out_channels'],
        heads=GRAPH_CONFIG['heads']
    ).to(DEVICE)
    
    optimizer_gat = optim.Adam(gat_model.parameters(), lr=GRAPH_CONFIG['learning_rate'])
    
    gat_model = train_gat(
        gat_model,
        graph_data,
        optimizer_gat,
        epochs=GRAPH_CONFIG['gat_epochs'],
        device=DEVICE
    )
    
    embeddings = get_graph_embeddings(gat_model, graph_data)
    print(f"✓ Graph embeddings generated: {embeddings.shape}")
    
    # Save embeddings
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    torch.save(embeddings, os.path.join(OUTPUT_PATH, 'graph_embeddings.pt'))
    print(f"✓ Embeddings saved to {OUTPUT_PATH}graph_embeddings.pt")
    
    # ========== STEP 2: GAN for Synthetic Scenarios ==========
    print("\n" + "=" * 80)
    print("STEP 2: Generating Synthetic Pest & Climate Scenarios with WGAN-GP")
    print("=" * 80)
    
    real_data = generate_real_data(
        num_samples=GAN_CONFIG['num_real_samples'],
        seq_len=GAN_CONFIG['seq_len'],
        feature_dim=GAN_CONFIG['feature_dim']
    )
    
    generator = Generator(
        z_dim=GAN_CONFIG['z_dim'],
        seq_len=GAN_CONFIG['seq_len'],
        feature_dim=GAN_CONFIG['feature_dim']
    ).to(DEVICE)
    
    critic = Critic(
        seq_len=GAN_CONFIG['seq_len'],
        feature_dim=GAN_CONFIG['feature_dim']
    ).to(DEVICE)
    
    optimizer_g = optim.Adam(generator.parameters(), lr=GAN_CONFIG['lr'], 
                            betas=(GAN_CONFIG['beta1'], GAN_CONFIG['beta2']))
    optimizer_c = optim.Adam(critic.parameters(), lr=GAN_CONFIG['lr'],
                            betas=(GAN_CONFIG['beta1'], GAN_CONFIG['beta2']))
    
    generator = train_wgan(
        generator, critic, real_data, optimizer_g, optimizer_c,
        epochs=GAN_CONFIG['epochs'],
        batch_size=GAN_CONFIG['batch_size'],
        critic_iters=GAN_CONFIG['critic_iters'],
        device=DEVICE,
        lambda_gp=GAN_CONFIG['lambda_gp']
    )
    
    synthetic_scenarios = generate_synthetic_scenarios(
        generator,
        num_samples=GAN_CONFIG['num_synthetic_samples'],
        device=DEVICE
    )
    print(f"✓ Synthetic scenarios generated: {synthetic_scenarios.shape}")
    
    # Save scenarios
    np.save(os.path.join(OUTPUT_PATH, 'synthetic_scenarios.npy'), synthetic_scenarios)
    print(f"✓ Scenarios saved to {OUTPUT_PATH}synthetic_scenarios.npy")
    
    # Visualize a sample scenario
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(synthetic_scenarios[0][:, 0], label='Temperature')
    plt.plot(synthetic_scenarios[0][:, 1], label='Rainfall')
    plt.title('Sample Synthetic Scenario - Weather')
    plt.xlabel('Day')
    plt.ylabel('Normalized Value')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(synthetic_scenarios[0][:, 2], label='Pest Level')
    plt.plot(synthetic_scenarios[0][:, 3], label='Climate Anomaly')
    plt.title('Sample Synthetic Scenario - Pests')
    plt.xlabel('Day')
    plt.ylabel('Normalized Value')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, 'sample_scenario.png'))
    print(f"✓ Sample scenario visualization saved to {OUTPUT_PATH}sample_scenario.png")
    
    # ========== STEP 3: RL Optimization ==========
    print("\n" + "=" * 80)
    print("STEP 3: Training PPO Agent for Optimal Dosage")
    print("=" * 80)
    
    env = AgriEnv(embeddings, synthetic_scenarios)
    print(f"✓ Environment created")
    print(f"  - State space: {env.observation_space.shape}")
    print(f"  - Action space: {env.action_space.shape}")
    
    actor = Actor(
        state_dim=RL_CONFIG['state_dim'],
        action_dim=RL_CONFIG['action_dim']
    ).to(DEVICE)
    
    rl_critic = RLCritic(
        state_dim=RL_CONFIG['state_dim']
    ).to(DEVICE)
    
    actor, rl_critic = train_ppo(
        env, actor, rl_critic,
        epochs=RL_CONFIG['epochs'],
        batch_size=RL_CONFIG['batch_size'],
        gamma=RL_CONFIG['gamma'],
        lr_actor=RL_CONFIG['lr_actor'],
        lr_critic=RL_CONFIG['lr_critic'],
        device=DEVICE
    )
    
    # Save models
    torch.save(actor.state_dict(), os.path.join(OUTPUT_PATH, 'actor_model.pt'))
    torch.save(rl_critic.state_dict(), os.path.join(OUTPUT_PATH, 'critic_model.pt'))
    print(f"✓ Models saved to {OUTPUT_PATH}")
    
    # ========== STEP 4: Inference Example ==========
    print("\n" + "=" * 80)
    print("STEP 4: Inference - Getting Optimal Recommendations")
    print("=" * 80)
    
    # Run inference for multiple scenarios
    num_tests = 5
    print(f"\nTesting {num_tests} random scenarios:")
    print("-" * 80)
    
    for i in range(num_tests):
        state = env.reset()
        optimal_action = get_optimal_action(actor, state, DEVICE)
        
        print(f"\nTest {i+1}:")
        print(f"  Initial Crop Health: {state[0]:.3f}")
        print(f"  Weather Conditions:")
        print(f"    - Temperature: {state[1]:.3f}")
        print(f"    - Rainfall: {state[2]:.3f}")
        print(f"    - Pest Level: {state[3]:.3f}")
        print(f"  Farm Network Embeddings: [{state[4]:.3f}, {state[5]:.3f}]")
        print(f"  ✓ Recommended Dosages:")
        print(f"    - Pesticide: {optimal_action[0]:.3f} (0-1 scale)")
        print(f"    - Fertilizer: {optimal_action[1]:.3f} (0-1 scale)")
    
    # ========== Summary ==========
    print("\n" + "=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)
    print("✓ Graph Intelligence: GAT trained with farmer network")
    print("✓ Synthetic Scenarios: WGAN-GP generated pest/climate data")
    print("✓ RL Optimization: PPO agent trained for optimal dosage")
    print(f"✓ All outputs saved to: {OUTPUT_PATH}")
    print("\nNext steps:")
    print("1. Run individual test scripts in 'tests/' folder")
    print("2. Analyze saved visualizations in 'outputs/' folder")
    print("3. Fine-tune hyperparameters in config.py")
    print("4. Replace synthetic data with real farm data in 'data/' folder")
    print("=" * 80)


if __name__ == "__main__":
    main()
