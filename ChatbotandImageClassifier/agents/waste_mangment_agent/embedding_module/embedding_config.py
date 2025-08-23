from pathlib import Path
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

# Configuration class
class agent_embedding_module:
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    PROJECT_ROOT: Path = ROOT_DIR
    DEFAULT_EMBEDDER: str = "sentence-transformers/all-MiniLM-L6-v2"
    CACHE_DIR: Path = PROJECT_ROOT / "cache"
    EMBEDDING_DIM: int = 384
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    NORMALIZE_EMBEDDINGS: bool = True

    def __init__(self, embedder_name=None, cache_dir=None, normalize=None):
        self.embedder_name = embedder_name or self.DEFAULT_EMBEDDER
        self.cache_dir = cache_dir or self.CACHE_DIR
        self.normalize = normalize if normalize is not None else self.NORMALIZE_EMBEDDINGS

    def summary(self) -> str:
        return (
            f"Embedder: {self.embedder_name}\n"
            f"Cache Dir: {self.cache_dir}\n"
            f"Device: {self.DEVICE}\n"
            f"Normalize: {self.normalize}\n"
            f"Embedding Dim: {self.EMBEDDING_DIM}"
        )

    # Mean pooling with attention mask
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, dim=1) / torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)

    # Embedding + similarity pipeline
    def embed(self, sentences):
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(self.embedder_name, cache_dir=self.cache_dir)
        model = AutoModel.from_pretrained(self.embedder_name, cache_dir=self.cache_dir).to(self.DEVICE)

        # Tokenize input
        encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt').to(self.DEVICE)

        # Forward pass
        with torch.no_grad():
            model_output = model(**encoded_input)

        # Pooling
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

        # Optional normalization
        if self.normalize:
            sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        return sentence_embeddings

