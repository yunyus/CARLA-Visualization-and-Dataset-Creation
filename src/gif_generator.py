from PIL import Image
import os
import os
import imageio

# Define the folder path containing the PNG images
folder_path = "rootput"

# Define the names of the PNG types
png_types = [
    "front_rgb",
    "front_sem",
    "pole1_rgb",
    "pole1_sem",
    "pole2_rgb",
    "pole2_sem"
]

# Create GIFs for each PNG type
for png_type in png_types:
    # Create a list to store the image paths
    image_paths = []

    # Find all PNG images starting with the specific type
    for filename in os.listdir(folder_path):
        if filename.startswith(png_type) and filename.endswith(".png"):
            image_paths.append(os.path.join(folder_path, filename))

    # Sort the image paths in alphanumeric order
    image_paths.sort()

    # Create GIF filename
    gif_filename = f"{png_type}.gif"

    # Read images and save as GIF
    images = [imageio.imread(image_path) for image_path in image_paths]
    gif_path = os.path.join(folder_path, gif_filename)
    imageio.mimsave(gif_path, images, duration=0.2)


    print(f"Created GIF: {gif_filename}")
