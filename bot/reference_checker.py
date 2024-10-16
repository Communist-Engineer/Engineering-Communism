import re
import requests

def parse_biblatex(biblatex_str):
    """
    Parse the BibLaTeX formatted string to extract titles and authors.
    Returns a list of dictionaries containing the 'title' and 'author'.
    """
    entries = []
    
    # Regular expression patterns for BibLaTeX fields
    title_pattern = re.compile(r'title\s*=\s*\{([^}]+?)(?::[^}]*)?\}')
    author_pattern = re.compile(r'author\s*=\s*\{([^,]+?)(?:,| and|})')
    year_pattern = re.compile(r"year\s*=\s*\{(\d{4})\}")
    
    # Split the input into individual entries
    bib_entries = re.split(r'\n@', biblatex_str)
    
    for entry in bib_entries:
        title_match = title_pattern.search(entry)
        author_match = author_pattern.search(entry)
        year_match = year_pattern.search(entry)
        
        if title_match:
            title = title_match.group(1)
        else:
            title = None
        
        if author_match:
            author = author_match.group(1)
            if author.split()[-1] != "al.":
                author = author.split()[-1]
            else:
                author = author.split()[-3]
        else:
            author = None
        if year_match:
            year = year_match.group(1)
        if title or author:
            entries.append({'title': title, 'author': author, 'year': year})
    
    return entries

def check_source_openlibrary(title, author):

    """
    Check if a source exists on Open Library using the title and/or author.
    Returns True if found, False otherwise.
    """
    base_url = "https://openlibrary.org/search.json"
    params = {
        "title": title
        #"author": author
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if len(data.get('docs', [])) > 0:
        for dp in data.get('docs', []):
            if 'author_name' in dp:
                for author_name in dp['author_name']:
                    if author.casefold() in author_name.casefold():
                        print("found Author")
                        if title.casefold() in dp['title'].casefold():
                            print("found title")
                            return dp['publish_year']
    # Check if any docs (books) were found
    return None

def check_source_crossref(title, author):
    """
    Check if a source exists on CrossRef using the title and/or author.
    Returns True if found, False otherwise.
    """
    base_url = "https://api.crossref.org/works"
    params = {
        "query.title": title
        #"query.author": author,
        #"rows": 1  # We only want the top result
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    if len(data['message']['items']) > 0:
        for item in data['message']['items']:
            for iTitle in item['title']:
                if title.casefold() in iTitle.casefold():
                    if 'author' in item:
                        for iAuthor in item['author']:
                            if 'family' in iAuthor:
                                if author.casefold() in iAuthor['family'].casefold():
                                    print("found author")
                                    year = []
                                    try:
                                        if 'published' in item:
                                            if 'date-parts' in item['published']:
                                                for iYear in item['published']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                        elif 'published-print' in item:
                                            if 'date-parts' in item['published-print']:
                                                for iYear in item['published-print']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                        elif 'published-online' in item:
                                            if 'date-parts' in item['published-online']:
                                                for iYear in item['published-online']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                        elif 'deposited' in item:
                                            if 'date-parts' in item['deposited']:
                                                for iYear in item['deposited']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                        elif 'issued' in item:
                                            if 'date-parts' in item['issued']:
                                                for iYear in item['issued']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                    except:
                                        return [0]
                            else: print(iAuthor)
                    elif 'editor' in item:
                        for editor in item['editor']:
                            if 'family' in editor:
                                if author.casefold() in editor['family'].casefold():
                                    year = []
                                    try:
                                        if 'published' in item:
                                            if 'date-parts' in item['published']:
                                                for iYear in item['published']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                        elif 'published-print' in item:
                                            if 'date-parts' in item['published-print']:
                                                for iYear in item['published-print']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                        elif 'published-online' in item:
                                            if 'date-parts' in item['published-online']:
                                                for iYear in item['published-online']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                        elif 'deposited' in item:
                                            if 'date-parts' in item['deposited']:
                                                for iYear in item['deposited']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                        elif 'issued' in item:
                                            if 'date-parts' in item['issued']:
                                                for iYear in item['issued']['date_parts']:
                                                    year.append(iYear[0])
                                                return year
                                            else:
                                                return [0]
                                    except:
                                        return [0]
                            else: print(editor)
        return None 
    # Check if any items (works) were found
    else:
        return None

def check_biblatex_sources(biblatex_str):
    """
    Main function to check if the sources in a BibLaTeX string exist in either Open Library or CrossRef.
    Returns a list of results indicating which sources exist.
    """
    entries = parse_biblatex(biblatex_str)
    results = []
    
    for entry in entries:
        print("checking: ", entry['title'], "by: ", entry['author'])
        exists_in_openlibrary = check_source_openlibrary(entry['title'], entry['author'])
        exists_in_crossref = check_source_crossref(entry['title'], entry['author'])
        exists = exists_in_openlibrary is not None or exists_in_crossref is not None
        print("exsists: ", str(exists) )
        year = None
        if exists_in_openlibrary:
            if entry.get('year') in exists_in_openlibrary:
                year = entry.get('year')
            else:
                year = max(exists_in_openlibrary)
                if year == 0:
                    year = entry.get('year')
        if year is None and exists_in_crossref:
            if entry.get('year') in exists_in_crossref:
                year = entry.get('year')
            else:
                year = max(exists_in_crossref)
                if year == 0:
                    year = entry.get('year')

        result = {
            'title': entry.get('title', 'Unknown Title'),
            'author': entry.get('author', 'Unknown Author'),
            'bib_year': entry.get('year', 'Unknown Year'),
            'ref_year': year,
            'exists': exists,
            'exists_in_openlibrary': exists_in_openlibrary,
            'exists_in_crossref': exists_in_crossref
        }
        results.append(result)
    
    return results

# Checking the references in the uploaded file
file_path = '../software/References.bib'

# Read the file content
with open(file_path, 'r') as file:
    bib_content = file.read()
results = check_biblatex_sources(bib_content)
print("number of references: ",len(results))
print("number of references found: ", sum(item.get('exists', False) for item in results))
preamble = ""
for bibItem in results:
    if not bibItem['exists']:
        preamble += f"The bibliography entry for {bibItem['title']} by {bibItem['author']} cannot be verified, please try to use the proper source or remove this source and citations. "
    if int(bibItem['bib_year']) != bibItem['ref_year']:
        preamble += f"The bibliography entry for {bibItem['title']} by {bibItem['author']} may have the incorrect publish year, my sources show it was published in {bibItem["ref_year"]}. "
print(preamble)