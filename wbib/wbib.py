"""Main functions for the use by end users.
"""


import pandas as pd
from pathlib import Path
from wbib import queries, render
from wikidata2df import wikidata2df
from jinja2 import Environment, PackageLoader

env = Environment(
    loader=PackageLoader("wbib", "templates"),
)

DEFAULT_QUERY_OPTIONS = {
    "map of institutions": {
        "label": "map of institutions",
        "query": queries.get_query_url_for_locations,
    },
    "articles": {
        "label": "articles",
        "query": queries.get_query_url_for_articles,
    },
    "list of authors": {
        "label": "list of authors",
        "query": queries.get_query_url_for_authors,
    },
    "list of topics": {
        "label": "list of co-studied topics",
        "query": queries.get_topics_as_table,
    },
    "list of journals": {
        "label": "list of venues",
        "query": queries.get_query_url_for_venues,
    },
    "curation of author items": {
        "label": "curation: curate author strings that are not yet linked to items",
        "query": queries.get_query_url_for_missing_author_items,
    },
    "curation of author affiliations": {
        "label": "curation: add affiliation/employment for authors lacking it",
        "query": queries.get_query_url_for_author_without_affiliation,
    },
}

DEFAULT_SESSIONS = [
    "map of institutions",
    "articles",
    "list of authors",
    "list of topics",
    "list of journals",
    "curation of author items",
    "curation of author affiliations",
]

EXAMPLE_PAGES = {"home": {"href": "/", "name": "Home"}}


def render_dashboard(
    info,
    mode="basic",
    query_options=DEFAULT_QUERY_OPTIONS,
    sections_to_add=DEFAULT_SESSIONS,
    site_title="Wikidata Bibtex",
    site_subtitle="Demonstration",
    filepath=".",
    pages={},
):
    """
    Renders a plain html string coding for a dashboard with embedded Wikidata SPARQL queries.
    At the same time, it saves the html to the file system via the filepath argument.


    ```
    DEFAULT_SESSIONS = [
        "map of institutions",
        "articles",
        "list of authors",
        "list of topics",
        "list of journals",
        "curation of author items",
        "curation of author affiliations",
    ]
    ```

    ```
    DEFAULT_QUERY_OPTIONS = {
        "map of institutions": {
            "label": "map of institutions",
            "query": wbib.queries.get_query_url_for_locations
        },
        "articles": {
            "label": "articles",
            "query": wbib.queries.get_query_url_for_articles
        },
        "list of authors": {
            "label": "list of authors",
            "query": wbib.queries.get_query_url_for_authors
        },
        "list of topics": {
            "label": "list of co-studied topics",
            "query": wbib.queries.get_topics_as_table
        },
        "list of journals": {
            "label": "list of venues",
            "query": wbib.queries.get_query_url_for_venues
        },
        "curation of author items": {
            "label": "curation: curate author strings that are not yet linked to items",
            "query": wbib.queries.get_query_url_for_missing_author_items
        },
        "curation of author affiliations": {
            "label": "curation: add affiliation/employment for authors lacking it",
            "query": queries.get_query_url_for_author_without_affiliation
        }
    }
    ```
    ```
    EXAMPLE_PAGES = {"home": {"href": "/", "name": "Home"}}
    ```
    Args:
        info (dict): Either a dict containing complex information for the selector or a list of QIDs.
        mode (str): A string representing the mode. If "advanced", then a config is expected for the
            info parameters. If "basic", a list of QIDs is expected. Defaults to "advanced".
        query_options (dict): A set of queries that might be used by the dashboard.
            See default for customizing queries or labels.
        sections_to_add (list): Names of the queries to be included in the dashboard.
            Standard is to include all.
        site_title (str): A title for the dashboard (if in "basic" mode)
        site_subtitle (str): A subtitle for the dashboard (if in "basic" mode)
        filepath (str): The filepath to write the dashboard to.
        pages (dict): The pages that will be part of the final dashboard, as to make a simple navbar.

    Returns:
        str: The html content for a static Wikidata-based dashboard.
            Note: also saves the file to the file system.
    """

    if mode == "advanced":
        if not isinstance(info, dict):
            raise TypeError(
                "In advanced mode, 'info' needs to be a dict obtained from the standard yaml file"
            )
        else:
            license_statement = info["license_statement"]
            scholia_credit_statement = info["scholia_credit"]
            creator_statement = info["creator_credit"]
            site_title = info["title"]
            site_subtitle = info["subtitle"]
            sections_to_add = info["sections"]

    if mode == "basic":

        license_statement = """
            This content is available under a <a target="_blank" href="https://creativecommons.org/publicdomain/zero/1.0/"> 
                Creative Commons CC0</a> license.
        """

        scholia_credit_statement = """
        SPARQL queries adapted from <a target="_blank" href="https://scholia.toolforge.org/">Scholia</a>
        """

        creator_statement = """
        Dashboard  generated via <a target="_blank" href="https://pypi.org/project/wbib/">Wikidata Bib</a>
        """

    sections = render.render_sections(sections_to_add, query_options, info, mode)

    template = env.get_template("template.html.jinja")
    rendered_template = template.render(
        site_title=site_title,
        site_subtitle=site_subtitle,
        sections=sections,
        license_statement=license_statement,
        scholia_credit=scholia_credit_statement,
        creator_statement=creator_statement,
        pages=pages,
    )

    filename = "{}.html".format(site_title.lower().strip().replace(" ", "_"))
    path_to_write = (
        Path(filepath).joinpath(filename) if filepath is "." else Path(filepath)
    )

    with open(path_to_write, "w") as html:
        html.write(rendered_template)

    return rendered_template


def convert_doi_to_qid(list_of_dois):
    """
    Converts a list of DOI ids to Wikidata QIDs.

    Args:
      list_of_dois (list): DOIs without prefix. For example:
        ["10.3897/RIO.2.E9342", "10.3389/fimmu.2019.02736"]

    Returns:
      dict: A dict with two key-value pairs. The "missing" key contains a set
          with the DOIs not found, the "qids" key contain a set with the
          QIDs found on Wikidata.
    """

    formatted_dois = '{ "' + '" "'.join(list_of_dois) + '"}'
    query = f"""SELECT ?id ?item  ?itemLabel
  WHERE {{
      {{
      SELECT ?item ?id WHERE {{
          VALUES ?unformatted_id {formatted_dois}
          BIND(UCASE(?unformatted_id) AS ?id)
          ?item wdt:P356 ?id.
      }}
      }}
      SERVICE wikibase:label 
      {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}}}
  """

    query_result = wikidata2df(query)

    result = {}

    result["qids"] = list(query_result["item"].values)
    result["missing"] = []

    for doi in list_of_dois:
        if doi.upper() not in list(query_result["id"].values):
            result["missing"].append(doi)

    result["qids"] = set(result["qids"])
    result["missing"] = set(result["missing"])
    return result
