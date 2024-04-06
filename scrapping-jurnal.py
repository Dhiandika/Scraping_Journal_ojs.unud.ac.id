import os
import requests
from bs4 import BeautifulSoup
import threading

# Function to replace forbidden characters in a string


def replace_forbidden_chars(string):
    forbidden_chars = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", '"']
    for char in forbidden_chars:
        string = string.replace(char, "-")
    return string

# Function to extract the download URL from the <a> tag with class "download"


def extract_download_url(pdf_url):
    response = requests.get(pdf_url)
    soup = BeautifulSoup(response.content, "html.parser")
    download_url = None
    for a_tag in soup.find_all("a", class_="download", href=True):
        download_url = a_tag["href"]
        break  # Assuming there is only one download link
    return download_url

# Function to extract the URL of <a> tag with class "obj_galley_link pdf"


def extract_pdf_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    pdf_url = None
    for a_tag in soup.find_all("a", class_="obj_galley_link pdf", href=True):
        pdf_url = a_tag["href"]
        break  # Assuming there is only one PDF link
    return pdf_url

# Function to extract inner URLs and their titles within <div class="obj_article_summary"> tags


def extract_inner_urls_and_titles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    inner_urls_titles = []
    for div_tag in soup.find_all("div", class_="obj_article_summary"):
        a_tag = div_tag.find("a", href=True)
        if a_tag:
            inner_url = a_tag["href"]
            inner_title = a_tag.text.strip()
            inner_urls_titles.append((inner_url, inner_title))
    return inner_urls_titles

# Function to download the PDF file from the given download URL


def download_pdf(download_url, filename):
    response = requests.get(download_url)
    with open(filename, 'wb') as f:
        f.write(response.content)

# Function to handle PDF download for each article


def download_article_pdf(article, base_folder):
    article_folder = replace_forbidden_chars(article['title'])
    article_folder_path = os.path.join(base_folder, article_folder)
    if not os.path.exists(article_folder_path):
        os.makedirs(article_folder_path)

    print(f"Downloading PDFs for '{article['title']}'...")

    inner_urls_titles = extract_inner_urls_and_titles(article['url'])
    for inner_url, inner_title in inner_urls_titles:
        inner_title = replace_forbidden_chars(inner_title)
        pdf_url = extract_pdf_url(inner_url)
        if pdf_url:
            download_url = extract_download_url(pdf_url)
            if download_url:
                filename = f"{inner_title}.pdf"
                download_pdf(download_url, os.path.join(
                    article_folder_path, filename))
                print(f"Downloaded: {filename}")
            else:
                print(f"No download URL found for '{inner_title}'.")
        else:
            print(f"No PDF URL found for '{inner_title}'.")


# Fetch the webpage content
url = "PASTE THE LINK"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
title_tags = soup.find_all("a", class_="title")

# Extract URLs and titles
articles = []
for tag in title_tags:
    article = {
        "title": tag.text.strip(),
        "url": tag.get("href")
    }
    articles.append(article)

# Create a folder to store downloaded PDFs
base_folder = "downloaded_pdfs"
if not os.path.exists(base_folder):
    os.makedirs(base_folder)

# Download PDFs concurrently using threading
threads = []
for article in articles:
    thread = threading.Thread(
        target=download_article_pdf, args=(article, base_folder))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("All PDFs downloaded successfully.")
