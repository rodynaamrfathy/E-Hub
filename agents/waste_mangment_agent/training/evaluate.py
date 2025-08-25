import gymnasium as gym
from stable_baselines3 import PPO
from..envs.knowledge_enviroment import KnowledgeEnv
model = PPO.load("chat_agent_rl")

env = KnowledgeEnv()
obs, _ = env.reset()

for _ in range(10):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, _, _ = env.step(action)
    print(f"Action: {action}, Reward: {reward}, Obs: {obs}")
    if done:
        obs, _ = env.reset()
