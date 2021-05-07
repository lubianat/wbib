import urllib.parse


def format_with_prefix(list_of_qids):

    list_with_prefix = ["wd:" + i for i in list_of_qids]
    return "{ " + " ".join(list_with_prefix) + " }"


def get_selector(info, mode="advanced"):
    """
    The selector that decides the scope of the dashboard. It MUST have the keywords
    ?work and ?author. 
    You can override everything here by adapting the query on WDQS:
    https://w.wiki/3Cmd

    Args:
        info: either a dict containing complex information for the selector or a list of QIDs
        mode: a string representing the mode. If "advanced", then a config is expected for the
          info parameters. If "basic", a list of QIDs is expected. Defaults to "advanced".

    """

    if mode == "advanced":
        fields_of_work = info["restriction"]["author_area"]

        if fields_of_work is not None:
            field_of_work_selector = (
                """
                VALUES ?field_of_work """
                + format_with_prefix(fields_of_work)
                + """
                ?author wdt:P101 ?field_of_work.
                """
            )
        else:
            field_of_work_selector = ""

        topic_of_work = info["restriction"]["topic_of_work"]

        if topic_of_work is not None:
            topic_of_work_selector = (
                """
                VALUES ?topics """
                + format_with_prefix(topic_of_work)
                + """
                ?work wdt:P921/wdt:P279* ?topics.
                """
            )
        else:
            topic_of_work_selector = ""

        region = info["restriction"]["institution_region"]

        if region is not None:
            region_selector = (
                """
                VALUES ?regions """
                + format_with_prefix(region)
                + """
                ?country wdt:P361* ?regions.
                ?author ( wdt:P108 | wdt:P463 | wdt:P1416 ) / wdt:P361* ?organization . 
                ?organization wdt:P17 ?country.
                """
            )
        else:
            region_selector = ""

        gender = info["restriction"]["gender"]
        if gender is not None:
            gender_selector = (
                """
                VALUES ?gender """
                + format_with_prefix(gender)
                + """
                ?author wdt:P21 ?gender.
                """
            )
        else:
            gender_selector = ""

        event = info["restriction"]["event"]

        if event is not None:

            # P823 - speaker
            # P664 - organizer
            # P1334 - has participant
            # ^P710 - inverse of (participated in)
            event_selector = (
                """
                VALUES ?event """
                + format_with_prefix(event)
                + """
                ?event wdt:P823 |  wdt:P664 | wdt:P1344 | ^wdt:P710 ?author.
                """
            )
        else:
            event_selector = ""

        author_is_topic_of = info["restriction"]["author_is_topic_of"]

        if author_is_topic_of is not None:
            author_is_topic_of_selector = (
                """
                VALUES ?biographical_work """
                + format_with_prefix(author_is_topic_of)
                + """
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
    else:
        selector = f"""
        VALUES ?work {format_with_prefix(info)} .
        ?work wdt:P50 ?author .
        """
    return selector


def render_url(query):
    return "https://query.wikidata.org/embed.html#" + urllib.parse.quote(query, safe="")


def get_query_url_for_author_without_affiliation(info, mode="basic"):
    query = (
        """
# tool: scholia
# title: Employees and affiliated with a specified organization
SELECT
  (SAMPLE(?number_of_works_) AS ?works)
  (SAMPLE(?wikis_) AS ?wikis)
  ?author ?authorLabel ?authorDescription
  (SAMPLE(?orcid_) AS ?orcid)
WITH {
  SELECT DISTINCT ?author WHERE {
"""
        + get_selector(info, mode)
        + """
    
    MINUS {?author ( wdt:P108 | wdt:P463 | wdt:P1416 ) / wdt:P361* ?organization .}
  } 
} AS %authors
WITH {
  SELECT
    (COUNT(?work) AS ?number_of_works_) ?author
  WHERE {
    INCLUDE %authors
    OPTIONAL { ?work wdt:P50 ?author . }

    # No biological pathways; they skew the statistics too much 
    MINUS { ?work wdt:P31 wd:Q4915012 } 
  } 
  GROUP BY ?author
} AS %authors_and_number_of_works
WHERE {
  INCLUDE %authors_and_number_of_works
  OPTIONAL { ?author wdt:P496 ?orcid_ . }
  OPTIONAL { ?author wikibase:sitelinks ?wikis_ }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,nl,no,ru,sv,zh" . } 
}
GROUP BY ?author ?authorLabel ?authorDescription 
ORDER BY DESC(?works)
  """
    )

    return render_url(query)


def get_query_url_for_missing_author_items(info, mode="basic"):
    query = (
        """
  #defaultView:Table
  SELECT
    (COUNT(?work) AS ?count) 
    ?author_name
    (URI(CONCAT(
        'https://author-disambiguator.toolforge.org/names_oauth.php?doit=Look+for+author&name=',
        ENCODE_FOR_URI(?author_name))) AS ?author_resolver_url)
  WHERE {
    {
      SELECT DISTINCT ?author_name {
    """
        + get_selector(info, mode)
        + """
        ?work wdt:P50 ?author . 
        ?author skos:altLabel | rdfs:label ?author_name_ .
        
        # The SELECT-DISTINCT-BIND trick here is due to Stanislav Kralin
        # https://stackoverflow.com/questions/53933564
        BIND (STR(?author_name_) AS ?author_name)
      }
      LIMIT 2000
    }
    OPTIONAL { ?work wdt:P2093 ?author_name . }
  }
  GROUP BY ?author_name 
  HAVING (?count > 0)
  ORDER BY DESC(?count)
  """
    )

    return render_url(query)


def get_query_url_for_articles(info, mode="basic"):
    query = (
        """

  #defaultView:Table
  SELECT
  (MIN(?dates) AS ?date)
  ?work ?workLabel
  (GROUP_CONCAT(DISTINCT ?type_label; separator=", ") AS ?type)
  (SAMPLE(?pages_) AS ?pages)
  ?venue ?venueLabel
  (GROUP_CONCAT(DISTINCT ?author_label; separator=", ") AS ?authors)
  WHERE {
"""
        + get_selector(info, mode)
        + """
  ?work wdt:P50 ?author .
  OPTIONAL {
    ?author rdfs:label ?author_label_ . FILTER (LANG(?author_label_) = 'en')
  }
  BIND(COALESCE(?author_label_, SUBSTR(STR(?author), 32)) AS ?author_label)
  OPTIONAL { ?work wdt:P31 ?type_ . ?type_ rdfs:label ?type_label . FILTER (LANG(?type_label) = 'en') }
  ?work wdt:P577 ?datetimes .
  BIND(xsd:date(?datetimes) AS ?dates)
  OPTIONAL { ?work wdt:P1104 ?pages_ }
  OPTIONAL { ?work wdt:P1433 ?venue }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,jp,no,ru,sv,zh". }  
  }
  GROUP BY ?work ?workLabel ?venue ?venueLabel
  ORDER BY DESC(?date)  

  """
    )

    return render_url(query)


def get_query_url_for_topic_bubble(info, mode="basic"):

    query = (
        """

  #defaultView:BubbleChart
  SELECT ?score ?topic ?topicLabel
  WITH {
    SELECT
      (SUM(?score_) AS ?score)
      ?topic
    WHERE {
          {
        SELECT (100 AS ?score_) ?topic WHERE {
        """
        + get_selector(info, mode)
        + """
          ?work  wdt:P921 ?topic . 
        }
      }
      UNION
      {
        SELECT (1 AS ?score_) ?topic WHERE {
        """
        + get_selector(info, mode)
        + """
          ?citing_work wdt:P2860 ?work .
          ?citing_work wdt:P921 ?topic . 
        }
      }
    }
    GROUP BY ?topic
  } AS %results 
  WHERE {
    INCLUDE %results
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en,da,de,es,jp,no,ru,sv,zh". }
  }
  ORDER BY DESC(?score)
  LIMIT 50

  """
    )
    return render_url(query)


def get_topics_as_table(info, mode="basic"):
    query_3 = (
        """


  #defaultView:Table
  SELECT ?count ?theme ?themeLabel ?example_work ?example_workLabel
  WITH {
    SELECT (COUNT(?work) AS ?count) ?theme (SAMPLE(?work) AS ?example_work)
    WHERE {
    """
        + get_selector(info, mode)
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

  """
    )
    return render_url(query_3)


def get_query_url_for_venues(info, mode="basic"):
    query_4 = (
        """


  # Venue statistics for a collection
  SELECT
    ?count (SAMPLE(?short_name_) AS ?short_name)
    ?venue ?venueLabel
    ?topics ?topicsUrl
  WITH {
    SELECT
      (COUNT(DISTINCT ?work) as ?count)
      ?venue
      (GROUP_CONCAT(DISTINCT ?topic_label; separator=", ") AS ?topics)
    WHERE {
    """
        + get_selector(info, mode)
        + """
      ?work wdt:P1433 ?venue .
      OPTIONAL {
        ?venue wdt:P921 ?topic .
        ?topic rdfs:label ?topic_label . FILTER(LANG(?topic_label) = 'en') }
    }
    GROUP BY ?venue
  } AS %result
  WHERE {
    INCLUDE %result
    OPTIONAL { ?venue wdt:P1813 ?short_name_ . }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,jp,nl,no,ru,sv,zh". }  
  } 
  GROUP BY ?count ?venue ?venueLabel ?topics ?topicsUrl
  ORDER BY DESC(?count)

  """
    )
    return render_url(query_4)


def get_query_url_for_locations(info, mode="basic"):
    query_5 = (
        """
#defaultView:Map
SELECT 
?organization ?organizationLabel 
(CONCAT(STR(?count), " result(s)") as ?counts)
?geo ?layer
?sample_author ?sample_authorLabel
?sample_work  ?sample_workLabel

  WITH {
    SELECT DISTINCT ?organization ?geo 
    (COUNT(DISTINCT ?work) AS ?count) 
    (SAMPLE(?work) as ?sample_work) 
    (SAMPLE(?author) as ?sample_author) WHERE {

    """
        + get_selector(info, mode)
        + """
          ?work wdt:P50 ?author .
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


def get_query_url_for_citing_authors(info, mode="basic"):
    query_6 = (
        """


  #defaultView:Table
  SELECT
    ?count
    ?citing_author ?citing_authorLabel

    # Either show the ORCID iD or construct part of a URL to search on the ORCID homepage
    (COALESCE(?orcid_, CONCAT("orcid-search/quick-search/?searchQuery=", ENCODE_FOR_URI(?citing_authorLabel))) AS ?orcid)
  WITH {
    SELECT (COUNT(?citing_work) AS ?count) ?citing_author WHERE {
    """
        + get_selector(info, mode)
        + """
      ?citing_work wdt:P2860 ?work . 
      ?citing_work wdt:P50 ?citing_author .
    }
    GROUP BY ?citing_author 
    ORDER BY DESC(?count)
    LIMIT 500
  } AS %counts
  WITH {
    # An author might have multiple ORCID iDs
    SELECT
      ?count
      ?citing_author
      (SAMPLE(?orcids) AS ?orcid_)
    WHERE {
      INCLUDE %counts
      OPTIONAL { ?citing_author wdt:P496 ?orcids }
    }
    GROUP BY ?count ?citing_author
  } AS %result
  WHERE {
    INCLUDE %result

    SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,jp,nl,no,ru,sv,zh". }
  } 
  ORDER BY DESC(?count)


  """
    )
    return render_url(query_6)


def get_query_url_for_authors(info, mode="basic"):
    query_7 = (
        """
  #defaultView:Table
  SELECT (COUNT(?work) AS ?count) ?author ?authorLabel ?orcids  WHERE {
  """
        + get_selector(info, mode)
        + """
    ?work wdt:P50 ?author .
      OPTIONAL { ?author wdt:P496 ?orcids }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,jp,nl,no,ru,sv,zh". }

    }
  GROUP BY ?author ?authorLabel ?orcids 
  ORDER BY DESC(?count)

  """
    )
    return render_url(query_7)

