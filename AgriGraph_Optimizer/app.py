import os
import io
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
import streamlit as st

from config import DEVICE, GRAPH_CONFIG, GAN_CONFIG, RL_CONFIG, DATA_PATH, OUTPUT_PATH

# Import project modules
from modules.graph_module import (
    FarmerGAT, build_farmer_graph, train_gat, get_graph_embeddings
)
from modules.gan_module import (
    Generator, Critic, generate_real_data, train_wgan, generate_synthetic_scenarios
)
from modules.rl_module import (
    AgriEnv, Actor, Critic as RLCritic, train_ppo, get_optimal_action
)

st.set_page_config(page_title="AgriGraph Optimizer", layout="wide")
st.title("🌾 AgriGraph Optimizer – Farmer Decision Support")
st.caption("Graph + GAN + RL integrated assistant for pesticide and fertilizer decisions")

# Initialize session state
if "embeddings" not in st.session_state:
    st.session_state.embeddings = None
if "synthetic" not in st.session_state:
    st.session_state.synthetic = None
if "actor" not in st.session_state:
    st.session_state.actor = None
if "critic" not in st.session_state:
    st.session_state.critic = None
if "env" not in st.session_state:
    st.session_state.env = None
if "graph_data" not in st.session_state:
    st.session_state.graph_data = None
if "graph_nx" not in st.session_state:
    st.session_state.graph_nx = None

# Sidebar controls
st.sidebar.header("⚙️ Controls")
quick_mode = st.sidebar.checkbox("Quick Mode (faster demo)", value=True)
num_nodes = st.sidebar.slider("Graph: number of nodes (if synthetic)", 20, 200, GRAPH_CONFIG.get("num_nodes", 100))
learning_rate = st.sidebar.number_input("GAT LR", value=float(GRAPH_CONFIG.get("learning_rate", 0.01)))

st.sidebar.markdown("---")
upload = st.sidebar.file_uploader("Upload farms.csv (optional)", type=["csv"])
if upload is not None:
    # Save uploaded file to data/farms.csv
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "wb") as f:
        f.write(upload.read())
    st.sidebar.success("Uploaded farms.csv and saved to data/")

st.sidebar.markdown("---")
st.sidebar.write("Outputs directory:")
st.sidebar.code(OUTPUT_PATH)

# Utility: figure to streamlit

