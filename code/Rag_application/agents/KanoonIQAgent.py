import os
import re
from weasyprint import HTML
from agents.indian_kanon_api import IndianKanoon
from weasyprint import HTML
from pdf2image import pdfinfo_from_path, exceptions

cnt = 1

def sanitize_title(title):
    """
    Sanitizes document title for a valid filename.
    """
    sanitized_title = re.sub(r'[<>:"/\\|?*]', '', title)  # Remove invalid filename characters
    sanitized_title = re.sub(r'\s+', '_', sanitized_title)  # Replace spaces with underscores
    sanitized_title = re.sub(r'[^a-zA-Z0-9_\-]', '', sanitized_title)  # Remove non-alphanumeric characters (excluding _ and -)
    sanitized_title = re.sub(r'_{2,}', '_', sanitized_title)  # Replace multiple underscores with a single underscore
    sanitized_title = re.sub(r'\.', '', sanitized_title)  # Remove all periods
    sanitized_title = sanitized_title[:255]  # Truncate to 255 characters
    return sanitized_title


def clean_html_text(html_content):
    """
    Cleans and extracts text from HTML content.
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text


def validate_pdf(output_path):
    """
    Validates a PDF by checking if it can be processed by pdf2image.
    """
    try:
        pdfinfo_from_path(output_path)
        return True
    except exceptions.PDFPageCountError:
        print(f"PDF validation failed for {output_path}: Unable to get page count.")
        return False
    except Exception as e:
        print(f"Unexpected error validating PDF for {output_path}: {e}")
        return False

def toPDF(doc_content):
    """
    Converts document content to PDF and validates it.
    """
    if 'errmsg' in doc_content.keys():
        print(f"Error fetching document: {doc_content['errmsg']}")
        return None

    # Sanitize title for a valid filename
    sanitized_title = sanitize_title(doc_content['title'])
    output_path = f"./data/{sanitized_title}.pdf"

    try:
        # Extract and clean the content
        content = doc_content.get('doc', '')
        if not content.strip():  # Skip empty or invalid content
            print(f"Document {doc_content['title']} has no valid content.")
            return None

        html_text = clean_html_text(content)

        # Convert text to PDF
        HTML(string=html_text).write_pdf(output_path)

        # Validate the generated PDF
        if not validate_pdf(output_path):
            os.remove(output_path)  # Clean up invalid PDFs
            return None

    except Exception as e:
        print(f"Error creating PDF: {e}")
        return None

    return output_path


def KanoonIQAgent(user_query):
    """
    Fetch documents, convert them to PDFs, and store only valid ones.
    """
    ik = IndianKanoon()

    # Fetch documents from Indian Kanoon
    docs = ik.search(user_query)
    if('errmsg' in docs.keys()):
        print(f"Error fetching documents: {docs['errmsg']}")
        return
    else:
        docs = docs['docs']
        
    for doc in docs:
        docid = doc['tid']
        doc_content = ik.doc(docid)

        pdf_path = None

        if len(doc_content.get('doc', '')) <= 100000:
            # Generate and validate PDF for each document
            pdf_path = toPDF(doc_content)

        if pdf_path:
            print(f"Adding to DB: {pdf_path}")
            # Add your database logic here
        else:
            print(f"Skipping invalid document: {docid}")

# Test the function
# KanoonIQAgent("murder ANDD stabbing")

# dict_keys(['tid', 'catids', 'doctype', 'publishdate', 'authorid', 'bench', 'title', 'numcites', 'numcitedby', 'headline', 'fragment', 'docsource', 'author', 'authorEncoded', 'citation'])

# dict_keys(['tid', 'publishdate', 'title', 'doc', 'numcites', 'numcitedby', 'docsource', 'citetid', 'divtype', 'relatedqs', 'cats', 'courtcopy', 'query_alert', 'agreement']) 