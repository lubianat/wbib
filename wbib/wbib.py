"""Main module."""
import os
import glob
import urllib.parse
import pandas as pd
from wbib import queries
import unicodedata
from wikidata2df import wikidata2df


def convert_doi_to_qid(list_of_dois):
    """
  Args:
    dois: A list of dois without prefix (e.g. ["10.3897/RIO.2.E9342", "10.3389/fimmu.2019.02736"])

  Returns:
    result: A dict with two key-value pairs. The "missing" key contains a set with the DOIs not found, 
    the "qids" key contain a set with the QIDs found on Wikidata. 
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
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}}}
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


def format_with_prefix(list_of_qids):
    list_with_prefix = ["wd:" + i for i in list_of_qids]
    return "{ " + " ".join(list_with_prefix) + " }"


def render_dashboard(
    qids_for_articles, site_title="Wikidata Bibtex", site_subtitle="Demonstration"
):
    """
    Renders the html for a default dashboard

    Args:
        qids_for_articles: An array of Wikidata Qids (Q[0-9]*) for scholarly works       
        site_title = The title of the dashboard
        site_subtitle = An explaining subtitle for the dashboard

    Returns:
        An html as an string. 

    """
    url1 = queries.get_query_url_for_articles(format_with_prefix(qids_for_articles))
    url1_legend = "Articles in the bibtex file"
    url2 = queries.get_query_url_for_topic_bubble(format_with_prefix(qids_for_articles))
    url2_legend = "Topics of those articles"
    url4 = queries.get_query_url_for_venues(format_with_prefix(qids_for_articles))
    url4_legend = "Most common journals "
    url5 = queries.get_query_url_for_authors(format_with_prefix(qids_for_articles))
    url5_legend = "Authors of the works"
    url6 = queries.get_query_url_for_locations(format_with_prefix(qids_for_articles))
    url6_legend = "Map of institutions"
    url7 = queries.get_query_url_for_citing_authors(
        format_with_prefix(qids_for_articles)
    )
    url7_legend = "Authors that cited those works"

    license_statement = """
            This content is available under a <a target="_blank" href="https://creativecommons.org/publicdomain/zero/1.0/"> 
            Creative Commons CC0</a> license.
    """
    scholia_credit_statement = """
    SPARQL queries adapted from <a target="_blank" href="https://scholia.toolforge.org/">Scholia</a>
    """

    creator_statement = """
    Dashboard  generated via Wikidata Bib
    """

    html = (
        """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>"""
        + site_title
        + """</title>
  <meta property="og:description" content="powered by Wikidata">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet"
    integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
  <link href="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js" rel="stylesheet"
    integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.2/css/bulma.min.css">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
</head>
<body>
  <section class="section">
    <div class="container">
      <div class="columns is-centered">
        <div class="column is-half has-text-centered">
          <h1 class="title is-1"> """
        + site_title
        + """</h1>
          <h2>"""
        + site_subtitle
        + """</h2>
        </div>
      </div>
    </div>
    <div class="column is-half has-text-centered">
  </section>
   </section>

      <h5 class="title is-5" style="text-align:center;"> """
        + url1_legend
        + """</h5>
        <p align="center">
          <iframe width=75% height="400" src="""
        + '"'
        + url1
        + '"'
        + """></iframe>
        </p>
    <br></br>
    <h5 class="title is-5" style="text-align:center;">"""
        + url2_legend
        + """ </h5>
        <p align="center">
        <iframe width=75%  height="400" src="""
        + '"'
        + url2
        + '"'
        + """></iframe>
        </p>
        <br></br>
      <h5 class="title is-5" style="text-align:center;display:block;"> """
        + url4_legend
        + """</h5>
                  <p align="center">
          <iframe width=75%   height="400" src="""
        + '"'
        + url4
        + '"'
        + """></iframe>
          </p>
   <br></br>
      <h5 class="title is-5" style="text-align:center;"> """
        + url5_legend
        + """  </h5>
        <p align="center">
            <iframe width=75%  height="400" src="""
        + '"'
        + url5
        + '"'
        + """></iframe>
        </p>
<br></br>
      <h5 class="title is-5" style="text-align:center;"> """
        + url6_legend
        + """ </h5>
      <p align="center">
            <iframe width=75%  height="400" src="""
        + '"'
        + url6
        + '"'
        + """></iframe>
      </p>
<br></br>
      <h5 class="title is-5" style="text-align:center;"> """
        + url7_legend
        + """ </h5>
      <p align="center">
            <iframe width=75%  height="400" src="""
        + '"'
        + url7
        + '"'
        + """></iframe>
      </p>
<br></br>
  </p>
  </div>
 </br>
  <footer class="footer">
    <div class="container">
      <div class="content has-text-centered">
        <p>"""
        + license_statement
        + """  </p>
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

