# ByteArt - V2

Encode any file into a decodable, randomizable pixel art image — and decode it back.

ByteArt lets you visually encode sequences of bytes (including text, images, videos, executables, documents, etc.) into PNG files. It features a reversible, structurally connected encoding algorithm that produces pixel art reminiscent of a random walk.

No error detection or correction is applied.

---

## Highlights

### 1. Improved Codec

* `PNGTextCodec` has been renamed to `PNGBytesCodec`.
* Supports full binary encoding/decoding:

  * `encode_bytes()` - encode raw bytes
  * `encode_file()` - encode any file to PNG
  * `decode_bytes()` - decode PNG back to raw bytes
  * `decode_to_file()` - decode PNG to original file
  * `encode_text()` / `decode_text()` retained for compatibility
* Works with any file format: text, images, executables, videos, etc.

### 2. Full GUI (tkinter-based)

* 3 main tabs:

  * **Encode**: File → PNG
  * **Decode**: PNG → File
  * **Text Mode**: Encode/decode plain text
* Features:

  * Integrated file browser
  * Progress bar for long operations
  * File info (name, size)
  * Error handling via messagebox
  * Threaded tasks to keep UI responsive
  * Optional random seed for reproducibility

---

## How to Use

Just run `main.py`. No command-line usage required.

### Encode a File

1. Go to **Encode** tab
2. Select any file (e.g., `.jpg`, `.exe`, `.txt`, etc.)
3. Choose where to save the resulting PNG
4. Click **Encode File**

### Decode a File

1. Go to **Decode** tab
2. Select a previously encoded PNG
3. Choose where to save the decoded file
4. Click **Decode File**

### Text Mode

1. Go to **Text Mode** tab
2. Type or paste any text
3. Encode to image or decode from image as desired

---

## Encoding Algorithm Overview

* Input: Sequence of bytes
* Output: RGBA image encoding the byte stream

### Steps:

1. Start from position (0, 0)
2. For each byte pair (b1, b2):

   * Store b1 in the Red channel
   * Store b2 in the Blue channel
   * Choose a random direction (up/down/left/right)
   * Find a free spot in that direction within 1-63 pixels
   * Encode the distance and direction in Green channel:

     * 6 bits for distance
     * 2 bits for direction
     * Green = (distance << 2) | direction
   * Set Alpha = 255
3. Last pixel has Green = 0 to mark EOF
4. Image is padded with transparent pixels to form a rectangle

### Connectivity & Decoding

* Every pixel points to the next, forming a graph
* The start pixel is the only one **not** pointed to by any other
* Decoding reconstructs the byte stream by walking the graph

---

## Installation

Python 3.7+

Install dependencies:

```bash
pip install pillow
```

Run the app:

```bash
python main.py
```

---

## Example (Old Text-Based Usage)

> Retained for compatibility — now handled through GUI.

```python
from codec import PNGBytesCodec

text = "Hello, ByteArt! \U0001F680\U0001F3A8"
out_path = "encoded.png"

PNGBytesCodec.encode_text(text, out_path, random_seed=42)
decoded = PNGBytesCodec.decode_text(out_path)
print(decoded)
```

---

## Notes

* Fully supports any Unicode characters
* Encoded images look like purple-ish random walks
* Use random seed for reproducibility
* Automatically locates start pixel on decoding
* No special markers required

## Example

The following is a 5-paragraphs lorem-ipsum

<img src="https://github.com/AndreaRiboni/ByteArt/blob/main/data/lorem_ipsum.webp?raw=true" width="200px" />
