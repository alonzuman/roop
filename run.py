#!/usr/bin/env python3

import sys
import os
import tempfile
import shutil
from roop.core import run

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python run.py --faces <source_face1> [source_face2 ...] --target <target_image> [output_path]")
        print("\nArguments:")
        print("  --faces: One or more source face images in the order you want them mapped to faces in target")
        print("  --target: Path to the image containing faces you want to replace")
        print("  output_path: (Optional) Path for the output image. If not provided, will append '_swapped' to target name")
        print("\nExample:")
        print("  # Replace first face with face1.jpg and second face with face2.jpg:")
        print("  python run.py --faces face1.jpg face2.jpg --target group_photo.jpg")
        sys.exit(1)

    # Parse arguments
    args = sys.argv[1:]
    if '--faces' not in args or '--target' not in args:
        print("Error: Both --faces and --target arguments are required")
        sys.exit(1)

    # Get faces and target
    faces_index = args.index('--faces')
    target_index = args.index('--target')
    
    # Extract source faces
    if target_index > faces_index:
        source_faces = args[faces_index + 1:target_index]
    else:
        source_faces = args[faces_index + 1:]
    
    if not source_faces:
        print("Error: At least one source face is required")
        sys.exit(1)

    # Get target path
    if target_index == len(args) - 1:
        print("Error: Target image path is required after --target")
        sys.exit(1)
    target_path = args[target_index + 1]

    # Handle output path - it would be the last argument if not part of --faces or after --target
    remaining_args = args[target_index + 2:]
    if remaining_args and not remaining_args[0].startswith('--'):
        output_path = remaining_args[0]
    else:
        base, ext = os.path.splitext(target_path)
        output_path = f"{base}_swapped{ext}"

    # Create a temporary directory for intermediate results
    with tempfile.TemporaryDirectory() as temp_dir:
        current_target = target_path
        
        for i, source_face in enumerate(source_faces):
            # Create temporary output path for this iteration
            temp_output = os.path.join(temp_dir, f"temp_output_{i}{os.path.splitext(target_path)[1]}")
            
            # Set up command line arguments for each iteration
            sys.argv = [
                sys.argv[0],
                '--source', source_face,
                '--target', current_target,
                '--output', temp_output,
                '--reference-face-position', str(i),  # Select the next face in sequence
            ]

            # Run the face swap
            run()
            
            # Update current target for next iteration
            current_target = temp_output

        # Copy the final result to the output path
        shutil.copy2(current_target, output_path)
