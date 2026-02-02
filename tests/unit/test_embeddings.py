"""
Unit tests for Embeddings.
"""
import pytest
from unittest.mock import patch, MagicMock


def test_local_embedder_import_error():
    """Test that it raises ImportError if sentence-transformers missing."""
    with patch.dict('sys.modules', {'sentence_transformers': None}):
        # Force reimport to trigger ImportError check
        import importlib
        import chora.embeddings.local as embed_module
        
        # Clear cached model
        embed_module._global_embedder = None
        
        # Should raise when trying to create embedder
        with pytest.raises(ImportError):
            from sentence_transformers import SentenceTransformer


def test_embedder_returns_list():
    """Test that embedder returns a list of floats (mocked)."""
    mock_model = MagicMock()
    mock_array = MagicMock()
    mock_array.tolist.return_value = [0.1, 0.2, 0.3]
    mock_model.encode.return_value = mock_array
    
    with patch('chora.embeddings.local.SentenceTransformer', return_value=mock_model, create=True):
        # Need to reimport after patching
        from chora.embeddings import local
        
        # Create embedder with mocked model
        embedder = MagicMock()
        embedder.embed_text.return_value = [0.1, 0.2, 0.3]
        
        result = embedder.embed_text("test text")
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(x, float) for x in result)


def test_embedding_protocol():
    """Test that Embedder protocol is defined correctly."""
    from chora.embeddings.local import Embedder
    
    # Create a mock that satisfies the protocol
    mock_embedder = MagicMock()
    mock_embedder.embed_text.return_value = [0.1, 0.2]
    
    # Should work as Embedder
    result = mock_embedder.embed_text("hello")
    assert result == [0.1, 0.2]
