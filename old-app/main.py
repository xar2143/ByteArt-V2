from codec import PNGTextCodec


def main():
    """Demo the codec functionality."""
    sample_text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer fermentum urna in augue feugiat vulputate. Aenean vel tortor ut nisl efficitur vestibulum vitae et erat. Aenean et nisi in nunc tempus porta. Donec sed justo elit. Maecenas et arcu metus. Phasellus accumsan sollicitudin tortor eu vestibulum. Nunc eu commodo justo. Curabitur hendrerit ipsum vel eros sagittis, a facilisis nibh posuere. Praesent commodo dapibus fermentum. In mi velit, mollis et vehicula a, ultrices at enim. Aliquam blandit tempus dolor, vel consequat eros sollicitudin et. Etiam pulvinar sem id mi varius, et malesuada odio condimentum. In hac habitasse platea dictumst. Nam id blandit arcu. In lobortis mi turpis, at sodales ipsum dapibus in.

Pellentesque pellentesque odio vel augue mollis rhoncus. Vivamus iaculis dignissim vehicula. Fusce nec gravida odio, scelerisque placerat lorem. Duis vel posuere dolor. Curabitur blandit leo libero, eget faucibus tellus efficitur vitae. Phasellus commodo dolor sed libero lacinia euismod. Cras nisi eros, posuere placerat feugiat eget, vehicula eu felis. Nulla facilisi. Sed auctor dignissim aliquet. Nam id congue sapien. Duis vitae velit justo. In et pretium velit.

Fusce sem odio, fringilla vel turpis non, semper pulvinar sapien. Phasellus consectetur tincidunt odio, ac volutpat urna feugiat sed. Donec imperdiet ornare ornare. Aliquam erat volutpat. Integer convallis pharetra maximus. Pellentesque mollis eros id elit convallis convallis. Nulla dignissim erat nec semper iaculis. Aliquam erat volutpat. Nam a magna orci.

Aliquam porta tincidunt arcu nec rhoncus. Vestibulum sollicitudin pellentesque nisi. Duis sodales neque tincidunt lobortis accumsan. Curabitur convallis accumsan ex, vel facilisis diam cursus auctor. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Aenean ornare vestibulum metus, nec aliquam augue ullamcorper vitae. Nunc pharetra arcu in ipsum consectetur fermentum. Vivamus nulla tellus, molestie sit amet mollis non, faucibus sit amet nisl. Sed commodo mattis sapien.

Phasellus cursus pretium dui et convallis. Maecenas in metus non ligula congue finibus condimentum at mauris. Duis commodo enim neque, quis porta enim bibendum at. Fusce id massa egestas, placerat lacus at, mattis neque. Suspendisse in malesuada lacus, eget vehicula tortor. Phasellus ipsum turpis, interdum id magna sit amet, tempus scelerisque metus. Donec ultricies lorem in mauris semper tempus."""  # Mixed BMP + non-BMP code points
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
