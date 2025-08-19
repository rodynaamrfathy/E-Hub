from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from exa_py import Exa

# --- Setup Exa tool ---
exa = Exa(api_key="7b2f3660-a49f-45be-b6ff-ee4d02668f7b")

def exa_search(query: str) -> str:
    results = exa.search(query, num_results=3)
    if not results.results:
        return "No results found."
    
    return "\n".join([f"- {r.title}: {r.text}" for r in results.results])


search_tool = Tool.from_function(
    name="exa_search",
    description="Search the web using Exa for up-to-date information.",
    func=exa_search
)

# --- Setup Ollama model ---
llm = ChatOllama(model="llama3:8b")
sorting_rules = {
    "egypt": {
        "plastic": "Drop at PET bins or recycling centers.",
        "organic": "Compost at home or dispose in organic bins.",
        "e-waste": "Bring to designated drop-off centers."
    }
}
def classify_waste(item: str) -> str:
    categories = {
        "plastic": ["bottle", "bag", "container"],
        "paper": ["cardboard", "paper", "newspaper"],
        "organic": ["food", "banana peel", "vegetables"],
        "e-waste": ["phone", "laptop", "battery"],
        "hazardous": ["paint", "chemicals", "medicine"]
    }
    for cat, keywords in categories.items():
        if any(k in item.lower() for k in keywords):
            return f"{item} is classified as {cat} waste."
    return f"Unknown category for {item}. Please check local rules."
classify_tool = Tool.from_function(
    name="waste_classifier",
    description="Classify waste items into recycling categories.",
    func=classify_waste
)


def get_sorting_rules(item: str, country: str="egypt") -> str:
    return sorting_rules.get(country.lower(), {}).get(item.lower(), "No rules found.")
rules_tool = Tool.from_function(
    name="sorting_rules",
    description="Get region-specific sorting guidance for a waste category.",
    func=get_sorting_rules
)
eco_alternatives = {
    "plastic bottle": "Use a reusable stainless steel or glass bottle.",
    "plastic bag": "Switch to cloth tote bags or biodegradable bags.",
    "paper": "Go digital when possible; use both sides of paper before recycling.",
    "food waste": "Compost food scraps to create natural fertilizer.",
    "battery": "Switch to rechargeable batteries instead of disposables.",
    "electronics": "Donate or sell old devices instead of discarding them."
}
def eco_friendly_tips(item: str) -> str:
    for k, v in eco_alternatives.items():
        if k in item.lower():
            return f"Eco-friendly tip for {item}: {v}"
    return f"No specific alternative found for {item}. Try reducing single-use items and choosing reusable options."

eco_tips_tool = Tool.from_function(
    name="eco_tips",
    description="Suggest eco-friendly alternatives and behavioral nudges for waste items.",
    func=eco_friendly_tips
)



# --- Initialize agent ---
agent = initialize_agent(
    tools=[search_tool,classify_tool,eco_tips_tool],  # add more as you build
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
# --- Run a query ---
response = agent.run("I usually use plastic bags. What should I use instead?")
print(response)

response = agent.run("Give me an alternative to single-use batteries.")
print(response)

