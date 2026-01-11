"""
Test Script for RL Module
Tests the PPO agent and agriculture environment
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import numpy as np
from config import DEVICE, RL_CONFIG
from modules.rl_module import (
    AgriEnv, Actor, Critic, train_ppo, get_optimal_action, compute_gae
)


def test_rl_module():
    """Test RL module"""
    print("=" * 80)
    print("Testing RL Module")
    print("=" * 80)
    
    # Create dummy data
    print("\n[Setup] Creating dummy embeddings and scenarios...")
    embeddings = torch.randn(50, 2)  # 50 nodes, 2 features
    scenarios = np.random.randn(100, 30, 4)  # 100 scenarios, 30 steps, 4 features
    print(f"✓ Dummy data created")
    
    # Test 1: Initialize environment
    print("\n[Test 1] Initializing Agriculture Environment...")
    try:
        env = AgriEnv(embeddings, scenarios)
        print(f"✓ Environment initialized successfully")
        print(f"  - State space: {env.observation_space.shape}")
        print(f"  - Action space: {env.action_space.shape}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 2: Reset environment
    print("\n[Test 2] Testing environment reset...")
    try:
        state = env.reset()
        print(f"✓ Reset successful")
        print(f"  - Initial state: {state}")
        print(f"  - Crop health: {state[0]:.3f}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 3: Step through environment
    print("\n[Test 3] Testing environment step...")
    try:
        action = np.array([0.5, 0.5])  # Medium pesticide and fertilizer
        next_state, reward, done, info = env.step(action)
        print(f"✓ Step successful")
        print(f"  - Next state: {next_state}")
        print(f"  - Reward: {reward:.3f}")
        print(f"  - Done: {done}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 4: Initialize Actor
    print("\n[Test 4] Initializing Actor...")
    try:
        actor = Actor(
            state_dim=RL_CONFIG['state_dim'],
            action_dim=RL_CONFIG['action_dim']
        ).to(DEVICE)
        print(f"✓ Actor initialized successfully")
        print(f"  - Parameters: {sum(p.numel() for p in actor.parameters())}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 5: Initialize Critic
    print("\n[Test 5] Initializing Critic...")
    try:
        critic = Critic(
            state_dim=RL_CONFIG['state_dim']
        ).to(DEVICE)
        print(f"✓ Critic initialized successfully")
        print(f"  - Parameters: {sum(p.numel() for p in critic.parameters())}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 6: Forward pass
    print("\n[Test 6] Testing forward passes...")
    try:
        state_tensor = torch.from_numpy(state).float().to(DEVICE).unsqueeze(0)
        mu, sigma = actor(state_tensor)
        value = critic(state_tensor)
        print(f"✓ Forward passes successful")
        print(f"  - Actor output (mu): {mu.squeeze().cpu().detach().numpy()}")
        print(f"  - Actor output (sigma): {sigma.squeeze().cpu().detach().numpy()}")
        print(f"  - Critic output (value): {value.item():.3f}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 7: Compute GAE
    print("\n[Test 7] Testing GAE computation...")
    try:
        rewards = [0.5, 0.6, 0.7]
        values = [0.4, 0.5, 0.6]
        next_value = 0.7
        advantages = compute_gae(rewards, values, next_value)
        print(f"✓ GAE computed successfully")
        print(f"  - Advantages: {advantages}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 8: Train for a few epochs
    print("\n[Test 8] Training PPO (5 epochs)...")
    try:
        env_train = AgriEnv(embeddings, scenarios)
        actor_train, critic_train = train_ppo(
            env_train, actor, critic,
            epochs=5, batch_size=16, device=DEVICE
        )
        print(f"✓ Training successful")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 9: Get optimal action
    print("\n[Test 9] Testing inference...")
    try:
        state_test = env.reset()
        optimal_action = get_optimal_action(actor_train, state_test, DEVICE)
        print(f"✓ Inference successful")
        print(f"  - State: {state_test}")
        print(f"  - Optimal action (pesticide, fertilizer): {optimal_action}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 10: Run full episode
    print("\n[Test 10] Running full episode...")
    try:
        state = env.reset()
        total_reward = 0
        steps = 0
        done = False
        
        while not done and steps < 30:
            action = get_optimal_action(actor_train, state, DEVICE)
            state, reward, done, _ = env.step(action)
            total_reward += reward
            steps += 1
        
        print(f"✓ Episode completed successfully")
        print(f"  - Steps: {steps}")
        print(f"  - Total reward: {total_reward:.3f}")
        print(f"  - Final crop health: {state[0]:.3f}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✓ All RL Module tests passed!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_rl_module()
    sys.exit(0 if success else 1)
