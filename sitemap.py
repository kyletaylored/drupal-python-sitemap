import sys, os, requests, yaml
from bs4 import BeautifulSoup
from tqdm import tqdm
import xml.etree.ElementTree as ET

# Parse for node type
def parse_url_for_node_type(body):
    if body.has_attr('class'):
        for elem in (body.attrs['class']):
            if 'node-type-' in elem:
                str(elem)
                return elem[10:]

# Parse for page type
def parse_url_for_page_type(body):
    if body.has_attr('class'):
        for elem in (body.attrs['class']):
            if 'page-' in elem:
                str(elem)
                return elem[5:]           

def main():
    try:
        # Open sitemap, loop through
        print("Enter path to sitemap.xml (i.e. http://example.com/sitemap.xml)")
        sitemap = input("(press enter to use ./sitemap.xml): \n\n")

        if not sitemap:
            sitemap = 'sitemap.xml'
        
        # Check for interwebs
        if sitemap[:4] == 'http':
            xml = requests.get(sitemap)
            file = xml.text
        elif os.path.isfile(sitemap):
            with open(sitemap, 'r') as content_file:
                file = content_file.read()
        else:
            raise Exception("No file exists.")
                    
        # Parse XML with BS
        s = BeautifulSoup(file, 'html.parser')
        surls = s.findAll('url')
        xurls = []
        for url in surls:
            loc = url.find('loc').string
            xurls.append(loc)

        # Throw error if missing.
        if not xurls:
            raise Exception("No URLs to cycle.")

        pages = {}
        types = {}
        count = 0

        for u in tqdm(xurls):
            # For debugging
            # count = count + 1
            # if count == 25:
            #     break

            # Cast to string, strip newline (it happens)
            str(u)
            u = u.rstrip()
            
            # fetch page, get soup
            page = requests.get(u)
            soup = BeautifulSoup(page.text, 'html.parser')
            body = soup.find('body')
            
            # get class, update counters
            if body:
                t = parse_url_for_node_type(body)
                p = parse_url_for_page_type(body)

                # Count types
                if t in types:
                    count = types[t]['count'] + 1
                    tObj = {'count': count}
                    types[t].update(tObj)
                else:
                    tObj = {t: {'count': 1}}
                    types.update(tObj)
                
                # Capture URL
                if 'urls' in types[t]:
                    url_list = types[t]['urls']
                    url_list.append(u)
                    types[t]['urls'] = url_list
                else:
                    url_list = [u]
                    types[t]['urls'] = url_list

                # Store page type with node type.
                types[t]['page'] = "null" if not p else p

        # Output to screen, save to file.
        if types:
            with open('sitemap.yml', 'w') as outfile:
                yaml.dump(types, outfile, default_flow_style=False)
        return 0

    except Exception as e:
        print(e)
        return 1

# Run main
if __name__ == '__main__':
    sys.exit(main())
