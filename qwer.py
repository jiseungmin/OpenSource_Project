from newsdataapi import NewsDataApiClient

# API key authorization, Initialize the client with your API key

api = NewsDataApiClient(apikey="pub_44039082bc349806241e6117906ca0659c2d4")

# Request parameters with keywords
keywords = ""

# Fetch the news articles with the specified keywords, language, and country
response = api.news_api(country="kr")

print(response)