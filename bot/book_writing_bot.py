import re
import sys
from enum import Enum
import argparse
import json
import os, time, random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timedelta
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
    bib_title_pattern = re.compile(r'title\s*=\s*\{(.+?)\}')
    bib_author_pattern = re.compile(r'author\s*=\s*\{(.+?)\}')
    
    # Split the input into individual entries
    bib_entries = re.split(r'\n@', biblatex_str)
    
    for entry in bib_entries:
        title_match = title_pattern.search(entry)
        author_match = author_pattern.search(entry)
        year_match = year_pattern.search(entry)
        bib_author_match = bib_author_pattern.search(entry)
        bib_title_match = bib_title_pattern.search(entry)
        
        if title_match:
            title = title_match.group(1)
        else:
            title = None
        if bib_title_match:
            bib_title = bib_title_match.group(1)
        if bib_author_match:
            bib_author = bib_author_match.group(1)
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
            entries.append({'title': title, 'author': author, 'year': year, 'bib_author': bib_author, 'bib_title': bib_title})
    
    return entries

def check_source_openlibrary(title, author):

    """
    Check if a source exists on Open Library using the title and/or author.
    Returns True if found, False otherwise.
    """
    try:
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
                                if 'publish_year' in dp:
                                    return dp['publish_year']
                                else:
                                    return [0]
        # Check if any docs (books) were found
        return None
    except:
        print("issue getting from openlibrary.")
        return None

def check_source_crossref(title, author):
    """
    Check if a source exists on CrossRef using the title and/or author.
    Returns True if found, False otherwise.
    """
    try:
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
    except:
        print("issue getting from crossref")
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
            'bib_title': entry.get('bib_title', 'Unknown Title'),
            'bib_author': entry.get('bib_author', 'Unknown Author'),
            'bib_year': entry.get('year', 'Unknown Year'),
            'ref_year': year,
            'exists': exists,
            'exists_in_openlibrary': exists_in_openlibrary,
            'exists_in_crossref': exists_in_crossref
        }
        results.append(result)
    
    return results
def wait_until_time_reached_and_refresh(driver):
    try:
        # Locate the div containing the message
        element = driver.find_element(By.XPATH, "//div[contains(@class, 'text-sm') and contains(@class, 'text-token-text-error')]")
        
        # Extract the text content
        message_text = element.text

        # Regular expression to find the time in the message
        match = re.search(r"please try again after (\d{1,2}:\d{2} (?:AM|PM))", message_text)
        
        if match:
            # Extract the timestamp string
            timestamp_str = match.group(1)
            
            # Convert extracted time to a datetime object
            timestamp = datetime.strptime(timestamp_str, '%I:%M %p').time()
            
            # Get the current time
            now = datetime.now()
            current_time = now.time()
            
            # Calculate how long to wait
            wait_time = ((datetime.combine(now, timestamp) - now).total_seconds())

            # If the calculated wait time is negative, it means the time is for the next day
            if wait_time < 0:
                wait_time += 86400  # Add a full day in seconds

            print(f"Waiting for {wait_time} seconds until {timestamp_str}.")
            time.sleep((wait_time + 60))

            # Refresh the page
            driver.refresh()
            print("Page refreshed.")
        else:
            print("The message does not contain a valid timestamp.")
    except Exception as e:
        print(f"An error occurred: {e}")

def start_chrome_with_custom_paths_and_profile(chrome_path, chromedriver_path, user_data_dir, profile_dir):
    # Check if the specified paths exist
    if not os.path.exists(chrome_path):
        raise FileNotFoundError(f"The Chrome binary at {chrome_path} does not exist. Please check the path.")

    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"The ChromeDriver binary at {chromedriver_path} does not exist. Please check the path.")

    # Set up Chrome options to use the specified chrome.exe
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # Path to the user data directory
    chrome_options.add_argument(f"--profile-directory={profile_dir}")  # Profile directory (e.g., 'Default', 'Profile 1')


    # Set up the service to use the specified chromedriver.exe
    service = Service(executable_path=chromedriver_path)

    try:
        # Initialize the WebDriver with custom paths
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Driver Started")
        return driver
    except OSError as e:
        raise RuntimeError(f"Failed to start the ChromeDriver. Make sure the versions of Chrome, ChromeDriver, and Python are compatible. Error: {e}")

