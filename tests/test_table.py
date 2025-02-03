import pytest

from datashow.query import SqlQuery
from datashow.table import get_facets


@pytest.mark.django_db
def test_facet(dataset):
    table = dataset.tables.first()
    columns = {c.name: c for c in table.get_columns()}
    column = columns["classification"]
    column.facet_count = 5
    form_data = {"classification": "Ministerium"}
    facets = get_facets(table, form_data)
    assert len(facets) == 1
    facet = facets[0]
    assert facet.column.name == "classification"
    keys = facet.keys
    assert len(keys) == 2
    assert keys[0].key == "Ministerium"
    assert keys[0].active
    assert keys[0].count == 15

    query = SqlQuery(table, form_data).with_facet(column)
    sql = """SELECT "ministries"."classification" AS key, COUNT(*) AS count FROM ministries  GROUP BY key ORDER BY count DESC LIMIT 5"""
    assert query.to_sql().strip() == sql
    assert str(query) == f"{sql}  []"
    column.sortable = True
    query = SqlQuery(table, form_data).with_facet(column)
    assert query.to_sql().strip() == (
        """SELECT "ministries"."classification" AS key, COUNT(*) AS count FROM ministries  GROUP BY key ORDER BY key ASC LIMIT 5"""
    )
