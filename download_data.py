import click
import os
import pickle

from Bio import Entrez
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# TODO: use pubmed as param and get info from other dbs
def search(query, max_results=5):
    """Searches the query in pubmed's API"""
    with Entrez.esearch(
        db="pubmed", sort="relevance", term=query, retmax=max_results
    ) as handle:
        results = Entrez.read(handle)
        return results["IdList"]


def fetch_details(id_list: list[str]):
    # read docs for other retmode values
    with Entrez.efetch(db="pubmed", id=",".join(id_list), retmode="xml") as handle:
        records = Entrez.read(handle)
    return records


@click.command()
@click.option(
    "--query",
    required=True,
    help="Query string to search on pubmed's API.",
)
@click.option(
    "--max_results",
    default=5,
    help="Maximum number of results for the pubmed query",
)
@click.option(
    "--filename",
    default="pubmed_data.pkl",
    help="Pickle filename to save query results.",
)
def download_data(query: str, filename: str, max_results: int):
    '''
    Downloads papers from PubMed according to the given query and then creates a pickle file with the results.
    '''

    # Email for NCBI's user agreement
    email = os.getenv("EMAIL")
    if email is None:
        print("Missing user email. Add the environment variable `EMAIL` to the .env file with the user's email.")
        return

    # TODO: add stub
    Entrez.email = email  # type: ignore

    # create folder path if it doesn't exist
    path = Path(filename)
    parent_path = str(path.parent)
    if parent_path != "." and not os.path.exists(parent_path):
        os.makedirs(parent_path)

    # queries pubmed
    ids = search(query, max_results)
    breakpoint()
    articles = fetch_details(ids)

    # gets content (pickle for now)
    file = open(str(path), "wb")
    pickle.dump(
        {
            "query": query,
            "results": articles,
        },
        file,
    )
    file.close()


if __name__ == "__main__":
    download_data()
