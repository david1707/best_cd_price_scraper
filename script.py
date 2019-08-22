from bs4 import BeautifulSoup
import requests
import lxml

import pandas as pd


# Grab user's band and sanitaze it
band_name = input('Please, enter a band name:\n').strip()
formated_band_name = band_name.replace(' ', '+')
print(f'Searching {band_name}. Wait, please...')

# Set intiial URLS
base_url = 'http://www.best-cd-price.co.uk'
search_url = f'http://www.best-cd-price.co.uk/search-Keywords/1-/229816/{formated_band_name}.html'

data = {
    'Image': [],
    'Name': [],
    'URL': [],
    'Artist': [],
    'Binding': [],
    'Format': [],
    'Release Date': [],
    'Label': [],
}

def export_and_print(data=[]):
    table = pd.DataFrame(data, columns=[
                         'Image', 'Name', 'URL', 'Artist', 'Binding', 'Format', 'Release Date', 'Label'])
    table.index = table.index + 1
    clean_band_name = band_name.lower().replace(' ', '_')
    table.to_csv(f'{clean_band_name}_albums.csv',
                 sep=',', encoding='utf-8', index=False)
    print('Scraping done. Here are the results:')
    print(table)


def get_cd_attributes(cd):
        # Getting the CD attributes
    image = cd.find('img', class_='ProductImage')['src']

    name = cd.find('h2')
    name = name.find('a').text if name else ''

    url = cd.find('h2').find('a')['href']
    url = base_url + url

    artist = cd.find('li', class_="Artist")
    artist = artist.find('a').text if artist else ''

    binding = cd.find('li', class_="Binding")
    binding = binding.text.replace('Binding: ', '') if binding else ''

    format_album = cd.find('li', class_="Format")
    format_album = format_album.text.replace(
        'Format: ', '') if format_album else ''

    release_date = cd.find('li', class_="ReleaseDate")
    release_date = release_date.text.replace(
        'Released: ', '') if release_date else ''

    label = cd.find('li', class_="Label")
    label = label.find('a').text if label else ''

    # Add attributes to 'data' object
    data['Image'].append(image if image else '')
    data['Name'].append(name if name else '')
    data['URL'].append(url if url else '')
    data['Artist'].append(artist if artist else '')
    data['Binding'].append(binding if binding else '')
    data['Format'].append(format_album if format_album else '')
    data['Release Date'].append(release_date if release_date else '')
    data['Label'].append(label if label else '')


def parse_url(url):
    # HTTP GET requests
    page = requests.get(url)

    # Checking if we fetched the URL
    if page.status_code == requests.codes.ok:

        bs = BeautifulSoup(page.text, 'lxml')

        check_no_results = bs.find('ul', class_="SearchResults").find('p')
        if check_no_results and check_no_results.text:
            print('Search returned no results.')
            return None

        # Fetching all items
        list_all_cd = bs.findAll('li', class_='ResultItem')

        for cd in list_all_cd:
            get_cd_attributes(cd)

        # Fetching the next page or finishing the script
        next_page_text = bs.find(
            'ul', class_="SearchBreadcrumbs").findAll('li')[-1].text

        # If there's a 'Next' page, navigate towards it
        if next_page_text == 'Next':
            next_page_parcial = bs.find('ul', class_="SearchBreadcrumbs").findAll(
                'li')[-1].find('a')['href']
            next_page_url = base_url + next_page_parcial
            parse_url(next_page_url)
        # No more 'Next' pages, finish the script
        else:
            export_and_print(data)


parse_url(search_url)
