import datetime as dt

from researcher.models import Paper, PaperStatus, SearchQuery
from researcher.storage import Storage


def make_paper(**overrides):
    base = dict(
        arxiv_id="1234.5678",
        title="Test Paper",
        authors=["Alice"],
        abstract="This is a test.",
        categories=["cs.LG"],
        pdf_url="https://arxiv.org/pdf/1234.5678.pdf",
        published_at=dt.datetime.now(dt.timezone.utc),
    )
    return Paper(**{**base, **overrides})


def test_search_filters_by_category(tmp_path):
    storage = Storage(tmp_path / "db.json")
    storage.upsert_paper(make_paper(id="a", categories=["cs.LG"]))
    storage.upsert_paper(make_paper(id="b", categories=["cs.AI"]))

    results, total = storage.search(SearchQuery(category="cs.LG"))

    assert total == 1
    assert results[0].id == "a"


def test_search_filters_by_status(tmp_path):
    storage = Storage(tmp_path / "db.json")
    storage.upsert_paper(make_paper(id="a", status=PaperStatus.NEW))
    storage.upsert_paper(make_paper(id="b", status=PaperStatus.READ))

    results, total = storage.search(SearchQuery(status=PaperStatus.READ))

    assert total == 1
    assert results[0].id == "b"
