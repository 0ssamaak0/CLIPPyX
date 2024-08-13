import yaml
import openai

# Load the configuration file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(stream=f)
openai_endpoint = config["text_embed"]["openai_endpoint"]
openai_api_key = config["text_embed"]["openai_api_key"]
openai_model = config["text_embed"]["openai_model"]


client = openai.OpenAI(base_url=openai_endpoint, api_key=openai_api_key)


def get_text_embeddings(text):
    """
    Sends a POST request to the OpenAI API to get embeddings for the given text.

    Parameters:
    text (str): The text for which to get embeddings.

    Returns:
    list: The embeddings for the given text as a list of floats.
    """
    response = client.embeddings.create(
        model=openai_model,
        input=text,
    )
    return response.data[0].embedding
