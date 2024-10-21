import transformers
from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer
import torch

# Initialize the model and tokenizer
def load_model():
    model_id = 'HuggingFaceH4/zephyr-7b-beta'

    # Load in 4-bit quantization config (if needed)
    bnb_config = transformers.BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type='nf4',
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    model_config = transformers.AutoConfig.from_pretrained(
        model_id,
        trust_remote_code=True,
        max_new_tokens=1024
    )

    model = transformers.AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        config=model_config,
        quantization_config=bnb_config,
        device_map='auto'
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # Create pipeline with extended max length
    query_pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.float16,
        max_length=6000,
        max_new_tokens=500,
        device_map="auto"
    )

    llm = HuggingFacePipeline(pipeline=query_pipeline)
    return llm

# Use the model for generating recommendations
def get_recommendation(prompt):
    model = load_model()
    response = model(prompt=prompt)
    return response
