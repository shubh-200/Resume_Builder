from pdf2image import convert_from_path
import os
import re
import time
import json
import base64
import platform
import subprocess
import streamlit as st
import streamlit.components.v1 as components
from fpdf import FPDF
from pathlib import Path
from datetime import datetime
from langchain_core.output_parsers import JsonOutputParser
# from pylatex import Document
# from pylatex.utils import NoEscape
from rem_build.templates.pdf_gen import pdf_generator_vroom
import shutil

OS_SYSTEM = platform.system().lower()


def write_file(file_path, data):
    with open(file_path, "w") as file:
        file.write(data)


def read_file(file_path, mode="r"):
    with open(file_path, mode) as file:
        file_contents = file.read()
    return file_contents


def write_json(file_path, data):
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)


def read_json(file_path: str):
    with open(file_path) as json_file:
        return json.load(json_file)


def job_doc_name(job_details: dict, output_dir: str = "output", type: str = ""):
    company_name = clean_string(job_details["company_name"])
    job_title = clean_string(job_details["job_title"])[:15]
    doc_name = "_".join([company_name, job_title])
    doc_dir = os.path.join(output_dir, company_name)
    os.makedirs(doc_dir, exist_ok=True)

    if type == "jd":
        return os.path.join(doc_dir, f"{doc_name}_JD.json")
    elif type == "resume":
        return os.path.join(doc_dir, f"{doc_name}_resume.json")
    elif type == "cv":
        return os.path.join(doc_dir, f"{doc_name}_cv.txt")
    else:
        return os.path.join(doc_dir, f"{doc_name}_")


def clean_string(text: str):
    text = text.title().replace(" ", "").strip()
    text = re.sub(r"[^a-zA-Z0-9]+", "", text)
    return text


def open_file(file: str):
    if OS_SYSTEM == "darwin":  # macOS
        os.system(f"open {file}")
    elif OS_SYSTEM == "linux":
        try:
            os.system(f"xdg-open {file}")
        except FileNotFoundError:
            print("Error: xdg-open command not found. Please install xdg-utils.")
    elif OS_SYSTEM == "windows":
        try:
            os.startfile(file)
        except AttributeError:
            print("Error: os.startfile is not available on this platform.")
    else:
        # Default fallback for other systems
        try:
            os.system(f"xdg-open {file}")
        except FileNotFoundError:
            print(f"Error: xdg-open command not found. Please install xdg-utils. Alternatively, open the file manually.")


def save_log(content: any, file_name: str):
    timestamp = int(datetime.timestamp(datetime.now()))
    file_path = f"logs/{file_name}_{timestamp}.txt"
    write_file(file_path, content)


def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        func_run_log = f"Function {func.__name__} took {
            execution_time:.4f} seconds to execute"
        print(func_run_log)
        # if 'is_st' in kwargs and kwargs['is_st']:
        #     st.write(func_run_log)

        return result

    return wrapper


def text_to_pdf(text: str, file_path: str):
    """Converts the given text to a PDF and saves it to the specified file path.

    Args:
        text (str): The text to be converted to PDF.
        file_path (str): The file path where the PDF will be saved.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Encode the text explicitly using 'latin-1' encoding
    encoded_text = text.encode('utf-8').decode('latin-1')
    pdf.multi_cell(0, 5, txt=encoded_text)
    pdf.output(file_path)
    # try:
    #     open_file(file_path)
    # except Exception as e:
    #     print("Unable to open the PDF file.")


def download_pdf(pdf_path: str):
    bytes_data = read_file(pdf_path, "rb")
    base64_pdf = base64.b64encode(bytes_data).decode('utf-8')

    dl_link = f"""
    <html>
    <head>
    <title>Start Auto Download file</title>
    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script>
    $('<a href="data:application/pdf;base64,{base64_pdf}" download="{os.path.basename(pdf_path)}">')[0].click().remove();
    </script>
    </head>
    </html>
    """
    components.html(
        dl_link,
        height=0,
    )
    # with open(pdf_path, "rb") as f:
    #     pdf_bytes = f.read()

    # st.download_button(label="Download Resume ⬇",
    #                     data=pdf_bytes,
    #                     file_name=os.path.basename(pdf_path),
    #                     mime="application/pdf")
    # pass


def display_pdf(file, type="pdf"):
    if type == 'image':
        # Store Pdf with convert_from_path function
        pages = convert_from_path(file, poppler_path='poppler-24.07.0/Library/bin')
        for page in pages:
            st.image(page, use_column_width=True)

    if type == "pdf":
        # Read file as bytes:
        bytes_data = read_file(file, "rb")

        # Convert to utf-8
        try:
            base64_pdf = base64.b64encode(bytes_data).decode('utf-8')
        except Exception as e:
            base64_pdf = base64.b64encode(bytes_data)

        # Iframe Embedding of PDF in HTML
        pdf_display = F'<iframe src="data:application/pdf;base64,{
            base64_pdf}" type="application/pdf" style="width:100%; height:100vh;"></iframe>'

        # # Embedding PDF in HTML
        # pdf_display =  f"""<embed
        # class="pdfobject"
        # type="application/pdf"
        # title="Embedded PDF"
        # src="data:application/pdf;base64,{base64_pdf}"
        # style="overflow: auto; width: 100%; height: 100vh">"""

        # Display file
        st.markdown(pdf_display, unsafe_allow_html=True)


