import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import settings
import ctypes


def click_element(driver, xpath):
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    ).click()


def login(browser):
    username = settings.USERNAME
    password = settings.PASSWORD
    text_inputs = browser.find_elements(
        By.CLASS_NAME, "newlogindialog_TextInput_2eKVn")
    text_inputs[0].send_keys(username)
    text_inputs[1].send_keys(password)
    click_element(
        browser, "//button[@type='submit']")

    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.ID, "global_header"))
    )
    if settings.MFA_METHOD == 1:
        pass
    elif settings.MFA_METHOD == 2:
        input("Please press Enter if you have allowed the login on your mobile phone.")
    elif settings.MFA_METHOD == 3:
        twofactor_code = input("Please enter your 2-FA Code: ")
        twofactor_inputs = browser.find_elements(
            By.XPATH, "//div[@class='newlogindialog_SegmentedCharacterInput_1kJ6q']/input")
        for i, digit in enumerate(twofactor_code):
            twofactor_inputs[i].send_keys(digit)
    time.sleep(2)


def update_codes_file(code, browser):
    try:
        browser.find_element(
            By.XPATH, f'//span[@class="checkout_error" and contains(@style, "display: block") and contains(text(), "{settings.AccountOwnsProduct}")]')
        with open("codes.txt", "r+") as f:
            file_content = f.read().replace(code, f"+{code}")
            f.seek(0)
            f.write(file_content)
    except:
        try:
            browser.find_element(
                By.XPATH, f'//span[@class="checkout_error" and contains(@style, "display: block") and contains(text(), "{settings.KeyNotValid}")]')
            with open("codes.txt", "r+") as f:
                file_content = f.read().replace(code, f"!{code}")
                f.seek(0)
                f.write(file_content)
        except:
            try:
                browser.find_element(
                    By.XPATH, f'//span[@class="checkout_error" and contains(@style, "display: block") and contains(text(), "{settings.TooManyAttemps}")]')
                msg = "Your steam account got rate limited. You have to wait 1 hour until you can continue."
                title = "Rate limit"
                ctypes.windll.user32.MessageBoxW(0, msg, title, 0x10)
                return False
            except:
                with open("codes.txt", "r+") as f:
                    file_content = f.read().replace(code, f"#{code}")
                    f.seek(0)
                    f.write(file_content)
                click_element(
                    browser, "//a[@href=\"javascript:DisplayPage('code');\"]")
    return True


browser = webdriver.ChromiumEdge()
browser.maximize_window()
browser.get("https://store.steampowered.com/")
time.sleep(5)
click_element(
    browser, "//a[@class='global_action_link']")
time.sleep(5)
login(browser)
with open("codes.txt", "r+") as f:
    codes = f.read().splitlines()

for code in codes:
    if not code.startswith("#") and not code.startswith("+") and not code.startswith("!"):
        browser.get(
            f"https://store.steampowered.com/account/registerkey?key={code}")
        time.sleep(1)
        click_element(browser, "//input[@type='checkbox']")
        click_element(browser, "//a[@id='register_btn']")
        time.sleep(2)
        if not update_codes_file(code, browser):
            break

browser.quit()
