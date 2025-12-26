import os

def is_text_file(file_path):
    """Check if a file is likely a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except (UnicodeDecodeError, IOError):
        return False

def parse_directory(output_file):
    """Walk through the directory and parse text files."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Walk through the directory
        for dirpath, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                
                # Only parse text files
                if is_text_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            # Write the file path and its content to the output file
                            outfile.write(f"File: {file_path}\n")
                            outfile.write(f"Contents:\n{content}\n")
                            outfile.write("-" * 80 + "\n")
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    # Specify the output file where the contents will be written
    output_file = 'superparser_output.txt'
    parse_directory(output_file)
    print(f"Parsing complete! Check the output in {output_file}")

