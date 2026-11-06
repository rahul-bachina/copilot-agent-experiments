"""Credit memo drafting. Catalogue ID B009.

The credit officer owns the recommendation and every approval. This package
drafts a cited memo. It does not decide credit.
"""

__all__ = ["draft_memo"]


def __getattr__(name: str):
    if name == "draft_memo":
        from .draft import draft_memo

        return draft_memo
    raise AttributeError(name)
