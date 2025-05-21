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
        # If we allow single image pass-through, we might need to pad it to 2x2 if grid is selected.
        # For now, this remains, but the task implies grid forces 2x2.
        # This could be revisited: if grid is selected and 1 image, should it be 1 image or 1 image in a 2x2 grid?
        # Based on current task, if len(img_set) is 1, it will be padded to 4.
        # So, this specific early return for len(img_set) == 1 might be redundant if padding always occurs.
        # However, the problem description focuses on 2 and 3 images, so let's keep this for now.
        # UPDATE: The problem statement implies that if less than 4 images, they should be padded.
        # So, this len(img_set) == 1 check should also lead to padding.
        # Let's remove this to ensure padding happens for 1, 2, or 3 images.
        pass # This line will be removed by the next block.

    # Ensure we have exactly 4 images, pad with blank images if necessary
    # The problem states "Ensuring that the padding logic ... is always executed if the initial len(img_set) ... is less than 4"
    # This means the conditions for 2 and 3 images should be removed, and this padding logic should handle it.
    
    # If img_set is empty, we can't get img_set[0].size. This shouldn't happen with valid PDFs.
    # If it can happen, a default size for blank images would be needed.
    # Assuming img_set will have at least one image if start_idx is valid.
    # If images itself is empty, convert_from_path would likely raise an error or return [].
    # If start_idx is beyond len(images), img_set will be empty.
    # The line `img_set = images[start_idx:start_idx+min(count, len(images)-start_idx)]` handles this.
    # If img_set is empty after slicing, we need a default size for blank images.
    # For now, assume img_set is not empty if we reach here and need padding.
    # If it was empty, `images[start_idx]` would also fail.
    
    # Determine the size for blank padding images.
    # Use the first image of the current set if available, otherwise, this logic needs a fallback.
    # This assumes that if img_set is not empty, img_set[0] is a valid image to get dimensions from.
    # If img_set is initially empty, this will fail.
    # However, `images[start_idx]` should be safe if `start_idx < len(images)`.
    # `min(count, len(images)-start_idx)` ensures we don't go out of bounds for `images`.
    # If `len(images)-start_idx` is 0 or negative, `img_set` will be empty.
    
    # If img_set is empty and we need to pad to 4, we need a default size.
    # Let's assume if img_set is empty, we can't proceed with grid creation or padding.
    # The calling code `min(args.pages_per_image, total_pages - start_idx)` should ensure `count` is appropriate.
    # If `total_pages - start_idx` is 0, `count` passed to `create_grid_image` will be 0, so `img_set` is empty.
    if not img_set and count > 0: # count is the original requested number for the grid
        # This case means we were asked to create a grid, but there are no images for this slot.
        # This might happen if e.g. pdf has 5 pages, and we are creating the second 2x2 grid.
        # The first grid gets 1,2,3,4. The second grid is for page 5. start_idx=4, count=4.
        # img_set = images[4:min(4+4, 5)] = images[4:5] -> one image. This will be padded.
        # What if pdf has 4 pages. start_idx=4, count=4. img_set = images[4:min(8,4)] = images[4:4] -> empty.
        # In this "empty" case, we should probably return None or an empty image, not try to pad.
        # The loop for num_combined_images should handle this by not calling create_grid_image.
        # `math.ceil(total_pages / args.pages_per_image)`
        # If total_pages = 4, pages_per_image = 4. num_combined_images = 1. Loop i=0. start_idx=0.
        # If total_pages = 5, pages_per_image = 4. num_combined_images = 2. Loop i=0, start_idx=0. Loop i=1, start_idx=4.
        #   For i=1, start_idx=4. `count_for_current_call` = `min(4, 5-4)` = `min(4,1)` = 1.
        #   `img_set` = `images[4:4+1]` which is one image. This will be padded.
        # So, `img_set` should not be empty if `create_grid_image` is called appropriately.
        # The `if len(img_set) == 1:` check before the removed blocks would have handled single images.
        # Now, single images (and 2, 3) will fall through to the padding logic.
        print("Warning: img_set is empty in create_grid_image. This should ideally not happen.")
        # Decide on behavior: return None, or an empty image, or raise error.
        # For now, let's assume it won't be empty based on call patterns.
        # If it were, img_set[0].size below would fail.

    # Ensure we have exactly 4 images, pad with blank images if necessary
    if img_set: # Proceed only if there's at least one image to determine padding size
        pad_img_size = img_set[0].size # Use the first actual image's size for padding
        while len(img_set) < 4:
            # Create a blank white image with the same dimensions as the first image of the set
            blank = Image.new('RGB', pad_img_size, color='white')
            img_set.append(blank)
    else: # img_set is empty. We cannot create a 2x2 grid.
        # This scenario should ideally be caught by the calling logic in main().
        # If we must return an image, it would be a blank 2x2 grid of some default cell size.
        # Or return None to signify no image could be created.
        print("Error: No images provided to create_grid_image. Returning None.")
        return None # Or handle error appropriately

    # All images in img_set (actual or padded) should ideally be the same size for a uniform grid.
    # The problem asks to use img_set[0].size for cell dimensions.
    grid_cell_width = img_set[0].size[0]
    grid_cell_height = img_set[0].size[1]

    # Determine total dimensions for the 2x2 grid
    total_width = 2 * grid_cell_width
    total_height = 2 * grid_cell_height
    
    # Print dimensions
    print(f"Creating combined 2x2 grid image of size {total_width}x{total_height}")
    print(f"Grid cell dimensions: {grid_cell_width}x{grid_cell_height}")
    
    # Create a new blank image with the calculated dimensions
    combined_image = Image.new('RGB', (total_width, total_height), color='white')
    
    # Paste images in a 2x2 grid
    print(f"  Pasting image 1 (top-left) at position (0, 0)")
    combined_image.paste(img_set[0], (0, 0))
    print(f"  Pasting image 2 (top-right) at position ({grid_cell_width}, 0)")
    combined_image.paste(img_set[1], (grid_cell_width, 0))
    print(f"  Pasting image 3 (bottom-left) at position (0, {grid_cell_height})")
    combined_image.paste(img_set[2], (0, grid_cell_height))
    print(f"  Pasting image 4 (bottom-right) at position ({grid_cell_width}, {grid_cell_height})")
    combined_image.paste(img_set[3], (grid_cell_width, grid_cell_height))
    
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