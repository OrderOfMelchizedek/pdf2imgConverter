from pdf2image import convert_from_path
import os
import sys
import argparse
from PIL import Image
import math

def create_horizontal_image(images, start_idx, count):
    """Combine multiple images horizontally (side by side)"""
    # Get subset of images to combine
    img_set = images[start_idx:start_idx+count]
    
    # Print debug info
    print(f"Creating horizontal image with {len(img_set)} pages (indices {start_idx} to {start_idx+count-1})")
    
    # Handle the case where we only have one image (last page of odd-numbered PDF)
    if len(img_set) == 1:
        # Just return a copy of the single image
        return img_set[0].copy()
    
    # Calculate dimensions for the combined image
    widths, heights = zip(*(img.size for img in img_set))
    total_width = sum(widths)
    max_height = max(heights)
    
    # Print dimensions
    print(f"Creating combined image of size {total_width}x{max_height}")
    
    # Create a new blank image with the calculated dimensions
    combined_image = Image.new('RGB', (total_width, max_height), color='white')
    
    # Paste each image next to the previous one
    x_offset = 0
    for i, img in enumerate(img_set):
        print(f"  Pasting image {i+1} at position ({x_offset}, 0)")
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.size[0]
    
    return combined_image

def create_vertical_image(images, start_idx, count):
    """Combine multiple images vertically (stacked)"""
    # Get subset of images to combine
    img_set = images[start_idx:start_idx+count]
    
    # Print debug info
    print(f"Creating vertical image with {len(img_set)} pages (indices {start_idx} to {start_idx+count-1})")
    
    # Handle the case where we only have one image (last page of odd-numbered PDF)
    if len(img_set) == 1:
        # Just return a copy of the single image
        return img_set[0].copy()
    
    # Calculate dimensions for the combined image
    widths, heights = zip(*(img.size for img in img_set))
    max_width = max(widths)
    total_height = sum(heights)
    
    # Print dimensions
    print(f"Creating combined image of size {max_width}x{total_height}")
    
    # Create a new blank image with the calculated dimensions
    combined_image = Image.new('RGB', (max_width, total_height), color='white')
    
    # Paste each image below the previous one
    y_offset = 0
    for i, img in enumerate(img_set):
        print(f"  Pasting image {i+1} at position (0, {y_offset})")
        combined_image.paste(img, (0, y_offset))
        y_offset += img.size[1]
    
    return combined_image