class SectionType(Enum):
    SECTION = "section"
    SUBSECTION = "subsection"
    SUBSUBSECTION = "subsubsection"

def replace_section_content(file_path, new_content, section_type, title):
    with open(file_path, 'r', encoding='utf-8') as file:
        latex_content = file.read()

    # Define regex patterns based on the section type
    if section_type == SectionType.SECTION:
        pattern = rf'(\\section\{{{re.escape(title)}\}})(.*?)(?=\\section|$)'
    elif section_type == SectionType.SUBSECTION:
        pattern = rf'(\\subsection\{{{re.escape(title)}\}})(.*?)(?=\\subsection|\\section|$)'
    elif section_type == SectionType.SUBSUBSECTION:
        pattern = rf'(\\subsubsection\{{{re.escape(title)}\}})(.*?)(?=\\subsubsection|\\subsection|\\section|$)'

    # Replace the content of the matched section
    new_content_with_title = f'\\\\{section_type.value}{{{title}}}\n{new_content}\n'
    updated_content = re.sub(pattern, new_content_with_title, latex_content, flags=re.DOTALL)

    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

    print(f"Updated {section_type.value} '{title}' successfully.")


class SectionNode:
    def __init__(self, title, section_type):
        self.title = title
        self.section_type = section_type
        self.word_count = 0
        self.subsections = []

    def add_subsection(self, subsection):
        self.subsections.append(subsection)

    def calculate_word_count(self):
        total_word_count = self.word_count
        for subsection in self.subsections:
            total_word_count += subsection.calculate_word_count()
        return total_word_count

    def __repr__(self):
        return f"{self.section_type.title()}: {self.title}, Words: {self.calculate_word_count()}"

def remove_latex_commands(text):
    text = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{[^\}]*\})?', '', text)
    text = re.sub(r'\\begin\{[a-zA-Z]*\}.*?\\end\{[a-zA-Z]*\}', '', text, flags=re.DOTALL)
    text = re.sub(r'%.*', '', text)
    text = re.sub(r'[\{\}\[\]]', '', text)
    return text

def count_words(text):
    words = re.findall(r'\b\w+\b', text)
    return len(words)

def parse_latex_structure(latex_content):
    sections = re.split(r'(?=\\section\{)', latex_content)
    document_structure = []

    for section in sections:
        if section.strip() == "":
            continue
        
        section_title_match = re.search(r'\\section\{([^}]*)\}', section)
        section_title = section_title_match.group(1) if section_title_match else "Unnamed Section"
        section_node = SectionNode(section_title, "section")

        subsections = re.split(r'(?=\\subsection\{)', section)
        section_body = subsections.pop(0)  # Section body without subsections

        # Count words in the section body (excluding subsections)
        cleaned_section_body = remove_latex_commands(section_body)
        section_word_count = count_words(cleaned_section_body)
        section_node.word_count = section_word_count

        for subsection in subsections:
            subsection_title_match = re.search(r'\\subsection\{([^}]*)\}', subsection)
            subsection_title = subsection_title_match.group(1) if subsection_title_match else "Unnamed Subsection"
            subsection_node = SectionNode(subsection_title, "subsection")

            subsubsections = re.split(r'(?=\\subsubsection\{)', subsection)
            subsection_body = subsubsections.pop(0)  # Subsection body without subsubsections

            # Count words in the subsection body (excluding subsubsections)
            cleaned_subsection_body = remove_latex_commands(subsection_body)
            subsection_word_count = count_words(cleaned_subsection_body)
            subsection_node.word_count = subsection_word_count

            for subsubsection in subsubsections:
                subsubsection_title_match = re.search(r'\\subsubsection\{([^}]*)\}', subsubsection)
                subsubsection_title = subsubsection_title_match.group(1) if subsubsection_title_match else "Unnamed Subsubsection"
                subsubsection_node = SectionNode(subsubsection_title, "subsubsection")

                # Count words in the subsubsection
                cleaned_subsubsection = remove_latex_commands(subsubsection)
                subsubsection_word_count = count_words(cleaned_subsubsection)
                subsubsection_node.word_count = subsubsection_word_count

                subsection_node.add_subsection(subsubsection_node)

            section_node.add_subsection(subsection_node)

        document_structure.append(section_node)

    return document_structure

