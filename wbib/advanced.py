import urllib.parse
import yaml


def render_section(query_name, query_options, yaml_file):

    legend = query_options[query_name]["label"]
    query_url = query_options[query_name]["query"]
    section = (
        """
    <h5 class="title is-5" style="text-align:center;">"""
        + legend
        + """ </h5>
        <p align="center">
        <iframe width=75%  height="400" src="""
        + '"'
        + query_url(yaml_file)
        + '"'
        + """></iframe>
        </p>
        <br></br>
  """
    )
    return section


def render_sections(query_name_list, query_options, yaml_file):

    sections = ""
    for name in query_name_list:
        sections += render_section(
            name, query_options=query_options, yaml_file=yaml_file
        )
    return sections


def render_header(site_title):
    header = (
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
      
      """
    )
    return header


def render_top(site_title, site_subtitle):
    top = (
        """
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
"""
    )
    return top


def format_with_prefix(list_of_qids):
    list_with_prefix = ["wd:" + i for i in list_of_qids]
    return " ".join(list_with_prefix)


def get_selector(yaml_file):
    """
    The selector that decides the scope of the dashboard. It MUST have the keywords
    ?work and ?author. 
    You can override everything here by adapting the query on WDQS:
    https://w.wiki/3Cmd
    """

    fields_of_work = yaml_file["restriction"]["author_area"]

    if fields_of_work is not None:
        field_of_work_selector = (
            """
        VALUES ?field_of_work {"""
            + format_with_prefix(fields_of_work)
            + """}
        ?author wdt:P101 ?field_of_work.
        """
        )
    else:
        field_of_work_selector = ""

    topic_of_work = yaml_file["restriction"]["topic_of_work"]

    if topic_of_work is not None:
        topic_of_work_selector = (
            """
        VALUES ?topics {"""
            + format_with_prefix(topic_of_work)
            + """}
        ?work wdt:P921/wdt:P279* ?topics.
        """
        )
    else:
        topic_of_work_selector = ""

    region = yaml_file["restriction"]["institution_region"]

    if region is not None:
        region_selector = (
            """
        VALUES ?regions {"""
            + format_with_prefix(region)
            + """}
        ?country wdt:P361* ?regions.
        ?author ( wdt:P108 | wdt:P463 | wdt:P1416 ) / wdt:P361* ?organization . 
        ?organization wdt:P17 ?country.
        """
        )
    else:
        region_selector = ""

    gender = yaml_file["restriction"]["gender"]
    if gender is not None:
        gender_selector = (
            """
        VALUES ?regions {"""
            + format_with_prefix(gender)
            + """}
        ?author wdt:P21 wd:Q6581072.
        """
        )
    else:
        gender_selector = ""

    event = yaml_file["restriction"]["event"]

    if event is not None:

        # P823 - speaker
        # P664 - organizer
        # P1334 - has participant
        # ^P710 - inverse of (participated in)
        event_selector = (
            """
        VALUES ?event {"""
            + format_with_prefix(event)
            + """}
        ?event wdt:P823 |  wdt:P664 | wdt:P1344 | ^wdt:P710 ?author.
        """
        )
    else:
        event_selector = ""

    author_is_topic_of = yaml_file["restriction"]["author_is_topic_of"]

    if author_is_topic_of is not None:
        author_is_topic_of_selector = (
            """
        VALUES ?biographical_work {"""
            + format_with_prefix(author_is_topic_of)
            + """}
        ?biographical_work wdt:P921 ?author.
        """
        )
    else:
        author_is_topic_of_selector = ""

    selector = (
        field_of_work_selector
        + topic_of_work_selector
        + region_selector
        + gender_selector
        + event_selector
        + author_is_topic_of_selector
        + """
    ?work wdt:P50 ?author.
    """
    )
    print(selector)

    return selector


def render_url(query):
    return "https://query.wikidata.org/embed.html#" + urllib.parse.quote(query, safe="")


def get_query_url_for_articles(yaml_file):
    query = (
        """
  #defaultView:Table
  SELECT
  (MIN(?dates) AS ?date)
  ?work ?workLabel
  (GROUP_CONCAT(DISTINCT ?type_label; separator=", ") AS ?type)
  ?journal ?journalLabel
  (GROUP_CONCAT(DISTINCT ?author_label; separator=", ") AS ?authores)
  WHERE {
  """
        + get_selector(yaml_file)
        + """
  OPTIONAL {
    ?author rdfs:label ?author_label_ . FILTER (LANG(?author_label_) = 'en')
  }
  BIND(COALESCE(?author_label_, SUBSTR(STR(?author), 32)) AS ?author_label)
  OPTIONAL { ?work wdt:P31 ?type_ . ?type_ rdfs:label ?type_label . FILTER (LANG(?type_label) = 'pt') }
  ?work wdt:P577 ?datetimes .
  BIND(xsd:date(?datetimes) AS ?dates)
  OPTIONAL { ?work wdt:P1433 ?journal }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,jp,no,ru,sv,zh". }  
  }
  GROUP BY ?work ?workLabel ?journal ?journalLabel
  ORDER BY DESC(?date)
  LIMIT 100 
  """
    )

    return render_url(query)


def get_topics_as_table(yaml_file):
    query_3 = (
        """
  #defaultView:Table
  SELECT ?count ?theme ?themeLabel ?example_work ?example_workLabel
  WITH {
    SELECT (COUNT(?work) AS ?count) ?theme (SAMPLE(?work) AS ?example_work)
    WHERE {
      """
        + get_selector(yaml_file)
        + """
      ?work wdt:P921 ?theme .
    }
    GROUP BY ?theme
  } AS %result
  WHERE {
    INCLUDE %result
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,jp,nl,no,ru,sv,zh" . } 
  }
  ORDER BY DESC(?count) 
  LIMIT 100
  """
    )
    return render_url(query_3)


def get_query_url_for_venues(yaml_file):
    query_4 = (
        """
  # Venue statistics for a collection
  SELECT
    ?count (SAMPLE(?short_name_) AS ?short_name)
    ?journal ?journalLabel
    ?topics ?topicsUrl
  WITH {
    SELECT
      (COUNT(DISTINCT ?work) as ?count)
      ?journal
      (GROUP_CONCAT(DISTINCT ?topic_label; separator=", ") AS ?topics)
    WHERE {
      """
        + get_selector(yaml_file)
        + """
      ?work wdt:P1433 ?journal .
      OPTIONAL {
        ?journal wdt:P921 ?topic .
        ?topic rdfs:label ?topic_label . FILTER(LANG(?topic_label) = 'en') }
    }
    GROUP BY ?journal
  } AS %result
  WHERE {
    INCLUDE %result
    OPTIONAL { ?journal wdt:P1813 ?short_name_ . }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,jp,nl,no,ru,sv,zh". }  
  } 
  GROUP BY ?count ?journal ?journalLabel ?topics ?topicsUrl
  ORDER BY DESC(?count)
  """
    )
    return render_url(query_4)


def get_query_url_for_locations(yaml_file):
    query_5 = (
        """
  #defaultView:Map
  SELECT ?organization ?organizationLabel ?geo ?count ?layer
  WITH {
    SELECT DISTINCT ?organization ?geo (COUNT(DISTINCT ?work) AS ?count) WHERE {
      """
        + get_selector(yaml_file)
        + """
      ?author ( wdt:P108 | wdt:P463 | wdt:P1416 ) / wdt:P361* ?organization . 
      ?organization wdt:P625 ?geo .
    }
    GROUP BY ?organization ?geo ?count
    ORDER BY DESC (?count)
    LIMIT 2000
  } AS %organizations
  WHERE {
    INCLUDE %organizations
    BIND(IF( (?count < 1), "No results", IF((?count < 2), "1 result", IF((?count < 5), "1 < results ≤ 10", IF((?count < 101), "10 < results ≤ 100", IF((?count < 1001), "100 < results ≤ 1000", IF((?count < 10001), "1000 < results ≤ 10000", "10000 or more results") ) ) ) )) AS ?layer )
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }        
  }
  ORDER BY DESC (?count)
  """
    )
    return render_url(query_5)


def get_query_url_for_authors(yaml_file):
    query_7 = (
        """
  #defaultView:Table
  SELECT (COUNT(?work) AS ?article_count) ?author ?authorLabel ?orcids  ?organizationLabel  ?countryLabel WHERE {
    """
        + get_selector(yaml_file)
        + """
  OPTIONAL { ?author ( wdt:P108 | wdt:P463 | wdt:P1416 ) ?organization .
           OPTIONAL { ?organization wdt:P17 ?country . }               
           }
  OPTIONAL { ?author wdt:P496 ?orcids }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,jp,nl,no,ru,sv,zh". }
    }
  GROUP BY ?author ?authorLabel ?orcids  ?organizationLabel ?countryLabel
  ORDER BY DESC(?article_count)
  """
    )
    return render_url(query_7)


DEFAULT_ADVANCED_QUERY_OPTIONS = {
    "map of institutions": {
        "label": "map of institutions",
        "query": get_query_url_for_locations,
    },
    "articles": {"label": "articles", "query": get_query_url_for_articles,},
    "list of authors": {
        "label": "list of authors",
        "query": get_query_url_for_authors,
    },
    "list of topics": {
        "label": "list of co-studied topics",
        "query": get_topics_as_table,
    },
    "list of journals": {"label": "list of venues", "query": get_query_url_for_venues,},
}

DEFAULT_ADVANCED_SESSIONS = [
    "map of institutions",
    "articles",
    "list of authors",
    "list of topics",
    "list of journals",
]


def render_dashboard(
    config,
    query_options=DEFAULT_ADVANCED_QUERY_OPTIONS,
    sections_to_add=DEFAULT_ADVANCED_SESSIONS,
):
    """
  - Args:
     - config: A .yaml file with the configs
  """
    license_statement = config["license_statement"]
    scholia_credit_statement = config["scholia_credit"]
    creator_statement = config["creator_credit"]
    site_title = config["title"]
    site_subtitle = config["subtitle"]

    html = (
        render_header(site_title)
        + render_top(site_title, site_subtitle)
        + render_sections(sections_to_add, query_options, config)
        + """
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
