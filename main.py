import os

from anticaptchaofficial.imagetocoordinates import *
from anticaptchaofficial.imagecaptcha import *

import undetected_chromedriver as uc
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By


class Solver:
    def __init__(self, driver):
        self.verbose = VERBOSE
        self.key = KEY
        self.driver: uc.Chrome = driver
        self.img = None
        self.exercise = None
        self.result = None

    def solve(self):
        # Промежуточный шаг проверки (Галочка "Я не робот" или слайдер)
        self.intermediate_verification_step()

        # Получим картинку с заданием в based64 и текст задания
        self.get_img()
        self.get_exercise()

        # Отправляем на решение
        if self.exercise in ['Введите текст с картинки']:
            self.image_to_text_task()
        elif self.exercise in ['Нажмите в таком порядке:']:
            self.image_to_coordinates()
        else:
            raise Exception('Неизвестное задание у капчи', self.exercise)

        # нажимаем ОТПРАВИТЬ
        self.submit()

    def submit(self):
        self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    def get_exercise(self):
        if exercise := self.driver.find_elements(By.CSS_SELECTOR, 'span.AdvancedCaptcha-DescriptionText'):
            self.exercise = exercise[0].text.strip()
            return
        if exercise := self.driver.find_elements(By.CSS_SELECTOR, 'label.AdvancedCaptcha-FormLabel'):
            # иногда попадает задание "Введите текст с картинки"
            self.exercise = exercise[0].text.strip()
            return

    def get_img(self):
        # для отправки картинки на задание, надо чтобы у картинки было видно само задание.
        form_actions = self.driver.find_element(By.CSS_SELECTOR, 'div.AdvancedCaptcha-FormActions')
        form_footer = self.driver.find_element(By.CSS_SELECTOR, 'div.AdvancedCaptcha-Footer')
        self.driver.execute_script("arguments[0].style.display = 'none';", form_actions)
        self.driver.execute_script("arguments[0].style.display = 'none';", form_footer)

        advanced_captcha = self.driver.find_element(By.CSS_SELECTOR, 'div.AdvancedCaptcha.AdvancedCaptcha_silhouette')
        self.img = advanced_captcha.screenshot_as_base64
        # advanced_captcha.screenshot('img.png')

        self.driver.execute_script("arguments[0].style.display = 'flex';", form_actions)
        self.driver.execute_script("arguments[0].style.display = 'block';", form_footer)

    def intermediate_verification_step(self):
        if check_button := self.driver.find_elements(By.CSS_SELECTOR, '.CheckboxCaptcha-Button'):
            check_button[0].click()
        # тут будет код решения для слайдера

    def element_clicked(self, element, x=0, y=0):
        # кликаем на элемент с указанными x y отступами.
        # работает только если окно браузера развернуто.
        canvas_x_offset = self.driver.execute_script("return window.screenX + (window.outerWidth - window.innerWidth) / 2 - window.scrollX;")
        canvas_y_offset = self.driver.execute_script("return window.screenY + (window.outerHeight - window.innerHeight) - window.scrollY;")
        element_location = (element.rect["x"] + canvas_x_offset + x, element.rect["y"] + y)

        action = ActionBuilder(self.driver)
        action.pointer_action.move_to_location(*element_location)
        action.pointer_action.click()
        action.pointer_action.pause(1)
        action.perform()

    def image_to_text_task(self):
        solver = imagecaptcha()
        solver.set_verbose(self.verbose)
        solver.set_key(self.key)

        solver.set_soft_id(0)
        solver.set_comment(self.exercise)

        captcha_text = solver.solve_and_return_solution(None, body=self.img)
        if captcha_text != 0:
            self.result = captcha_text
            self.driver.find_element(By.CSS_SELECTOR, 'input.Textinput-Control').send_keys(self.result)
        else:
            print("task finished with error " + solver.error_code)

    def image_to_coordinates(self):
        solver = imagetocoordinates()
        solver.set_verbose(self.verbose)
        solver.set_key(self.key)
        solver.set_mode("points")

        solver.set_comment(self.exercise)
        coordinates = solver.solve_and_return_solution(None, body=self.img)
        if coordinates != 0:
            self.driver.maximize_window()
            self.result = coordinates
            # кликаем по полученным результатам
            for dx, dy in self.result:
                advanced_captcha = self.driver.find_element(By.CSS_SELECTOR, 'div.AdvancedCaptcha-ImageWrapper')
                self.element_clicked(advanced_captcha, dx, dy)
        else:
            print("task finished with error "+solver.error_code)


VERBOSE = os.getenv('VERBOSE_ANTICAPTCHA', 1)
KEY = os.getenv('KEY_API_ANTICAPTCHA')

if not KEY:
    raise Exception('Не указан ключ, https://anti-captcha.com/clients/settings/apisetup')
