from wbib import wbib

# Example of query_options dictionary:
# import queries
# query_options = {
#     "map of institutions": {
#         "label": "Map of institutions",
#         "query": queries.get_query_url_for_locations(),
#     },
#     "100 most recent articles": {
#         "label": "100 most recent articles",
#         "query": queries.get_query_url_for_articles(),
#     },
#     "list of authors": {
#         "label": "list of authors",
#         "query": queries.get_query_url_for_authors(),
#     },
#     "list of topics": {
#         "label": "list of co-studied topics",
#         "query": queries.get_topics_as_table(),
#     },
#     "list of journals": {
#         "label": "list of co-studied topics",
#         "query": queries.get_query_url_for_venues(),
#     },
# }


def render_section(query_name, query_options, qids_for_articles):
    """
  Renders the html code for one embedded SPARQL query.

  Args:
    query_name: 
      A query name that should match a valid key in the 
      "query_options" dictionary.
    query_options: 
      A dict containing the different SPARQL query options for the dashboard
    qids_for_articles:
      A list of qids for the articles of interest

  Returns:
    sections: A string containing the html for a single iframes

   """

    legend = query_options[query_name]["label"]
    query_function = query_options[query_name]["query"]
    query_url = query_function(wbib.format_with_prefix(qids_for_articles))
    section = f"""<h5 class="title is-5" style="text-align:center;">{legend}</h5>
      <p align="center">
      <iframe width=75%  height="400" src="{query_url}"></iframe>
      </p>
      <br></br>"""
    return section


def render_sections(chosen_queries, query_options, qids_for_articles):
    """
  Renders the html code for multiple embedded SPARQL queries.

  Args:
    chosen_queries: 
      A list of query names that should match the valid keys in the 
      "query_options" dictionary.
    query_options: 
      A dict containing the different SPARQL query options for the dashboard
    qids_for_articles:
      A list of qids for the articles of interest

  Returns:
    sections: A string containing the html for multiple iframes

   """

    sections = ""
    for name in chosen_queries:
        sections += render_section(
            name, query_options=query_options, qids_for_articles=qids_for_articles
        )
    return sections


def render_header(site_title):
    header = f"""<!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{site_title}</title>
        <meta property="og:description" content="powered by Wikidata">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet"
          integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
        <link href="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js" rel="stylesheet"
          integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.2/css/bulma.min.css">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
      </head> """
    return header


def render_top(site_title, site_subtitle):
    top = f"""<body>
      <section class="section">
        <div class="container">
          <div class="columns is-centered">
            <div class="column is-half has-text-centered">
              <h1 class="title is-1">{site_title}</h1>
              <h2>{site_subtitle}</h2>
            </div>
          </div>
        </div>
        <div class="column is-half has-text-centered">
      </section>
      </section>"""
    return top

