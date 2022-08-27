import requests
from pprint import pprint
from terminaltables import AsciiTable


def predict_rub_salary_hh(response):
    salarys = []
    for item in response.json()["items"]:
        try:
          if item["salary"]["currency"] != "RUR":
              pass
        except TypeError:
            continue
        if (item["salary"]["from"]) and (item["salary"]["to"]):
            salarys.append((item["salary"]["from"] + item["salary"]["to"]) / 2)
        elif (not item["salary"]["from"]) and (item["salary"]["to"]):
            salarys.append(item["salary"]["to"] * 0.8)
        elif (item["salary"]["from"]) and (not item["salary"]["to"]):
            salarys.append(item["salary"]["from"] * 1.2)
    return int(sum(salarys)), len(salarys)

def predict_rub_salary_sj(response):
    salarys = []
    for job in response.json()["objects"]:
      salary_from = job['payment_from']
      salary_to = job['payment_to']
      if (salary_from == 0) and (salary_to == 0):
          pass
      elif (salary_from) and (salary_to):
          salarys.append((salary_from + salary_to) / 2)
      elif (not salary_from) and (salary_to):
          salarys.append(salary_to * 0.8)
      elif (salary_from) and (not salary_to):
          salarys.append(salary_from * 1.2)
    return int(sum(salarys)), len(salarys)


def write_vacancies_data_hh(languages):
  page = 0
  pages_number = 1
  for vacancy in languages:
    vacancies_found = 0
    vacancied_proccessed = 0
    average_salary = 0
    while page < pages_number:
      payload = {
          "text": f"программист {vacancy}",
          "area": "1",
          "page": page,
          "per_page": 100
      }
      url = "https://api.hh.ru/vacancies"
      response = requests.get(url, params=payload)
      response.raise_for_status()
      vacancies_json = response.json()
      pages_number = vacancies_json["pages"]
      vacancies_found = vacancies_json["found"]
      salarys_data, proccessed = predict_rub_salary_hh(response)
      vacancied_proccessed += proccessed
      average_salary += salarys_data
      page += 1
    languages[vacancy]["vacancies_found"] = vacancies_found
    languages[vacancy]["vacancied_proccessed"] = vacancied_proccessed
    languages[vacancy]["average_salary"] = int(average_salary / vacancied_proccessed)
    page = 0 

def write_vacancies_data_sj(languages):
  page = 0
  for vacancy in languages:
    vacancies_found = 0
    vacancied_proccessed = 0
    average_salary = 0
    while True:
      headers = {
        "X-Api-App-Id": "v3.r.136905290.58ef3d98e9579e1dfe51f0c2764bacb575aa91e5.7ac2a7108764b64c3ebd0f220a9f0212407a5c37",
        "Content-Type": "application/x-www-form-urlencoded"
  
      }
      payload = {
          "keyword": f"Программист {vacancy}",
          "town": 4,
          "count": 100,
          "page": page
      }
      url = "https://api.superjob.ru/2.0/vacancies"
      response = requests.get(url, headers=headers, params=payload)
      response.raise_for_status()
      vacancies_json = response.json()
      salarys_data, proccessed = predict_rub_salary_sj(response)
      vacancied_proccessed += proccessed
      average_salary += salarys_data
      vacancies_found = vacancies_json["total"]
      page += 1
      if not response.json()["more"]:
        break
    languages[vacancy]["vacancies_found"] = vacancies_found
    languages[vacancy]["vacancied_proccessed"] = vacancied_proccessed
    languages[vacancy]["average_salary"] = int(average_salary / vacancied_proccessed)
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

  
def create_table(data, title):
    table = [
      ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]  
    ]
    for language in data:
      stat = data[language]
      table.append([language, stat["vacancies_found"], stat["vacancied_proccessed"], stat["average_salary"]])
    table_instance = AsciiTable(table, title)
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)
    print()


def get_hh_table(languages):
    languages = create_language_json(languages)
    write_vacancies_data_hh(languages)
    create_table(languages, "HeadHunterMoscow")


def get_sj_table(languages):
    languages = create_language_json(languages)
    write_vacancies_data_sj(languages)
    create_table(languages, "SuperJobMoscow")


def main():
    languages = ["Python", "Java"]
    get_hh_table(languages)
    get_sj_table(languages)

  
    
    


if __name__ == "__main__":
    main()