import click, os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document as LangChainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter

from models import Abstract, Author, Document, Journal

load_dotenv()

# read this from the db
EMBEDDING_SIZE = 256


@click.command()
@click.option(
    "--chunk_size",
    default=500,
    help="Number of characters for each text chunk.",
)
@click.option(
    "--chunk_overlap",
    default=100,
    help="Number of overlapping characters for each consecutive text chunk.",
)
def calculate_embeddings(chunk_size: int, chunk_overlap: int):
    """
    Calculates embeddings for all documents in the database according to the given paramaters (NOTE: `embedding_size` must be the same number
    as the size defined in the Abstract model's `embedding` attribute), creates Abstract objects, and then commits them to the database.

    """

    # add error message for missing `GOOGLE_API_KEY`
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db_url = os.getenv("DATABASE_URL")
    if db_url is None:
        click.echo(
            "Missing `DATABASE_URL` environment variable. Please add it to the `.env` file."
        )
        return
    engine = create_engine(db_url)

    with Session(engine) as session:
        # Transforms the db documents into LangChain documents to use LangChain's TextSplitter
        lc_documents = [
            LangChainDocument(
                page_content=document.abstract,
                metadata={"source": document.id, "title": document.title},
            )
            for document in session.query(Document)
        ]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True,
        )

        chunks = text_splitter.split_documents(lc_documents)
        text_chunks = [doc.page_content for doc in chunks]
        ids = [doc.metadata["source"] for doc in chunks]
        titles = [doc.metadata["title"] for doc in chunks]

        embeddings = embedding_model.embed_documents(
            texts=text_chunks,
            task_type="RETRIEVAL_DOCUMENT",
            titles=titles,
            output_dimensionality=EMBEDDING_SIZE,
        )

        current_index = ids[0]
        chunk_index = 0
        # use zip instead?
        for i, embedding in enumerate(embeddings):
            if current_index != ids[i]:
                chunk_index = 0
            abstract = Abstract(
                document_id=ids[i],
                chunk_index=chunk_index,
                text=text_chunks[i],
                embedding=embedding,
            )
            chunk_index += 1
            session.add(abstract)

        session.commit()


if __name__ == "__main__":
    calculate_embeddings()
