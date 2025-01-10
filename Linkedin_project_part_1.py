
########## ADVANCED PROGRAMMING PROJECT
####### FIRST PART: WEB SCRAPING 
##### AUTHORS: Frezard Paul, Sartori Romain, Vasta Francesca
 


import pandas as pd #For handling and analyzing data.
from bs4 import BeautifulSoup #For parsing HTML 
from tqdm import tqdm #For showing progress bars (useful in loops).
import requests #For making HTTP requests 
import re #regular expressions
import os #For interacting with the operating system (not used in the current snippet).
import time #For adding delays in your code.
from selenium import webdriver #For web automation (scraping and interaction with web pages).
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# choose one of the driver to your liking 
#driver: This is the instance of the Selenium WebDriver. 
#It controls the browser and allows you to interact with it.
driver = webdriver.Firefox()
wait = WebDriverWait(driver, 10)
driver.get("https://www.linkedin.com/feed/") 
#with driver.get we open the specified URL in the browser.

#Accept cookies (if needed)
#This section tries to find and click the cookie acceptance button. 
#If the button is not found, it prints a message
#Begins a block where code is executed and exceptions are handled.
try:
    wait = WebDriverWait(driver, 10)
    accept_cookies_button = driver.find_element(By.XPATH, '/html/body/div[1]/main/div[1]/div/section/div/div[2]/button[1]')
    #Finds the button element on the page to accept cookies using its XPath.
    accept_cookies_button.click()#the method .click is used to click the located button
    print("Cookies accepted.")
except:
    #Catches any exceptions if the button is not found or another error occurs.
    print("The cookie button has not been found.")


#TEMPORARY ACCOUNT CREATED FOR THE PROJECT
#Copies password and username
linkedin_username = 'DS2E.master@gmail.com'#storing the username in a variable
linkedin_password = 'DS2E_master0-' #storing the password in a variable


#Paste username and the password
email_input = driver.find_element(By.ID, 'username') 
#Finds the email input field on the login page using its ID 
email_input.send_keys(linkedin_username)
wait = WebDriverWait(driver, 10)
password_input = driver.find_element(By.ID, 'password')
password_input.send_keys(linkedin_password)
# Set an explicit wait time (10 seconds)
wait = WebDriverWait(driver, 10)
password_input.send_keys(Keys.RETURN)


#Click to close the linkedin chat if it is opened by default: 
try: 
    wait = WebDriverWait(driver, 10)
    close_chat_button = driver.find_element(By.CSS_SELECTOR,'button.msg-overlay-bubble-header__control svg[data-test-icon="chevron-down-small"]')
    close_chat_button.click()
    print('Chat is closed')
except:
    print("Wasn't needed")


## SEARCH THE JOB 'DATA SCIENTIST'
def search_for_query(driver, query):
    # Attente explicite pour que l'élément soit interactif
    search_bar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'search-global-typeahead__input'))
    )
    search_bar.click()
    search_bar.send_keys(query)
    time.sleep(1)
    search_bar.send_keys(Keys.RETURN)

search_query = 'Data Scientist'
search_for_query(driver, search_query)   


#CLick on show all job results def search_for_query(driver, query):
All_results = WebDriverWait(driver, 10).until(
         EC.element_to_be_clickable((By.LINK_TEXT, "See all job results in France")))
All_results.click()

########## DEFINITION OF SOME USEFUL FUNCTION 

########## FIRST FUNCTION

# Function to CLICK ELEMENTS based on CSS with the help of the text
def click_element_CSS(css, driver, wait_time=30, contains_text=None):
    try:
        #wait for element to be clicked
        elements = WebDriverWait(driver, wait_time).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css))
        )
        # Filter elements based on the text they contain, if specified
        for element in elements:
            if contains_text is None or contains_text in element.text:
                print(f"Clicking on element: {css} with text '{element.text}'")  # Debug
                element.click()
                time.sleep(1)  # wait
                break
    except Exception as e:
        print(f"Failed to click on {css}: {e}")  # Log error

