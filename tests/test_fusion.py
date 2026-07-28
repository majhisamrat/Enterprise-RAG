import pytest
from app.retrieval.fusion import ReciprocalRankFusion


def test_rrf_fusion():
    fusion = ReciprocalRankFusion(k=60)
    dense_results = [
        {"chunk_id": "chunk_1", "text": "Dense chunk 1"},
        {"chunk_id": "chunk_2", "text": "Dense chunk 2"},
    ]
    sparse_results = [
        {"chunk_id": "chunk_2", "text": "Dense chunk 2"},
        {"chunk_id": "chunk_3", "text": "Sparse chunk 3"},
    ]

    fused = fusion.fuse(dense_results, sparse_results)
    assert len(fused) == 3
    # chunk_2 appears in both lists so its RRF score should be highest
    assert fused[0]["chunk_id"] == "chunk_2"
