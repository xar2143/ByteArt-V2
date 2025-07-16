"""
Unit tests for PNGTextCodec using pytest.
"""

import pytest
import tempfile
import os
from pathlib import Path
from PIL import Image

from app.codec import PNGTextCodec


class TestPNGTextCodec:
    """Test suite for PNGTextCodec."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = Path(self.temp_dir) / "test.png"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_image_path.exists():
            self.test_image_path.unlink()
        os.rmdir(self.temp_dir)
    
    def test_encode_decode_simple_text(self):
        """Test basic encoding and decoding of simple ASCII text."""
        text = "Hello, World!"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        decoded = PNGTextCodec.decode(self.test_image_path)
        
        assert decoded == text
    
    def test_encode_decode_unicode_text(self):
        """Test encoding and decoding of Unicode text with special characters."""
        text = "Hello, 世界! 🌍 café naïve résumé"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        decoded = PNGTextCodec.decode(self.test_image_path)
        
        assert decoded == text
    
    def test_encode_decode_emoji_text(self):
        """Test encoding and decoding of text with emojis."""
        text = "🚀 Rocket to the 🌙 moon! 🎉"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        decoded = PNGTextCodec.decode(self.test_image_path)
        
        assert decoded == text
    
    def test_encode_decode_empty_string(self):
        """Test encoding and decoding of empty string."""
        text = ""
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        decoded = PNGTextCodec.decode(self.test_image_path)
        
        assert decoded == text
    
    def test_encode_decode_single_character(self):
        """Test encoding and decoding of single character."""
        text = "A"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        decoded = PNGTextCodec.decode(self.test_image_path)
        
        assert decoded == text
    
    def test_encode_decode_long_text(self):
        """Test encoding and decoding of longer text."""
        text = "Lorem ipsum dolor sit amet, " * 10
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        decoded = PNGTextCodec.decode(self.test_image_path)
        
        assert decoded == text
    
    def test_encode_decode_newlines_and_tabs(self):
        """Test encoding and decoding of text with control characters."""
        text = "Line 1\nLine 2\n\tTabbed line\r\nWindows line ending"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        decoded = PNGTextCodec.decode(self.test_image_path)
        
        assert decoded == text
    
    def test_encode_creates_valid_png(self):
        """Test that encoding creates a valid PNG file."""
        text = "Test image creation"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        
        assert self.test_image_path.exists()
        
        # Verify it's a valid PNG by opening with PIL
        with Image.open(self.test_image_path) as img:
            assert img.format == "PNG"
            assert img.mode == "RGBA"
    
    def test_deterministic_encoding_with_seed(self):
        """Test that same seed produces identical images."""
        text = "Deterministic test"
        seed = 12345
        
        path1 = Path(self.temp_dir) / "test1.png"
        path2 = Path(self.temp_dir) / "test2.png"
        
        try:
            PNGTextCodec.encode(text, path1, random_seed=seed)
            PNGTextCodec.encode(text, path2, random_seed=seed)
            
            # Compare file contents
            with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
                assert f1.read() == f2.read()
        finally:
            for path in [path1, path2]:
                if path.exists():
                    path.unlink()
    
    def test_different_seeds_produce_different_images(self):
        """Test that different seeds produce different images."""
        text = "Random test"
        
        path1 = Path(self.temp_dir) / "test1.png"
        path2 = Path(self.temp_dir) / "test2.png"
        
        try:
            PNGTextCodec.encode(text, path1, random_seed=1)
            PNGTextCodec.encode(text, path2, random_seed=2)
            
            # Files should be different
            with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
                assert f1.read() != f2.read()
            
            # But decode to same text
            assert PNGTextCodec.decode(path1) == text
            assert PNGTextCodec.decode(path2) == text
        finally:
            for path in [path1, path2]:
                if path.exists():
                    path.unlink()
    
    def test_decode_nonexistent_file(self):
        """Test decoding a non-existent file raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            PNGTextCodec.decode("nonexistent.png")
    
    def test_decode_empty_image(self):
        """Test decoding an image with no payload raises ValueError."""
        # Create empty transparent image
        img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        img.save(self.test_image_path)
        
        with pytest.raises(ValueError, match="No payload found"):
            PNGTextCodec.decode(self.test_image_path)
    
    def test_pathlib_path_support(self):
        """Test that Path objects work as well as strings."""
        text = "Path test"
        path_obj = Path(self.test_image_path)
        
        PNGTextCodec.encode(text, path_obj, random_seed=42)
        decoded = PNGTextCodec.decode(path_obj)
        
        assert decoded == text
    
    def test_direction_encoding_constants(self):
        """Test that direction encoding constants are consistent."""
        # Test that encoding and decoding directions match
        for direction, bits in PNGTextCodec._DIR_BITS.items():
            assert PNGTextCodec._DIRS_DECODE[bits] == direction
        
        # Test that all directions are covered
        assert len(PNGTextCodec._DIR_BITS) == 4
        assert len(PNGTextCodec._DIRS_DECODE) == 4
        assert len(PNGTextCodec._DIRECTIONS) == 4
    
    def test_max_distance_constant(self):
        """Test that MAX_DISTANCE is within valid range."""
        assert PNGTextCodec.MAX_DISTANCE == 63  # 2^6 - 1
        assert PNGTextCodec.MAX_DISTANCE > 0
    
    def test_find_next_position_no_infinite_loop(self):
        """Test that _find_next_position doesn't loop infinitely."""
        import random
        rng = random.Random(42)
        
        # Create a scenario where all positions are blocked
        used_positions = set()
        for x in range(-100, 100):
            for y in range(-100, 100):
                used_positions.add((x, y))
        
        # This should either find a position or raise RuntimeError quickly
        with pytest.raises(RuntimeError, match="No available positions found"):
            PNGTextCodec._find_next_position(0, 0, used_positions, rng)
    
    def test_byte_pair_encoding(self):
        """Test that byte pairs are encoded correctly in pixels."""
        # Test specific Unicode character that uses multiple bytes
        text = "€"  # Euro symbol
        bytes_utf16 = text.encode("utf-16")
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        
        # Load the image and check pixel values
        pixel_data = PNGTextCodec._load_pixel_data(self.test_image_path)
        
        # Should have pixels corresponding to the UTF-16 encoding
        assert len(pixel_data) >= len(bytes_utf16) // 2
    
    def test_eof_sentinel(self):
        """Test that EOF sentinel (green=0) is properly handled."""
        text = "EOF test"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        pixel_data = PNGTextCodec._load_pixel_data(self.test_image_path)
        
        # Should have at least one pixel with green=0 (EOF)
        eof_pixels = [pos for pos, (r, g, b) in pixel_data.items() if g == 0]
        assert len(eof_pixels) == 1
    
    def test_start_pixel_identification(self):
        """Test that start pixel is correctly identified."""
        text = "Start pixel test"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        pixel_data = PNGTextCodec._load_pixel_data(self.test_image_path)
        
        start_pixel = PNGTextCodec._find_start_pixel(pixel_data)
        
        # Start pixel should exist in the pixel data
        assert start_pixel in pixel_data
    
    def test_non_bmp_characters(self):
        """Test encoding/decoding of characters outside Basic Multilingual Plane."""
        # Mathematical script capital letters (U+1D49C to U+1D4B5)
        text = "𝒜𝒷𝒸𝒹ℯ𝒻ℊ"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        decoded = PNGTextCodec.decode(self.test_image_path)
        
        assert decoded == text
    
    def test_mixed_scripts(self):
        """Test text with mixed writing systems."""
        text = "Hello नमस्ते 你好 Здравствуйте مرحبا 🌍"
        
        PNGTextCodec.encode(text, self.test_image_path, random_seed=42)
        decoded = PNGTextCodec.decode(self.test_image_path)
        
        assert decoded == text


if __name__ == "__main__":
    pytest.main([__file__])