def show_matplotlib(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    st.image(buf)

# Tabs for workflow
tab_graph, tab_gan, tab_rl, tab_infer, tab_outputs = st.tabs([
    "Farmer Graph", "Synthetic Scenarios", "RL Training", "Recommendations", "Outputs"
])

# ===================== Farmer Graph Tab =====================
with tab_graph:
    st.subheader("Step 1: Build Farmer Network and Train GAT")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("Build graph from data or synthetic if missing. Then train GAT to produce farm embeddings.")
        gat_epochs = 10 if quick_mode else GRAPH_CONFIG.get("gat_epochs", 200)
        st.write(f"Epochs: {gat_epochs}")
        build_btn = st.button("Build Graph + Train GAT")
        load_graph_btn = st.button("Load Saved Embeddings")

    if build_btn:
        with st.spinner("Building graph and training GAT..."):
            # Build graph
            data, graph_nx = build_farmer_graph(csv_path=DATA_PATH, num_nodes=num_nodes, device=DEVICE)
            st.session_state.graph_data = data
            st.session_state.graph_nx = graph_nx

            # Train GAT
            gat_model = FarmerGAT(
                in_channels=GRAPH_CONFIG.get("in_channels", 4),
                hidden_channels=GRAPH_CONFIG.get("hidden_channels", 16),
                out_channels=GRAPH_CONFIG.get("out_channels", 2),
                heads=GRAPH_CONFIG.get("heads", 4)
            ).to(DEVICE)

            opt = torch.optim.Adam(gat_model.parameters(), lr=learning_rate)
            gat_model = train_gat(gat_model, data, opt, epochs=gat_epochs, device=DEVICE)
            embeddings = get_graph_embeddings(gat_model, data)
            st.session_state.embeddings = embeddings

            os.makedirs(OUTPUT_PATH, exist_ok=True)
            torch.save(embeddings, os.path.join(OUTPUT_PATH, "graph_embeddings.pt"))
            st.success("Embeddings generated and saved.")

    if load_graph_btn:
        path = os.path.join(OUTPUT_PATH, "graph_embeddings.pt")
        if os.path.exists(path):
            st.session_state.embeddings = torch.load(path, map_location=DEVICE)
            st.success("Loaded embeddings from outputs.")
        else:
            st.error("No saved embeddings found.")

    # Visualize graph stats
    if st.session_state.graph_nx is not None:
        G = st.session_state.graph_nx
        st.write(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
        # If lat/lon in data, scatter plot
        try:
            df = pd.read_csv(DATA_PATH)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.scatter(df["lon"], df["lat"], c=df.get("soil_ph", 7.0), cmap="viridis", s=40)
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            ax.set_title("Farm Locations (color=soil pH)")
            ax.grid(True)
            show_matplotlib(fig)
        except Exception as e:
            st.info("Upload farms.csv to see scatter map.")

# ===================== GAN Tab =====================
with tab_gan:
    st.subheader("Step 2: Generate Synthetic Pest & Climate Scenarios (WGAN-GP)")
    gan_epochs = 100 if quick_mode else GAN_CONFIG.get("epochs", 5000)
    batch_size = GAN_CONFIG.get("batch_size", 64)
    critic_iters = GAN_CONFIG.get("critic_iters", 5)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.write(f"Training epochs: {gan_epochs}, batch size: {batch_size}, critic iters: {critic_iters}")
        train_gan_btn = st.button("Train GAN + Generate Scenarios")
        load_gan_btn = st.button("Load Saved Scenarios")

    if train_gan_btn:
        with st.spinner("Training WGAN-GP and generating scenarios..."):
            real_data = generate_real_data(
                num_samples=GAN_CONFIG.get("num_real_samples", 1000),
                seq_len=GAN_CONFIG.get("seq_len", 30),
                feature_dim=GAN_CONFIG.get("feature_dim", 4)
            )
            generator = Generator(
                z_dim=GAN_CONFIG.get("z_dim", 100),
                seq_len=GAN_CONFIG.get("seq_len", 30),
                feature_dim=GAN_CONFIG.get("feature_dim", 4)
            ).to(DEVICE)
            critic = Critic(
                seq_len=GAN_CONFIG.get("seq_len", 30),
                feature_dim=GAN_CONFIG.get("feature_dim", 4)
            ).to(DEVICE)
            opt_g = torch.optim.Adam(generator.parameters(), lr=GAN_CONFIG.get("lr", 2e-4), betas=(GAN_CONFIG.get("beta1", 0.5), GAN_CONFIG.get("beta2", 0.9)))
            opt_c = torch.optim.Adam(critic.parameters(), lr=GAN_CONFIG.get("lr", 2e-4), betas=(GAN_CONFIG.get("beta1", 0.5), GAN_CONFIG.get("beta2", 0.9)))
            generator = train_wgan(
                generator, critic, real_data, opt_g, opt_c,
                epochs=gan_epochs, batch_size=batch_size, critic_iters=critic_iters, device=DEVICE,
                lambda_gp=GAN_CONFIG.get("lambda_gp", 10)
            )
            synthetic = generate_synthetic_scenarios(generator, num_samples=GAN_CONFIG.get("num_synthetic_samples", 500), device=DEVICE)
            st.session_state.synthetic = synthetic
            np.save(os.path.join(OUTPUT_PATH, "synthetic_scenarios.npy"), synthetic)
            st.success("Synthetic scenarios generated and saved.")

    if load_gan_btn:
        path = os.path.join(OUTPUT_PATH, "synthetic_scenarios.npy")
        if os.path.exists(path):
            st.session_state.synthetic = np.load(path)
            st.success("Loaded scenarios from outputs.")
        else:
            st.error("No saved scenarios found.")

    # Visualize a scenario
    if st.session_state.synthetic is not None:
        st.write("Sample synthetic scenario (first sequence):")
        scen = st.session_state.synthetic[0]
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(scen[:, 0], label="Temperature")
        ax.plot(scen[:, 1], label="Rain")
        ax.plot(scen[:, 2], label="Pest")
        ax.plot(scen[:, 3], label="Climate Anomaly")
        ax.legend()
        ax.grid(True)
        ax.set_xlabel("Day")
        ax.set_ylabel("Normalized")
        show_matplotlib(fig)

# ===================== RL Tab =====================
with tab_rl:
    st.subheader("Step 3: Train PPO Agent for Dosage Optimization")
    rl_epochs = 50 if quick_mode else RL_CONFIG.get("epochs", 1000)
    batch_size_rl = RL_CONFIG.get("batch_size", 32)
    st.write(f"Training epochs: {rl_epochs}, batch size: {batch_size_rl}")

    train_rl_btn = st.button("Train PPO Agent")
    load_models_btn = st.button("Load Saved PPO Models")

    if train_rl_btn:
        if st.session_state.embeddings is None or st.session_state.synthetic is None:
            st.error("Please generate/load embeddings and scenarios first (Steps 1 & 2).")
        else:
            with st.spinner("Training PPO agent..."):
                env = AgriEnv(st.session_state.embeddings, st.session_state.synthetic)
                st.session_state.env = env
                actor = Actor(state_dim=RL_CONFIG.get("state_dim", 6), action_dim=RL_CONFIG.get("action_dim", 2)).to(DEVICE)
                rl_critic = RLCritic(state_dim=RL_CONFIG.get("state_dim", 6)).to(DEVICE)
                actor, rl_critic = train_ppo(env, actor, rl_critic, epochs=rl_epochs, batch_size=batch_size_rl, gamma=RL_CONFIG.get("gamma", 0.99), lr_actor=RL_CONFIG.get("lr_actor", 3e-4), lr_critic=RL_CONFIG.get("lr_critic", 3e-4), device=DEVICE)
                st.session_state.actor = actor
                st.session_state.critic = rl_critic
                torch.save(actor.state_dict(), os.path.join(OUTPUT_PATH, "actor_model.pt"))
                torch.save(rl_critic.state_dict(), os.path.join(OUTPUT_PATH, "critic_model.pt"))
                st.success("PPO models trained and saved.")

    if load_models_btn:
        actor_path = os.path.join(OUTPUT_PATH, "actor_model.pt")
        critic_path = os.path.join(OUTPUT_PATH, "critic_model.pt")
        if os.path.exists(actor_path) and os.path.exists(critic_path):
            actor = Actor(state_dim=RL_CONFIG.get("state_dim", 6), action_dim=RL_CONFIG.get("action_dim", 2)).to(DEVICE)
            rl_critic = RLCritic(state_dim=RL_CONFIG.get("state_dim", 6)).to(DEVICE)
            actor.load_state_dict(torch.load(actor_path, map_location=DEVICE))
            rl_critic.load_state_dict(torch.load(critic_path, map_location=DEVICE))
            st.session_state.actor = actor
            st.session_state.critic = rl_critic
            st.success("Loaded PPO models from outputs.")
        else:
            st.error("Saved PPO models not found.")

# ===================== Inference Tab =====================
with tab_infer:
    st.subheader("Step 4: Get Recommendations")
    st.write("Choose a farm node and scenario/day, then get recommended pesticide/fertilizer dosages.")

    if st.session_state.actor is None or st.session_state.embeddings is None:
        st.info("Train or load PPO models and embeddings first.")
    else:
        embeddings = st.session_state.embeddings
        synthetic = st.session_state.synthetic
        node_id = st.number_input("Farm node id", min_value=0, max_value=int(embeddings.size(0) - 1), value=0)
        scen_index = st.number_input("Scenario index", min_value=0, max_value=int(len(synthetic) - 1), value=0)
        day_index = st.slider("Day in scenario", 0, synthetic.shape[1] - 1, 0)
        crop_health = st.slider("Initial crop health", 0.0, 1.0, 0.5)

        temp, rain, pest, _ = synthetic[scen_index][day_index]
        embed = embeddings[node_id].cpu().numpy()
        state = np.array([crop_health, temp, rain, pest, embed[0], embed[1]], dtype=np.float32)

        if st.button("Recommend Dosages"):
            action = get_optimal_action(st.session_state.actor, state, DEVICE)
            st.success("Recommended Dosages (0-1 scale)")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Pesticide", f"{action[0]:.3f}")
            with col2:
                st.metric("Fertilizer", f"{action[1]:.3f}")

        # Show current weather/pest values
        with st.expander("Current Scenario Values"):
            st.write({"Temperature": float(temp), "Rain": float(rain), "Pest": float(pest), "Embeddings": [float(embed[0]), float(embed[1])]})

# ===================== Outputs Tab =====================
with tab_outputs:
    st.subheader("Saved Outputs")
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    files = os.listdir(OUTPUT_PATH)
    if files:
        st.write("Files in outputs/")
        for f in files:
            st.write("•", f)
        # Preview images if available
        img_paths = [os.path.join(OUTPUT_PATH, f) for f in files if f.lower().endswith(".png")]
        for p in img_paths:
            st.image(p, caption=os.path.basename(p))
    else:
        st.info("No outputs saved yet.")

st.sidebar.markdown("---")
st.sidebar.caption("Tip: Use Quick Mode for fast demos. Switch off for full training.")
