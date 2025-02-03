import csv

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_dataset_index(client, dataset):
    url = dataset.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_dataset_table(client, dataset):
    table = dataset.tables.first()
    url = table.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200
    assert response.content.decode("utf-8").strip().startswith("<!DOCTYPE html>")

    response = client.get(table.get_absolute_url(), headers={"hx-boosted": "true"})
    assert response.status_code == 200
    assert response.content.decode("utf-8").strip().startswith("<div ")


@pytest.mark.django_db
def test_dataset_default_table(client, dataset):
    table = dataset.tables.first()
    dataset.default_table = table
    dataset.save()

    url = reverse(
        "datashow:dataset-table",
        kwargs={"slug": dataset.slug, "table_slug": table.slug},
    )
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == table.get_absolute_url()

    url = table.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_dataset_table_export(client, dataset):
    table = dataset.tables.first()
    url = reverse(
        "datashow:dataset-table-export",
        kwargs={"slug": dataset.slug, "table_slug": table.slug},
    )
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"

    reader = csv.reader(response.getvalue().decode("utf-8").splitlines())
    rows = list(reader)
    assert len(rows) == table.row_count + 1
    assert rows[0] == [c.name for c in table.get_visible_columns()]


@pytest.mark.django_db
def test_dataset_row(client, dataset):
    table = dataset.tables.first()
    url = reverse(
        "datashow:dataset-row",
        kwargs={"slug": dataset.slug, "table_slug": table.slug, "row_slug": "43"},
    )
    response = client.get(url)
    # No primary key defined, no way to get a row
    assert response.status_code == 404

    pk_column = [c for c in table.get_columns() if c.name == "id"][0]
    table.primary_key = pk_column
    table.save()
    response = client.get(url)
    assert response.status_code == 200

    url = reverse(
        "datashow:dataset-row",
        kwargs={
            "slug": dataset.slug,
            "table_slug": table.slug,
            "row_slug": "non-existing",
        },
    )
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_dataset_default_table_row(client, dataset):
    table = dataset.tables.first()
    pk_column = [c for c in table.get_columns() if c.name == "id"][0]
    table.primary_key = pk_column
    table.save()

    url = reverse(
        "datashow:dataset-row",
        kwargs={"slug": dataset.slug, "row_slug": "43"},
    )
    response = client.get(url)
    # No default table defined
    assert response.status_code == 404

    table = dataset.tables.first()
    dataset.default_table = table
    dataset.save()

    url = reverse(
        "datashow:dataset-row",
        kwargs={"slug": dataset.slug, "row_slug": "43"},
    )
    response = client.get(url)
    assert response.status_code == 200

    url = reverse(
        "datashow:dataset-row",
        kwargs={"slug": dataset.slug, "table_slug": table.slug, "row_slug": "43"},
    )
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse(
        "datashow:dataset-row",
        kwargs={"slug": dataset.slug, "row_slug": "43"},
    )
