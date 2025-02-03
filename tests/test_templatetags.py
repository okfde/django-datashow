import pytest

from datashow.templatetags.datashow_tags import (
    listify,
    querystring,
    sort_queryparam,
)


@pytest.mark.django_db
def test_querystring(rf):
    request = rf.get("/?foo=bar&baz=qux")
    context = {"request": request}

    assert querystring(context) == "foo=bar&baz=qux"
    assert querystring(context, "foo") == "baz=qux"
    assert querystring(context, "foo", "") == "foo=&baz=qux"
    assert querystring(context, "foo", "new") == "foo=new&baz=qux"
    assert querystring(context, "foo", "bar") == ""
    assert querystring(context, "foo", None) == "baz=qux"


@pytest.mark.django_db
def test_sort_queryparam(rf):
    request = rf.get("/?sort=foo,-bar")
    context = {"request": request}

    assert sort_queryparam(context, "foo") == ""
    assert sort_queryparam(context, "baz") == "sort=foo%2C-bar%2Cbaz"
    assert sort_queryparam(context, "baz", ascending=False) == "sort=foo%2C-bar%2C-baz"
    assert sort_queryparam(context, "foo", remove=True) == "sort=-bar"
    assert sort_queryparam(context, "bar", remove=True) == "sort=foo%2C-bar"
    assert sort_queryparam(context, "-bar", remove=True) == "sort=foo"

    request = rf.get("/?sort=foo")
    context = {"request": request}
    assert sort_queryparam(context, "foo", remove=True) == ""


def test_listify():
    assert listify([1, 2, 3]) == [1, 2, 3]
    assert listify("abc") == ["a", "b", "c"]
    assert listify((1, 2, 3)) == [1, 2, 3]