def generate_marxist_prompts_with_chapter_title(latex_content, chapterIndex):
    # Pattern to match the chapter title
    print(latex_content)
    chapter_pattern = r'\\chapter\{(.+?)\}'
    # Pattern to match sections and their corresponding content until the next section
    section_pattern = r'\\section\{(.+?)\}(.*?)(?=\\section|$)'  
    # Pattern to match subsections and their corresponding content until the next subsection or section
    subsection_pattern = r'\\subsection\{(.+?)\}(.*?)(?=\\subsection|\\section|$)' 
    # Pattern to match subsubsections
    subsubsection_pattern = r'\\subsubsection\{(.+?)\}'

    # Extract the chapter title
    chapter_title = re.search(chapter_pattern, latex_content).group(1)
    with open(f"../software/mainmatter/chap{chapterIndex}.tex", 'w') as outputFile:
        outputFile.write("\\chapter{%s}\n\\begin{refsection}\n\n" % chapter_title)

    sections = re.findall(section_pattern, latex_content, re.DOTALL)

    prompts = []
    i = 1
    for section, content in sections:
        subsections = re.findall(subsection_pattern, content, re.DOTALL)
        subsections_list = ''
        
        for subsection, subcontent in subsections:
            subsubsections = re.findall(subsubsection_pattern, subcontent)
            subsubsections_list = ''.join([f'\\subsubsection{{{subsub}}}\n' for subsub in subsubsections])
            subsections_list += f'\\subsection{{{subsection}}}\n{subsubsections_list}'

        if i == 1:
            prompt_preamble = (f"For a chapter titled '{chapter_title}', please provide an in-depth Marxist analysis for the section titled '{section}', do not use 'from a Marxist perspective' or the like as it is implied. "
                    f"Have the content of the output be in LaTeX format, do not remove any of the layout that is included in the section. "
                    f"Use the \\cite[pp.~]{{}} markup in the content to cite sources. Also, please provide a separate output for the bibliography in the biblatex format. ")
            i += 1
        else:
            prompt_preamble = (f"Great job. Let's move onto the next section. ")
        prompt_text = (f"Here is its outline of the section: {{{section}}} {subsections_list}")
        
        prompts.append({"prompt_preamble": prompt_preamble, "prompt_section": prompt_text})
    return prompts
