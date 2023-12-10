import re
from time import sleep
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains


def page_processing():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    count_errors = 0

    for i in range(5, 6):
        errors = {
            'Сайт ошибки': [],
            'Ошибка': []
        }
        goods = {'Артикул': [],
                 'Название товара': [],
                 'Цена, руб.': [],
                 'Цена до скидки, руб.': [],
                 'Цена с Ozon Premium, руб.': [],
                 'НДС, %': [],
                 'Ozon ID': [],
                 'Коммерческий тип': [],
                 'Штрихкод (Серийный номер / EAN)': [],
                 'Вес в упаковке, г': [],
                 'Ширина упаковки, мм': [],
                 'Высота упаковки, мм': [],
                 'Длина упаковки, мм': [],
                 'Ссылка на главное фото': [],
                 'Ссылки на дополнительные фото': [],
                 'Ссылки на фото 360': [],
                 'Артикул фото': [],
                 'Код ОКПД/ТН ВЭД текстиль': [],
                 'Тип': [],
                 'Бренд': [],
                 'Название модели': [],
                 'Целевая аудитория': [],
                 'Состав ткани': [],
                 'Аннотация': [],
                 'Комплектация': [],
                 'Товар подлежит обязательной маркировке': [],
                 'Rich-контент JSON': [],
                 'Использовать шаблонизатор наименований': [],
                 'Объединить на одной карточке': [],
                 'Цвет товара': [],
                 'Название цвета': [],
                 'Образец цвета': [],
                 'Плотность плетения ткани': [],
                 'Вид принта': [],
                 'Режим стирки': [],
                 'Отделка': [],
                 'Минимальный возраст ребенка': [],
                 'Максимальный возраст ребенка': [],
                 'Пол ребенка': [],
                 'Серии': [],
                 'Гарантия': [],
                 'Страна-изготовитель': [],
                 'Класс опасности товара': [],
                 'Количество заводских упаковок': [],
                 'Ошибка': [],
                 'Предупреждение': []
                 }
        for page in range(i*10 + 1, (i+1)*10 + 1):
            url = f"https://m.sima-land.ru/postelnoe-bele/p{page}/?c_id=297&f=%7B%22settlements_balance%22%3A%5B%2227503892%22%5D%7D"
            print(f"[INFO] Новая Страница объектов - {url}")
            req = requests.get(url=url, headers=headers)
            with open("data/test.html", 'w', encoding="utf-8") as file:
                file.write(req.text)
            with open("data/test.html", encoding="utf-8") as file:
                src = file.read()
            links = []
            soup = BeautifulSoup(src, 'lxml')
            items = soup.find("div", class_="N3Azx").find_all(class_="Vhtah")
            for item in items:
                links.append("https://m.sima-land.ru" + item.find("a").get("href"))
            s = Service(r"C:\Users\Админ\Desktop\PyCharm\qwerty\chromedriver.exe")
            count = 1
            for item in links:
                print(f"[INFO] Страница {page}. Итерация на странице: {count}. Производим операции со страницей {item}. ")
                count += 1
                options = webdriver.ChromeOptions()
                options.headless = True
                options.add_argument("--disable-blink-features=AutomationControlled")
                driver = webdriver.Chrome(service=s, options=options)
                try:
                    driver.get(url=item)
                    button = driver.find_element(By.XPATH, "//a[contains(text(),'Показать полностью')]")
                    actions = ActionChains(driver)
                    actions.move_to_element(button).perform()
                    sleep(0.5)
                    element = driver.find_element(By.XPATH, "//*[contains(text(),'Похожие товары')]")
                    actions = ActionChains(driver)
                    actions.move_to_element(element).perform()
                    sleep(0.5)
                    driver.find_element(By.XPATH, "//a[contains(text(),'Показать полностью')]").click()
                    with open("test.html", "w", encoding='utf-8') as file:
                        file.write(driver.page_source)
                except Exception as ex:
                    errors['Сайт ошибки'].append(url)
                    errors['Ошибка'].append(ex)
                    count_errors += 1
                    print(f"[WARNING] На сайте {item} произошла ошибка webdriver`а, количество ошибок {count_errors}")
                finally:
                    driver.close()
                    driver.quit()
                with open("test.html", encoding="utf-8") as file:
                    src = file.read()
                soup = BeautifulSoup(src, 'lxml')
                try:
                    gabar = soup.find("div", title="Упаковка и фасовка").find("div", text=re.compile(
                        "Размер упаковки")).find_next_sibling().find_next_sibling().text.split("х")
                    dimensions = []
                    for i in range(len(gabar)):
                        dimensions.append(int(float(gabar[i].split()[0].replace(',', '.')) * 10))
                    dimensions.sort()
                except:
                    print(f"[WARNING] На сайте {item} не шаблонные значения габаритов. Ссылка на страницу будет добавлена в файл 'errors.xlsx'")
                    errors['Сайт ошибки'].append(url)
                    errors['Ошибка'].append("Не шаблнные значения габаритов, пожалуйста, проверьте их и заполните в ручную этот товар")
                name = soup.find(class_="ScEhm").find_next_sibling().text
                category = soup.find(class_="ScEhm").find('a').text
                if category != "Матрасы":
                    try:
                        goods['Артикул'].append(
                            soup.find(class_="Kpji6", text="Артикул").find_next_sibling().find_next_sibling().text)
                    except Exception:
                        goods['Артикул'].append('-')
                    goods['Название товара'].append(name)
                    try:
                        goods['Цена, руб.'].append(soup.find(
                            class_="ScEhm").find_next_sibling().find_next_sibling().find_next_sibling().text.split("₽")[0][
                                                   :-1])
                    except Exception:
                        goods['Цена, руб.'].append('-')
                    goods['Цена до скидки, руб.'].append('')
                    goods['Цена с Ozon Premium, руб.'].append('')
                    goods['НДС, %'].append('Не облагается')
                    goods['Ozon ID'].append('')
                    try:
                        comercial_type = get_commercial_type(name, category)
                        goods['Коммерческий тип'].append(comercial_type)
                    except Exception:
                        goods['Коммерческий тип'].append('-')
                    goods['Штрихкод (Серийный номер / EAN)'].append('')
                    try:
                        mass = soup.find("div", text=re.compile(
                            "Вес брутто")).find_next_sibling().find_next_sibling().text
                        if mass.split()[1] == "г":
                            goods['Вес в упаковке, г'].append(mass.split()[0])
                        else:
                            goods['Вес в упаковке, г'].append(str(float(mass.split()[0])*1000)[:-2])
                    except Exception:
                        goods['Вес в упаковке, г'].append('-')
                    try:
                        goods['Ширина упаковки, мм'].append(dimensions[0])
                    except Exception:
                        goods['Ширина упаковки, мм'].append('-')
                    try:
                        goods['Высота упаковки, мм'].append(dimensions[1])
                    except Exception:
                        goods['Высота упаковки, мм'].append('-')
                    try:
                        goods['Длина упаковки, мм'].append(dimensions[2])
                    except Exception:
                        goods['Длина упаковки, мм'].append('-')
                    try:
                        goods['Ссылка на главное фото'].append(soup.find("picture").next_element.next_element.get("srcset"))
                    except Exception:
                        goods['Ссылка на главное фото'].append('-')
                    goods['Ссылки на дополнительные фото'].append('')
                    goods['Ссылки на фото 360'].append('')
                    goods['Артикул фото'].append('')
                    goods['Код ОКПД/ТН ВЭД текстиль'].append(get_code(category))
                    try:
                        goods['Тип'].append(get_type(category, name))
                    except Exception:
                        goods['Тип'].append('-')
                    try:
                        goods['Бренд'].append(
                            soup.find(class_="Kpji6", text="Торговая марка").find_next_sibling().find_next_sibling().text)
                    except Exception:
                        goods['Бренд'].append('sima-land')
                    try:
                        if not ("1,5" in name):
                            goods['Название модели'].append(soup.find(class_="ScEhm").find_next_sibling().text.split(",")[0])
                        else:
                            goods['Название модели'].append(soup.find(class_="ScEhm").find_next_sibling().text.split(",")[0] +
                                                           ',' + soup.find(class_="ScEhm").find_next_sibling().text.split(",")[1])
                    except Exception:
                        goods['Название модели'].append('-')
                    goods['Целевая аудитория'].append('')
                    try:
                        goods['Состав ткани'].append(
                            soup.find("div", text="Состав ткани").find_next_sibling().find_next_sibling().text)
                    except Exception:
                        goods['Состав ткани'].append('-')
                    goods['Аннотация'].append('')
                    goods['Комплектация'].append('')
                    goods['Товар подлежит обязательной маркировке'].append('')
                    goods['Rich-контент JSON'].append('')
                    goods['Использовать шаблонизатор наименований'].append('')
                    goods['Объединить на одной карточке'].append('')
                    goods['Цвет товара'].append('')
                    goods['Название цвета'].append('')
                    goods['Образец цвета'].append('')
                    goods['Плотность плетения ткани'].append('')
                    goods['Вид принта'].append('')
                    goods['Режим стирки'].append('')
                    goods['Отделка'].append('')
                    goods['Минимальный возраст ребенка'].append('')
                    goods['Максимальный возраст ребенка'].append('')
                    goods['Пол ребенка'].append('')
                    goods['Серии'].append('')
                    goods['Гарантия'].append('')
                    try:
                        goods['Страна-изготовитель'].append(
                            soup.find("div", text="Страна производитель").find_next_sibling().find_next_sibling().text)
                    except Exception:
                        goods['Страна-изготовитель'].append('-')
                    goods['Класс опасности товара'].append('')
                    goods['Количество заводских упаковок'].append('')
                    goods['Ошибка'].append('')
                    goods['Предупреждение'].append('')
        df = pd.DataFrame(goods)
        df.to_excel(f'results/results/51-60page_ready.xlsx')
        df = pd.DataFrame(errors)
        df.to_excel(f'results/errors/51-60errors_ready.xlsx')
        print(f"[INFO] Запись страниц 51-60 завершена")


