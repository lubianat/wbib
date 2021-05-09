# Basic usage:

```python
from wbib import wbib
```

## Generate list of QIDs from a list of DOIs

```python
dois = ["10.3897/RIO.2.E9342", "10.3389/fimmu.2019.02736", "wrong or missing DOI"]
qids = wbib.convert_doi_to_qid(dois)
print(qids)
```

The output:

`{'missing': {'"wrong or missing DOI"'}, 'qids': {'Q92072015', 'Q61654697'}}`

## Render dashboard from a list of QIDs

```python
qids = ["Q35185544", "Q34555562", "Q21284234"]
html = wbib.render_dashboard(info=qids, mode="basic")
with open("dashboard.html","w") as f:
        f.write(html)
```

See results [here](./basic/dashboard.html)
