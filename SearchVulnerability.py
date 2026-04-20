import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

with open("first504_ofless4000ins_nonv.csv", newline="", encoding="utf-8") as infile, \
    open("scan_results_first504_ofless4000ins_nonv_2.csv", "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)
    writer.writerow(["slug", "has_vulnerability"])

    for row in reader:
        slug = row["slug"]
        url = f"https://www.wordfence.com/threat-intel/vulnerabilities/wordpress-plugins/{slug}"

        driver.get(url)
        time.sleep(4)

        page_text = driver.page_source.lower()

        if "triple" in page_text:
            result = 1
        else:
            result = 0

        writer.writerow([slug, result])

        print(slug, result)

        time.sleep(2)

driver.quit()