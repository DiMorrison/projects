from selenium import webdriver
from selenium.webdriver.common.by import By
import random


def main():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("http://vimdiesel.tk/")

    driver.implicitly_wait(5)
    login = driver.find_element(By.XPATH, '/html/body/div/div[1]/header/div/div[2]/label/span[2]')
    login.click()

    driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div/a/p').click()
    driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div/div/div/div[2]/button[1]').click()
    key = random.randint(100, 999999)
    driver.find_element(By.NAME, 'email').send_keys(str(key) + "@email.com")
    driver.find_element(By.NAME, 'username').send_keys("TestUser" + str(key))
    driver.find_element(By.NAME, 'password').send_keys("Password" + str(key) + "!")
    driver.find_element(By.NAME, 'password2').send_keys("Password" + str(key) + "!")

    driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div/form/div[2]/button[2]').click()

    driver.find_element(By.NAME, 'brojKartice').send_keys("1111444488889999")
    driver.find_element(By.NAME, 'datumValjanosti').send_keys("10/10")
    driver.find_element(By.NAME, 'cvv').send_keys("111")

    driver.find_element(By.XPATH, '/html/body/div/div[2]/div/div/form/div[2]/button[2]').click()
    if driver.find_elements(By.XPATH,
                            "//*[text()[contains(., 'USER WITH SAME NAME OR EMAIL ALREADY EXISTS')]]").__len__() != 0:
        print("FAIL")
    else:
        print("PASS - EXPECTED")
    print(key)
    driver.close()
    driver.quit()


if __name__ == "__main__":
    main()
