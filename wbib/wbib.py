""" Main functions for the use by end users.

A set of core functions that may be called from wbib.
Other modules will contain the specific queries and auxiliary functions.

  Typical usage example:
  
  qids = ["Q35185544", "Q34555562", "Q21284234"] 
  render_dashboard(
    qids_for_articles= qids,
    site_title="Wikidata Bibtex",
    site_subtitle="Demonstration")

"""


import pandas as pd
from wbib import queries, render
from wikidata2df import wikidata2df


DEFAULT_QUERY_OPTIONS = {
    "map of institutions": {
        "label": "map of institutions",
        "query": queries.get_query_url_for_locations,
    },
    "articles": {"label": "articles", "query": queries.get_query_url_for_articles,},
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


def render_dashboard(
    info,
    mode="basic",
    query_options=DEFAULT_QUERY_OPTIONS,
    sections_to_add=DEFAULT_SESSIONS,
    site_title="Wikidata Bibtex",
    site_subtitle="Demonstration",
):
    """
    Args:
        info: either a dict containing complex information for the selector or a list of QIDs
        mode: a string representing the mode. If "advanced", then a config is expected for the
          info parameters. If "basic", a list of QIDs is expected. Defaults to "advanced".
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

    html = (
        render.render_header(site_title)
        + render.render_top(site_title, site_subtitle)
        + render.render_sections(sections_to_add, query_options, info, mode)
        + """
  </p>
  </div>
 </br>
  <footer class="footer">
    <div class="container">
      <div class="content has-text-centered">
        <p>"""
        + license_statement
        + """  </p>def format_with_prefix(list_of_qids):

    list_with_prefix = ["wd:" + i for i in list_of_qids]
    return "{ " + " ".join(list_with_prefix) + " }"
        <p>"""
        + scholia_credit_statement
        + """</p>
        <p>"""
        + creator_statement
        + """ </p>
      </div>
    </div>
  </footer>
</body>
</html>
  """
    )
    return html


def convert_doi_to_qid(list_of_dois):
    """
  Converts a list of DOI ids to Wikidata QIDs.

  Args:
    list_of_dois: 
      A list of dois without prefix. For example:  
      ["10.3897/RIO.2.E9342", "10.3389/fimmu.2019.02736"]

  Returns:
    result: 
        A dict with two key-value pairs. The "missing" key contains a set
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
