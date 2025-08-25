import os
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import ProgressBarCallback
from stable_baselines3.common.monitor import Monitor

from ..envs.knowledge_enviroment import KnowledgeEnv


log_dir = "/Users/maryamsaad/Documents/Agentic_Rag/agents/waste_mangment_agent/logs"
os.makedirs(log_dir, exist_ok=True)

env = KnowledgeEnv()
env = Monitor(env, log_dir)

model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir, learning_rate= 0.001, seed=2045)

# Training with tqdm progress bar
callback = ProgressBarCallback()
model.learn(total_timesteps=100, callback=callback,progress_bar=True,)

model.save("chat_agent_rl")
