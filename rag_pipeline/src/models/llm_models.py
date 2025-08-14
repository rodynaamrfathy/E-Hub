from langchain_ollama import OllamaLLM
from rag_pipeline.src.abstracts.abstract_llm import BaseLLM
from rag_pipeline.config.settings import DEVICE , LLM_CACHE_DIR
from langchain_core.outputs import Generation, LLMResult
from langchain_core.language_models.llms import LLM
from transformers import AutoModelForCausalLM, AutoTokenizer
from pydantic import Field
import torch
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class OLLAMA_LLM(BaseLLM):
    def __init__(self, model_name, cache_folder):
        logger.info(f"🤖 Initializing OLLAMA_LLM with model: {model_name}")
        logger.info(f"📁 Cache folder: {cache_folder}")
        super().__init__(model_name, cache_folder)
        logger.info("✅ OLLAMA_LLM initialized successfully")

    def load_model(self):
        logger.info(f"🔥 Loading OLLAMA model: {self.model_name}")
        logger.info("⚙️ Configuration - Temperature: 0.3, Context: 4096")
        
        try:
            with tqdm(total=1, desc="🤖 Loading OLLAMA", unit="model") as pbar:
                model = OllamaLLM(
                    model=self.model_name, 
                    temperature=0.3, 
                    num_ctx=4096
                )
                pbar.update(1)
            
            logger.info("✅ OLLAMA model loaded successfully")
            logger.info(f"📊 Model details - Name: {self.model_name}, Temperature: 0.3, Context: 4096")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load OLLAMA model: {str(e)}")
            raise


class Hugging_Face_LLM(LLM):
    model_name: str = Field(...)
    cache_folder: str = Field(default=LLM_CACHE_DIR)

    tokenizer: AutoTokenizer = None
    model: AutoModelForCausalLM = None

    def _call(self, prompt: str, stop=None) :
        if self.tokenizer is None or self.model is None:
            self.load_model()

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=512)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        if stop:
            for s in stop:
                if s in text:
                    text = text.split(s)[0]

        return text

    def _generate(self, prompts, stop=None) :
        generations = [[Generation(text=self._call(prompt, stop=stop))] for prompt in prompts]
        return LLMResult(generations=generations)

    def load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir=self.cache_folder
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            cache_dir=self.cache_folder,
            torch_dtype=DEVICE,
            device_map="auto"
        )

    @property
    def _llm_type(self) -> str:
        return "custom_huggingface_llm"
