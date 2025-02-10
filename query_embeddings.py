import click, os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from sqlalchemy import asc, create_engine
from sqlalchemy.orm import Session

from models import Abstract

load_dotenv()


@click.command()
@click.option(
    "--query",
    required=True,
    help="Text query to compare to the pubmed abstracts.",
)
# TODO: add similarity parameter
@click.option(
    "--limit",
    default=3,
    help="Text query to compare to the pubmed abstracts.",
)
def query_embeddings(query: str, limit: int):

    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db_url = os.getenv("DATABASE_URL")
    if db_url is None:
        click.echo(
            "Missing `DATABASE_URL` environment variable. Please add it to the `.env` file."
        )
        return
    engine = create_engine(db_url)

    with Session(engine) as session:
        query_embedding = embedding_model.embed_query(
            query,
            task_type="RETRIEVAL_QUERY",
            # TODO: read this from the db instead
            output_dimensionality=256,
        )

        results = (
            session.query(Abstract)
            .add_columns(
                Abstract.embedding.l2_distance(query_embedding).label("similarity")
            )
            .order_by(asc("similarity"))
            .limit(limit)
            .all()
        )
        for result, result_similarity in results:
            print(f"similarity: {result_similarity}")
            print(f"chunk: {result.text}")
            print(f"chunk index: {result.chunk_index}")
            print(f"document title: {result.document.title}")
            print(f"full text: {result.document.abstract}")

            print("\n---------------------------------------------\n")


if __name__ == "__main__":
    query_embeddings()
