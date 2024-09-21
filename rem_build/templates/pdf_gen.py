import os


def convert_to_utf8(input_file, output_file):
    # Convert Windows-1252 encoded file to UTF-8
    with open(input_file, 'r', encoding='windows-1252') as f:
        content = f.read()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(
        f"File '{input_file}' converted to UTF-8 and saved as '{output_file}'.")

def get_filename_without_extension(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


def pdf_generator_vroom(tex_file_path, output_dir):
    file_name = get_filename_without_extension(tex_file_path)
    # custom_pdf_name = "custom_output"

    # Define the UTF-8 output file path
    utf8_tex_file = "utf8_" + file_name

    # Convert the original .tex file to UTF-8 if it's not already in UTF-8
    convert_to_utf8(tex_file_path, utf8_tex_file)

    command = "pdflatex --shell-escape -jobname=" + file_name + \
        " -output-directory=" + output_dir + " " + utf8_tex_file

    print(command)
    if os.path.exists(utf8_tex_file):
        os.system(command)
    else:
        print(utf8_tex_file + " does not exist.")

    # Optional: Uncomment if you need to delete the UTF-8 converted file afterward
    # os.remove(utf8_tex_file)