def create_grid_image(images, start_idx, count):
    """Combine multiple images in a grid layout (2x2)"""
    # Get subset of images to combine
    img_set = images[start_idx:start_idx+min(count, len(images)-start_idx)]
    
    # Print debug info
    print(f"Creating grid image with {len(img_set)} pages (indices {start_idx} to {start_idx+len(img_set)-1})")
    
    # If we have only one image, just return it
    if len(img_set) == 1:
        return img_set[0].copy()
    
    # Handle cases with 2-3 images (non-grid layouts)
    if len(img_set) < 4:
        if len(img_set) == 2:
            # For 2 images, create a horizontal layout instead
            return create_horizontal_image(images, start_idx, 2)
        elif len(img_set) == 3:
            # For 3 images, create a custom layout (2 on top, 1 on bottom)
            # First calculate dimensions
            widths, heights = zip(*(img.size for img in img_set))
            
            # For the top row (first 2 images)
            top_width = widths[0] + widths[1]
            top_height = max(heights[0], heights[1])
            
            # Total dimensions
            total_width = max(top_width, widths[2])
            total_height = top_height + heights[2]
            
            # Create the combined image
            combined = Image.new('RGB', (total_width, total_height), color='white')
            
            # Paste the images
            combined.paste(img_set[0], (0, 0))
            combined.paste(img_set[1], (widths[0], 0))
            combined.paste(img_set[2], (0, top_height))
            
            return combined
    
    # Ensure we have exactly 4 images, pad with blank images if necessary
    while len(img_set) < 4:
        # Create a blank white image with the same dimensions as the first image
        blank = Image.new('RGB', img_set[0].size, color='white')
        img_set.append(blank)
    
    # Calculate dimensions for the combined image
    widths, heights = zip(*(img.size for img in img_set))
    max_width = max(widths[:2])  # Max width of first two images
    max_width2 = max(widths[2:])  # Max width of last two images
    max_height = max(heights[0], heights[2])  # Max height of first and third images
    max_height2 = max(heights[1], heights[3])  # Max height of second and fourth images
    
    # Determine total dimensions
    total_width = max_width + max_width2
    total_height = max_height + max_height2
    
    # Print dimensions
    print(f"Creating combined image of size {total_width}x{total_height}")
    
    # Create a new blank image with the calculated dimensions
    combined_image = Image.new('RGB', (total_width, total_height), color='white')
    
    # Paste images in a 2x2 grid
    print(f"  Pasting image 1 at position (0, 0)")
    combined_image.paste(img_set[0], (0, 0))
    print(f"  Pasting image 2 at position ({max_width}, 0)")
    combined_image.paste(img_set[1], (max_width, 0))
    print(f"  Pasting image 3 at position (0, {max_height})")
    combined_image.paste(img_set[2], (0, max_height))
    print(f"  Pasting image 4 at position ({max_width}, {max_height})")
    combined_image.paste(img_set[3], (max_width, max_height))
    
    return combined_image

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert PDF to images with various layout options')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--layout', choices=['single', 'horizontal', 'vertical', 'grid'], 
                        default='single', help='Layout of pages in the output image')
    parser.add_argument('--pages-per-image', type=int, choices=[1, 2, 4], 
                        default=None, help='Number of pages to combine in each output image')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set default pages per image based on layout if not specified
    if args.pages_per_image is None:
        if args.layout == 'single':
            args.pages_per_image = 1
        elif args.layout in ['horizontal', 'vertical']:
            args.pages_per_image = 2
        elif args.layout == 'grid':
            args.pages_per_image = 4
    
    # Validate arguments
    if args.layout == 'single' and args.pages_per_image != 1:
        args.pages_per_image = 1
        print("Warning: Single layout only supports 1 page per image. Setting pages-per-image to 1.")
    elif args.layout in ['horizontal', 'vertical'] and args.pages_per_image > 2:
        args.pages_per_image = 2
        print("Warning: Horizontal and vertical layouts only support up to 2 pages per image. Setting pages-per-image to 2.")
    elif args.layout == 'grid' and args.pages_per_image != 4:
        args.pages_per_image = 4
        print("Warning: Grid layout requires 4 pages per image. Setting pages-per-image to 4.")
    
    # Ensure horizontal and vertical layouts have at least 2 pages per image
    if args.layout in ['horizontal', 'vertical'] and args.pages_per_image < 2:
        args.pages_per_image = 2
        print(f"Setting pages-per-image to 2 for {args.layout} layout")
        
    print(f"Using layout: {args.layout} with {args.pages_per_image} pages per image")
    
    # Get the base name of the PDF file without extension
    pdf_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
    
    # Directory of the main script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Main output directory
    main_output_dir = os.path.join(script_dir, "output")
    
    # Create main output directory if it doesn't exist
    if not os.path.exists(main_output_dir):
        os.makedirs(main_output_dir)
    
    # PDF-specific output directory within the main output directory
    output_dir = os.path.join(main_output_dir, f"{pdf_name}_{args.layout}")
    
    # Create PDF-specific output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Convert the PDF into individual images, one image per page
    images = convert_from_path(args.pdf_path)
    total_pages = len(images)
    
    # Process based on the selected layout
    if args.layout == 'single':
        # Original behavior: one page per image
        for i, image in enumerate(images):
            image_file = os.path.join(output_dir, f'page_{i+1}.png')
            image.save(image_file, 'PNG')
            print(f'Saved {image_file}')
    else:
        # Calculate how many combined images we'll create
        num_combined_images = math.ceil(total_pages / args.pages_per_image)
        
        for i in range(num_combined_images):
            start_idx = i * args.pages_per_image
            
            # Create combined image based on layout
            if args.layout == 'horizontal':
                combined = create_horizontal_image(images, start_idx, min(args.pages_per_image, total_pages - start_idx))
            elif args.layout == 'vertical':
                combined = create_vertical_image(images, start_idx, min(args.pages_per_image, total_pages - start_idx))
            elif args.layout == 'grid':
                combined = create_grid_image(images, start_idx, min(args.pages_per_image, total_pages - start_idx))
            
            # Save the combined image
            page_range = f'{start_idx+1}-{min(start_idx+args.pages_per_image, total_pages)}'
            image_file = os.path.join(output_dir, f'pages_{page_range}.png')
            combined.save(image_file, 'PNG')
            print(f'Saved {image_file}')
    
    print("PDF conversion complete.")

if __name__ == "__main__":
    main()