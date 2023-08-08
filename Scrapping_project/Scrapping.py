# Import necessary libraries
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import codecs
import re
from webdriver_manager.chrome import ChromeDriverManager
import time
import os, shutil


def clearOutputDir(path):
    """
       Clear the output directory by removing all files and subdirectories.

       parameters:
           path (str): The path to the output directory to clear.
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)

    # Loop through all files and subdirectories in the output directory and delete them
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path) # Remove the file
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path) # Remove the subdirectory
        except Exception as e:
            # Print an error message if the file or subdirectory couldn't be deleted
            print('Failed to delete %s. Reason: %s' % (file_path, e))

#Print an information message with a 'INFO:' prefix.
def printInfoMessage(message):
    print(f'INFO: {message}')

#Print an information message with a 'WARN:' prefix.
def printWarnMessage(message):
    print(f'WARN: {message}')

#Print an information message with a 'ERROR:' prefix.
def printErrorMessage(message):
    print(f'ERROR: {message}')


def fetchHTMLContent(url):
    """
        Fetch the HTML content from a given URL using Selenium.

        parameters:
            url (str): The URL to fetch.

        Returns:
            str: The HTML content of the URL
    """
    response = None
    printInfoMessage(f'Started fetching html content from {url}, total three attempts will be made after that please re-run the script')
    # Try to fetch the HTML content three times
    for attempt in range(0, 3):

        try:
            # Setting up Chrome driver and wait time
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) #
            wait = WebDriverWait(driver, 20)
            # Opening the URL in Chrome browser
            driver.get(url)
            # Getting the current URL and waiting for the page to fully load
            get_url = driver.current_url
            wait.until(EC.url_to_be(url))

            # If the URL matches the original URL, get the HTML content and break the loop
            if get_url == url:
                response = driver.page_source
                printInfoMessage(f'Finished fetching html content from {url}')
                break

        # If something goes wrong, print a warning message and sleep for 5 seconds before trying again
        except Exception as ex:
            printWarnMessage(f'Something went wrong while contacting server attempt: {attempt}, Sleeping for 5 seconds')
            time.sleep(5)

    return response


def beautifyHTML(page, content):
    """
        Parse and beautify the HTML content.

        parameters:
            page (str): The file path to the HTML page to parse and beautify
            content (str): The HTML content to parse and beautify

        Returns:
            BeautifulSoup object: The parsed and beautified HTML content.
    """
    response = None

    # If a file path is provided, open the file and parse the HTML content
    if page is not None:
        with open(page, encoding='utf8') as fp:
            response = BeautifulSoup(fp, "html.parser")
    # If 'content' is provided, parse the HTML content directly
    else:
        response = BeautifulSoup(content, "html.parser")

    return response

def saveWebPage(content, path):
    """
       Saves the HTML content to a file.

       parameters:
           content (str): The HTML content to save.
           path (str): The file path where the HTML content should be saved.
    """
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

def extractSingleHTMLSection(bs, section, attributes):
    """
        Extracts a single section of HTML content from a BeautifulSoup object.

        parameters:
            bs (BeautifulSoup object): The BeautifulSoup object containing the HTML content.
            section (str): The HTML tag of the section to extract (e.g., 'div', 'table', etc.).
            attributes (dict): A dictionary of attributes and values that the section should have.

        Returns:
            BeautifulSoup object or None: The BeautifulSoup object representing the extracted section of HTML content.
    """
    if attributes != None:
        return bs.find(section, attributes)
    else:
        return bs.find(section)

def extractMultipleHTMLSection(bs, section, attributes):
    """
        Extracts multiple sections of HTML content from a BeautifulSoup object.

        parameters:
            bs (BeautifulSoup object): The BeautifulSoup object containing the HTML content.
            section (str): The HTML tag of the sections to extract (e.g., 'div', 'table', etc.).
            attributes (dict): A dictionary of attributes and values that the sections should have.

        Returns:
            list: A list of BeautifulSoup objects representing the extracted sections of HTML content.
    """
    if attributes != None:
        return bs.find_all(section, attributes)
    else:
        return bs.find_all(section)


def fetchNextPageDetails(content):
    """
        Extracts the next page URL from the HTML content.

        parameters:
        content: str, the HTML content.

        Returns:
        str: The URL of the next page.
    """
    # Initialize response to None
    response = None

    # Beautify the HTML content using BeautifulSoup
    bs = beautifyHTML(None, content)

    pagination = extractSingleHTMLSection(bs, 'div', {'class': 'pagination'})   # Extract the pagination section from the HTML content
    nextPage = extractSingleHTMLSection(pagination, 'a', {'class': 'next'})  # Extract the next page link from the pagination section
    response = nextPage['href'] if nextPage is not None else None  # If the next page link is found, set it as the response

    return response


def fetchAllPages(absoluteUrl, relativeUrl, outputDir):
    """
    Fetches and saves all HTML pages of a website by following links to subsequent pages until no more pages are available.

    Parameters:
    absoluteUrl (str): The absolute URL of the website.
    relativeUrl (str): The relative URL of the first page to fetch.
    outputDir (str): The directory where the HTML files will be saved.

    Returns:
    response (list): A list of file paths for the saved HTML files.

    Raises:
    Exception: If unable to fetch HTML content from the website.
    """
    response = []  # initialize an empty list to store file paths of saved HTML files

    try:
        isNextPageAvailable = True  # flag to determine if there are more pages to fetch
        pageIndex = 1  # counter to keep track of the current page being fetched

        # print a message indicating that the process has started
        printInfoMessage('Started fetching content')

        while isNextPageAvailable:
            content = fetchHTMLContent(f'{absoluteUrl}{relativeUrl}')  # fetch HTML content from the website using the provided URLs

            if content is None:
                # if the content is not retrieved, raise an exception
                raise Exception(f'Unable to fetch HTML content from {absoluteUrl}{relativeUrl}')

            filePath = f'{outputDir}{pageIndex}.html'  # create a file path for the HTML file to be saved
            saveWebPage(content, filePath)  # save the HTML content to a file at the specified file path
            relativeUrl = fetchNextPageDetails(content)  # get the URL for the next page to be fetched
            response.append(filePath)  # add the file path to the response list
            pageIndex += 1  # increment the page counter

            # set the flag to False if there are no more pages to fetch
            isNextPageAvailable = True if relativeUrl is not None else False

        # print a message indicating that the process has completed successfully
        printInfoMessage('Finished fetching content')

    # If an exception was raised then set the response to None and raise Error message
    except Exception as ex:
        response = None
        printErrorMessage(f'Process failed due to Reason: {ex}, please re-run entire script')

    return response


def extractContentFromPages(pages):
    """
       This function extracts product details from multiple HTML pages and returns a dictionary of product information.
       Each product's information is stored in a separate dictionary with keys: 'href', 'name', 'dPrice', 'oPrice', 'rating',
       and 'review'.

       Parameters:
       pages (list): A list of HTML pages to extract product details from.

       Returns:
       dict: A dictionary containing all product details extracted from the input HTML pages.
    """
    response = {}

    try:
        productIndex = 1

        # Loop through each HTML page in the input list
        for page in pages:

            # Beautify the HTML and extract all product details sections
            bs = beautifyHTML(page, None)
            products = extractMultipleHTMLSection(bs, 'div', {'class': 'product-details'})

            # Loop through each product details section and extract relevant information
            for prd in products:
                prdTitle = extractSingleHTMLSection(prd, 'div', {'class': 'product-title'})
                prdH4 = extractSingleHTMLSection(prdTitle, 'h4', None)
                prdAnchor = extractSingleHTMLSection(prdH4, 'a', None)
                prdPrice = extractSingleHTMLSection(prd, 'span', {'class': 'money'})
                prdStars = extractSingleHTMLSection(prd, 'span', {'class': 'sr-only'})
                prdReviews = extractSingleHTMLSection(prd, 'a', {'class': 'text-m'})
                prdDel = extractSingleHTMLSection(prd, 'del', None)
                prdOriginalPrice = extractSingleHTMLSection(prdDel, 'span',{'class': 'money'}) if prdDel is not None else None

                # Extract relevant data from each section and add to the response dictionary
                href = prdAnchor['href'] if prdAnchor is not None else None
                name = prdAnchor.text if prdAnchor is not None else 'No Name'
                dPrice = prdPrice.text if prdPrice is not None else '$0.00 USD'
                oPrice = prdOriginalPrice.text if prdOriginalPrice is not None else dPrice
                dPrice = '$0.00 USD' if prdOriginalPrice is None else dPrice
                rating = prdStars.text if prdStars is not None else '0.0 star rating'
                review = prdReviews.text if prdReviews is not None else '0 Reviews'

                response[productIndex] = {'href': href, 'name': name, 'dPrice': dPrice, 'oPrice': oPrice,
                                          'rating': rating, 'review': review}
                productIndex += 1

    # If an exception was raised then set the response to None and raise Error message
    except Exception as ex:
        response = None
        printErrorMessage(f'Process failed due to Reason: {ex}, please re-run function extractContentFromPages')

    return response



def generateProductDetails(details, outputDir):
    """
    Generate a CSV file from a dictionary of product details and save it in the specified output directory.

    Parameters:
        details (dict): Dictionary of product details
        outputDir (str): Output directory to save the generated CSV file

    Returns:
        None
    """

    # Convert dictionary to DataFrame
    df = pd.DataFrame(details.values())

    # Clean up some columns by removing non-numeric and non-decimal characters
    for col in ['dPrice', 'oPrice', 'rating', 'review']:
        df[col] = df[col].str.replace('[^.0-9_]', '', regex=True).str.strip()

    # Rename columns for better readability
    df = df.rename(
        columns={'href': 'URL', 'name': 'Name', 'dPrice': 'Disc-Price', 'oPrice': 'Original-Price', 'rating': 'Star',
                 'review': 'Total-Review'})

    # Export the DataFrame as a CSV file in the specified output directory
    filePath = f'{outputDir}ProductDetails.csv'
    df.to_csv(filePath, index=False)
    printInfoMessage(f'File exported successfully... at {filePath}')



def fetchAllProductInformation(urls, absoluteUrl, outputDir):
    """
        Fetches the HTML content of all the provided URLs and saves them as HTML files in the given output directory.

        Parameters:
        urls (list): A list of relative URLs to fetch HTML content from.
        absoluteUrl (str): The absolute base URL from which the relative URLs will be appended to.
        outputDir (str): The directory path to save the fetched HTML files in.

        Returns:
        list: A list of file paths of the saved HTML files.
    """
    response = []

    pageIndex = 1 # start the page index at 1

    try:
        # iterate through each URL in the list of URLs and fetch the HTML content of the current URL
        for url in urls:
            content = fetchHTMLContent(f'{absoluteUrl}{url}')

            # if content was not successfully fetched then raise error message
            if content is None:
                raise Exception(f'Unable to fetch HTML content from {absoluteUrl}{relativeUrl}')


            filePath = f'{outputDir}P-{pageIndex}.html' # create a file path for the current web page
            saveWebPage(content, filePath) # save the web page content to a file
            response.append(filePath) # add the file path to the list of responses
            pageIndex += 1 # increment the page index

    # if an exception was raised then set the response to None and raise Error message
    except Exception as ex:
        response = None
        printErrorMessage(f'Process failed due to Reason: {ex}, please re-run function fetchAllProductInformation')

    return response



def extractProductInformation(pages):
    """
      Extracts product information from a list of HTML pages.

      Parameters:
      - pages (list): A list of HTML pages as strings.

      Returns:
        - response (dict): A dictionary containing the extracted product information for each page.
    """
    response = {}

    try:
        # Initialize product index
        productIndex = 1

        # Loop through HTML pages
        for page in pages:
            try:
                # Beautify HTML and extract relevant sections
                bs = beautifyHTML(page, None)
                description = extractSingleHTMLSection(bs, 'div', {'id': 'description'})
                specification = extractSingleHTMLSection(bs, 'div', {'id': 'description-1'})
                reviews = extractSingleHTMLSection(bs, 'div', {'class': 'yotpo-reviews yotpo-active'})
                allReview = extractMultipleHTMLSection(reviews, 'div', {'class': 'content-review'})

                # Extract text from relevant sections
                desc = ''
                for li in description.find('ul').find_all('li'):
                    desc = desc + li.text

                spec = ''
                for li in specification.find('ul').find_all('li'):
                    spec = spec + li.text

                rev = ''
                for review in allReview:
                    rev = rev + review.text

                # Add extracted information to response dictionary
                response[productIndex] = {'Description': desc, 'Specification': spec, 'Review': rev}
                productIndex += 1
            except Exception as ex:
                # If there is an error parsing the page, print a message and continue to the next page
                print(f'Failed to parse {page}')

    # if an exception was raised then set the response to None and raise Error message
    except Exception as ex:
        response = None
        printErrorMessage(f'Process failed due to Reason: {ex}, please re-run function extractProductInformation')

    return response


def generateProductInformationFile(prodInfo, outputDir):
    """
        Converts a dictionary of product information to a pandas DataFrame, and exports it to a CSV file.

        Parameters:
        - prodInfo (dict): A dictionary containing the product information, as generated by the `extractProductInformation` function.
        - outputDir (str): A string specifying the directory where the output CSV file should be saved.

        Returns:
        - None
    """
    # Convert product information dictionary to pandas DataFrame
    df = pd.DataFrame(prodInfo.values())

    # Define file path and name for the output CSV file
    filePath = f'{outputDir}ProductDeSpRe.csv'

    # Export DataFrame to CSV file without index column
    df.to_csv(filePath, index=False)

    # Print success message with file path
    printInfoMessage(f'File exported successfully... at {filePath}')

# Clear the output directory
clearOutputDir('Output')

# Define the main URL and URL for scraping
absoluteUrl = 'https://vapordna.com'
relativeUrl = '/collections/disposable-vaporizers'

#Set the output directory
outputDir = 'Output/'

#Fetch all pages
allPages = fetchAllPages(absoluteUrl, relativeUrl, outputDir)  #

#Extract product details from the pages
prdDetails = extractContentFromPages(allPages)

#Generate a CSV file containing product details
generateProductDetails(prdDetails, 'Output/')

#Read the product details CSV file
df = pd.read_csv('Output/ProductDetails.csv')

#Fetch all product information from the product URLs
prods = fetchAllProductInformation(list(df['URL']), absoluteUrl, outputDir)

#Extract product information from the pages
productInfos = extractProductInformation(prods)

#Generate a CSV file containing product information
generateProductInformationFile(productInfos, outputDir)




