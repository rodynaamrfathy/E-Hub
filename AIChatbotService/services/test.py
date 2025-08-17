import asyncio
from AIChatbotService.services.database_service import DatabaseService
from AIChatbotService.database import db_manager

db_service = DatabaseService()

async def main():

    #  initialize DB first
    await db_manager.initialize()

    db_service = DatabaseService()

    # -------------------------------
    # Conversations
    # -------------------------------
    print("\n--- Create Conversation ---")
    conv = await db_service.create_conversation(
        user_id="123e4567-e89b-12d3-a456-426614174000",  # <-- Replace with real UUID
        title="My First Conversation"
    )
    print(f"Created conversation: {conv.conv_id}, Title: {conv.title}")

    print("\n--- Get Conversation ---")
    fetched_conv = await db_service.get_conversation(str(conv.conv_id))
    print(f"Fetched: {fetched_conv.conv_id}, Title: {fetched_conv.title}")

    print("\n--- Update Conversation Title ---")
    updated = await db_service.update_conversation_title(str(conv.conv_id), "Updated Title")
    print("Updated:", updated)

    print("\n--- User Conversations ---")
    user_convs = await db_service.get_user_conversations(str(conv.user_id))
    for c in user_convs:
        print(f"{c.conv_id}: {c.title}")

    # -------------------------------
    # Messages
    # -------------------------------
    print("\n--- Add Message ---")
    msg = await db_service.add_message(str(conv.conv_id), "user", "Hello, AI!")
    print(f"Message: {msg.msg_id}, Content: {msg.content}")

    print("\n--- Get Conversation Messages ---")
    messages = await db_service.get_conversation_messages(str(conv.conv_id))
    for m in messages:
        print(f"{m.sender}: {m.content}")

    # -------------------------------
    # Embeddings
    # -------------------------------
    print("\n--- Create Embedding ---")
    emb = await db_service.create_embedding("Hello, AI!", [0.12, 0.45, 0.78])
    print(f"Embedding created: {emb.id}")

    # -------------------------------
    # Strategies
    # -------------------------------
    print("\n--- Create Strategy ---")
    strategy = await db_service.create_strategy("chatbot", "Basic chatbot strategy")
    print(f"Strategy: {strategy.strategy_id}, {strategy.name}")

    print("\n--- Add Strategy to Conversation ---")
    conv_strat = await db_service.add_strategy_to_conversation(str(conv.conv_id), strategy.strategy_id)
    print(f"Linked Strategy {conv_strat.strategy_id} to Conversation {conv_strat.conv_id}")

    print("\n--- Get Conversation Strategies ---")
    strategies = await db_service.get_conversation_strategies(str(conv.conv_id))
    for s in strategies:
        print(f"{s.strategy_id}: {s.name}")

    # -------------------------------
    # Clean up (Delete)
    # -------------------------------
    print("\n--- Delete Message ---")
    deleted_msg = await db_service.delete_message(str(msg.msg_id))
    print("Deleted:", deleted_msg)

    print("\n--- Delete Conversation ---")
    deleted_conv = await db_service.delete_conversation(str(conv.conv_id))
    print("Deleted:", deleted_conv)


if __name__ == "__main__":
    asyncio.run(main())
