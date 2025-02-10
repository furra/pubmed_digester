from datetime import datetime
from pgvector.sqlalchemy import Vector  # type: ignore
from sqlalchemy import (
    ARRAY,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List


class Base(DeclarativeBase):
    pass


class Journal(Base):
    __tablename__ = "journals"

    id: Mapped[int] = mapped_column(primary_key=True)
    nlm_id: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String())
    issn: Mapped[str] = mapped_column(String(20))
    documents: Mapped[List["Document"]] = relationship(back_populates="journal")

    __table_args__ = (UniqueConstraint("nlm_id", name="model_nlm_id_key"),)

    def __repr__(self) -> str:
        return (
            f"Journal(id={self.id!r}, country={self.country!r}, title={self.title!r})"
        )


author_document_association = Table(
    "author_document",
    Base.metadata,
    Column("author_id", Integer, ForeignKey("authors.id")),
    Column("document_id", Integer, ForeignKey("documents.id")),
    UniqueConstraint(
        "author_id", "document_id", name="model_author_id_document_id_key"
    ),
)


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    identifier: Mapped[str | None] = mapped_column(String(20))
    affiliation: Mapped[str | None] = mapped_column(String())
    last_name: Mapped[str] = mapped_column(String(30))
    fore_name: Mapped[str] = mapped_column(String(30))
    initials: Mapped[str] = mapped_column(String(8))
    documents: Mapped[List["Document"]] = relationship(
        "Document", secondary=author_document_association, back_populates="authors"
    )

    __table_args__ = (
        UniqueConstraint("identifier", name="model_author_identifier_key"),
    )

    def __repr__(self) -> str:
        return f"Author(id={self.id!r}, identifier={self.identifier!r}, fore_name={self.fore_name!r}, last_name={self.last_name!r})"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    identifier: Mapped[str | None] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String())
    abstract: Mapped[str] = mapped_column(String())
    date: Mapped[datetime | None] = mapped_column(insert_default=None)
    date_completed: Mapped[datetime | None] = mapped_column(insert_default=None)
    date_revised: Mapped[datetime | None] = mapped_column(insert_default=None)
    language: Mapped[str] = mapped_column(String(15))
    authors: Mapped[List["Author"]] = relationship(
        "Author", secondary=author_document_association, back_populates="documents"
    )
    journal_id: Mapped[int | None] = mapped_column(ForeignKey("journals.id"))
    journal: Mapped["Journal"] = relationship(back_populates="documents")
    publication_type: Mapped[str] = mapped_column(String(30))
    mesh_terms: Mapped[List[str]] = Column(MutableList.as_mutable(ARRAY(String())))  # type: ignore
    keyword_list: Mapped[List[str]] = Column(MutableList.as_mutable(ARRAY(String())))  # type: ignore
    abstract_chunks: Mapped[List["Abstract"]] = relationship(back_populates="document")

    __table_args__ = (
        UniqueConstraint("identifier", name="model_document_identifier_key"),
    )

    def __repr__(self) -> str:
        date = self.date.strftime("%d-%m-%Y") if self.date is not None else None
        return f"Journal(id={self.id!r}, title={self.title!r}, identifier={self.identifier!r}, date={date})"


class Abstract(Base):
    __tablename__ = "abstracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    document: Mapped["Document"] = relationship(back_populates="abstract_chunks")
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String())
    embedding = mapped_column(Vector(256))

    def __repr__(self) -> str:
        return f"Abstract(id={self.id!r}, document_id={self.document_id!r}, chunk={self.chunk_index!r}, text={self.text[:50]!r})"
