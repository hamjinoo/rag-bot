from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.vector_store import vector_client
from app.parsers import parse_document


async def process_upload(file) -> str:
    text, metadata = parse_document(file)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
    )
    chunks = splitter.create_documents([text], metadatas=[metadata])
    vector_client.add_documents(chunks)
    return metadata["doc_id"]
