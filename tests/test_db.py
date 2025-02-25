from datashow.query import make_fts_query


def test_make_fts_query():
    q = ""
    assert make_fts_query(q) == ""

    q = "foo bar"
    assert make_fts_query(q) == '"foo"* "bar"*'

    # Don't prefix-query quoted parts
    q = 'foo "bar baz"'
    assert make_fts_query(q) == '"foo"* "bar baz"'

    # Balance quotes
    q = 'foo "bar baz'
    assert make_fts_query(q) == '"foo"* "bar baz"'

    # Don't prefix query parts shorter than MIN_WORD_PREFIX_LENGTH
    q = 'fo "bar baz'
    assert make_fts_query(q) == '"fo" "bar baz"'

    # Quote parts with special characters
    q = "fo -*"
    assert make_fts_query(q) == '"fo" "-*"'
