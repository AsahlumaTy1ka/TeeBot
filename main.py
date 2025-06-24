from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from tempfile import mkdtemp
import time
from groups import gc_names

# Group names from external file
group_names = gc_names()


def login_facebook(driver, email, password):
    driver.get("https://www.facebook.com/")
    wait = WebDriverWait(driver, 60000)

    email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    email_input.clear()
    email_input.send_keys(email)

    password_input = driver.find_element(By.ID, "pass")
    password_input.clear()
    password_input.send_keys(password)

    login_button = driver.find_element(By.NAME, "login")
    login_button.click()

    time.sleep(60)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Search Facebook']")))
    print("Logged in successfully!")


def get_first_read_more_link(driver):
    driver.get("https://gtec0.github.io")
    time.sleep(3)
    try:
        read_more_link = driver.find_element(By.PARTIAL_LINK_TEXT, "[Read More]").get_attribute("href")
        return read_more_link
    except:
        print("[ERROR] Could not find a 'Read More' link.")
        return None


def post_to_groups(driver, post_link):
    wait = WebDriverWait(driver, 30)
    if not post_link:
        print("[ERROR] No post link found to share.")
        return

    for group in group_names:
        try:
            driver.get(group)
            time.sleep(5)
            post_box = wait.until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Write something...')]")))
            post_box.click()
            time.sleep(2)
            postin = driver.find_element(By.CSS_SELECTOR, "div[role='textbox']")
            driver.execute_script("arguments[0].scrollIntoView();", postin)
            postin.click()
            time.sleep(2)
            postin.send_keys(post_link)
            time.sleep(2)
            post_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@aria-label and (contains(@aria-label, 'Post') or contains(text(), 'Post'))]")
            ))
            driver.execute_script("arguments[0].scrollIntoView();", post_button)
            post_button.click()
            print(f"[SUCCESS] Posted to {group}")
            time.sleep(10)
        except Exception as e:
            print(f"[ERROR] Could not post to {group}: {e}")


def switch_to_page(driver, page_name):
    wait = WebDriverWait(driver, 30)
    try:
        profile_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Your profile' and @role='button']")))
        profile_button.click()
        print("[+] Clicked profile button.")
        time.sleep(2)

        see_all_profiles = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'See all profiles')]")))
        see_all_profiles.click()
        print("[+] Clicked 'See all profiles' button.")

        page_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{page_name}')]")))
        page_option.click()
        print(f"[+] Switched to page: {page_name}")
        time.sleep(5)
    except Exception as e:
        print(f"[ERROR] Could not switch to page {page_name}: {e}")


def fbShare(driver, s_link, group_index=0):
    if group_index >= len(group_names):
        print("[+] Finished sharing to all groups!")
        return

    print(f"[+] Getting post to share! (Group {group_index + 1}/{len(group_names)})")
    driver.get(s_link)
    time.sleep(5)
    body_tag = driver.find_element(By.TAG_NAME, "body")

    print("[+] Looking for share button...")
    while True:
        body_tag.send_keys(Keys.TAB)
        time.sleep(0.2)
        focused_elem = driver.switch_to.active_element
        if "Share" in focused_elem.text:
            print("[+] Highlighted, clicking...")
            body_tag.send_keys(Keys.ENTER)
            time.sleep(1)
            break
        print("[+] Share not found, tabbing...")

    print("[+] Looking for groups button...")
    while True:
        body_tag.send_keys(Keys.TAB)
        time.sleep(0.2)
        focused_elem = driver.switch_to.active_element
        if "Group" in focused_elem.text:
            print("[+] Highlighted, clicking...")
            body_tag.send_keys(Keys.ENTER)
            time.sleep(1)
            break
        print("[+] Group not found, tabbing...")

    group_name = group_names[group_index]
    print(f"[+] Searching for group: {group_name}")
    while True:
        body_tag.send_keys(Keys.TAB)
        time.sleep(0.2)
        focused_elem = driver.switch_to.active_element
        if group_name in focused_elem.text:
            print(f"[+] Found group: {group_name}, clicking...")
            body_tag.send_keys(Keys.ENTER)
            time.sleep(1)
            break
        print("[+] Group not found, tabbing...")

    while True:
        body_tag.send_keys(Keys.TAB)
        time.sleep(0.2)
        focused_elem = driver.switch_to.active_element
        if "Post" in focused_elem.text:
            print("[+] Post button highlighted, clicking...")
            body_tag.send_keys(Keys.ENTER)
            time.sleep(3)
            break
        print("[+] Post button not found, tabbing...")

    print(f"[+] Shared to group: {group_name}")
    fbShare(driver, s_link, group_index + 1)


def main():
    # in future, use env vars here
    EMAIL = ""
    PASSWORD = ""

    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--start-maximized")
    chrome_options.headless = False

    temp_profile = mkdtemp()

    chrome_options.add_argument(f"--user-data-dir={temp_profile}")
    service = Service()  # Optional, can specify chromedriver path here
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://www.facebook.com")

    login_facebook(driver, EMAIL, PASSWORD)
    switch_to_page(driver, "GTec")
    fbShare(driver, "https://www.facebook.com/share/p/1672T8MfBo/")
    # post_link = get_first_read_more_link(driver)
    # post_to_groups(driver, post_link)

    driver.quit()


if __name__ == "__main__":
    main()