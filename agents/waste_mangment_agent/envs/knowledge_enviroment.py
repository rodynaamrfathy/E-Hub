import gymnasium as gym
from gymnasium import spaces
import numpy as np
from ..core.agent import WasteManagementAgent
from ..tools.eco_friendly_alt.eco_friendly_alts import EcoTips
from ..tools.sorting.sorting import SortingRules
import random
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from ..core.agent import WasteManagementAgent
from ..tools.eco_friendly_alt.eco_friendly_alts import EcoTips
from ..tools.sorting.sorting import SortingRules


class KnowledgeEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.agent = WasteManagementAgent()
        self.sorting_kb = SortingRules()
        self.eco_kb = EcoTips()

        # Action space: decide which KB or fallback to use
        # 0=fallback, 1=sorting, 2=eco, 3=combined reasoning
        self.action_space = spaces.Discrete(4)

        # Observations: classification categories + unknown
        self.knowledge = self.agent.knowledge
        self.observation_space = spaces.Discrete(len(self.knowledge) + 1)

        self.current_step = 0
        self.max_steps = 20

        self.possible_queries = [
            "You are a waste managment agent. Choose the right tool.",
            "Manage this waste item: classify, sort, recycle, or suggest alternatives.",
            "You are an eco assistant. Use the correct tool to answer.",
            "Pick the correct waste management tool for this case.",
            "You are a waste management assistant. Given a user request or an image, decide which tool to use.",
            "Classify waste items from an image, search for recycling information, provide sorting/disposal rules, or suggest eco-friendly alternatives.",
            "Given an item or question, route it to the appropriate waste management tool.",
            "I need waste management guidance. Decide which action is appropriate: classification, sorting, recycling info search, or eco alternatives.",
        ]



    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.state = 0
        return self.state, {}

    def step(self, action):
        self.current_step += 1
        query=random.choice(self.possible_queries)
        classification = self.agent.process_query(query)

        # Lookup KBs
        eco_hit = self.eco_kb.find_best_alternative(classification)
        sorting_hit = self.sorting_kb.get_sorting_guidance(classification)

        # Map classification to observation index
        if classification in self.knowledge:
            obs = self.knowledge.index(classification)
        else:
            obs = len(self.knowledge)  # unknown

        # -------------------------
        # Dynamic reward shaping
        # -------------------------
        reward = 0.0

        # Knowledge usage bonus
        if action == 1 and sorting_hit:
            reward += 1.5
        elif action == 2 and eco_hit:
            reward += 1.5
        elif action == 3 and (eco_hit and sorting_hit):
            reward += 2.5  # highest reward for combining KBs
        elif action == 0:
            reward -= 0.5  # fallback penalty

        # Classification correctness
        if classification != "unknown":
            reward += 0.5

        # Encourage exploration (don’t repeat same obs)
        if obs == self.state:
            reward -= 0.2

        done = self.current_step >= self.max_steps
        self.state = obs

        return obs, reward, done, False, {
            "classification": classification,
            "eco_hit": eco_hit,
            "sorting_hit": sorting_hit,
            "action_taken": action,
        }
