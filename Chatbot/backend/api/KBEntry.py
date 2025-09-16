# # app.py
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict
# from uuid import uuid4
# from backend.services.conversation.tools.kb_ingestion import KB_IngestionPipeline

# app = FastAPI(title="Knowledge Base API")

# # Initialize the ingestion pipeline
# pipeline = KB_IngestionPipeline()

# # Define the request model
# class KBEntry(BaseModel):
#     id: Optional[str] = Field(default_factory=lambda: str(uuid4()))
#     content_type: Optional[str] = "unknown"
#     title: str
#     content: str
#     metadata: Optional[Dict] = {}
#     keywords: Optional[List[str]] = []

# @app.post("/kb/ingest")
# def ingest_entry(entry: KBEntry):
#     """
#     Ingest a single KB entry.
#     Returns status: inserted, updated, skipped, or failed.
#     """
#     result = pipeline.ingest_entry(entry.dict())
    
#     if not result or result["status"] == "failed":
#         raise HTTPException(status_code=400, detail=f"Failed to ingest entry: {entry.title}")
    
#     return result

# # Optional: batch ingestion endpoint
# @app.post("/kb/ingest/batch")
# def ingest_entries(entries: List[KBEntry]):
#     """
#     Ingest multiple KB entries at once.
#     Returns a summary of inserted/updated/skipped/failed counts.
#     """
#     summary = {"inserted": 0, "updated": 0, "skipped": 0, "failed": 0}
#     results = []

#     for entry in entries:
#         res = pipeline.ingest_entry(entry.dict())
#         results.append(res)
#         if res:
#             status = res["status"]
#             if status in summary:
#                 summary[status] += 1
#             else:
#                 summary["failed"] += 1
#         else:
#             summary["failed"] += 1

#     return {"summary": summary, "results": results}
