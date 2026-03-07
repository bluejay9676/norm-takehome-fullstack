from pydantic import BaseModel
import qdrant_client
from llama_cloud import LlamaCloud

from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import Document, Node
from dataclasses import dataclass
from typing import Iterator
from llama_index.core.query_engine import CitationQueryEngine
import os
import re



LLAMA_CLOUD_PARSE_JOB_ID = "pjb-amjzbjn4myi6pp43vtk3kkxfilpc"

key = os.environ["OPENAI_API_KEY"]
llama_cloud = LlamaCloud(api_key=os.environ['LLAMA_CLOUD_API_KEY'])

SECTION_METADATA_KEY = "Section"

@dataclass
class Input:
    query: str
    file_path: str

@dataclass
class Citation:
    source: str
    text: str

def transform_nodes_to_citations(nodes: list[Node]) -> list[Citation]:
    citations = []
    for node in nodes:
        citations.append(Citation(
            source=node.metadata[SECTION_METADATA_KEY],
            text=node.get_text()
        ))
    return citations

class Output(BaseModel):
    query: str
    response: str
    citations: list[Citation]

class DocumentService:
    # Process the docs/laws.pdf: first pass = Llama Cloud parse, second pass = line reader (or directory reader) -> Document.
    def create_documents(self, file_path: str, by_paragraph: bool = True) -> Iterator[Document]:
        # ----- First pass: parse with Llama Cloud -----
        if LLAMA_CLOUD_PARSE_JOB_ID:
            result = llama_cloud.parsing.get(
                job_id=LLAMA_CLOUD_PARSE_JOB_ID,
                expand=["text_full", "metadata", "text"],
            )
        else:
            file_obj = llama_cloud.files.create(file=file_path, purpose="parse")
            result = llama_cloud.parsing.parse(
                file_id=file_obj.id,
                tier="agentic",
                version="latest",
                expand=["text_full", "metadata", "text"],
            )

        # ----- Second pass: re-parse full text, extract hierarchy, yield Document per section -----
        full_text = result.text_full
        if not full_text and result.text and result.text.pages:
            full_text = "\n".join(p.text for p in result.text.pages)

        if not full_text:
            return

        # Section header: outline number (e.g. "1.", "1.1.") OR "some characters :" (colon)
        section_re = re.compile(
            r"^(?:(?P<num>\d+(?:\.\d+)*)\.\s+(?P<rest1>.*)|(?P<title>.+):\s*(?P<rest2>.*))$"
        )
        current_section: str | None = None
        current_lines: list[str] = []
        previous_rest: str = ""
        for line in full_text.splitlines():
            m = section_re.match(line.strip())
            if m:
                # Flush previous section
                if current_section is not None and current_lines:
                    text = "\n".join(current_lines).strip()
                    if text:
                        yield Document(
                            metadata={SECTION_METADATA_KEY: current_section},
                            text=text,
                        )

                num_part = m.group("num")
                rest = m.group("rest1") or ""
                # Numbered outline (e.g. "1. Peace", "1.1. The law...")
                if m.group("num") is not None:
                    if rest and len(rest) < 20 and not rest.endswith("."):
                        current_section = f"{num_part}. {rest}"
                        previous_rest = rest
                    else:
                        current_section = f"{num_part}. {previous_rest}"
                    current_lines = [line] if rest else []

            else:
                if line.strip() or current_section is not None:
                    current_lines.append(line)

        if current_section is not None and current_lines:
            text = "\n".join(current_lines).strip()
            if text:
                yield Document(
                    metadata={SECTION_METADATA_KEY: current_section},
                    text=text,
                )



class QdrantService:
    def __init__(self, k: int = 2):
        self.index = None
        self.k = k
    
    def connect(self) -> None:
        client = qdrant_client.QdrantClient(location=":memory:")
        vstore = QdrantVectorStore(client=client, collection_name='temp')

        Settings.embed_model = OpenAIEmbedding()
        Settings.llm = OpenAI(api_key=key, model="gpt-4")

        self.index = VectorStoreIndex.from_vector_store(vector_store=vstore)

    def load(self, docs: list[Document] | None = None) -> None:
        if docs is None:
            docs = []
        for doc in docs:
            self.index.insert(doc)
    
    def query(self, query_str: str) -> Output:
        query_engine = CitationQueryEngine.from_args(
            self.index,
            similarity_top_k=self.k,
        )

        response = query_engine.query(query_str)
        citations = transform_nodes_to_citations(response.source_nodes)
        return Output(
            query=query_str,
            response=str(response),
            citations=citations
        )



# if __name__ == "__main__":
#     # Example workflow
#     doc_serivce = DocumentService() # implemented
#     docs = doc_serivce.create_documents("../docs/laws.pdf") 

#     index = QdrantService() # implemented
#     index.connect() # implemented
#     index.load(list(docs)) # implemented

#     output = index.query("what happens if I steal?") 
#     print(output)





