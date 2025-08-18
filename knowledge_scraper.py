import json
import os
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import io
from PyPDF2 import PdfReader
from rag_pipeline.src.models.multilingual_embedder import MultilingualEmbedder

def create_embedder():
    """Initialize the multilingual embedder."""
    return MultilingualEmbedder(
        model_name="sentence-transformers/all-mpnet-base-v2", 
        batch_size=32
    )


def extract_pdf_content(response):
    """Extract text from a PDF response."""
    pdf_bytes = io.BytesIO(response.content)
    reader = PdfReader(pdf_bytes)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text).strip() or "PLACEHOLDER_CONTENT"


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
import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_and_save_json(urls, output_dir="knowledge_base", chunk_size=500):
    """
    Scrapes a webpage or PDF, extracts content, chunks it, embeds chunks, and saves as JSON.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize embedder
    embedder = create_embedder()

    # Ensure urls is iterable
    if isinstance(urls, str):
        urls = [urls]

    for idx, url in enumerate(urls, start=1):
        try:
            print(f"🌐 Fetching content from {url}...")
            response = requests.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.google.com/"
                },
                timeout=10
            )

            if response.status_code != 200:
                print(f"❌ Failed to fetch {url}, status {response.status_code}. Skipping...")
                continue   # skip to next URL

            # --- Detect PDFs ---
            content_type = response.headers.get("Content-Type", "").lower()
            if url.endswith(".pdf") or "application/pdf" in content_type:
                print("📄 Detected PDF, extracting text...")
                content = extract_pdf_content(response)
                title = url.split("/")[-1]  # fallback title from filename
                author = "PLACEHOLDER_AUTHOR"
                date_published = "PLACEHOLDER_DATE"
                category = "PLACEHOLDER_CATEGORY"
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                title, author, date_published, category = extract_metadata(soup, url)
                content = extract_content(soup)

            # Extract website name
            website_name = re.match(r"https?://([^/]+)", url).group(1).replace("www.", "").title()

            # Chunk content
            chunks = chunk_content(content, chunk_size)
            print(f"📄 Created {len(chunks)} chunks from content")

            # Generate embeddings for chunks
            embeddings = embed_chunks(embedder, chunks)

            # Build chunk objects
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
                        "id": f"doc_{idx:03d}",
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
            continue  # skip to next
        except Exception as e:
            print(f"❌ Unexpected error for {url}: {e}")
            continue  # skip to next


if __name__ == "__main__":
    # Example usage with single URL
    # scrape_and_save_json(
    #     "https://www.efsa.europa.eu/en/efsajournal/pub/2980", 
    #     "knowledge_base"
    # )
    
    # Example usage with multiple URLs
    urls = [
        "https://www.tomra.com/reverse-vending/media-center/feature-articles/what-is-rpet-plastic",
        "https://www.bo-re-tech.com/en/article/pet-bottle-recycling-process.html",
        "https://www.avient.com/sites/default/files/2022-04/Sustainable%20Material%20Answers_%20%20Recycled%20PET%202022_0.pdf",
        "https://www.efsa.europa.eu/en/efsajournal/pub/2980",
        "https://bottledwater.org/rpet-facts/",
        "https://scrapmanagement.com/blog/what-is-rpet/"
    ]
    scrape_and_save_json(urls, "knowledge_base")