# this script is for ingesting new knowledge into our KB DB 
import uuid
import json
from Chatbot.backend.services.conversation.tools.embeddermodel import embedder
from services.db.postgres import get_db_session
from services.repositories.kb_service import KBContentService


class KB_IngestionPipeline:
    def __init__(self) -> None:
        self.embedder=embedder()
        self.get_db_session = get_db_session
        self.kb_service  = None

    async def init_service(self):
        """Initialize KB service with async DB session."""
        async for db in self.get_db_session():
            self.kb_service = KBContentService(db)
            break

    async def ingest_entry(self, entry):
        """Insert or update a KB entry in the database (only if changed)."""
        if self.kb_service is None:
            await self.init_service()

        try:
            # Use existing id if provided, otherwise generate new one
            new_id = entry.get("id", str(uuid.uuid4()))

            # Prepare fields
            content_type = entry.get("content_type", "unknown")
            title = entry.get("title", "")
            content = entry.get("content", "")
            metadata = entry.get("metadata", {})
            keywords = entry.get("keywords", [])

            # --- 🔎 Step 1: Check if entry already exists ---
            existing = await self.kb_service.get_by_id(kb_id=new_id)

            if existing:
                existing_row = existing

                # Normalize stored values
                stored_metadata = existing_row["metadata"]
                stored_keywords = (
                    existing_row["keywords"] if isinstance(existing_row["keywords"], list) else json.loads(existing_row["keywords"])
                )

                # If nothing changed, skip re-inserting
                if (
                    existing_row["title"] == title
                    and existing_row["content"] == content
                    and stored_metadata == metadata
                    and stored_keywords == keywords
                ):
                    print(f"⏭️ Skipped (unchanged): {title}")
                    return {"status": "skipped", "id": new_id}

            # --- 🔄 Step 2: Generate embedding only if new or changed ---
            embedding_text = f"{title}. {content}"
            embeddings = self.embedder.get_embeddings([embedding_text])
            if len(embeddings) == 0:
                print(f"⚠️ Skipping entry (no embedding): {title}")
                return {"status": "failed", "id": new_id}

            embedding = embeddings[0].tolist()

            # --- 💾 Step 3: Upsert (insert/update if changed) ---
            # sql = """
            #     INSERT INTO kb_content (id, content_type, title, content, metadata, keywords,embedding)
            #     VALUES (%s, %s, %s, %s, %s, %s, %s)
            #     ON CONFLICT (id) DO UPDATE SET
            #         content_type = EXCLUDED.content_type,
            #         title = EXCLUDED.title,
            #         content = EXCLUDED.content,
            #         metadata = EXCLUDED.metadata,
            #         keywords = EXCLUDED.keywords,
            #         embedding = EXCLUDED.embedding
            #     RETURNING id;
            # """

            # result = run_query_params(
            #     sql,
            #     params=(new_id, content_type, title, content, metadata, keywords, embedding),
            #     fetch=True
            # )

            upsert_data = {
                "id":  new_id,
                "content_type": content_type,
                "title": title,
                "content": content,
                "metadata": metadata,
                "keywords": keywords,
                "embedding": embedding,
            }

            result = await self.kb_service.upsert_kb_entry(upsert_data)


            if result:
                if existing:
                    print(f"🔄 Updated: {title} (ID: {new_id})")
                    return {"status": "updated", "id": new_id}
                else:
                    print(f"✅ Inserted: {title} (ID: {new_id})")
                    return {"status": "inserted", "id": new_id}

            return {"status": "failed", "id": new_id}

        except Exception as e:
            print(f"❌ Error processing entry {entry.get('title', 'Unknown')}: {e}")
            return {"status": "failed", "id": entry.get("id", None)}



# if __name__ == "__main__":
#     pipeline = KB_IngestionPipeline()

#     # Dummy entries for testing (simulating your YAML KB)
#     sample_entries = [
#         {
#             "id": str(uuid.uuid4()),
#             "content_type": "faq",
#             "title": "Waste Management",
#             "content": "Solutions for handling industrial and municipal waste.",
#             "metadata": {"category": "environment"},
#             "keywords": ["waste", "management", "environment"],
#         },
#         {
#             "id": str(uuid.uuid4()),
#             "content_type": "policy",
#             "title": "AI Safety Policy",
#             "content": "Guidelines for ethical use of AI in organizations.",
#             "metadata": {"category": "AI"},
#             "keywords": ["AI", "safety", "policy"],
#         }
#     ]

#     print("\n🚀 Starting KB ingestion test...\n")

#     inserted, updated, skipped, failed = 0, 0, 0, 0
#     for entry in sample_entries:
#         result = pipeline.ingest_entry(entry)
#         if result:
#             if result["status"] == "inserted":
#                 inserted += 1
#             elif result["status"] == "updated":
#                 updated += 1
#             elif result["status"] == "skipped":
#                 skipped += 1
#             else:
#                 failed += 1
#         else:
#             failed += 1

#     print(f"\n📊 Test Ingestion Summary:")
#     print(f"✅ Inserted: {inserted}")
#     print(f"🔄 Updated: {updated}")
#     print(f"⏭️ Skipped: {skipped}")
#     print(f"❌ Failed: {failed}")

##suggested api
# @app.post("/kb/ingest")
# def ingest_entry(entry: samplelistentry):
#     result = pipeline.ingest_entry(entry.dict())
#     if not result or result["status"] == "failed":
#         raise HTTPException(status_code=400, detail="Failed to ingest entry")
#     return result
