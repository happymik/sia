import requests

def save_image_from_url(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved successfully at {save_path}")
        return save_path
    else:
        print(f"Failed to retrieve image from URL: {image_url}")


from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper

def generate_image_dalle(input_prompt):
    image_url = DallEAPIWrapper().run(input_prompt)
    return image_url