# CSS list with also the text, if specified, or none
css_list = [
    # filter to obtain job offers published in the last 24 hours
    ("button[aria-label='Date posted filter. Clicking this button displays all Date posted filter options.']", None),
    ("label.search-reusables__value-label[for='timePostedRange-r86400']", None),
    ('div.reusable-search-filters-buttons > button.artdeco-button--primary.ml2', "Show"),  # Cerca "Show" nel testo
    
    # Filter to select the job type “internship”
    ("button[aria-label='Experience level filter. Clicking this button displays all Experience level filter options.']", None),
    ("label.search-reusables__value-label[for='experience-1']", None),
    ('div.reusable-search-filters-buttons > button.artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view.ml2', "Show")  # Cerca "Show" nel testo
]

# Loop to apply filters on all elemen
def apply_filters_with_loop(driver, css_list):
    for css, text in css_list:
        click_element_CSS(css, driver, contains_text=text)

# call function
apply_filters_with_loop(driver, css_list)


########## SECOND FUNCTION

# this function allows to scroll to the bottom of the container which contains jobs

def scroll_list_to_bottom(driver, wait=3):

    try:
        #Scroll to the end of the list to load all job offers and mimics human interaction
        column_on_the_left = driver.find_element(By.XPATH, "/html/body/div[6]/div[3]/div[4]/div/div/main/div/div[2]/div[1]/div")

        #initial height
        last_scroll=0

        while True:
            #scroll of 500px each time to mimic human interaction
            driver.execute_script("arguments[0].scrollTop += 500;", column_on_the_left)
            time.sleep(wait)  # add waiting time
            
            #obtain new height page
            new_position_scroll = driver.execute_script("return arguments[0].scrollTop;", column_on_the_left)
            
            # Verify if scoll is over. if new heigh is equal to last height, we reached the bottom
            if new_position_scroll == last_scroll:
                print("Reached end of the column")
                break
            last_scroll = new_position_scroll  # update the height for next page
    
    except Exception as e:
        print(f"Error during scrollinh: {e}")


########### THIRD FUNCTION 

# Function to collect jobs on each page
def scrape_jobs_on_page(driver):
    
    # Scroll to load jobs
    scroll_list_to_bottom(driver)
    #Wait for jobs to load
    #WebDriverWait(driver, 10).until(
        #EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.job-card-list__title')))

    WebDriverWait(driver, 40).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/jobs/view')]")))

    # extract all “enabled” and “disabled” job elements
    job_title_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'job-card-list__title') or contains(@class, 'disabled') and contains(@class, 'job-card-list__title')]")

    print(f"Found {len(job_title_elements)} job cards on this page.")  # Debugging line
    
    job_titles = []
    job_links = []
    

    for job_title_element in job_title_elements:
        # Get job title
        job_title = job_title_element.text.strip() if job_title_element.text else "No title found"
        
        # Get job link
        job_link = job_title_element.get_attribute('href')
        
        job_titles.append(job_title)
        job_links.append(job_link)

    return job_titles, job_links


########## FOURTH FUNCTION 

# This function allows to go to the next page without using the button "next", because the button is not always available

def click_button_page(driver, current_page):
    try:
        # Trova tutti i bottoni della paginazione
        buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[contains(@aria-label, 'Page')]"))
        )
        
        # Trova il bottone corrispondente alla pagina successiva
        next_page_number = current_page + 1  # Incrementa il numero della pagina
        for button in buttons:
            # Verifica se il bottone ha il testo della pagina successiva
            if button.text.strip() == str(next_page_number):
                # Scorri per assicurarti che il bottone sia visibile
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                
                # Aspetta che il bottone sia cliccabile e clicca
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button)).click()
                
                print(f"Clicked on Page {next_page_number}")  # Debug
                time.sleep(3)  # Pausa per permettere il caricamento della nuova pagina
                return True  # Restituisce True se è stato cliccato con successo
        
        print("No more pages to click.")
        return False  # Restituisce False se non ci sono più bottoni per pagine successive

    except Exception as e:
        print(f"Errore durante il clic sui bottoni della paginazione: {e}")
        return False  # Restituisce False in caso di errore

######## FIFTH FUNCTION 
# This function allows to scrape all pages and collects the job links

