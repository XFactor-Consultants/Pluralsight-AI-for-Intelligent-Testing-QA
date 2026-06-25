#m1
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

APP_URL = "http://localhost:3000/login"

HEALED_LOCATORS = {
    "email-input":    "user-email",
    "password-field": "user-password",
    "login-submit":   "submit-btn",
}

def make_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def find_with_healing(driver, element_id):
    try:
        return driver.find_element(By.ID, element_id)
    except NoSuchElementException:
        fallback = HEALED_LOCATORS.get(element_id)
        if fallback:
            print(f"  [healed] '{element_id}' not found — retrying with '{fallback}'")
            return driver.find_element(By.ID, fallback)
        raise

def run_login_test(driver, label, heal=False):
    print(f"\n[{label}]")
    try:
        driver.get(APP_URL)
        if heal:
            find_with_healing(driver, "email-input").send_keys("qa@example.com")
            find_with_healing(driver, "password-field").send_keys("password123")
            find_with_healing(driver, "login-submit").click()
        else:
            driver.find_element(By.ID, "email-input").send_keys("qa@example.com")
            driver.find_element(By.ID, "password-field").send_keys("password123")
            driver.find_element(By.ID, "login-submit").click()
        print("  PASS")
    except NoSuchElementException as e:
        print(f"  FAIL — element not found: '{e.msg}'")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_login_test(make_driver(), "Standard Selenium — expected FAIL", heal=False)
    run_login_test(make_driver(), "Healenium Self-Healing — expected PASS", heal=True)
