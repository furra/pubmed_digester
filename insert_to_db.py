import click, os, pickle


from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import TypedDict

from models import Author, Document, Journal

load_dotenv()

DateType = TypedDict("DateType", {"Year": str, "Month": str, "Day": str})


def parse_date(date: DateType | None) -> datetime | None:
    return (
        datetime(year=int(date["Year"]), month=int(date["Month"]), day=int(date["Day"]))
        if date is not None
        else None
    )


def first_item_or_none(attribute: list[str]) -> str | None:
    return next(iter(attribute), None)


@click.command()
@click.option(
    "--filename",
    required=True,
    help="Pickle filename to read results from.",
)
def insert_to_db(filename):
    '''
    Reads a pickle file with results from PubMed, creates the database models, and finally inserts them into the database.
    '''
    engine = create_engine(os.getenv("DATABASE_URL"))

    with Session(engine) as session:

        articles = pickle.load(open(filename, "rb"))
        for article in articles["results"]["PubmedArticle"]:
            # check for data first
            citation = article["MedlineCitation"]
            article = citation["Article"]
            abstract = article.get("Abstract", {}).get("AbstractText", None)

            # skip if there's no abstract
            if abstract[0] is None:
                print(f"{identifier}/{title}")
                continue
            abstract = "\n\n".join([str(text) for text in abstract])
            # Journal class
            journal_info = citation["MedlineJournalInfo"]
            journal = Journal(
                nlm_id=journal_info["NlmUniqueID"],
                country=journal_info["Country"],
                title=article["Journal"]["Title"],
                issn=str(article["Journal"]["ISSN"]),
            )
            session.add(journal)

            # Author classes
            authors = []

            # throw this to a function and use list comprehension?
            for author_entry in article["AuthorList"]:
                affiliation = author_entry["AffiliationInfo"]
                affiliation = (
                    affiliation[0]["Affiliation"] if len(affiliation) > 0 else None
                )

                author_identifier = first_item_or_none(author_entry["Identifier"])

                author = Author(
                    identifier=(
                        str(author_identifier)
                        if author_identifier is not None
                        else None
                    ),
                    affiliation=affiliation,
                    last_name=author_entry["LastName"],
                    fore_name=author_entry["ForeName"],
                    initials=author_entry["Initials"],
                )
                authors.append(author)
            session.bulk_save_objects(authors)

            # Document class
            publication_type = first_item_or_none(article["PublicationTypeList"])
            document_identifier = first_item_or_none(article["ELocationID"])
            document = Document(
                title=article["ArticleTitle"],
                identifier=(
                    str(document_identifier)
                    if document_identifier is not None
                    else None
                ),
                date=parse_date(
                    article["ArticleDate"][0]
                    if len(article["ArticleDate"]) > 0
                    else None
                ),
                date_completed=parse_date(citation["DateCompleted"]),
                date_revised=parse_date(citation["DateRevised"]),
                language=first_item_or_none(article["Language"]),
                authors=authors,
                journal=journal,
                publication_type=(
                    str(publication_type) if publication_type is not None else None
                ),
                mesh_terms=[
                    str(mesh_term["DescriptorName"])
                    for mesh_term in citation["MeshHeadingList"]
                ],
                keyword_list=(
                    [str(keyword) for keyword in citation["KeywordList"][0]]
                    if len(citation["KeywordList"]) > 0
                    else []
                ),
                abstract=abstract,
            )
            session.add(document)
            session.flush()
        session.commit()


if __name__ == "__main__":
    insert_to_db()
