import pytest

from datashow.models import Dataset
from datashow.table import initialize_dataset


@pytest.fixture
def dataset():
    dataset = Dataset.objects.create(
        name="Test Dataset",
        slug="test-dataset",
        sqlite_file="./tests/data/sample.db",
    )
    initialize_dataset(dataset)
    yield dataset
