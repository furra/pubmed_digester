# Pubmed API digester with abstract retrieval through RAG.

## Overview
Downloads data from PubMed according to a given query and creates a pickle file. The data is then read from the file,the relevant information is extracted and then inserted into PostgreSQL database.
Afterwards, the abstract texts are processed and their embeddings calculated through an LLM, where they can finally be queried.

## To use this tool
Create a `.env` file with these variables:

- `GOOGLE_API_KEY`: API key to the LLM
- `EMAIL`: User's email to comply with PubMed's terms of use
- `DATABASE_URL`: URL to connect to the PostgreSQL database

## Creating the database
The file `create_db.py` reads the `models.py` file and creates the database (PostgreSQL) through SQLAlchemy.

```
python create_db.py
```

## Download data from PubMed
`biopython` is used to query the PubMed API in the `download_data.py` file:
```
python download_data.py --help
Usage: download_data.py [OPTIONS]

  Downloads papers from PubMed according to the given query and then creates a pickle file with the results.

Options:
  --query TEXT           Query string to search on pubmed's API.  [required]
  --max_results INTEGER  Maximum number of results for the pubmed query
  --filename TEXT        Pickle filename to save query results.
  --help                 Show this message and exit.

```

This creates a pickle (`.pkl`) file with the responding json in it.

## Inserting the downloaded papers to the database
The `insert_to_db.py` file reads a pickle file, creates the database models and then inserts them to the database.
```
python insert_to_db.py --help
Usage: insert_to_db.py [OPTIONS]

  Reads a pickle file with results from PubMed, creates the database models, and then inserts them into the database.

Options:
  --filename TEXT  Pickle filename to read results from.  [required]
  --help           Show this message and exit.

```

## Creating embeddings
Now, the `populate_embeddings.py` file has to be called to actually create the embeddings and insert them to the database:

```
python populate_embeddings.py --help
Usage: populate_embeddings.py [OPTIONS]

  Calculates embeddings for all documents in the database according to the
  given paramaters (NOTE: `embedding_size` must be the same number as the size
  defined in the Abstract model's `embedding` attribute), creates Abstract
  objects, and then commits them to the database.

Options:
  --chunk_size INTEGER     Number of characters for each text chunk.
  --chunk_overlap INTEGER  Number of overlapping characters for each
                           consecutive text chunk.
  --help                   Show this message and exit.
```

This creates the `Abstract` model with their corresponding embeddings.

## Creating embeddings
Finally, we can query the database with the `query_embeddings.py` file:
```
python query_embeddings.py --help
Usage: query_embeddings.py [OPTIONS]

Options:
  --query TEXT     Text query to compare to the pubmed abstracts.  [required]
  --limit INTEGER  Maximum number of results to be shown, ordered by text similarity (Euclidean L2 distance).
  --help           Show this message and exit.

```

Example:
```
~ python query_embeddings.py --query "fractal antenna"
similarity: 0.4116161522619592
chunk: The wide frequency range of interaction with EMF is the functional characteristic of a fractal antenna, and DNA appears to possess the two structural characteristics of fractal antennas, electronic conduction and self symmetry. These properties contribute to greater reactivity of DNA with EMF in the environment, and the DNA damage could account for increases in cancer epidemiology, as well as variations in the rate of chemical evolution in early geologic history.
chunk index: 0
document title: DNA is a fractal antenna in electromagnetic fields.
full text: To review the responses of deoxyribonucleic acid (DNA) to electromagnetic fields (EMF) in different frequency ranges, and characterise the properties of DNA as an antenna.

We examined published reports of increased stress protein levels and DNA strand breaks due to EMF interactions, both of which are indicative of DNA damage. We also considered antenna properties such as electronic conduction within DNA and its compact structure in the nucleus.

EMF interactions with DNA are similar over a range of non-ionising frequencies, i.e., extremely low frequency (ELF) and radio frequency (RF) ranges. There are similar effects in the ionising range, but the reactions are more complex.

The wide frequency range of interaction with EMF is the functional characteristic of a fractal antenna, and DNA appears to possess the two structural characteristics of fractal antennas, electronic conduction and self symmetry. These properties contribute to greater reactivity of DNA with EMF in the environment, and the DNA damage could account for increases in cancer epidemiology, as well as variations in the rate of chemical evolution in early geologic history.

---------------------------------------------

similarity: 0.44397101875391926
chunk: EMF interactions with DNA are similar over a range of non-ionising frequencies, i.e., extremely low frequency (ELF) and radio frequency (RF) ranges. There are similar effects in the ionising range, but the reactions are more complex.
chunk index: 0
document title: DNA is a fractal antenna in electromagnetic fields.
full text: To review the responses of deoxyribonucleic acid (DNA) to electromagnetic fields (EMF) in different frequency ranges, and characterise the properties of DNA as an antenna.

We examined published reports of increased stress protein levels and DNA strand breaks due to EMF interactions, both of which are indicative of DNA damage. We also considered antenna properties such as electronic conduction within DNA and its compact structure in the nucleus.

EMF interactions with DNA are similar over a range of non-ionising frequencies, i.e., extremely low frequency (ELF) and radio frequency (RF) ranges. There are similar effects in the ionising range, but the reactions are more complex.

The wide frequency range of interaction with EMF is the functional characteristic of a fractal antenna, and DNA appears to possess the two structural characteristics of fractal antennas, electronic conduction and self symmetry. These properties contribute to greater reactivity of DNA with EMF in the environment, and the DNA damage could account for increases in cancer epidemiology, as well as variations in the rate of chemical evolution in early geologic history.

---------------------------------------------

similarity: 0.4583081722578003
chunk: To review the responses of deoxyribonucleic acid (DNA) to electromagnetic fields (EMF) in different frequency ranges, and characterise the properties of DNA as an antenna.

We examined published reports of increased stress protein levels and DNA strand breaks due to EMF interactions, both of which are indicative of DNA damage. We also considered antenna properties such as electronic conduction within DNA and its compact structure in the nucleus.
chunk index: 0
document title: DNA is a fractal antenna in electromagnetic fields.
full text: To review the responses of deoxyribonucleic acid (DNA) to electromagnetic fields (EMF) in different frequency ranges, and characterise the properties of DNA as an antenna.

We examined published reports of increased stress protein levels and DNA strand breaks due to EMF interactions, both of which are indicative of DNA damage. We also considered antenna properties such as electronic conduction within DNA and its compact structure in the nucleus.

EMF interactions with DNA are similar over a range of non-ionising frequencies, i.e., extremely low frequency (ELF) and radio frequency (RF) ranges. There are similar effects in the ionising range, but the reactions are more complex.

The wide frequency range of interaction with EMF is the functional characteristic of a fractal antenna, and DNA appears to possess the two structural characteristics of fractal antennas, electronic conduction and self symmetry. These properties contribute to greater reactivity of DNA with EMF in the environment, and the DNA damage could account for increases in cancer epidemiology, as well as variations in the rate of chemical evolution in early geologic history.

---------------------------------------------
```