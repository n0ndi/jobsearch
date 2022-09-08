import os
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_value_salary(salary_to, salary_from):
    try:
        if salary_from and salary_to:
            return ((salary_from + salary_to) / 2)
        elif not salary_from and salary_to:
            return (salary_from * 0.8)
        elif salary_from and not salary_to:
            return (salary_from * 1.2)
    except TypeError:
        return None


def predict_rub_salary_hh(response):
    salaries = []
    vacancies_info = response.json()["items"]
    for job in vacancies_info:
        try:
            if job["salary"]["currency"] != "RUR":
                continue
        except TypeError:
            continue
        salary_to = job["salary"]["to"]
        salary_from = job["salary"]["from"]
        salary = get_value_salary(salary_to, salary_from)
        if salary:
            salaries.append(get_value_salary(salary_to, salary_from))
    return int(sum(salaries)), len(salaries)


def predict_rub_salary_sj(response):
    salaries = []
    vacancies_info = response.json()["objects"]
    for job in vacancies_info:
        salary_from = job['payment_from']
        salary_to = job['payment_to']
        salary = get_value_salary(salary_to, salary_from)
        if salary:
            salaries.append(get_value_salary(salary_to, salary_from))
    return int(sum(salaries)), len(salaries)


def write_vacancies_stats_hh(languages):
    town_code = 1
    count = 100
    page = 0
    pages_number = 1
    for language in languages:
        found_vacancies = 0
        vacancied_proccessed = 0
        average_salary = 0
        while page < pages_number:
            payload = {
              "text": f"программист {language}",
              "area": town_code,
              "page": page,
              "per_page": count
            }
            url = "https://api.hh.ru/vacancies"
            response = requests.get(url, params=payload)
            response.raise_for_status()
            vacancies_data = response.json()
            if not vacancies_data["items"]:
                break
            pages_number = vacancies_data["pages"]
            found_vacancies = vacancies_data["found"]
            salaries_info, proccessed = predict_rub_salary_hh(response)
            vacancied_proccessed += proccessed
            average_salary += salaries_info
            page += 1
        languages[language]["vacancies_found"] = found_vacancies
        languages[language]["vacancied_proccessed"] = vacancied_proccessed
        if vacancied_proccessed == 0:
            pass
        else:
            languages[language]["average_salary"] = int(average_salary / vacancied_proccessed)
        page = 0


def write_vacancies_stats_sj(languages, key):
    town_code = 4
    count = 100
    page = 0
    for language in languages:
        vacancied_proccessed = 0
        average_salary = 0
        while True:
            headers = {
                    "X-Api-App-Id": key,
                    "Content-Type": "application/x-www-form-urlencoded"
            }
            payload = {
                "keyword": f"Программист {language}",
                "town": town_code,
                "count": count,
                "page": page
            }
            url = "https://api.superjob.ru/2.0/vacancies"
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            vacancies_data = response.json()
            salaries_info, proccessed = predict_rub_salary_sj(response)
            vacancied_proccessed += proccessed
            average_salary += salaries_info
            found_vacancies = vacancies_data["total"]
            page += 1
            if not response.json()["more"]:
                break
        languages[language]["vacancies_found"] = found_vacancies
        languages[language]["vacancied_proccessed"] = vacancied_proccessed
        languages[language]["average_salary"] = int(average_salary / vacancied_proccessed)
        page = 0


def create_language_json(list):
    languages = {}
    for language in list:
        lang = {
            language: {
                "vacancies_found": None,
                "vacancied_proccessed": None,
                "average_salary": None
            }
         }
        languages.update(lang)
    return languages


def create_table(table_data, title):
    table = [
      ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]
    ]
    for language in table_data:
        stat = table_data[language]
        table.append([language, stat["vacancies_found"], stat["vacancied_proccessed"], stat["average_salary"]])
    table_instance = AsciiTable(table, title)
    table_instance.justify_columns[2] = 'right'
    return table_instance.table



def main():
    load_dotenv()
    key = os.environ["SJ_KEY"]
    languages = ["Python", "Java"]
    languages = create_language_json(languages)
    write_vacancies_stats_sj(languages, key)
    print(create_table(languages, "SuperJobMoscow"))
    write_vacancies_stats_hh(languages)
    print(create_table(languages, "HeadHunterMoscow"))



if __name__ == "__main__":
    main()
