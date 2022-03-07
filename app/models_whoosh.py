from whoosh.fields import *

PageWhoosh = Schema(
    livre_id=STORED,
    page_id=STORED,
    content=TEXT(stored=True)
)