def scrape_all_pages(driver):
    all_job_titles = []
    all_job_links = []
    page_number = 1  # to count pages

    while True:
        print(f"Scraping Page {page_number}")  # Debug
        job_titles, job_links = scrape_jobs_on_page(driver)
        all_job_titles.extend(job_titles)
        all_job_links.extend(job_links)

        #If there is button "Next"
        #if not click_next_page(driver): #page number must be given as a parameter if there is no button "next"
        #    print("No more pages. Scraping completed.")
        #   break  # The cycle is broken if there is no more button "Next"

        # Prova a cliccare i Button
        if not click_button_page(driver, page_number): #page number must be given as a parameter if there is no button "next"
            print("No more pages. Scraping completed.")
            break  # The cycle is broken if there is no more button "Next"

        page_number += 1  # Incrementa il numero della pagina
        time.sleep(5)  # Ritardo per sicurezza

    # make sure to scrape the last page
    #print(f"Scraping final page {page_number}")
    #job_titles, job_links = scrape_jobs_on_page(driver)
    #all_job_titles.extend(job_titles)
    #all_job_links.extend(job_links)

    return all_job_titles, all_job_links

#execute web scraping for all pages
all_job_titles, all_job_links = scrape_all_pages(driver)



############# CREATION OF THE DATA FRAME 
# Create data frame with Job titles and job links
job_offers_df = pd.DataFrame({
    'Job Title': all_job_titles,
    'Job Link': all_job_links
})

print(job_offers_df.shape)

print(job_offers_df.columns)
print(job_offers_df.head())


# Filter job titles with "/jobs/view/" (because the others are the recommended ones and not the result of our search)
filtered_df = job_offers_df[job_offers_df['Job Link'].str.contains('/jobs/view/')]

print(filtered_df.shape)


############ SIXTH FUNCTION 

# function to get job details
def get_job_details(filtered_links):
    # Initialise empty lists
    company_names = []
    company_links = []
    job_locations = []
    job_descriptions = []
    
    for index, job_link in enumerate(filtered_links, start=1):
    # click on job link
        print(f"I am clicking on job number: {index}")
        driver.get(job_link)
        time.sleep(3)  # Attendi che la pagina si carichi

        
        try:
            # Find the company link
            company = driver.find_element(By.CLASS_NAME, 'job-details-jobs-unified-top-card__company-name')
            company_href = company.find_element(By.TAG_NAME, 'a')
            job_location_element = driver.find_element(By.XPATH, "/html/body/div[7]/div[3]/div[2]/div/div/main/div[2]/div[1]/div/div[1]/div/div/div/div[3]/div/span[1]")

            # Extract company name
            company_name = company.text.strip()
            # Extract href
            company_link = company_href.get_attribute('href')
            # Extract location
            location = job_location_element.text.strip()
            
            # Append data to lists
            company_names.append(company_name)
            company_links.append(company_link)
            job_locations.append(location)
            
        except Exception as e:
            print("Error:", e)

            # If there is an error, append None
            company_names.append(None)
            company_links.append(None)
            job_locations.append(None)
        
        try:
            # Attendi che il pulsante "See more" sia cliccabile e cliccalo
            see_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Click to see more description']"))
            )
            see_more_button.click()
            time.sleep(2)  # Wait for the description to expand


            # Now extract the job description from the <p> tags inside the job details section
            description_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mt4"))
            )
            
            # Find all <p> tags inside the description container
            paragraphs = description_container.find_elements(By.TAG_NAME, 'p')
            
            # Combine the text of all <p> elements into a single string
            full_job_description = "\n".join([para.text for para in paragraphs])

            # Append job description to the list
            job_descriptions.append(full_job_description)


        except Exception as e:
            print("Error:", e)
            # If there is an error, append None for job description
            job_descriptions.append(None)

    return company_names, company_links, job_locations, job_descriptions

######### APPLYING THE FUNCTION 

# Obtain the details of each job offer (company names, links, locations, and descriptions)
company_names, company_links, job_locations, job_descriptions = get_job_details(filtered_df['Job Link'].tolist())

# Add new columns to the DataFrame
filtered_df['Company Name'] = company_names
filtered_df['Company Link'] = company_links
filtered_df['Location'] = job_locations
filtered_df['Job Description'] = job_descriptions

# Optional: Inspect the updated DataFrame
print(filtered_df.head())

# convert the enriched dataframe to a csv
filtered_df.to_csv('job_offers_linkedin.csv', index=False)


