import csv

from django.http import Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from .formatters import format_column
from .forms import FilterForm
from .models import Dataset, Table
from .table import RowQueryset, get_facets, get_row


def get_dataset(request, slug: str) -> Dataset:
    qs = Dataset.objects.all()
    if not request.user.has_perm("datashow.view_dataset"):
        qs = qs.filter(public=True)
    return get_object_or_404(qs.select_related("default_table"), slug=slug)


def get_table(dataset: Dataset, table_slug: str) -> Table:
    return get_object_or_404(
        dataset.tables.all().select_related("primary_key"), slug=table_slug
    )


def dataset_index(request, slug: str):
    dataset = get_dataset(request, slug)
    if dataset.default_table:
        return default_table_view(request, dataset=dataset, table=dataset.default_table)

    tables = dataset.tables.all().filter(visible=True)
    return render(
        request, "datashow/dataset_index.html", {"dataset": dataset, "tables": tables}
    )


class RowList(ListView):
    template_name = "datashow/dataset_table.html"
    context_object_name = "tables"
    dataset_slug_kwarg = "slug"
    table_slug_kwarg = "table_slug"

    def get_queryset(self):
        self.dataset = self.kwargs.get("dataset")
        if self.dataset is None:
            dataset_slug = self.kwargs.get(self.dataset_slug_kwarg)
            self.dataset = get_dataset(self.request, dataset_slug)
        self.table = self.kwargs.get("table")
        if self.table is None:
            table_slug = self.kwargs.get(self.table_slug_kwarg)
            self.table = get_table(self.dataset, table_slug)
        self.filter_form = FilterForm(self.table, data=self.request.GET)
        self.formdata = None
        if self.filter_form.is_valid():
            self.formdata = self.filter_form.cleaned_data
        return RowQueryset(self.table, formdata=self.formdata)

    def get_paginate_by(self, queryset):
        return self.table.pagination_size

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["dataset"] = self.dataset
        ctx["table"] = self.table
        ctx["columns"] = [
            (c, format_column(c)) for c in self.table.get_visible_columns()
        ]
        ctx["facets"] = get_facets(self.table, self.formdata)
        ctx["filter_form"] = self.filter_form
        return ctx

    def get_template_names(self) -> list[str]:
        if self.request.headers.get("hx-boosted", "") == "true":
            return ["datashow/_table.html"]
        return super().get_template_names()


default_table_view = RowList.as_view()


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def __init__(self, header_cols):
        self.header_cols = header_cols
        self.wrote_header = False

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        if not self.wrote_header:
            self.wrote_header = True
            return ",".join(self.header_cols) + "\n" + value
        return value


def table_csv_export(request, slug, table_slug):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.

    dataset = get_dataset(request, slug)
    table = get_table(dataset, table_slug)
    generator = RowQueryset(table, request=request).stream_raw()

    pseudo_buffer = Echo(table.get_sql_columns())
    writer = csv.writer(pseudo_buffer)

    return StreamingHttpResponse(
        (writer.writerow(row) for row in generator),
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="%s.csv"' % table.slug},
    )


def show_dataset_default_table_row(request, slug: str, row_slug: str):
    dataset = get_dataset(request, slug)
    if not dataset.default_table:
        raise Http404
    return dataset_row(request, dataset, dataset.default_table, row_slug)


def show_dataset_table_row(request, slug: str, table_slug: str, row_slug: str):
    dataset = get_dataset(request, slug)
    table = get_table(dataset, table_slug)
    return dataset_row(request, dataset, table, row_slug)


def dataset_row(request, dataset: Dataset, table: Table, row_slug: str):
    if not table.primary_key:
        raise Http404
    row, row_dict = get_row(table, row_slug)
    row_label = table.row_label(row_dict)
    return render(
        request,
        "datashow/dataset_row.html",
        {
            "dataset": dataset,
            "table": table,
            "row_label": row_label,
            "row": row,
            "object": row_dict,
        },
    )
