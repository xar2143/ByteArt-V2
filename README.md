# ByteArt
Encode sequences of bytes into decodable, randomizable pixel art.

The idea is to come up with a reversible encoding that visualizes sequences of bytes.

No error detection or correction has been applied.

## Encoding

We take as input a string `S`, which is internally converted into a sequence of bytes. In this project, I am using Unicode (UTF-16), but the idea works for any finite sequence of bytes.

The output is an RGBA image: 8 bits per channel.

## Algorithm

Input: a string `S` (considered as bytes).  
Output: an RGBA image encoding `S`.

The encoding works as follows:

0. Define the current position `pos` as the origin `(0, 0)`.
1. For each pair of bytes in `S`:
   1. Create a new pixel `p`.
   2. Load the next byte `b₁`, store it in `p`'s **red** channel.
   3. Load the next byte `b₂`, store it in `p`'s **blue** channel.
   4. Choose a random direction `dir` (right, left, down, up).
   5. Along `dir`, find the first free spot at a distance `dist` between 1 and 63 pixels.
      - `dist` is encoded in 6 bits, and `dir` is encoded in 2 bits.
   6. If no free spot is found in a direction, try another one.
   7. If no directions are left, the sequence cannot be encoded (raise an error).
   8. Place `p` at the found position.
   9. Encode the **green** channel as `g = (dist << 2) | dir`.
   10. Set the **alpha** channel to 255 (opaque).
   11. Update `pos` to be the new pixel’s position.
2. After all bytes are processed, the last pixel sets `g = 0` to indicate end-of-data (EOF sentinel).
3. The image may be padded with `(0, 0, 0, 0)` (transparent) pixels to form a valid rectangular image.

## Rationale

I want to create a random-walk-looking pixel art that is fully connected and aesthetically pleasing.

### Colors
I like the red-purple-blue gradient. Hence, I decided to fill the red and blue channels with data and leave the green channel mostly close to zero as a control channel.

This way, the result will look purple-ish, with subtle lighter tones where the green channel activates.

In order to minimize the green channel’s brightness, I encode the 6 bits of distance first, followed by 2 bits for direction. 
- Distance values are usually small (1–10), so most significant bits will often stay at 0.
- Directions are random and uniformly distributed between 0 and 3.

If we had encoded the direction first, the two most significant bits would be almost always non-zero, resulting in a much brighter green channel.

### Connectivity

When placing a pixel, we always move from an already occupied position to a new free neighbor, ensuring the pixel graph is fully connected.

### Sequence Start

Since the resulting image can spread randomly across the canvas, the start of the sequence is identified **structurally**:
- Every pixel points to the next pixel via its green channel.
- The **start pixel** is the only one **not pointed to** by any other pixel.
- During decoding, we find the start pixel by checking which pixel has no incoming pointer.

This ensures that decoding can reliably find the entry point of the sequence without needing any special reserved pixel.

## Example

Say that the string `S` corresponds to a sequence of bytes `S_b`.  
In this example, we assume it consists of two bytes: `01000101 00111110`.

| b₀ | b₁ | b₂ | b₃ | b₄ | b₅ | b₆ | b₇ | b₈ | b₉ | b₁₀ | b₁₁ | b₁₂ | b₁₃ | b₁₄ | b₁₅ |
|----|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|-----|-----|
| 0  | 1  | 0  | 0  | 0  | 1  | 0  | 1  | 0  | 0  | 1  | 1  | 1  | 1  | 1  | 0  |

- The first byte `01000101` is stored in the red channel.
- The next byte `00111110` is stored in the blue channel.
- Choose the direction `up` (encoded as `11`).
- The first free pixel in this direction is at distance 1 (`000001`).
- Encode green as `00000111`.
- Place the pixel at `(0, 1)`.

Since the string has ended, no more pixels are added, and the last pixel's green channel is set to `0` to mark the end of the sequence.

## Usage

### Installation

Make sure you have `Pillow` installed:

```bash
pip install pillow
```

### Encoding a String

To encode a string into a PNG image:

```python
from png_text_codec import PNGTextCodec  # Adjust the import based on your file/module name

# Your text
text = "Hello, ByteArt! 🚀🎨"

# Path to output PNG file
output_path = "encoded_image.png"

# Encode
PNGTextCodec.encode(text, output_path, random_seed=42)  # Optional seed for reproducibility
```

- `text`: The Unicode string you want to encode (UTF-16 encoded internally, so supports emojis and special characters).
- `output_path`: File path where the PNG image will be saved.
- `random_seed`: (Optional) If you want the output image to be reproducible.

### Decoding a String

To decode the text back from the PNG image:

```python
from png_text_codec import PNGTextCodec  # Adjust the import based on your file/module name

# Path to input PNG file
input_path = "encoded_image.png"

# Decode
decoded_text = PNGTextCodec.decode(input_path)

print(decoded_text)  # Should print: Hello, ByteArt! 🚀🎨
```

- `input_path`: File path to the PNG image to decode.
- Returns the original Unicode string.

### Notes

- The codec fully supports any Unicode characters, including emojis and characters outside the Basic Multilingual Plane (BMP).
- The encoded image will look like a random walk of purple-ish pixels.
- The `random_seed` ensures that the random walk is the same every time, useful for testing or reproducibility.
- The decoding process automatically finds the start of the sequence based on the pixel graph structure — no special markers are needed.

## Example

The following is a 5-paragraphs lorem-ipsum

![ByteArt Example](https://github.com/AndreaRiboni/ByteArt/blob/main/data/lorem_ipsum.webp?raw=true)
