import os, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

if __name__ == "__main__":
    # Paths to chrome.exe and chromedriver.exe
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Modify this path as needed
    chromedriver_path = r"C:\_project\chromedriver-win32\chromedriver-win32\chromedriver.exe"  # Modify this path as needed
    user_data_dir = r"C:\Users\adartt\AppData\Local\Google\Chrome\User Data"  # Modify this path as needed
    profile_dir = "Default"
    driver = None
    prompt =  "Explain division by 0"
    try:
        # Start Chrome with the custom paths
        driver = start_chrome_with_custom_paths_and_profile(chrome_path, chromedriver_path, user_data_dir, profile_dir)
        print("driver returned")
        
        # Example: Open a website
        driver.get('https://chatgpt.com/')

        time.sleep(3)
        
        inputElements = driver.find_elements(By.TAG_NAME, "textarea")

        i = 0
        # while i<10:
        inputElements[0].send_keys(prompt)
        time.sleep(2)
        inputElements[0].send_keys(Keys.ENTER)
        #time.sleep(10)
        wait = WebDriverWait(driver, 120)  # Wait up to 10 seconds
        search_box = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "btn-secondary")))
        inputElements = driver.find_elements(By.TAG_NAME, "p")
        time.sleep(5)
        results = []
        for element in inputElements:
            results.append(element.text)
            print(results)
            i+=1
        time.sleep(5)
        
    finally:
        # Make sure to close the browser after use
        driver.quit()