def get_commercial_type(name, category):
    if category == "Наволочки":
        return "Наволочка"
    elif category == "Декоративные наволочки":
        return "Наволочка для декоративной подушки"
    elif category == "Комплекты постельного белья":
        if "евро" in name.lower():
            return "КПБ Евро размер от 200х220"
        elif '1,5' in name.lower() and 'сп' in name.lower():
            return "КПБ 1,5-спальный"
        elif '2' in name.lower() and 'сп' in name.lower():
            return "КПБ 2-спальный"
        elif "детск" in name.lower():
            return "КПБ детский от 110х140"
        else:
            return "КПБ семейный"
    elif category == "Аксессуары для кроваток":
        return "Аксессуары для постельных принадлежностей"
    elif category == "Простыни":
        return "Простыня"
    elif category == "Накладки для пеленания":
        return "Матрас для пеленания"
    elif category == "Наматрасники":
        return "Наматрасник"
    elif category == "Пододеяльники":
        return "Пододеяльник"
    elif category == "Чехлы и наперники":
        return "Чехол для подушки"
    else:
        return "-"


def get_code(category):
    if category == "Комплекты постельного белья":
        return "ОКПД 13.92.12.114 - Комплекты постельного белья из хлопчатобумажных тканей"
    elif category == "Наволочки":
        return "ОКПД 13.92.12.113 - Наволочки из хлопчатобумажных тканей"
    elif category == "Простыни":
        return "ОКПД 13.92.12.191 - Простыни из прочих тканей"
    elif category == "Чехлы и наперники" or category == "Пододеяльники":
        return "ТН ВЭД 6302 31 000 - Белье постельное, столовое, туалетное и кухонное: белье постельное прочее: из хлопчатобумажной пряжи"
    else:
        return "-"


def get_type(category, name):
    if category == "Комплекты постельного белья":
        if "дестк" in name.lower():
            return "Детский комплект постельного белья"
        else:
            return "Комплекты постельного белья"
    elif category == "Наволочки":
        return "Наволочка"
    elif "наперник" in name.lower() or "нижняя наволочка" in name.lower():
        return "Наперник"
    elif "чехол" in name.lower():
        return "Чехол для подушки"
    elif category == "Простыни":
        return "Простыня"
    elif category == "Пододеяльники":
        return "Пододеяльник"
    else:
        return "-"


if __name__ == "__main__":
    page_processing()
