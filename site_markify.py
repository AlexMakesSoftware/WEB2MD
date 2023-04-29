import os
import sys
import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urlparse, urljoin

if len(sys.argv) != 2:
    print("Usage: python script_name.py [url]")
    sys.exit(1)

# Define a function to recursively download pages on the site
def download_page(url):
    # Parse the URL to get the domain and path
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    #ignore feeds and xml files
    if "feed" in path or "xml" in path or "rss" in path:
        return
    
    page_name = path   
    print(path)

    # If the path ends with a filename extension, remove it to get the page name
    if ".html" in page_name or ".htm" in page_name:        
        page_name = path.split("/")[-1].split(".")[0]    

    #If it starts with a slash, remove it
    if page_name.startswith('/'):
        page_name = page_name[1:]
    
    #Remove trailing slashes
    if page_name.endswith('/'):
        page_name = page_name[:-1]    

    #Any remaining pages, replace slashes with underscores
    page_name = page_name.replace('/', '_')

    print("Processing page: "+page_name)

    # Download the page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    preservedCopy = soup

    # Download all images referenced in this page to the images folder.
    for img in soup.find_all('img'):

        #if the image contains a srcset attribute, then it's a responsive image, so set the src to the largest image in the srcset
        if 'srcset' in img.attrs:
            #split on the commas to get the different immages in the srcset
            images = img['srcset'].split(',')
            
            #go through the list to find the biggest
            selectedUrl = ''
            selectedSize = 0
            for image in images:
                #split on the spaces to get the url and the size
                image = image.strip().split(' ')

                #if image contains more than one element...
                if len(image) > 1:
                    #if the size is bigger than the currently selected one, then select it
                    if int(image[1].replace('w', '')) > selectedSize:
                        selectedUrl = image[0]
                        selectedSize = int(image[1].replace('w', ''))
            #set the src to the selected image
            img['src'] = selectedUrl

        # Resolve absolute urls to relative ones.
        img_url = urljoin(url, img['src'])
        img_name = img_url.split('/')[-1]

        # Point it to the download folder.
        img_path = os.path.join('downloaded', 'images', img_name)

        # Download the image if it doesn't already exist
        if not os.path.exists(img_path):
            img_data = requests.get(img_url).content
            with open(img_path, 'wb') as handler:
                handler.write(img_data)

        img_path = img_path.replace('\\', '/')
        img_path = "/" + img_path
        img['src'] = img_path

    # Replace all anchor links that are internal to this domain with relative addresses instead.
    for a in soup.find_all('a'):
        if a.has_attr('href'):
            if a['href'].startswith('http'):
                if domain in a['href']:
                    a['href'] = a['href'].split(domain)[-1]
            else:
                a['href'] = a['href']

    # Convert the HTML to Markdown
    h = html2text.HTML2Text()
    h.wrap_links = False

    markdown = h.handle(str(soup))

    # Special case: misuse of italic tag. Replace all instances of '__' with ''
    markdown = markdown.replace('__', '')

    # Save it.
    page_path = os.path.join('downloaded', page_name + '.md')
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    # Recursively download all internal links on the page
    for link in preservedCopy.find_all('a'):
        if link.img:
            continue        
        if link.has_attr('href'):            
            href = link['href']

            #print("Processing "+ href)   
            if not "#" in href:
                link_url = urljoin(url, href)                
                link_parsed = urlparse(link_url)                
                
                if not link_parsed.netloc in domain:
                    #skip external links
                    continue

                if link_parsed.path not in visited:
                    visited.add(link_parsed.path)                    
                    download_page(link_url)


#Create downloaded/images/ folders if they don't exist
if not os.path.exists('downloaded'):
    os.mkdir('downloaded')
if not os.path.exists('downloaded/images'):
    os.mkdir('downloaded/images')    

# Start with the homepage and visit all internal links on the site
url = sys.argv[1]
visited = set()
visited.add(urlparse(url).path)
print("Added to visited: ", urlparse(url).path)
download_page(url)
