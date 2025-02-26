import pytest
from django.utils.safestring import SafeString

from datashow.formatters import (
    ALIGN_CENTER,
    ALIGN_RIGHT,
    NUMBER,
    format_column,
    format_value,
)
from datashow.models import Column, FormatterChoices


def test_float_column():
    column = Column(name="test", formatter=FormatterChoices.FLOAT)
    assert format_column(column) == ALIGN_RIGHT
    css, value = format_value(column, None, {})
    assert css == ALIGN_RIGHT
    assert isinstance(value, SafeString)
    assert "–" in value
    assert format_value(column, 1234.5, {}) == (NUMBER, "1,234.5")


def test_integer_column():
    column = Column(name="test", formatter=FormatterChoices.INTEGER)
    assert format_column(column) == ALIGN_RIGHT
    css, value = format_value(column, None, {})
    assert css == ALIGN_RIGHT
    assert isinstance(value, SafeString)
    assert "–" in value
    assert format_value(column, 1234, {}) == (NUMBER, "1,234")


def test_date_column():
    column = Column(name="test", formatter=FormatterChoices.DATE)
    assert format_column(column) == ALIGN_RIGHT
    css, value = format_value(column, None, {})
    assert css == ALIGN_RIGHT
    assert isinstance(value, SafeString)
    assert "–" in value
    assert format_value(column, "2023-10-01", {}) == (NUMBER, "10/01/2023")


def test_datetime_column():
    column = Column(name="test", formatter=FormatterChoices.DATETIME)
    assert format_column(column) == ALIGN_RIGHT
    css, value = format_value(column, None, {})
    assert css == ALIGN_RIGHT
    assert isinstance(value, SafeString)
    assert "–" in value
    assert format_value(column, "2023-10-01T12:34:56", {}) == (
        NUMBER,
        "10/01/2023 12:34 p.m.",
    )


def test_boolean_column():
    column = Column(name="test", formatter=FormatterChoices.BOOLEAN)
    assert format_column(column) == ALIGN_CENTER
    css, value = format_value(column, None, {})
    assert css == ALIGN_CENTER
    assert isinstance(value, SafeString)
    assert "–" in value
    assert format_value(column, True, {}) == (
        ALIGN_CENTER,
        '<span class="text-success">✅ Yes</span>',
    )
    assert format_value(column, False, {}) == (
        ALIGN_CENTER,
        '<span class="text-danger">❌ No</span>',
    )


def test_link_column():
    column = Column(
        name="test",
        formatter=FormatterChoices.LINK,
        formatter_arguments={"href": "http://example.com", "target": "_blank"},
    )
    css, value = format_value(column, "Example", {})
    assert css == ""
    assert value == '<a href="http://example.com" target="_blank">Example</a>'

    css, value = format_value(column, None, {})
    assert css == ""
    assert (
        value
        == '<a href="http://example.com" target="_blank"><span class="text-secondary">–</span></a>'
    )


def test_summary_column():
    column = Column(
        name="test",
        formatter=FormatterChoices.SUMMARY,
        formatter_arguments={"summary": "More details"},
    )
    css, value = format_value(
        column, "This is a detailed description.", {}, detail=False
    )
    assert css == ""
    assert (
        value
        == '<details class="datashow-summary"><summary><span>More details</span></summary>This is a detailed description.</details>'
    )


def test_abbreviation_column():
    column = Column(
        name="test",
        formatter=FormatterChoices.ABBREVIATION,
        formatter_arguments={"title": "Abbreviation"},
    )
    css, value = format_value(column, "abbr", {})
    assert css == ""
    assert value == '<abbr title="Abbreviation">abbr</abbr>'


def test_bad_abbreviation_args():
    column = Column(
        name="test",
        formatter=FormatterChoices.ABBREVIATION,
        formatter_arguments={"bad": "Abbreviation"},
    )
    css, value = format_value(column, "abbr", {})
    assert css == ""
    assert value == "<abbr>abbr</abbr>"


def test_iframe_column():
    column = Column(
        name="test",
        formatter=FormatterChoices.IFRAME,
        formatter_arguments={"width": "100%", "data-bar": "bar:{bar}"},
    )
    css, value = format_value(
        column,
        "http://example.org",
        {
            "bar": "baz",
        },
    )
    assert css == ""
    assert (
        value
        == '<iframe src="http://example.org" width="100%" data-bar="bar:baz"></iframe>'
    )
