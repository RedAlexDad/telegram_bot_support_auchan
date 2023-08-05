import replicate

# https://replicate.com/account/api-tokens
API_TOKEN = ''

client = replicate.Client(api_token=API_TOKEN)

output = client.run(
    # CV
    # "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
    # Стихотворение
    # "replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1",
    # Генерирует код
    # "replicate/hello-world:5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
    # input={"text": "python"}
    # paraphrase-gpt (Аналог GPT-3.5)
    # Примечание: очень долго отвечает
    "replicate/gpt-j-6b:b3546aeec6c9891f0dd9929c2d3bedbf013c12e02e7dd0346af09c37e008c827",
    input={"prompt": "Who founded Google and in what year?"}
)

for item in output:
    print(item)

