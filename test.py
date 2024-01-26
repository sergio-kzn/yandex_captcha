"""
скрипт для примера использования антикапчи
"""
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from main import Solver

URL = 'https://ya.ru/search/?text=%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80%D1%8B+%D0%B2+%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0%D1%85&lr=43'


def run_search():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-site-isolation-trials')
    chrome_options.add_argument("--disable-gpu")

    webdriver_service = Service(ChromeDriverManager().install())
    webdriver_service.start()
    driver = uc.Chrome(service=webdriver_service, options=chrome_options, version_main=120)

    driver.implicitly_wait(10)
    driver.get(URL)
    while True:  # обновляем страницу пока не получим капчу
        if end_page := driver.find_elements(By.CSS_SELECTOR, '.Pager-Content'):
            # удачная загрузка, капча не появилась
            driver.refresh()

        if 'showcaptcha' in driver.current_url:
            solver = Solver(driver)
            solver.solve()
            print('Капча решена', solver.result)
            break


if __name__ == '__main__':
    run_search()
