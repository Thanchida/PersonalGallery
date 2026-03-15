from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

# Load processor and model once at startup so route calls can reuse them.
# The model weights are downloaded automatically on first run.
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


def generate_caption(image_path: str) -> str:
    """Generate a caption for a local image path using BLIP."""
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=50)
    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption.strip()