reopenFile = False
def generate_marxist_prompts_per_subsection(latex_content, chapterIndex):
    print(latex_content)
    chapter_pattern = r'\\chapter\{(.+?)\}'
    # Pattern to match sections and their corresponding content until the next section
    section_pattern = r'\\section\{(.+?)\}(.*?)(?=\\section|$)'  
    # Pattern to match subsections and their corresponding content until the next subsection or section
    subsection_pattern = r'\\subsection\{(.+?)\}(.*?)(?=\\subsection|\\section|$)' 
    # Pattern to match subsubsections
    subsubsection_pattern = r'\\subsubsection\{(.+?)\}'

    # Extract the chapter title
    chapter_title = re.search(chapter_pattern, latex_content).group(1)
    if reopenFile:
        with open(f"../software/mainmatter/chap{chapterIndex}.tex", 'w') as outputFile:
            outputFile.write("\\chapter{%s}\n\\begin{refsection}" % chapter_title)
        
    sections = re.findall(section_pattern, latex_content, re.DOTALL)

    prompts = []
    
    for section, content in sections:
        subsections = re.findall(subsection_pattern, content, re.DOTALL)
        subsections_list = ''
        i = 1

        for subsection, subcontent in subsections:
            subsubsections = re.findall(subsubsection_pattern, subcontent)
            subsubsections_list = ''.join([f'\\subsubsection{{{subsub}}}\n' for subsub in subsubsections])
            subsections_list += f'\\subsection{{{subsection}}}\n{subsubsections_list}'
        
        prompt_preamble = (f"Please convene a committee of 100 of the most influential communists and 100 experts for the topic of '{section}'. The committee should debate the topic of '{section}' and come to a consensus to formulate output for a section in a book called 'Engineering Communism: On Software Engineering' for a chapter titled '{chapter_title}'. The output should be for the section titled '{section}' adhering to the following guidelines for the output. Please provide an in-depth Marxist analysis for the introduction for the section titled '{section}'. "
                    f"Do not write content for any of the subsections or subsubsections, just provide the content for the introduction of the section. "
                    f"Have the content of the output be in LaTeX format in a code block, do not remove any of the layout that is included in the section. "
                    f"Use the \\cite[pp.~]{{}} markup in the content to cite sources. Also, please provide a separate output for the bibliography in the biblatex format. ")
        prompt_text = (f"Write only the introduction for the section titled '{section}'. Here is the outline for the full section so that there is enough context: \\section{{{section}}} {subsections_list}")
        prompts.append({"prompt_preamble": prompt_preamble, "prompt_section": prompt_text})
        for subsection, subcontent in subsections:
            print(subsection)
            subsubsections = re.findall(subsubsection_pattern, subcontent)
            #subsubsections_list = ''.join([f'\\subsubsection{{{subsub}}}\n' for subsub in subsubsections])
            prompt_preamble = f"Great job, let's move on to the next subsection, please convene the committee of experts for '{subsection}'. "
            prompt_preamble += f"Include a separate output for the bibliography in BibLatex format. "
            prompt_text = f"Write only for the subsection titled '{subsection}'"
            prompt_text += f". " if len(subsubsections) == 0 else f" and all subsubsections that belong to the subsection. "
            prompt_text += f" Here is the outline for the full section so that there is enough context: \\section{{{section}}} {subsections_list}"
            prompts.append({"prompt_preamble": prompt_preamble, "prompt_section": prompt_text})
    return prompts
            

def request_another_response(driver, preamble, section):
    inputElements = driver.find_elements(By.ID, "prompt-textarea")
    promptStr = preamble + section
    promptStr = promptStr.replace("\n", " ")
    sleepTime = (random.randint(1, 5) * 15)
    print("sleeping for %i" % sleepTime)
    time.sleep(sleepTime)
    inputElements[0].send_keys(promptStr)
    time.sleep(3)
    userInput = input("Write and continue anyway? ")
    if userInput == 'y':
        return True
    input("please press enter to continue...")
    #inputElements[0].send_keys(Keys.ENTER)
    wait_for_button(driver)

def wait_for_button(driver):
    while True:
        print("waiting for scroll")
        wait_and_click_scroll_arrow(driver, timeout=120)
        input("press enter to evaluate response...")
        return
        print("waiting for button")
        try:
            endOfPrompt = None
            button_xpath = "//button[@aria-label='Read Aloud']"
        
            endOfPrompt = WebDriverWait(driver, 500).until(
                EC.presence_of_element_located((By.XPATH, button_xpath))
            )
            if endOfPrompt is not None:
                return
            time.sleep(5)
            button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn-secondary"))
            )
            

            # Check if the button text is "Continue generating"
            if "Continue generating" in button.text:
                time.sleep(random.randint(1,5))
                button.click()
                print("Clicked the 'Continue generating' button.")
            else:
                print("Button text is not 'Continue generating', no action taken.")
                return
        except Exception as e:
            print(e)
            #check for cap
            if endOfPrompt is not None:
                wait_until_time_reached_and_refresh(driver)

