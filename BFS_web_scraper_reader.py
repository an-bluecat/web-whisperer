from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time

from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document


class BFSWebScraperReader(BaseReader):
    """BFS Web Scraper for websites.
    Scrapes pages from the web using a breadth-first search algorithm.
    Args:
        prefix (str): URL prefix to focus the scraping.
        max_depth (int): Maximum depth for BFS.
    """

    def __init__(self, prefix: str, max_depth: int = 10) -> None:
        """Initialize with parameters."""
        self.prefix = prefix
        self.max_depth = max_depth
        self.driver = self.setup_driver()

    def setup_driver(self):
        opt = webdriver.ChromeOptions()
        opt.add_argument("--start-maximized")
        chromedriver_autoinstaller.install()
        return webdriver.Chrome(options=opt)

    def clean_url(self, url):
        return url.split('#')[0]

    def restart_driver(self):
        self.driver.quit()
        self.driver = self.setup_driver()

    # def extract_content(self):
    #     exclude_tags = ['header', 'footer', 'nav', 'aside']
    #     exclude_classes = ['header', 'footer', 'sidebar', 'navigation', 'menu',
    #                        'main-menu', 'footer-menu', 'widget', 'sidebar-widget', 'ad', 'advertisement']

    #     content = ''
    #     elements = self.driver.find_elements(By.XPATH, "//*")
    #     for element in elements:
    #         tag = element.tag_name.lower()
    #         class_name = element.get_attribute("class").lower()
    #         if tag not in exclude_tags and not any(cls in class_name for cls in exclude_classes):
    #             content += element.text + '\n'
    #     return content

    def extract_content(self):

        # exclude_tags = {'header', 'footer', 'nav', 'aside'}
        # exclude_classes = {'header', 'footer', 'sidebar', 'navigation', 'menu',
        #                    'main-menu', 'footer-menu', 'widget', 'sidebar-widget', 'ad', 'advertisement'}

        # content = ''
        # try:
        #     # Adjust the selector as needed for the specific website
        #     elements = self.driver.find_elements(
        #         By.XPATH, "//div | //p | //span")
        #     for element in elements:
        #         if element.is_displayed():
        #             tag = element.tag_name.lower()
        #             class_attribute = element.get_attribute("class")
        #             class_name = class_attribute.lower() if class_attribute else ""

        #             if tag not in exclude_tags and not any(cls in class_name for cls in exclude_classes):
        #                 element_text = element.text.strip()
        #                 if element_text:
        #                     content += element_text + '\n'

        # except Exception as e:
        #     print(f"Error occurred: {e}")

        # return content

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))
        body_element = self.driver.find_element(By.TAG_NAME, "body")
        return body_element.text.strip()

    # def extract_links(self, current_url):
        # try:
        #     self.driver.get(current_url)
        #     soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        #     links = [link.get('href')
        #              for link in soup.find_all('a') if link.get('href')]
        #     return links
        # except WebDriverException:
        #     self.restart_driver()
        # except Exception as e:
        #     print(
        #         f"Error occurred while extracting links from {current_url}: {e}")
        #     return []
    def extract_links(self):
        js_script = """
            var links = [];
            var elements = document.getElementsByTagName('a');
            for (var i = 0; i < elements.length; i++) {
                var href = elements[i].href;
                if (href) {
                    links.push(href);
                }
            }
            return links;
            """
        return self.driver.execute_script(js_script)

    def load_data(self, base_url: str) -> List[Document]:
        """Load data from the base URL using BFS algorithm.
        Args:
            base_url (str): Base URL to start scraping.
        Returns:
            List[Document]: List of scraped documents.
        """
        added_urls = set()
        urls_to_visit = [(base_url, 0)]
        documents = []

        while urls_to_visit:
            current_url, depth = urls_to_visit.pop(0)

            print(f"Visiting: {current_url}, {len(urls_to_visit)} left")

            if depth > self.max_depth:
                continue
            try:
                self.driver.get(current_url)
                page_content = self.extract_content()

                # links = self.driver.find_elements(By.TAG_NAME, 'a')
                links = self.extract_links()
                # clean all urls
                links = [self.clean_url(link) for link in links]
                # extract new links
                links = [link for link in links if link not in added_urls]
                print(f"Found {len(links)} new potential links")
                for href in links:
                    try:
                        if href.startswith(self.prefix):
                            urls_to_visit.append((href, depth + 1))
                            added_urls.add(href)
                    except Exception:
                        continue

                documents.append(Document(text=page_content,
                                 extra_info={"URL": current_url}))
                time.sleep(1)

            except WebDriverException:
                print(f"WebDriverException encountered, restarting driver...")
                self.restart_driver()
            except Exception as e:
                print(
                    f"An unexpected exception occurred: {e}, skipping URL...")
                continue

        self.driver.quit()
        return documents


# Example usage
# prefix = 'https://docs.llamaindex.ai/'
# base_url = 'https://docs.llamaindex.ai/'
# scraper = BFSWebScraperReader(prefix=prefix, max_depth=10)
# documents = scraper.load_data(base_url=base_url)


scraper = BFSWebScraperReader(
    prefix='https://docs.splunk.com/Documentation/SplunkCloud', max_depth=10)

# Start scraping from a base URL
documents = scraper.load_data(base_url='https://docs.splunk.com/Documentation/SplunkCloud')
print(documents)
