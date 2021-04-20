import urllib.parse

def render_url(query):
  return "https://query.wikidata.org/embed.html#" + urllib.parse.quote(query, safe='')
  
def get_query_url_for_articles(readings):
  query = """

  #defaultView:Table
  SELECT
  (MIN(?dates) AS ?date)
  ?work ?workLabel
  (GROUP_CONCAT(DISTINCT ?type_label; separator=", ") AS ?type)
  (SAMPLE(?pages_) AS ?pages)
  ?venue ?venueLabel
  (GROUP_CONCAT(DISTINCT ?author_label; separator=", ") AS ?authors)
  WHERE {
  VALUES ?work """ +  readings + """.
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
  
  return render_url(query)

def get_query_url_for_topic_bubble(readings):

  query = """

  #defaultView:BubbleChart
  SELECT ?score ?topic ?topicLabel
  WITH {
    SELECT
      (SUM(?score_) AS ?score)
      ?topic
    WHERE {
          {
        SELECT (100 AS ?score_) ?topic WHERE {
          VALUES ?work """ +  readings + """.
          ?work  wdt:P921 ?topic . 
        }
      }
      UNION
      {
        SELECT (1 AS ?score_) ?topic WHERE {
          VALUES ?work """ +  readings + """.
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
  return render_url(query) 

def get_topics_as_table(readings):
  query_3 = """


  #defaultView:Table
  SELECT ?count ?theme ?themeLabel ?example_work ?example_workLabel
  WITH {
    SELECT (COUNT(?work) AS ?count) ?theme (SAMPLE(?work) AS ?example_work)
    WHERE {
      VALUES ?work """ +  readings + """.
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
  return render_url(query_3) 

def get_query_url_for_venues(readings):
  query_4 = """


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
      VALUES ?work """ +  readings + """.
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
  return render_url(query_4) 

def get_query_url_for_locations(readings):
  query_5 = """
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

      VALUES ?work """ +  readings + """.
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
  return render_url(query_5)

def get_query_url_for_citing_authors(readings):
  query_6 = """


  #defaultView:Table
  SELECT
    ?count
    ?citing_author ?citing_authorLabel

    # Either show the ORCID iD or construct part of a URL to search on the ORCID homepage
    (COALESCE(?orcid_, CONCAT("orcid-search/quick-search/?searchQuery=", ENCODE_FOR_URI(?citing_authorLabel))) AS ?orcid)
  WITH {
    SELECT (COUNT(?citing_work) AS ?count) ?citing_author WHERE {
      VALUES ?work """ +  readings + """.
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
  return render_url(query_6)

def get_query_url_for_authors(readings):
  query_7 = """
  #defaultView:Table
  SELECT (COUNT(?work) AS ?count) ?author ?authorLabel ?orcids  WHERE {
    VALUES ?work """ +  readings + """.
    ?work wdt:P50 ?author .
      OPTIONAL { ?author wdt:P496 ?orcids }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en,da,de,es,fr,jp,nl,no,ru,sv,zh". }

    }
  GROUP BY ?author ?authorLabel ?orcids 
  ORDER BY DESC(?count)

  """
  return render_url(query_7)
