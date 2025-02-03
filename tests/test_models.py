import pytest
from django.forms import ValidationError

from datashow.models import Column, Dataset, Table


@pytest.mark.django_db
def test_dataset_initialization(dataset):
    assert dataset.tables.count() == 1
    table = dataset.tables.first()
    assert table.name == "ministries"
    assert table.columns.count() == 16
    assert set(table.columns.values_list("name", flat=True)) == {
        "id",
        "name",
        "email",
        "fax",
        "contact",
        "address",
        "url",
        "classification",
        "jurisdiction__slug",
        "categories",
        "other_names",
        "website_dump",
        "description",
        "request_note",
        "parent__id",
        "regions",
    }


@pytest.mark.django_db
def test_dataset(dataset):
    assert str(dataset) == "Test Dataset"
    other_dataset = Dataset.objects.create(name="Other")
    other_table = Table.objects.create(dataset=other_dataset, name="other")
    dataset.default_table = other_table
    with pytest.raises(ValidationError):
        dataset.clean()


@pytest.mark.django_db
def test_table(dataset):
    table = dataset.tables.first()
    assert str(table) == "ministries (Test Dataset)"
    other_dataset = Dataset.objects.create(name="Other Dataset")
    other_table = Table.objects.create(dataset=other_dataset, name="other")
    other_column = Column.objects.create(table=other_table, name="other", label="other")
    assert str(other_column) == "other - other (Other Dataset)"

    table.primary_key = other_column
    with pytest.raises(ValidationError):
        table.clean()

    assert table.get_row_count() == table.row_count

    table.row_label_template = "id:{id}"
    assert table.row_label({"id": 42}) == "id:42"
    table.row_label_template = "id:{foo}"
    table.row_label({"id": 42}) == ""
