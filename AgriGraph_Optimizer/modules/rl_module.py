"""
RL Module
Proximal Policy Optimization (PPO) for Optimal Pesticide & Fertilizer Dosage
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import MultivariateNormal
import numpy as np
import gym
from gym import spaces


class AgriEnv(gym.Env):
    """
    Agriculture Environment for Reinforcement Learning
    State: [crop_health, temp, rain, pest, embed1, embed2]
    Action: [pesticide_dosage, fertilizer_dosage] (normalized 0-1)
    """
    def __init__(self, graph_embeddings, synthetic_scenarios):
        super(AgriEnv, self).__init__()
        self.graph_embeddings = graph_embeddings
        self.scenarios = synthetic_scenarios
        self.action_space = spaces.Box(low=0, high=1, shape=(2,))
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(6,))
        self.reset()
    
    def reset(self):
        """Reset environment to initial state"""
        self.current_step = 0
        self.crop_health = 0.5
        self.scenario = self.scenarios[np.random.randint(0, len(self.scenarios))]
        self.node_id = np.random.randint(0, self.graph_embeddings.size(0))
        self.state = np.concatenate([
            [self.crop_health],
            self.scenario[0][:3],  # temp, rain, pest
            self.graph_embeddings[self.node_id].cpu().numpy()
        ])
        return self.state
    
    def step(self, action):
        """
        Execute one step in the environment
        
        Args:
            action: [pesticide, fertilizer] dosages (0-1)
        
        Returns:
            state: Next state
            reward: Reward for this step
            done: Whether episode is finished
            info: Additional info
        """
        pesticide, fertilizer = action
        temp, rain, pest, _ = self.scenario[self.current_step]
        
        # Calculate neighbor risk (average embedding of other nodes)
        neighbor_risk = np.mean([
            self.graph_embeddings[n].cpu().numpy()[0] 
            for n in range(self.graph_embeddings.size(0)) 
            if n != self.node_id
        ])
        
        # Crop health dynamics
        delta_health = (
            fertilizer * (0.5 + rain * 0.1) -  # Fertilizer benefit with rain
            pesticide * pest * 0.2 -            # Pesticide effectiveness
            temp * 0.05                         # Temperature stress
        ) * (1 - neighbor_risk * 0.1)          # Neighbor influence
        
        self.crop_health = np.clip(self.crop_health + delta_health, 0, 1)
        
        # Reward: maximize health, minimize costs, match pest level
        reward = (
            self.crop_health -                  # Crop health benefit
            (pesticide + fertilizer) * 0.2 -    # Input costs
            abs(pest - pesticide) * 0.1         # Mismatch penalty
        )
        
        self.current_step += 1
        done = self.current_step >= len(self.scenario) or self.crop_health <= 0.1
        
        # Update state
        self.state = np.concatenate([
            [self.crop_health],
            self.scenario[min(self.current_step, len(self.scenario)-1)][:3],
            self.graph_embeddings[self.node_id].cpu().numpy()
        ])
        
        return self.state, reward, done, {}


class Actor(nn.Module):
    """Actor network for PPO (policy)"""
    def __init__(self, state_dim, action_dim):
        super(Actor, self).__init__()
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.mu = nn.Linear(64, action_dim)
        self.sigma = nn.Linear(64, action_dim)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        mu = torch.tanh(self.mu(x))  # Actions in [-1, 1], will scale to [0, 1]
        sigma = F.softplus(self.sigma(x)) + 1e-5
        return mu, sigma


class Critic(nn.Module):
    """Critic network for PPO (value function)"""
    def __init__(self, state_dim):
        super(Critic, self).__init__()
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.v = nn.Linear(64, 1)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.v(x)


def compute_gae(rewards, values, next_value, gamma=0.99, lam=0.95):
    """
    Compute Generalized Advantage Estimation
    
    Args:
        rewards: List of rewards
        values: List of value estimates
        next_value: Value estimate of next state
        gamma: Discount factor
        lam: GAE lambda parameter
    
    Returns:
        List of advantages
    """
    advantages = []
    delta = 0
    for r, v in reversed(list(zip(rewards, values))):
        delta = r + gamma * next_value - v
        advantages.append(delta + gamma * lam * delta)
        next_value = v
    advantages.reverse()
    return advantages


def ppo_update(actor, critic, states, actions, log_probs_old, advantages, returns, 
               optimizer_actor, optimizer_critic, epochs=10, clip=0.2):
    """
    Perform PPO update
    
    Args:
        actor: Actor network
        critic: Critic network
        states: Batch of states
        actions: Batch of actions
        log_probs_old: Old log probabilities
        advantages: Computed advantages
        returns: Computed returns
        optimizer_actor: Actor optimizer
        optimizer_critic: Critic optimizer
        epochs: Number of PPO epochs
        clip: PPO clip parameter
    """
    for _ in range(epochs):
        # Actor update
        mu, sigma = actor(states)
        dist = MultivariateNormal(mu.float(), torch.diag_embed(sigma.float()))
        log_probs = dist.log_prob(actions.float())
        ratios = torch.exp(log_probs - log_probs_old.detach())
        
        surr1 = ratios * advantages.detach()
        surr2 = torch.clamp(ratios, 1 - clip, 1 + clip) * advantages.detach()
        actor_loss = -torch.min(surr1, surr2).mean()
        
        optimizer_actor.zero_grad()
        actor_loss.backward(retain_graph=True)
        optimizer_actor.step()
        
        # Critic update
        values = critic(states).squeeze()
        critic_loss = F.mse_loss(values, returns.detach())
        
        optimizer_critic.zero_grad()
        critic_loss.backward()
        optimizer_critic.step()


def train_ppo(env, actor, critic, epochs=1000, batch_size=32, gamma=0.99, 
              lr_actor=3e-4, lr_critic=3e-4, device='cpu'):
    """
    Train PPO agent
    
    Args:
        env: Agriculture environment
        actor: Actor network
        critic: Critic network
        epochs: Number of training epochs
        batch_size: Batch size for updates
        gamma: Discount factor
        lr_actor: Actor learning rate
        lr_critic: Critic learning rate
        device: Device to train on
    
    Returns:
        Trained actor and critic
    """
    print(f"[RL Module] Training PPO for {epochs} epochs...")
    optimizer_actor = optim.Adam(actor.parameters(), lr=lr_actor)
    optimizer_critic = optim.Adam(critic.parameters(), lr=lr_critic)
    
    for epoch in range(epochs):
        batch_states, batch_actions, batch_log_probs, batch_rewards, batch_values = [], [], [], [], []
        state = env.reset()
        done = False
        ep_rewards = []
        
        while not done:
            state_tensor = torch.from_numpy(state).float().to(device)
            mu, sigma = actor(state_tensor.unsqueeze(0))
            dist = MultivariateNormal(mu.squeeze(0).float(), torch.diag(sigma.squeeze(0).float()))
            action = dist.sample()
            log_prob = dist.log_prob(action)
            
            # Scale action from [-1, 1] to [0, 1]
            action_scaled = (action.cpu().numpy() + 1) / 2
            next_state, reward, done, _ = env.step(action_scaled)
            value = critic(state_tensor.unsqueeze(0)).item()
            
            batch_states.append(state_tensor)
            batch_actions.append(action)
            batch_log_probs.append(log_prob)
            batch_rewards.append(reward)
            batch_values.append(value)
            
            state = next_state
            ep_rewards.append(reward)
            
            # Update when batch is full
            if len(batch_states) == batch_size:
                next_state_tensor = torch.from_numpy(next_state).float().to(device)
                next_value = critic(next_state_tensor.unsqueeze(0)).item()
                
                advantages = compute_gae(batch_rewards, batch_values, next_value, gamma)
                returns = [a + v for a, v in zip(advantages, batch_values)]
                
                states = torch.stack(batch_states)
                actions = torch.stack(batch_actions)
                log_probs_old = torch.stack(batch_log_probs)
                advantages = torch.tensor(advantages, dtype=torch.float32, device=device)
                returns = torch.tensor(returns, dtype=torch.float32, device=device)
                
                ppo_update(actor, critic, states, actions, log_probs_old, 
                          advantages, returns, optimizer_actor, optimizer_critic)
                
                batch_states, batch_actions, batch_log_probs, batch_rewards, batch_values = [], [], [], [], []
        
        if epoch % 100 == 0:
            avg_reward = np.mean(ep_rewards) if ep_rewards else 0
            print(f"[RL Module] PPO Epoch {epoch}/{epochs}, Avg Reward: {avg_reward:.4f}")
    
    print("[RL Module] PPO training completed!")
    return actor, critic


def get_optimal_action(actor, state, device='cpu'):
    """
    Get optimal action from trained actor
    
    Args:
        actor: Trained actor network
        state: Current state
        device: Device to compute on
    
    Returns:
        Optimal action [pesticide, fertilizer]
    """
    actor.eval()
    with torch.no_grad():
        state_tensor = torch.from_numpy(state).float().to(device)
        mu, _ = actor(state_tensor.unsqueeze(0))
        action = (mu.squeeze(0).cpu().numpy() + 1) / 2  # Scale to [0, 1]
    return action
