from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import chromedriver_autoinstaller
import time


def scrape_with_prefix(base_url, prefix):
    def setup_driver():
        opt = webdriver.ChromeOptions()
        opt.add_argument("--start-maximized")
        chromedriver_autoinstaller.install()
        return webdriver.Chrome(options=opt)

    def clean_url(url):
        # Split the URL at '#' and return the first part
        return url.split('#')[0]

    def restart_driver(driver):
        driver.quit()
        return setup_driver()

    def extract_content(driver):
        # Define tags and classes to exclude
        exclude_tags = ['header', 'footer', 'nav', 'aside']
        exclude_classes = ['header', 'footer', 'sidebar', 'navigation', 'menu',
                           'main-menu', 'footer-menu', 'widget', 'sidebar-widget', 'ad', 'advertisement']

        content = ''
        elements = driver.find_elements(By.XPATH, "//*")
        for element in elements:
            tag = element.tag_name.lower()
            class_name = element.get_attribute("class").lower()
            if tag not in exclude_tags and not any(cls in class_name for cls in exclude_classes):
                content += element.text + '\n'
        return content

    driver = setup_driver()
    added_urls = set()
    urls_to_visit = [base_url]

    while urls_to_visit:
        current_url = urls_to_visit.pop(0)

        try:
            driver.get(current_url)
            print(f"Visiting: {current_url}")

            # Extract and print filtered page content
            page_content = extract_content(driver)
            print(f"Filtered Content: {page_content[:100]}...")

            # Finding and processing links
            links = driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    href = clean_url(link.get_attribute('href'))
                    if href not in added_urls and href and href.startswith(prefix):
                        print(f"Found matching link: {href}")
                        urls_to_visit.append(href)
                        added_urls.add(href)
                except Exception as e:
                    print(
                        f"Encountered an exception with a link: {e}, skipping...")
                    continue

            time.sleep(1)

        except WebDriverException as e:
            print(f"WebDriverException encountered: {e}, restarting driver...")
            driver = restart_driver(driver)
        except Exception as e:
            print(f"An unexpected exception occurred: {e}, skipping URL...")
            continue

    driver.quit()


# Example usage
prefix = 'https://docs.llamaindex.ai/'
base_url = 'https://docs.llamaindex.ai/'
scrape_with_prefix(base_url, prefix)
