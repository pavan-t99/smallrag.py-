from transformers import MarianMTModel

model = MarianMTModel.from_pretrained(
    "Helsinki-NLP/opus-mt-en-te",
    force_download=True
)