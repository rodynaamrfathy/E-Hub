import json
import os
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from rag_pipeline.src.models.multilingual_embedder import MultilingualEmbedder

def create_embedder():
    """Initialize the multilingual embedder."""
    return MultilingualEmbedder(
        model_name="sentence-transformers/all-mpnet-base-v2", 
        batch_size=32
    )


def extract_metadata(soup, url):
    """Extract metadata from the webpage."""
    # Extract title
    title = soup.title.string.strip() if soup.title else "PLACEHOLDER_TITLE"

    # Extract author
    author_meta = soup.find("meta", {"name": "author"})
    author = (author_meta["content"].strip() 
             if author_meta and author_meta.get("content") 
             else "PLACEHOLDER_AUTHOR")

    # Extract publish date
    date_meta = (soup.find("meta", {"property": "article:published_time"}) or 
                soup.find("meta", {"name": "date"}))
    date_published = (date_meta["content"] 
                     if date_meta and date_meta.get("content") 
                     else "PLACEHOLDER_DATE")

    # Extract category from URL
    category_match = re.search(r"/category/([^/]+)/", url)
    category = category_match.group(1) if category_match else "PLACEHOLDER_CATEGORY"

    return title, author, date_published, category


def extract_content(soup):
    """Extract and process text content from the webpage."""
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    content = "\n".join(paragraphs) if paragraphs else "PLACEHOLDER_CONTENT"
    return content


def chunk_content(content, chunk_size=500):
    """Split content into chunks for embedding."""
    if not content or content == "PLACEHOLDER_CONTENT":
        return [content]
    
    # Simple chunking by character count
    chunks = []
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i + chunk_size]
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk.strip())
    
    return chunks if chunks else [content]


def embed_chunks(embedder, chunks):
    """Generate embeddings for text chunks."""
    if not chunks or (len(chunks) == 1 and chunks[0] in ["PLACEHOLDER_CONTENT", ""]):
        print("⚠️ No valid content to embed, using placeholder embeddings")
        return [[0.0, 0.0, 0.0]] * len(chunks)
    
    try:
        print(f"🧠 Generating embeddings for {len(chunks)} chunks...")
        embeddings = embedder.embed_documents(chunks)
        
        # Convert numpy array to list for JSON serialization
        if hasattr(embeddings, 'tolist'):
            embeddings = embeddings.tolist()
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        return embeddings
        
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        print("⚠️ Using placeholder embeddings")
        return [[0.0, 0.0, 0.0]] * len(chunks)


def scrape_and_save_json(urls, output_dir="knowledge_base", chunk_size=500):
    """
    Scrapes a webpage, extracts content, chunks it, embeds chunks, and saves as JSON.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize embedder
    embedder = create_embedder()
    # Ensure urls is iterable
    if isinstance(urls, str):
        urls = [urls]
    for url in urls:

        try:
            print(f"🌐 Fetching content from {url}...")
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

            if response.status_code != 200:
                print(f"❌ Failed to fetch {url}, status {response.status_code}")
                return

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract metadata
            title, author, date_published, category = extract_metadata(soup, url)

            # Extract content
            content = extract_content(soup)
            
            # Extract website name
            website_name = re.match(r"https?://([^/]+)", url).group(1).replace("www.", "").title()
            
            # Chunk content
            chunks = chunk_content(content, chunk_size)
            print(f"📄 Created {len(chunks)} chunks from content")
            
            # Generate embeddings for chunks
            embeddings = embed_chunks(embedder, chunks)

            # Build JSON structure with embedded chunks
            chunk_objects = []
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_objects.append({
                    "chunk_id": f"chunk_{i+1:03d}",
                    "text": chunk_text,
                    "embedding": embedding,
                    "metadata": {
                        "title": title,
                        "author": author,
                        "date_published": date_published,
                        "date_collected": datetime.now().strftime("%Y-%m-%d"),
                        "category": category,
                        "source": url,
                        "chunk_index": i
                    }
                })

            kb_entry = {
                "website": {
                    "name": website_name,
                    "url": re.match(r"https?://[^/]+", url).group(0)
                },
                "documents": [
                    {
                        "id": "doc_001",
                        "url": url,
                        "content": content,
                        "chunks": chunk_objects
                    }
                ]
            }

            # Save to JSON
            filename = os.path.join(output_dir, f"{website_name.lower().replace(' ', '_')}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(kb_entry, f, ensure_ascii=False, indent=4)

            print(f"✅ Saved JSON knowledge base for {website_name} → {filename}")
            print(f"📊 Total chunks embedded: {len(chunk_objects)}")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching {url}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    # Example usage with single URL
    # scrape_and_save_json(
    #     "https://www.efsa.europa.eu/en/efsajournal/pub/2980", 
    #     "knowledge_base"
    # )
    
    # Example usage with multiple URLs
    urls = [
        "https://www.efsa.europa.eu/en/efsajournal/pub/2980",
        "https://bottledwater.org/rpet-facts/"
    ]
    scrape_and_save_json(urls, "knowledge_base")