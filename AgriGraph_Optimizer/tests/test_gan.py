"""
Test Script for GAN Module
Tests the WGAN-GP synthetic scenario generation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.optim as optim
import matplotlib.pyplot as plt
from config import DEVICE, GAN_CONFIG, OUTPUT_PATH
from modules.gan_module import (
    Generator, Critic, generate_real_data, train_wgan, 
    generate_synthetic_scenarios, gradient_penalty
)


def test_gan_module():
    """Test GAN module"""
    print("=" * 80)
    print("Testing GAN Module")
    print("=" * 80)
    
    # Test 1: Generate real data
    print("\n[Test 1] Generating real data...")
    try:
        real_data = generate_real_data(
            num_samples=100,
            seq_len=GAN_CONFIG['seq_len'],
            feature_dim=GAN_CONFIG['feature_dim']
        )
        print(f"✓ Real data generated successfully")
        print(f"  - Shape: {real_data.shape}")
        print(f"  - Range: [{real_data.min().item():.3f}, {real_data.max().item():.3f}]")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 2: Initialize Generator
    print("\n[Test 2] Initializing Generator...")
    try:
        generator = Generator(
            z_dim=GAN_CONFIG['z_dim'],
            seq_len=GAN_CONFIG['seq_len'],
            feature_dim=GAN_CONFIG['feature_dim']
        ).to(DEVICE)
        print(f"✓ Generator initialized successfully")
        print(f"  - Parameters: {sum(p.numel() for p in generator.parameters())}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 3: Initialize Critic
    print("\n[Test 3] Initializing Critic...")
    try:
        critic = Critic(
            seq_len=GAN_CONFIG['seq_len'],
            feature_dim=GAN_CONFIG['feature_dim']
        ).to(DEVICE)
        print(f"✓ Critic initialized successfully")
        print(f"  - Parameters: {sum(p.numel() for p in critic.parameters())}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 4: Forward pass
    print("\n[Test 4] Testing forward passes...")
    try:
        z = torch.randn(10, GAN_CONFIG['z_dim'], device=DEVICE)
        fake = generator(z)
        critic_real = critic(real_data[:10].to(DEVICE))
        critic_fake = critic(fake)
        print(f"✓ Forward passes successful")
        print(f"  - Generated shape: {fake.shape}")
        print(f"  - Critic real output: {critic_real.mean().item():.3f}")
        print(f"  - Critic fake output: {critic_fake.mean().item():.3f}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 5: Gradient penalty
    print("\n[Test 5] Testing gradient penalty...")
    try:
        gp = gradient_penalty(critic, real_data[:10].to(DEVICE), fake.detach(), DEVICE)
        print(f"✓ Gradient penalty computed successfully")
        print(f"  - GP value: {gp.item():.3f}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 6: Train for a few epochs
    print("\n[Test 6] Training WGAN-GP (10 epochs)...")
    try:
        optimizer_g = optim.Adam(generator.parameters(), lr=GAN_CONFIG['lr'],
                                betas=(GAN_CONFIG['beta1'], GAN_CONFIG['beta2']))
        optimizer_c = optim.Adam(critic.parameters(), lr=GAN_CONFIG['lr'],
                                betas=(GAN_CONFIG['beta1'], GAN_CONFIG['beta2']))
        generator = train_wgan(
            generator, critic, real_data, optimizer_g, optimizer_c,
            epochs=10, batch_size=32, critic_iters=3, device=DEVICE
        )
        print(f"✓ Training successful")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 7: Generate synthetic scenarios
    print("\n[Test 7] Generating synthetic scenarios...")
    try:
        synthetic = generate_synthetic_scenarios(generator, num_samples=10, device=DEVICE)
        print(f"✓ Synthetic scenarios generated successfully")
        print(f"  - Shape: {synthetic.shape}")
        print(f"  - Range: [{synthetic.min():.3f}, {synthetic.max():.3f}]")
        
        # Visualize
        plt.figure(figsize=(10, 4))
        plt.plot(synthetic[0][:, 0], label='Temp', alpha=0.7)
        plt.plot(synthetic[0][:, 1], label='Rain', alpha=0.7)
        plt.plot(synthetic[0][:, 2], label='Pest', alpha=0.7)
        plt.legend()
        plt.title('Sample Synthetic Scenario')
        plt.grid(True)
        os.makedirs(OUTPUT_PATH, exist_ok=True)
        plt.savefig(os.path.join(OUTPUT_PATH, 'test_gan_output.png'))
        print(f"  - Visualization saved to {OUTPUT_PATH}test_gan_output.png")
        plt.close()
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✓ All GAN Module tests passed!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_gan_module()
    sys.exit(0 if success else 1)
