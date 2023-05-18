from selenium import webdriver
from selenium.webdriver.common.by import By


def main():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("http://vimdiesel.tk/")

    driver.implicitly_wait(3)
    login = driver.find_element(By.XPATH, '/html/body/div/div[1]/header/div/div[2]/label/span[2]')
    login.click()

    driver.find_element(By.NAME, 'username').send_keys('administrator')
    driver.find_element(By.NAME, 'password').send_keys('Password1!')
    driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div/form/div/div/button').click()

    if driver.find_elements(By.XPATH,
                            "//*[text()[contains(., 'Pogrešno korisničko ime ili lozinka!')]]").__len__() != 0:
        print("FAIL")
    else:
        print("PASS - EXPECTED")
    driver.quit()


if __name__ == "__main__":
    main()
