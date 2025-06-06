from codec import PNGTextCodec


def main():
    """Demo the codec functionality."""
    sample_text = "Hello, 🌍🚀!  𝄞🎶 𠜎"  # Mixed BMP + non-BMP code points
    output_file = "encoded_demo.png"
    
    print(f"Original text: {sample_text}")
    
    # Encode
    PNGTextCodec.encode(sample_text, output_file, random_seed=42)  # Deterministic
    print(f"Encoded to: {output_file}")
    
    # Decode
    decoded_text = PNGTextCodec.decode(output_file)
    print(f"Decoded text: {decoded_text}")
    
    # Verify
    print(f"Round-trip successful: {sample_text == decoded_text}")


if __name__ == "__main__":
    main()