def check_for_bib(bib):
    # Regex pattern to match BibLaTeX entries
    bib_entry_pattern = re.compile(
        r'@(\w+)\{(\w+),\s*'       # Matches @entry_type{label,
        r'(.*?)'                    # Matches the content inside the entry
        r'\}\s*$',                  # Matches the closing }
        re.DOTALL                   # Allows the dot to match newline characters
    )
    
    # Match against the entire content
    match = bib_entry_pattern.search(bib.strip())
    
    if not match:
        return False

    # Extract the entry type, label, and content
    entry_type = match.group(1)
    label = match.group(2)
    content = match.group(3)
    
    # Check that the entry type and label are valid
    if not entry_type.isalpha() or not label:
        return False

    # Regex pattern to match key-value pairs inside the entry
    key_value_pattern = re.compile(
        r'\b\w+\b\s*=\s*\{.*?\}\s*,',  # Matches key = {value},
        re.DOTALL                      # Allows the dot to match newline characters
    )
    
    # Find all key-value pairs
    key_values = key_value_pattern.findall(content)
    
    # Check if any key-value pairs were found
    if not key_values:
        return False

    # If all checks passed, the format is correct
    return True

def check_for_cite(content):
    # Regex pattern to match \cites[pp.~...]{} 
    cite_pattern = re.compile(
        r'\\cites?\[pp\.\~\d+(\-\d+)?\]\{.*?\}',  # Matches \cite or \cites with pp.~{...}
        re.DOTALL
    )
    
    # Search for any matching patterns
    match = cite_pattern.search(content)
    
    # Return True if any matches are found, else False
    return bool(match)

def extract_citations(content):
    """Extracts all citation keys from the content."""
    cite_pattern = re.compile(r'\\cites?\[pp\.\~\d+(\-\d+)?\]\{(.*?)\}')
    citations = cite_pattern.findall(content)
    # Extracting just the citation keys
    return [cite[1] for cite in citations]

def extract_bib_keys(bib):
    """Extracts all keys from the bibliography."""
    bib_key_pattern = re.compile(r'@[\w]+\{(.*?),')
    return bib_key_pattern.findall(bib)

def check_for_valid_cites(bib, content):
    """Checks if all citations in the content are in the bibliography."""
    cited_keys = extract_citations(content)
    bib_keys = extract_bib_keys(bib)
    
    # Check if every cited key is in the bibliography
    return all(cite in bib_keys for cite in cited_keys)
def extract_number(text):
    # Use regular expression to find all numbers in the text
    numbers = re.findall(r'\d+', text)
    # Convert the first found number to an integer and return it
    print(int(numbers[0]) if numbers else None)
    return int(numbers[0]) if numbers else None

def contains_marxist_phrase(input_string):
    # Convert the input string to lowercase and check for the phrase
    return "from a marxist" in input_string.lower()

def check_content_length(document_structure):
    returnArray = []
    for section in document_structure:
        #check if introduction
        if "Unnamed Section" in str(section):
            for subsection in section.subsections:
                if extract_number(str(subsection)) < (500 if not subsection.subsections else len(subsection.subsections) * 250):
                    returnArray.append(subsection)
                for subsubsection in subsection.subsections:
                    if extract_number(str(subsubsection)) < 250:
                        returnArray.append(subsection)
        else:
            if extract_number(str(section)) < (len(section.subsections) * 500):
                returnArray.append(section)
            
        # if extract_number(str(section)) < (len(section.subsections) * 300):
        #     returnArray.append(section)
        # for subsection in section.subsections:
        #     if extract_number(str(subsection))/10 < (300 if not subsection.subsections else len(subsection.subsections) * 150):
        #         returnArray.append(subsection)
        #     for subsubsection in subsection.subsections:
        #         if extract_number(str(subsubsection))/10 < 150:
        #             returnArray.append(subsection)
    return returnArray

def check_intro_summary_content_length(document_structure):
    returnArray = []
    for section in document_structure:
        if extract_number(str(section)) < (len(section.subsections) * 250):
            returnArray.append(section)
        for subsection in section.subsections:
            if extract_number(str(subsection)) < (250 if not subsection.subsections else len(subsection.subsections) * 100):
                returnArray.append(subsection)
            for subsubsection in subsection.subsections:
                if extract_number(str(subsubsection)) < 100:
                    returnArray.append(subsection)
    return returnArray

