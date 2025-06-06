"""
PNG Text Codec - Encode and decode Unicode text to/from PNG images.

This module provides functionality to hide Unicode text (including emojis and 
non-BMP characters) inside PNG images by encoding bytes as pixel data with 
spatial relationships indicated by color channels.
"""

from __future__ import annotations

import random
from typing import List, Tuple

from pathlib import Path
from PIL import Image


class PNGTextCodec:
    """
    A codec for encoding/decoding Unicode text to/from PNG images.
    
    The encoding works by:
    1. Converting text to UTF-16 bytes
    2. Storing each byte pair in a pixel (R=high byte, B=low byte)
    3. Using the green channel to encode distance+direction to next pixel
       (bits 7-2 = distance, bits 1-0 = direction)
    4. Creating a chain of pixels that can be followed to reconstruct the text
    """
    
    # Direction encoding constants
    _DIR_BITS = {
        (1, 0): 0b00,   # → right
        (-1, 0): 0b01,  # ← left
        (0, 1): 0b10,   # ↓ down
        (0, -1): 0b11,  # ↑ up
    }
    
    _DIRS_DECODE = {
        0b00: (1, 0),   # → right
        0b01: (-1, 0),  # ← left
        0b10: (0, 1),   # ↓ down
        0b11: (0, -1),  # ↑ up
    }
    
    _DIRECTIONS = list(_DIR_BITS.keys())

    MAX_DISTANCE = 2 ** 6 - 1

    @classmethod
    def encode(
        cls,
        text: str,
        output_path: str | Path,
        *,
        random_seed: int | None = None,
    ) -> None:
        """
        Encode text as a PNG image.
        
        Args:
            text: Unicode string to encode (supports emojis & non-BMP chars)
            output_path: Where to save the PNG file
            max_distance: Maximum step distance between pixels (1-63)
            random_seed: Seed for reproducible output (None for random)
            
        Raises:
            ValueError: If max_distance is not in valid range
        """
        rng = random.Random(random_seed) if random_seed is not None else random
        
        # Convert text to UTF-16 bytes
        byte_seq = text.encode("utf-16", "surrogatepass")
        if len(byte_seq) % 2:  # Ensure even length
            byte_seq += b"\x00"
            
        # Group bytes into pairs
        byte_pairs = [
            (byte_seq[i], byte_seq[i + 1]) 
            for i in range(0, len(byte_seq), 2)
        ]
        
        pixels = cls._encode_pixels(byte_pairs, rng)
        cls._save_image(pixels, output_path)
    
    @classmethod
    def decode(cls, image_path: str | Path) -> str:
        """
        Decode text from a PNG image created by encode().
        
        Args:
            image_path: Path to the encoded PNG file
            
        Returns:
            The original Unicode text
            
        Raises:
            ValueError: If image has no payload or broken pixel chain
        """
        # Load non-transparent pixels
        pixel_data = cls._load_pixel_data(image_path)
        
        if not pixel_data:
            raise ValueError("No payload found in the image")
            
        # Find starting pixel and walk the chain
        start_pixel = cls._find_start_pixel(pixel_data)
        byte_sequence = cls._extract_bytes(pixel_data, start_pixel)
        
        # Convert bytes back to text
        text = bytes(byte_sequence).decode("utf-16", "surrogatepass")
        
        # Remove any trailing null padding
        return text.rstrip("\x00")
    
    @classmethod
    def _encode_pixels(
        cls, 
        byte_pairs: List[Tuple[int, int]], 
        rng
    ) -> List[Tuple[int, int, int, int, int]]:  # (x, y, r, g, b)
        """Generate pixel data for byte pairs."""
        pixels = []
        used_positions = {(0, 0)}
        current_x = current_y = 0
        
        for idx, (high_byte, low_byte) in enumerate(byte_pairs):
            # Determine green value (pointer to next pixel or EOF)
            if idx < len(byte_pairs) - 1:
                # Find next available position
                next_x, next_y, green = cls._find_next_position(
                    current_x, current_y, used_positions, rng
                )
                used_positions.add((next_x, next_y))
            else:
                # Last pixel - EOF sentinel
                green = 0
                next_x = next_y = None
            
            pixels.append((current_x, current_y, high_byte, green, low_byte))
            
            if next_x is not None:
                current_x, current_y = next_x, next_y
                
        return pixels
    
    @classmethod
    def _find_next_position(
        cls, x: int, y: int, used: set, rng
    ) -> Tuple[int, int, int]:
        """Find next available position and return coordinates + green value."""
        directions = list(cls._DIRECTIONS)  # Copy the directions list
        
        while directions:
            dx, dy = rng.choice(directions)
            directions.remove((dx, dy))  # Remove this direction to avoid retrying
            
            for distance in range(1, cls.MAX_DISTANCE + 1):
                next_x, next_y = x + dx * distance, y + dy * distance
                if (next_x, next_y) not in used:
                    direction_code = cls._DIR_BITS[(dx, dy)]
                    green = (distance << 2) | direction_code
                    return next_x, next_y, green
        
        # If we get here, all directions at all distances are blocked
        raise RuntimeError("No available positions found within max_dist")
    
    @classmethod
    def _save_image(
        cls, 
        pixels: List[Tuple[int, int, int, int, int]], 
        output_path: str | Path
    ) -> None:
        """Create and save the PNG image from pixel data."""
        # Calculate canvas bounds
        min_x = min(p[0] for p in pixels)
        max_x = max(p[0] for p in pixels)
        min_y = min(p[1] for p in pixels)
        max_y = max(p[1] for p in pixels)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        # Create transparent canvas
        canvas = [[(0, 0, 0, 0) for _ in range(width)] for _ in range(height)]
        
        # Place pixels
        for x, y, r, g, b in pixels:
            canvas_x, canvas_y = x - min_x, y - min_y
            canvas[canvas_y][canvas_x] = (r, g, b, 255)  # Opaque
        
        # Save image
        img = Image.new("RGBA", (width, height))
        img.putdata([pixel for row in canvas for pixel in row])
        img.save(Path(output_path))
    
    @classmethod
    def _load_pixel_data(cls, image_path: str | Path) -> dict:
        """Load non-transparent pixels from image."""
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        pixels = img.load()
        
        data = {}
        for y in range(height):
            for x in range(width):
                r, g, b, alpha = pixels[x, y]
                if alpha:  # Non-transparent pixel
                    data[(x, y)] = (r, g, b)
                    
        return data
    
    @classmethod
    def _find_start_pixel(cls, pixel_data: dict) -> Tuple[int, int]:
        """Find the starting pixel (not pointed to by any other pixel)."""
        pointed_to = set()
        
        for (x, y), (_, g, _) in pixel_data.items():
            if g == 0:  # EOF sentinel
                continue
                
            distance = g >> 2
            direction_code = g & 0x03
            dx, dy = cls._DIRS_DECODE[direction_code]
            target = (x + dx * distance, y + dy * distance)
            pointed_to.add(target)
        
        origins = [pos for pos in pixel_data if pos not in pointed_to]
        
        if len(origins) != 1:
            raise ValueError("Cannot uniquely identify the starting pixel")
            
        return origins[0]
    
    @classmethod
    def _extract_bytes(cls, pixel_data: dict, start: Tuple[int, int]) -> List[int]:
        """Follow the pixel chain and extract byte sequence."""
        bytes_list = []
        current = start
        
        while True:
            if current not in pixel_data:
                raise ValueError("Broken pointer chain - missing target pixel")
                
            r, g, b = pixel_data[current]
            bytes_list.extend([r, b])  # High byte, low byte
            
            if g == 0:  # EOF sentinel
                break
                
            # Follow pointer to next pixel
            distance = g >> 2
            direction_code = g & 0x03
            dx, dy = cls._DIRS_DECODE[direction_code]
            current = (current[0] + dx * distance, current[1] + dy * distance)
            
        return bytes_list
