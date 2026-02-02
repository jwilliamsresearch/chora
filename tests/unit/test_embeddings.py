"""
Unit tests for Embeddings.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys

def test_local_embedder_import_error():
    """Test that it raises ImportError if sentence-transformers missing."""
    with patch.dict(sys.modules, {'sentence_transformers': None}):
        # Mocking the module to be None should force ImportError
        from chora.embeddings.local import LocalEmbedder
        with pytest.raises(ImportError):
            LocalEmbedder()

def test_create_embedder_success():
    """Test successful creation and embedding (Mocked)."""
    mock_st = MagicMock()
    mock_model = MagicMock()
    mock_st.SentenceTransformer.return_value = mock_model
    mock_model.encode.return_value = MagicMock(tolist=lambda: [0.1, 0.2])
    
    with patch.dict(sys.modules, {'sentence_transformers': mock_st}):
        from chora.embeddings.local import LocalEmbedder
        embedder = LocalEmbedder()
        
        vec = embedder.embed_text("test")
        assert vec == [0.1, 0.2]
        mock_model.encode.assert_called_with("test")
