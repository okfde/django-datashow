import pytest

from datashow.forms import SEARCH_PARAM, SORT_PARAM, FilterForm
from datashow.models import Dataset, FilterChoices
from datashow.query import SqlQuery
from datashow.table import initialize_dataset

# FILE: datashow/forms/test_forms.py


@pytest.fixture
def table():
    dataset = Dataset.objects.create(
        name="Test Dataset",
        slug="test-dataset",
        sqlite_file="./tests/data/sample.db",
    )
    initialize_dataset(dataset)
    table = dataset.tables.first()
    columns = table.get_columns()
    table.primary_key = columns[0]
    columns[0].sortable = True
    columns[0].filter = FilterChoices.INTEGER_RANGE
    columns[0].filter_arguments = {"min": 0, "max": 100}
    columns[1].searchable = True
    columns[1].sortable = True
    columns[2].facet_count = 5
    yield table


@pytest.mark.django_db
def test_filter_form(table):
    form = FilterForm(table)
    assert SORT_PARAM in form.fields
    assert SEARCH_PARAM in form.fields
    assert "id__range" in form.fields

    assert not form.is_filtered()

    form = FilterForm(
        table,
        {
            SEARCH_PARAM: "foo",
            "email": "-",
            "sort": "id,-name",
            "id__range_min": "10",
            "id__range_max": "20",
        },
    )
    form.is_valid()
    print(form.errors)
    assert form.cleaned_data == {
        SEARCH_PARAM: "foo",
        "email": "-",
        "sort": ["id", "-name"],
        "id__range": [10, 20],
    }


@pytest.mark.django_db
def test_query(table):
    data = {
        SEARCH_PARAM: "foo",
        "email": "-",
        "sort": ["id", "-name"],
        "id__range": [10, 20],
    }
    query = SqlQuery(table, data).with_list()
    assert query.limit == table.pagination_size
    assert query.offset is None
    assert query.order == ['"ministries"."id" ASC', '"ministries"."name" DESC']
    assert query.where == [
        "ministries__fts MATCH ?",
        '"ministries"."email" IS NULL',
        '"ministries"."id" BETWEEN ? AND ?',
    ]
    assert query.params == ["foo", 10, 20]
    assert len(query.select) == len(table.get_sql_columns())
    assert table.as_sql() in query._from

    data = {
        SEARCH_PARAM: "foo",
        "email": "Test",
        "sort": ["id", "-name"],
        "id__range": [10, None],
    }
    query = SqlQuery(table, data).with_list()
    assert query.where == [
        "ministries__fts MATCH ?",
        '"ministries"."email" = ?',
        '"ministries"."id" >= ?',
    ]
    assert query.params == ["foo", "Test", 10]

    data = {
        SEARCH_PARAM: "foo",
        "email": "Test",
        "sort": ["id", "-name"],
        "id__range": [None, 20],
    }
    query = SqlQuery(table, data).with_list()
    assert query.where == [
        "ministries__fts MATCH ?",
        '"ministries"."email" = ?',
        '"ministries"."id" <= ?',
    ]
    assert query.params == ["foo", "Test", 20]

    data = {
        "id__range": [None, None],
    }
    query = SqlQuery(table, data).with_list()
    assert query.where == []
    assert query.params == []

    data = {
        "id__range": None,
    }
    query = SqlQuery(table, data).with_list()
    assert query.where == []
    assert query.params == []

    data = {
        "sort": ["foo", "classification"],
    }
    query = SqlQuery(table, data).with_list()
    assert query.order == []
