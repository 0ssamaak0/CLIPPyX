import yaml

# Load the configuration file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
checkpoint = config['clip']['transformers_clip_checkpoint']

# load model and tokenizer
model = CLIPModel.from_pretrained(checkpoint)
processor = CLIPProcessor.from_pretrained(checkpoint)