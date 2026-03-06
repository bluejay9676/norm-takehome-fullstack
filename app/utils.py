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

    """
    Update this service to load the pdf and extract its contents.
    The example code below will help with the data structured required
    when using the QdrantService.load() method below. Note: for this
    exercise, ignore the subtle difference between llama-index's 
    Document and Node classes (i.e, treat them as interchangeable).

    # example code
    def create_documents() -> list[Document]:

        docs = [
            Document(
                metadata={"Section": "Law 1"},
                text="Theft is punishable by hanging",
            ),
            Document(
                metadata={"Section": "Law 2"},
                text="Tax evasion is punishable by banishment.",
            ),
        ]

        return docs

    The parsing logic should accurately identify and separate different laws or sections within the
    PDF, ensuring the data structure aligns with the Document class requirements.
    """

    # Process the docs/laws.pdf: first pass = Llama Cloud parse, second pass = line reader (or directory reader) -> Document.
    def create_documents(self, file_path: str, by_paragraph: bool = True) -> Iterator[Document]:
        # ----- First pass: parse with Llama Cloud -----
        if LLAMA_CLOUD_PARSE_JOB_ID:
            result = llama_cloud.parsing.get(
                job_id=LLAMA_CLOUD_PARSE_JOB_ID,
                expand=["markdown_full", "text_full", "metadata", "text"],
            )
        else:
            file_obj = llama_cloud.files.create(file=file_path, purpose="parse")
            result = llama_cloud.parsing.parse(
                file_id=file_obj.id,
                tier="agentic",
                version="latest",
                expand=["markdown_full", "text_full", "metadata", "text"],
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
                # Numbered outline (e.g. "1. Peace", "1.1. The law...")
                if m.group("num") is not None:
                    num_part, rest = m.group("num"), (m.group("rest1") or "").strip()
                    if rest and len(rest) < 20 and not rest.endswith("."):
                        current_section = f"{num_part}. {rest}"
                        previous_rest = rest
                    else:
                        current_section = f"{num_part}. {previous_rest}"
                    current_lines = [line] if rest else []
                # Colon-style header (e.g. "Section Name :" or "Law 1:")
                else:
                    title_part = (m.group("title") or "").strip()
                    rest = (m.group("rest2") or "").strip()
                    current_section = title_part or "Section"
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

        """
        This method needs to initialize the query engine, run the query, and return
        the result as a pydantic Output class. This is what will be returned as
        JSON via the FastAPI endpount. Fee free to do this however you'd like, but
        a its worth noting that the llama-index package has a CitationQueryEngine...

        Also, be sure to make use of self.k (the number of vectors to return based
        on semantic similarity).

        # Example output object
        citations = [
            Citation(source="Law 1", text="Theft is punishable by hanging"),
            Citation(source="Law 2", text="Tax evasion is punishable by banishment."),
        ]

        output = Output(
            query=query_str, 
            response=response_text, 
            citations=citations
            )
        
        return output

        """
        query_engine = CitationQueryEngine.from_args(
            self.index,
            similarity_top_k=self.k,
        )

        response = query_engine.query(query_str)
        citations = transform_nodes_to_citations(response.source_nodes)
        return Output(
            query=query_str,
            response=response,
            citations=citations
        )
       

if __name__ == "__main__":
    # Example workflow
    doc_serivce = DocumentService() # implemented
    docs = doc_serivce.create_documents("../docs/laws.pdf") 

    index = QdrantService() # implemented
    index.connect() # implemented
    index.load(list(docs)) # implemented

    output = index.query("what happens if I steal?") 
    print(output)





