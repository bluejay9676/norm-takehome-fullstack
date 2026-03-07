from fastapi import FastAPI, Query
from app.utils import Output, Input
from app.utils import DocumentService, QdrantService
from contextlib import asynccontextmanager
from app.constants import DOCUMENT_SERVICE, QDRANT_SERVICE



services = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    services[DOCUMENT_SERVICE] = DocumentService()
    documents = list(services[DOCUMENT_SERVICE].create_documents("../docs/laws.pdf"))
    services[QDRANT_SERVICE] = QdrantService()
    services[QDRANT_SERVICE].connect()
    services[QDRANT_SERVICE].load(documents)
    yield
    return


app = FastAPI(lifespan=lifespan)


"""
Please create an endpoint that accepts a query string, e.g., "what happens if I steal 
from the Sept?" and returns a JSON response serialized from the Pydantic Output class.
"""

@app.post("/query")
async def legal_advice(input_data: Input) -> Output:
    output = services[QDRANT_SERVICE].query(input_data.query)
    return output


# Create an API endpoint that accepts a query string and returns a JSON response.
# ● This endpoint should interact with the QdrantService to process the query and return the results.
# ● Ensure the output is correctly serialized using the Output class from pydantic.
# ● Use Docker to containerize the application. Feel free to modify the existing Dockerfile to suit any
# changes made during development.