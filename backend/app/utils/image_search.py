import open_clip
import torch
from PIL import Image
import numpy as np

model, _, preprocess = open_clip.create_model_and_transforms(
    'ViT-B-32',
    pretrained='laion2b_s34b_b79k'
)
tokenizer = open_clip.get_tokenizer('ViT-B-32')

def extract_caption(img_path, candidate_texts=None):

    img = Image.open(img_path).convert("RGB")
    image_input = preprocess(img).unsqueeze(0)  

    with torch.no_grad():
        image_features = model.encode_image(image_input)

    if candidate_texts is None:
        candidate_texts = [
            "red dress",
            "blue jeans",
            "smartphone",
            "handbag",
            "laptop",
            "shoes",
            "watch",
            "headphones",
            "jacket",
            "sunglasses",
        ]

    text_inputs = tokenizer(candidate_texts)
    with torch.no_grad():
        text_features = model.encode_text(text_inputs)

    similarities = (image_features @ text_features.T).squeeze(0).cpu().numpy()

    best_idx = np.argmax(similarities)
    best_caption = candidate_texts[best_idx]

    return best_caption
