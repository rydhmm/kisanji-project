"""
GAN Module
Generative Adversarial Networks for Synthetic Pest & Climate Scenario Generation
Using WGAN-GP (Wasserstein GAN with Gradient Penalty) for stability
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np


class Generator(nn.Module):
    """Generator network for creating synthetic pest and climate scenarios"""
    def __init__(self, z_dim=100, seq_len=30, feature_dim=4):
        super(Generator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(z_dim, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, seq_len * feature_dim),
            nn.Tanh()
        )
        self.seq_len = seq_len
        self.feature_dim = feature_dim
    
    def forward(self, z):
        return self.model(z).view(-1, self.seq_len, self.feature_dim)


class Critic(nn.Module):
    """Critic network for WGAN-GP"""
    def __init__(self, seq_len=30, feature_dim=4):
        super(Critic, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(seq_len * feature_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 1)
        )
    
    def forward(self, x):
        return self.model(x.view(x.size(0), -1))


def gradient_penalty(critic, real, fake, device, lambda_gp=10):
    """
    Calculate gradient penalty for WGAN-GP
    
    Args:
        critic: Critic network
        real: Real data samples
        fake: Generated fake samples
        device: Device to perform calculations on
        lambda_gp: Gradient penalty coefficient
    
    Returns:
        Gradient penalty loss
    """
    alpha = torch.rand(real.size(0), 1, 1, device=device).expand_as(real)
    interpolates = alpha * real + (1 - alpha) * fake
    interpolates.requires_grad_(True)
    disc_interpolates = critic(interpolates)
    gradients = torch.autograd.grad(
        outputs=disc_interpolates,
        inputs=interpolates,
        grad_outputs=torch.ones_like(disc_interpolates),
        create_graph=True,
        retain_graph=True
    )[0]
    gradients = gradients.view(gradients.size(0), -1)
    return ((gradients.norm(2, dim=1) - 1) ** 2).mean() * lambda_gp


def generate_real_data(num_samples=1000, seq_len=30, feature_dim=4):
    """
    Generate realistic-looking climate and pest data (placeholder)
    In production, replace with actual historical data
    
    Args:
        num_samples: Number of sequences to generate
        seq_len: Length of each sequence
        feature_dim: Number of features (temp, rain, pest_level, climate_anomaly)
    
    Returns:
        Tensor of shape (num_samples, seq_len, feature_dim)
    """
    print(f"[GAN Module] Generating {num_samples} real data samples...")
    # Simulate realistic patterns
    real_data = torch.randn(num_samples, seq_len, feature_dim)
    # Add some structure (e.g., seasonal patterns)
    t = torch.linspace(0, 2 * np.pi, seq_len).unsqueeze(0).unsqueeze(-1)
    real_data += 0.3 * torch.sin(t.expand(num_samples, seq_len, feature_dim))
    return real_data


def train_wgan(generator, critic, real_data, optimizer_g, optimizer_c, 
               epochs=5000, batch_size=64, critic_iters=5, device='cpu', lambda_gp=10):
    """
    Train WGAN-GP for synthetic scenario generation
    
    Args:
        generator: Generator network
        critic: Critic network
        real_data: Real training data
        optimizer_g: Generator optimizer
        optimizer_c: Critic optimizer
        epochs: Number of training epochs
        batch_size: Batch size
        critic_iters: Number of critic iterations per generator iteration
        device: Device to train on
        lambda_gp: Gradient penalty coefficient
    
    Returns:
        Trained generator
    """
    print(f"[GAN Module] Training WGAN-GP for {epochs} epochs...")
    generator.train()
    critic.train()
    
    for epoch in range(epochs):
        # Train Critic
        for _ in range(critic_iters):
            idx = np.random.randint(0, real_data.size(0), batch_size)
            real = real_data[idx].to(device)
            z = torch.randn(batch_size, 100, device=device)
            fake = generator(z)
            
            optimizer_c.zero_grad()
            c_loss = -critic(real).mean() + critic(fake.detach()).mean() + \
                     gradient_penalty(critic, real, fake.detach(), device, lambda_gp)
            c_loss.backward()
            optimizer_c.step()
        
        # Train Generator
        z = torch.randn(batch_size, 100, device=device)
        optimizer_g.zero_grad()
        g_loss = -critic(generator(z)).mean()
        g_loss.backward()
        optimizer_g.step()
        
        if epoch % 500 == 0:
            print(f"[GAN Module] WGAN Epoch {epoch}/{epochs}, C Loss: {c_loss.item():.4f}, G Loss: {g_loss.item():.4f}")
    
    print("[GAN Module] WGAN training completed!")
    return generator


def generate_synthetic_scenarios(generator, num_samples=100, device='cpu'):
    """
    Generate synthetic pest and climate scenarios using trained generator
    
    Args:
        generator: Trained generator network
        num_samples: Number of scenarios to generate
        device: Device to generate on
    
    Returns:
        Numpy array of synthetic scenarios
    """
    print(f"[GAN Module] Generating {num_samples} synthetic scenarios...")
    generator.eval()
    with torch.no_grad():
        z = torch.randn(num_samples, 100, device=device)
        scenarios = generator(z).cpu().numpy()
    print(f"[GAN Module] Generated scenarios shape: {scenarios.shape}")
    return scenarios
