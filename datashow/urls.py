from django.urls import path
from django.utils.translation import pgettext_lazy

from .views import (
    RowList,
    dataset_index,
    show_dataset_default_table_row,
    show_dataset_table_row,
    table_csv_export,
)

app_name = "datashow"

urlpatterns = [
    path(
        "<slug:slug>/",
        dataset_index,
        name="dataset_index",
    ),
    path(
        pgettext_lazy("url part", "<slug:slug>/table/<slug:table_slug>/"),
        RowList.as_view(),
        name="dataset_table",
    ),
    path(
        pgettext_lazy("url part", "<slug:slug>/table/<slug:table_slug>/export/"),
        table_csv_export,
        name="dataset_table_export",
    ),
    path(
        "<slug:slug>/<slug:row_slug>/",
        show_dataset_default_table_row,
        name="dataset_row",
    ),
    path(
        pgettext_lazy(
            "url part", "<slug:slug>/table/<slug:table_slug>/<slug:row_slug>/"
        ),
        show_dataset_table_row,
        name="dataset_row",
    ),
]
