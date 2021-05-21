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


def render_section(query_name, query_options, info, mode):

    legend = query_options[query_name]["label"]
    query_url = query_options[query_name]["query"]

    return {"legend": legend, "query": query_url(info, mode)}


def render_sections(query_name_list, query_options, info, mode):

    sections = []
    for name in query_name_list:
        sections.append(
            render_section(name, query_options=query_options, info=info, mode=mode)
        )

    return sections
