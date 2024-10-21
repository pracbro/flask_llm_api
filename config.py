class Config:
    MODEL_ID = 'HuggingFaceH4/zephyr-7b-beta'
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# You can extend this class for different environments
