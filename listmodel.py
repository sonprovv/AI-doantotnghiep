from google import genai
client = genai.Client(api_key="AIzaSyBwjF1FoNFFK6wrJXvN6xwPQTI9UAiivys")
models = client.models.list()

for m in models:
    print(m)
