import meilisearch
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

client = meilisearch.Client(
    os.getenv("MEILISEARCH_URL"), os.getenv("MEILISEARCH_API_KEY")
)


async def search_products(query: str, filters: str = None):
    # Apply filters if provided
    filter_query = filters if filters else ""
    print(filters)
    search_results = client.index("products").search(query, {"filter": filter_query})
    return search_results