def convert_backslash_to_forward_slash(path):
    return path.replace("\\", "/")


def save_latex_as_pdf(tex_file_path: str, dst_path: str):
    # try:
    tex_file_path = convert_backslash_to_forward_slash(tex_file_path)
    output_pdf_path = convert_backslash_to_forward_slash(dst_path)
    destination_folder = os.path.dirname(output_pdf_path)

    pdf_generator_vroom(tex_file_path=tex_file_path,
                        output_dir=destination_folder,
                        # custom_output=output_pdf_path
                        )
    # os.system(f'pdflatex {tex_file_path}')

    # os.system('del main')

    #     # Ensure the directories exist
    #     if not os.path.exists(tex_file_path):
    #         raise FileNotFoundError(
    #             f"The .tex file was not found: {tex_file_path}")

    #     if not os.path.exists(destination_folder):
    #         os.makedirs(destination_folder)

    #     # Call pdflatex to convert LaTeX to PDF
    #     prev_loc = os.getcwd()
    #     print(f"Text File Path: {tex_file_path} \n")
    #     print(f"Dest File Path: {dst_path} \n")
    #     print(f"Dest Dir Path: {destination_folder} \n")
    #     os.chdir(os.path.dirname(tex_file_path))

    #     result = subprocess.run(
    #         ["pdflatex", "-output-directory", destination_folder, tex_file_path],
    #         # stdout=subprocess.PIPE,
    #         # stderr=subprocess.PIPE,
    #         capture_output=True,
    #         text=True  # Ensure the output is captured as text, not bytes
    #     )

    #     # Print the stdout and stderr to check for LaTeX errors or warnings
    #     print("STDOUT:", result.stdout)
    #     print("STDERR:", result.stderr)

    #     if result.returncode != 0:
    #         print("LaTeX compilation failed with return code:", result.returncode)

    #     os.chdir(prev_loc)
    #     resulted_pdf_path = tex_file_path.replace(".tex", ".pdf")
    #     dst_tex_path = output_pdf_path.replace(".pdf", ".tex")

    #     os.rename(resulted_pdf_path, output_pdf_path)
    #     os.rename(tex_file_path, dst_tex_path)

    #     if result.returncode != 0:
    #         print("Exit-code not 0, check result!")
    #     try:
    #         pass
    #         # open_file(dst_path)
    #     except Exception as e:
    #         print("Unable to open the PDF file.")
    #         st.write("Unable to open the PDF file.")

    #     filename_without_ext = os.path.basename(tex_file_path).split(".")[0]
    #     unnessary_files = [
    #         file
    #         for file in os.listdir(os.path.dirname(os.path.realpath(tex_file_path)))
    #         if file.startswith(filename_without_ext)
    #     ]

    #     for file in unnessary_files:
    #         file_path = os.path.join(os.path.dirname(tex_file_path), file)
    #         if os.path.exists(file_path):
    #             os.remove(file_path)
    # except Exception as e:
    #     print(e)
    #     return None


def get_default_download_folder():
    """Get the default download folder for the current operating system."""
    downlaod_folder_path = os.path.join(
        str(Path.home()), "Downloads", "JobLLM_Resume_CV")
    print(f"downlaod_folder_path: {downlaod_folder_path}")
    os.makedirs(downlaod_folder_path, exist_ok=True)
    return downlaod_folder_path


def parse_json_markdown(json_string: str) -> dict:
    try:
        # Try to find JSON string within first and last triple backticks
        if json_string[3:13].lower() == "typescript":
            json_string = json_string.replace(json_string[3:13], "", 1)

        if 'JSON_OUTPUT_ACCORDING_TO_RESUME_DATA_SCHEMA' in json_string:
            json_string = json_string.replace(
                "JSON_OUTPUT_ACCORDING_TO_RESUME_DATA_SCHEMA", "", 1)

        if json_string[3:7].lower() == "json":
            json_string = json_string.replace(json_string[3:7], "", 1)

        parser = JsonOutputParser()
        parsed = parser.parse(json_string)

        return parsed
    except Exception as e:
        print(e)
        return None


def get_prompt(system_prompt_path: str) -> str:
    """
    Reads the content of the file at the given system_prompt_path and returns it as a string.

    Args:
        system_prompt_path (str): The path to the system prompt file.

    Returns:
        str: The content of the file as a string.
    """
    with open(system_prompt_path, encoding="utf-8") as file:
        return file.read().strip() + "\n"


def key_value_chunking(data, prefix=""):
    """Chunk a dictionary or list into key-value pairs.

    Args:
        data (dict or list): The data to chunk.
        prefix (str, optional): The prefix to use for the keys. Defaults to "".

    Returns:
        A list of strings representing the chunked key-value pairs.
    """
    chunks = []

    def stop_needed(value): return '.' if not isinstance(
        value, (str, int, float, bool, list)) else ''

    if isinstance(data, dict):
        for key, value in data.items():
            if value is not None:
                chunks.extend(key_value_chunking(value, prefix=f"{
                              prefix}{key}{stop_needed(value)}"))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            if value is not None:
                chunks.extend(key_value_chunking(value, prefix=f"{
                              prefix}_{index}{stop_needed(value)}"))
    else:
        if data is not None:
            chunks.append(f"{prefix}: {data}")

    return chunks
