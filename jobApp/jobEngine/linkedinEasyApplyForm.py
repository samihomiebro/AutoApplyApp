from bs4 import BeautifulSoup
import json
import requests
from linkedinEasyApplyLegacyCode import EasyApplyLinkedin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchElementException
import os
import time
import csv
from formFillBase import FormFillBase
from seleniumWrapper import WebScraper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumForm import Field, SeleniumFormHandler
from selenium.webdriver.support.ui import Select
from candidateProfile import CandidateProfile
from collections.abc import Iterable


''' use linkedin easy apply form template'''


class LinkedInEasyApplyForm(SeleniumFormHandler):
    def __init__(self, candidate_profile: CandidateProfile, url=None, csv_links='jobApp/data/links.csv'):
        self.links = []
        self.csv_file = csv_links
        super().__init__(url=url)
        if csv_links:
            print("loading links from file directly")
            self.load_links_from_csv()
        scraper = WebScraper('jobApp/secrets/linkedin.json', headless=False)
        bot = scraper.createJobSearchSession()
        self.driver = bot.driver  # pass the new driver to current one
        self.label_elements_map = {}
        self.candidate = candidate_profile
        self.button_apply_clicked = False

        # self.driver.implicitly_wait(20)

    def load_links_from_csv(self):
        # load only onsite links
        links = []  # list of intern lists
        if os.path.isfile(self.csv_file):
            # Read
            with open(self.csv_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for i, row in enumerate(reader):
                    if row[5] == "None":  # append only easy apply links
                        links.append(row[4])  # intern links
        self.links = links
        print(f"onsite apply links count: {len(links)}")

    def get_the_url(self, url=None):
        if url is None:
            url = self.url
        # navigate to the URL
        try:  # try to open link in browser
            # Open a new window and switch to it
            # self.driver.execute_script("window.open('','_blank');")
            # self.driver.switch_to.window(self.driver.window_handles[1])
            # print("opening job link in new tab")
            # self.driver.execute_script("window.open(arguments[0], '_blank');", url)
            self.driver.get(url)
            # self.status= True
            # self.driver.switch_to.window(self.driver.window_handles[0])
            # self.driver.quit()
        except:
            print("can't open link in the browser")
            self.status = False

    def clickApplyPage(self):
        # click on the easy apply button, skip if already applied to the position
        try:
            print("try clicking button easy apply")
            # Wait for the button element to be clickable
            button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@aria-label, 'Easy Apply')]"))
            )
            # button = self.driver.find_element(By.XPATH, "//span[@class='artdeco-button__text' and text()='Easy Apply']")
            button.click()
            self.button_apply_clicked = True
            print("button apply clicked")

            # if already applied or not found
        except:
            print('easy apply job button is not found, retry..')
            self.status = False

    def _find_application_form(self):
      # fill the expected first page template
        try:
            self.div_element_form_holder = self.driver.find_element(
                By.CSS_SELECTOR, 'div.artdeco-modal.artdeco-modal--layer-default.jobs-easy-apply-modal')
            if self.div_element_form_holder:
                # Find the form element within the div
                form_element = self.div_element_form_holder.find_element(
                    By.TAG_NAME, 'form')
                if form_element:
                    print(f"form_element found: form object {form_element}")
                    self.form = form_element  # pass the form to parent
                else:
                    # The form element was not found within the div
                    print('Form element not found')
            else:
                # The div element was not found
                print('Div element not found')
        except:
            print("no page found")
    #### user details section ######
    def _send_user_contact_infos(self, user: CandidateProfile, elements_dict: dict[WebElement]):
        for label, element in elements_dict.items():
            if label == 'First name':
                self.send_value(element, user.firstname)
            elif label == 'Last name':
                self.send_value(element, user.lastname)
            #elif label == 'Phone country code':
            #    self.select_option(element, user.phone_code)
            elif label == 'Mobile phone number':
                self.send_value(element, user.phone_number)
            elif label == 'Email address':
                self.select_option(element, user.email)
            else:
                raise ValueError("Unsupported label: {}".format(label))

    def _send_user_documents(self, user: CandidateProfile, elements_dict: dict[WebElement]):
        for label, element in elements_dict.items():
            if label == 'Upload resume':
                self.send_value(element, user.resume.file_path)
            elif label == "Upload cover letter": # ignore cover letter: need specification later
                pass
            else:
                raise ValueError("Unsupported label: {}".format(label))

    def _send_user_answers(self, user: CandidateProfile, elements_dict: dict[WebElement]):
        # try to answer most form questions
        for label, element in elements_dict.items():
            if "salary" or "Gehalt" in label:
                self.send_value(element, "70000")
            elif "someone" in label:
                self.send_value(element, "no")
            elif "English" or "German" in label:
                self.send_value(element, "C1")
            elif "Englisch" or "Deustch" in label:
                self.send_value(element, "Verhandlungssicher")
            elif "Visa" in label:
                self.send_value(element, "No")
            else:
                self.send_value(element , "5")


    def send_value(self, element: WebElement, value: str):
        element_type = element.get_attribute("type")
        if element_type == "file":
            print("The web element is a file input.")
            print(f"sending file path: {value}")
            element.send_keys(value)
        elif element_type == "text":
            element.clear()
            element.send_keys(value)
        else:
            print("input type not recognized")

    def select_option(self, select_element, user_value):
        select = Select(select_element)
        if isinstance(select.options, Iterable):
            if user_value in select.options:
                select.select_by_visible_text(user_value)
            else:  # return first option to bypass error; needed to be corrected
                select.select_by_visible_text(
                    select.first_selected_option.text)
            return
        else:
            select.select_by_visible_text(select.first_selected_option.text)

    def _find_divs_document_upload(self) -> list[WebElement]:
        if self.form != None:  # if form is found
            try:
                div_elements = self.form.find_elements(
                    By.XPATH, "//div[contains(@class, 'js-jobs-document-upload__container') and contains(@class, 'display-flex') and contains(@class, 'flex-wrap')]")
                return div_elements
            except NoSuchElementException:
                print("No upload elements found")

    def _find_divs_selection_grouping(self) -> list[WebElement]:
        if self.form != None:  # if form is found
            try:
                # Find the div with class "jobs-easy-apply-form-section__grouping"
                divs = self.form.find_elements(
                    By.CSS_SELECTOR, 'div.jobs-easy-apply-form-section__grouping')
                print("found divs with selection grouping")
                return divs
            except NoSuchElementException:
                print("No div elements found")

    def _createDictFromFormDiv(self, divs:  list[WebElement]):
        # Iterate over the divs and extract the label and corresponding input/select values
        for div in divs:
            try: 
                label_element = div.find_element(By.TAG_NAME, 'label')
                label = label_element.text.strip()
                print(f"Label: {label}")
                try:
                    # Attempt to find the 'input' element inside the 'div' element
                    input_element = div.find_element(By.TAG_NAME, 'input')
                    value = input_element.get_attribute('value').strip()
                    print(f"Input Value: {value}")
                    # assign label with input element object
                    self.label_elements_map[label] = input_element
                except NoSuchElementException:
                    # Handle the case when 'input' element is not found
                    print("Input element not found.")
                except:
                    # Handle any other unexpected exceptions that may occur during the 'input' element search.
                    print("An unexpected error occurred while searching for the input element.")
                else:
                    try:
                        # Attempt to find the 'select' element inside the 'div' element
                        select_element = div.find_element(By.TAG_NAME, 'select')
                        # Create a Select object
                        select = Select(select_element)
                        # assign label with select element object
                        selected_option = select.options
                        print(f"Selected option: {selected_option}")  # This will print the visible text of the selected option.
                        self.label_elements_map[label] = select_element
                    except NoSuchElementException:
                        # Handle the case when 'select' element is not found
                        print("Select element not found.")
                    except:
                        # Handle any other unexpected exceptions that may occur during the 'select' element search.
                        print("An unexpected error occurred while searching for the select element.")
            except NoSuchElementException:
                # Handle the case when 'select' element is not found
                print("no label element not found.")        # Iterate over the dictionary
                return
        for key in self.label_elements_map:
            value = self.label_elements_map[key]
            print(f"Key: {key}, Value: {value}")

    #@Note: use translator to compare with contact info
    def fillFormPage(self):
        if self._find_header(self.form) == "Contact info" or "Kontaktinfo":
            self._fill_contact_info(self.form)
            self.label_elements_map.clear()
        if self._find_header(self.form) == "Resume" or "Lebenslauf":
            self._fill_resume(self.form)
            self.label_elements_map.clear()
        if self._find_header(self.form) == "Additional" or "Additional Questions" or "Weitere Fragen":
            pass

    def fillOptionsSelectPage(self):
        # fill the expected options select page template
        pass
    def _fill_contact_info(self, form: WebElement):
        #self._find_application_form()  # try to find the form
        try:
            divs = self._find_divs_selection_grouping()
            if len(divs) != 0:
                # create the key,value pair for each element on the form
                self._createDictFromFormDiv(divs)
                # fill the form with candidate data
                self._send_user_contact_infos(self.candidate, self.label_elements_map)
                # click next buttton
                #self._clickNextPage(self.form)
        except:
            print("no contact infos to fill")
            return

    def _fill_resume(self, form: WebElement):
        #self._find_application_form()  # try to find the form
        try:
            divs = self._find_divs_document_upload()
            if len(divs) != 0:
                # create the key,value pair for each element on the form
                self._createDictFromFormDiv(divs)
                # fill the form with candidate data
                self._send_user_documents(self.candidate, self.label_elements_map)
                # click next buttton
                #self._clickNextPage(self.form)
        except:
            print("no resume to fill")
            return
    def _fill_additionals(self, form: WebElement):
        #self._find_application_form()  # try to find the form
        try:
            divs = self._find_divs_selection_grouping()
            if len(divs) != 0:
                # create the key,value pair for each element on the form
                self._createDictFromFormDiv(divs)
                # fill the form with candidate data
                self._send_user_documents(self.candidate, self.label_elements_map)
                # click next buttton
                #self._clickNextPage(self.form)
        except:
            print("no resume to fill")
            return
    ######## find hear ####
    def _find_header(self, form: WebElement):
        try:
            # Find the <h3> element with class "t-16 t-bold".
            h3_element = form.find_element(By.CSS_SELECTOR, 'h3.t-16.t-bold')
            # Print the inner text of the element.
            print(f"page header: {h3_element.text}")
            return h3_element.text
        except NoSuchElementException:
            print("no header found")
    ####### Click Buttons Pages #########
    def clickApplyPage(self):
        # click on the easy apply button, skip if already applied to the position
        try:
            print("try clicking button easy apply")
            # Wait for the button element to be clickable
            button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@aria-label, 'Easy Apply')]"))
            )
            # button = self.driver.find_element(By.XPATH, "//span[@class='artdeco-button__text' and text()='Easy Apply']")
            button.click()
            print("button apply clicked")
        # if already applied or not found
        except:
            print('easy apply job button is not found, skipping')
            self.status = False
    def _clickNextPage(self, form: WebElement):
        # click the next page button
        # Find the button using its aria-label attribute
        try:
            button = form.find_element(By.XPATH, "//span[text()='Next']")
            # Click the button
            button.click()
            self.nextClicked = True
            return True
        except NoSuchElementException:
            # Handle the case when 'select' element is not found
            print("next button element not found.")
            self.nextClicked = False
            return False
    def _clickReviewPage(self, form: WebElement):
        # click the review page button
        # Find the button using its aria-label attribute
        try:
            button = form.find_element(By.XPATH, "//span[text()='Review']")
            # Click the button
            button.click()
            self.ReviewClicked = True
            return True
        except NoSuchElementException:
            # Handle the case when 'select' element is not found
            print("Review button element not found.")
            self.ReviewClicked = False
            return False
    def _clickSubmitPage(self, form: WebElement):
        # click the submit page button
        # Find the button using its aria-label attribute
        try:
            button = form.find_element(By.XPATH, "//span[text()='Submit application']")
            # Click the button
            button.click()
            self.SubmitClicked = True
            return True
        except NoSuchElementException:
            # Handle the case when 'select' element is not found
            print("Submit button element not found.")
            self.SubmitClicked = False
            return False
    ########### Detect PAge #############
    def _detectNextButtonForm(self, form: WebElement):
        # Find the button using its aria-label attribute
        try:
            button = form.find_element(By.XPATH, "//span[text()='Next']")
            return True
        except NoSuchElementException:
            # Handle the case when 'select' element is not found
            print("next button element not found.")
            return False
    def _detectReviewButtonForm(self, form: WebElement):
        # Find the button using its aria-label attribute
        try:
            button = form.find_element(By.XPATH, "//span[text()='Review']")
            return True
        except NoSuchElementException:
            # Handle the case when 'select' element is not found
            print("Review button element not found.")
            return False
    def _detectSubmitButtonForm(self, form: WebElement):
        # Find the button using its aria-label attribute
        try:
            button = form.find_element(By.XPATH, "//span[text()='Submit application']")
            return True
        except NoSuchElementException:
            # Handle the case when 'select' element is not found
            print("Submit button element not found.")
            return False
    def _detect_form_page_type(self, form: WebElement):
        # detect if the current page has next, review or submit 
        if self._detectSubmitButtonForm(form): # only submit
            print("page form with submit detected")
            return self._execute_submit(form)
        if self._detectReviewButtonForm(form): # recursive one
            print("page form with submit detected")
            self._execute_review(form)
            return self._detect_form_page_type(form)
        if self._detectNextButtonForm(form): # recursive many
            print("page form with next detected")
            self._execute_next(form)
            return self._detect_form_page_type(form)

    ########### each case func ########
    def _execute_submit(self, form:WebElement):
        # on page submit execute
        return self._clickSubmitPage(form)
    def _execute_review(self, form:WebElement):
        # on page review execute
        self.fillFormPage()
        # return button clicker
        return self._clickReviewPage(form)

    def _execute_next(self, form:WebElement): # this 90% of the cases 
        # on page next execute
        self.fillFormPage()
        # return button clicker
        return self._clickNextPage(form)

    ####### Apply Phase #####
    def applyForJob(self, job_link: str) -> bool:
        # return true if job was success, false if job not found, deleted or can't apply
        self.get_the_url(job_link)  # get the url form the job
        self.clickApplyPage()  # try to click apply button: retry when not clicked
        if not self.button_apply_clicked:
            time.sleep(3)
            self.clickApplyPage()
        # detect form page type: 
        self._find_application_form()  # try to find the form
        self._detect_form_page_type(self.form)



        return False

    #### apply for all jobs ######
    def applyForAllLinks(self):
        for link in self.links:
            print(f"parsing link: {link}")
            self.get_the_url(link)
            self.clickApplyPage()
        while (1):
            pass


if __name__ == '__main__':
    easyApplyForm = LinkedInEasyApplyForm()
    easyApplyForm.applyForAllLinks()