def wait_and_click_scroll_arrow(driver, timeout=10):
    """
    Waits for the SVG element to be present and clickable, then clicks it.

    Args:
    driver (webdriver): Selenium WebDriver instance.
    timeout (int): Maximum time to wait for the element to be clickable.
    """
    try:
        # Wait for the SVG element to be present in the DOM and visible
        svg_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "icon-md.text-token-text-primary"))
        )
        time.sleep(random.randint(1,5))
        svg_element.click()
        print("SVG element clicked successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    return True

if __name__ == "__main__":
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Modify this path as needed
    chromedriver_path = r"C:\_project\chromedriver-win32\chromedriver-win32\chromedriver.exe"  # Modify this path as needed
    user_data_dir = r"C:\Users\adartt\AppData\Local\Google\Chrome\User Data"  # Modify this path as needed
    profile_dir = "Default"
    driver = None
    continueHere = False
    allowStart = False
    try:
        #Start Chrome with the custom paths
        driver = start_chrome_with_custom_paths_and_profile(chrome_path, chromedriver_path, user_data_dir, profile_dir)
        print("driver returned")
        for chapterIndex in range(6,12):
            driver.get('https://chatgpt.com/g/g-OpNdRVsFT-communist-writer')
            input("press enter to continue...")
            
            
            with open(f"../software/mainmatter/chap{chapterIndex}.outline.tex", 'r') as file:
                latex_content = file.read()
                prompts = generate_marxist_prompts_per_subsection(latex_content, chapterIndex)

                #prompts = generate_marxist_prompts_with_chapter_title(latex_content, chapterIndex)
            index = 0 #return to 0 when starting a new chapter
            for prompt in prompts:
                if not continueHere:
                    print(prompt['prompt_section'])
                    print("from a marxist perspective" not in prompt['prompt_section'].lower())
                    user_input = input("continue here (y/n): ")
                    if user_input.lower() == 'y':
                        continueHere = True
                    
                    else:
                        index += 1
                        continue
                inputElements = driver.find_elements(By.ID, "prompt-textarea")
                print(prompt['prompt_preamble'] + prompt['prompt_section'])
                promptStr = prompt['prompt_preamble'] + prompt['prompt_section']
                promptStr = promptStr.replace("\n", " ")
                inputElements[0].send_keys(promptStr)
                time.sleep(2)
                if not allowStart:
                    user_input = input("allow prompt to send (y/n): ")
                    if user_input.lower() == 'y':
                        allowStart = True
                input("Press enter to send prompt...")
                if allowStart:
                    inputElements[0].send_keys(Keys.ENTER)
                wait_for_button(driver)
                target_divs = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "code"))
                )
                #print("content:\n" + str(target_divs[-2].text))
                #print("bib:\n"+ str(target_divs[-1].text))
                # Extract content from all matching elements
                while True:
                    preamble = ""
                    yearamble = ""
                    # check for bibliography
                    print(str(target_divs[-1].text))
                    print(str(target_divs[-2].text))
                    hasBib = check_for_bib(str(target_divs[-1].text))
                    print(f"HasBib: {hasBib}")
                    # check for \cite[pp.~]{}
                    hasCite = check_for_cite(str(target_divs[-2].text) if hasBib else str(target_divs[-1].text))
                    print(f"HasCite: {hasCite}")
                    # check for valid citations
                    hasValidCites = False
                    if hasBib and hasCite:
                        hasValidCites = check_for_valid_cites(str(target_divs[-1].text), str(target_divs[-2].text))
                        print(f"hasValidCites: {hasValidCites}")
                    # check for content length and add preambles
                    document_structure = parse_latex_structure(str(target_divs[-2].text) if hasBib else str(target_divs[-1].text))
                    #remove_latex_commands(str(target_divs[-2].text) if hasBib else str(target_divs[-1].text))
                    isLongEnough = False
                    if hasBib:
                        bibResults = check_biblatex_sources(str(target_divs[-1].text))
                        "The following bibliography entries cannot be verified: "
                        bibpreamble = ""
                        bibyearamble = ""
                        yearamble = ""
                        for bibItem in bibResults:
                            if not bibItem['exists']:
                                bibpreamble += f"{bibItem['bib_title']} by {bibItem['bib_author']}, "
                            if int(bibItem['bib_year']) != bibItem['ref_year'] and bibItem['ref_year'] is not None:
                                bibyearamble += f"{bibItem['title']} by {bibItem['author']}; possible year is {bibItem["ref_year"]}, "
                        if bibpreamble != "":
                            bibpreamble = bibpreamble[:-2] + ". "
                            preamble += "The following bibliography entries cannot be verified: " + bibpreamble + "Please use sources that can be verified, it would help if the authors name was listed <first name> <last name> and if there are more than 1 author it is semicolon delimited list. "
                        if bibyearamble != "":
                            yearamble = "The following bibliography entries may have the wrong year: " + bibyearamble[:-2] + ". "
                    if index == 0 or index + 1 == len(prompts):
                        longEnoughArray = check_content_length(document_structure)
                        if hasBib and hasCite and not hasValidCites:
                            preamble += "Not all the citations were included in the bibliography. Please make sure anything you cite is in the bibliography. "
                        if hasBib and not hasCite:
                            preamble += "No citations were made. Please add citations using the \\cite[pp.~]{} markup for LaTex. "
                        if len(longEnoughArray) > 0:
                            preamble = "Not enough content was generated. Please add more context, data, statistics, examples, quotes from sources, analysis and Marxist Analysis to generate more content. " + preamble

                    else:
                        longEnoughArray = check_content_length(document_structure)
                        if not hasBib:
                            preamble += "No bibliography was provided, please add a seperate output for the bibliography in BibLatex format. "
                        if not hasCite:
                            preamble += "No citations were made. Please add citations using the \\cite[pp.~]{} markup for LaTex. "
                        if not hasValidCites and (hasBib and hasCite):
                            preamble += "Not all the citations were included in the bibliography. Please make sure anything you cite is in the bibliography. "
                        if len(longEnoughArray) > 0:
                            preamble = "Not enough content was generated. Please add more context, data, statistics, examples, quotes from sources, analysis and Marxist Analysis to generate more content. " + preamble

                    if "from a marxist perspective" not in prompt['prompt_section'].lower() and contains_marxist_phrase(str(target_divs[-2].text) if hasBib else str(target_divs[-1].text)):
                        preamble += "Do not include the phrase 'From a Marxists perspective' or similar phrases, as it is implied. "
                    if preamble != "":
                        preamble += yearamble
                        print(preamble)
                        if request_another_response(driver, preamble, prompt['prompt_section']):
                            break
                        target_divs = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.TAG_NAME, "code"))
                        )
                        
                    else:
                        break
                index += 1
                print("content:\n" + str(target_divs[-2].text))
                print("bib:\n"+ str(target_divs[-1].text))
                try:
                    with open(f"../software/mainmatter/chap{chapterIndex}.tex", 'a', encoding='utf-8') as outputFile:
                        outputFile.write("\n\n")
                        outputFile.write(str(target_divs[-2].text))
                    with open("../software/References.bib", 'a', encoding='utf-8') as bibliography:
                        bibliography.write(str(target_divs[-1].text))
                    print("sleeping to avoid detection")
                    time.sleep(90)
                except Exception as e:
                    print(e)
                    print("an error happened writing please manually copy and paste before continuing. ")
                    input("press enter to continue...")
            with open(f"../software/mainmatter/chap{chapterIndex}.tex", 'a', encoding='utf-8') as outputFile:
                outputFile.write("\\printbibliography[heading=subbibliography]\n\\end{refsection}")
    except Exception as e:
        print(e)   
    finally:
        # Make sure to close the browser after use
        driver.quit()
        print("finished")
