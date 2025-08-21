from waste_mangment_agent.core.agent import WasteManagementAgent
def main():
    """Main function to run the waste management agent"""
    print("🌱 Waste Management & Recycling Guidance Agent")
    print("=" * 50)
    
    # Initialize agent
    agent = WasteManagementAgent(region="egypt")
    
    print("Available tools:", ", ".join(agent.get_available_tools()))
    print("\nType 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("\n🗑️  Ask me about waste management: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thanks for helping the environment! Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Processing your request...")
            response = agent.process_query(user_input)
            print(f"\n✅ {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for helping the environment! Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()