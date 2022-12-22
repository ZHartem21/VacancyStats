import os

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

HH_VACANCIES_URL = 'https://api.hh.ru/vacancies/'
SJ_VACANCIES_URL = 'https://api.superjob.ru/2.0/vacancies/'
PROGRAMMING_LANGUAGES = ['Python', 'Javascript', 'Java', 'Ruby', 'PHP', 'C++',
                         'C#', 'Swift', 'Go', 'Shell']
HH_MOSCOW_ID = 1
SJ_PROGRAMMING_ID = 48
SJ_MOSCOW_ID = 4


def calculate_predicted_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        salary_approximation = salary_from * 1.2
        return salary_approximation
    if not salary_from and salary_to:
        salary_approximation = salary_to * 0.8
        return salary_approximation
    if salary_from and salary_to:
        salary_approximation = (salary_from +
                                salary_to) / 2
        return salary_approximation
    return False


def predict_rub_salary(vacancy):
    if not vacancy['salary']:
        return False
    salary = vacancy['salary']
    if not salary['currency'] == 'RUR':
        return False
    salary_approximation = calculate_predicted_salary(
            salary['from'],
            salary['to']
        )
    return salary_approximation


def get_all_vacancies_by_language(language):
    params = {
            'text': f'Программист {language}',
            'area': HH_MOSCOW_ID,
    }
    vacancies = []
    page = 1
    pages = 10
    while page < pages:
        params['page'] = page
        page_response = requests.get(
            HH_VACANCIES_URL,
            params=params
        )
        page_response.raise_for_status()
        decoded_page_response = page_response.json()
        page = decoded_page_response.get('page')
        pages = decoded_page_response.get('pages')
        page += 1
        vacancies.extend(decoded_page_response.get('items'))
    return (vacancies, decoded_page_response.get('found'))


def get_salary_average_and_processed(vacancies):
    processed_salaries = []
    for vacancy in vacancies:
        processed_salaries.append(predict_rub_salary(vacancy))
    if len(processed_salaries):
        salary_average = sum(processed_salaries)/len(processed_salaries)
    else:
        return (None, None)
    return (int(salary_average), len(processed_salaries))


def get_hh_stats_table():
    vacancies_salary_statistics = {}
    vacancies_table = [
        (
            'Язык программирования',
            'Найдено вакансий',
            'Обработано вакансий',
            'Средняя зарплата'
        )
    ]
    for language in PROGRAMMING_LANGUAGES:
        vacancies, vacancies_total = get_all_vacancies_by_language(language)
        average, processed = get_salary_average_and_processed(vacancies)
        vacancies_salary_statistics[language] = {
            'vacancies_found': vacancies_total,
            'vacancies_processed': processed,
            'average_salary': average
        }
    for language in vacancies_salary_statistics:
        vacancies_table.append(
            (
                language,
                vacancies_salary_statistics[language].get('vacancies_found'),
                vacancies_salary_statistics[language].get(
                    'vacancies_processed'
                ),
                vacancies_salary_statistics[language].get('average_salary')
            )
        )
    table_instance = AsciiTable(vacancies_table, 'HeadHunter Moscow')
    return table_instance


def predict_rub_salary_for_sj(vacancy):
    if not vacancy['currency'] == 'rub':
        return False
    salary_approximation = calculate_predicted_salary(
            vacancy['payment_from'],
            vacancy['payment_to']
        )
    return salary_approximation


def get_all_vacancies_by_language_for_sj(language, access_token):
    params = {
            'catalogues': SJ_PROGRAMMING_ID,
            'keyword': language,
            'town': SJ_MOSCOW_ID,
    }
    response = requests.get(
        SJ_VACANCIES_URL,
        headers={
            'X-Api-App-Id': access_token
        },
        params=params
    )
    response.raise_for_status()
    decoded_response = response.json()
    vacancies = []
    vacancies.extend(decoded_response['objects'])
    more = decoded_response['more']
    page = 1
    while more:
        params['page'] = page
        page_response = requests.get(
            SJ_VACANCIES_URL,
            headers={
                'X-Api-App-Id': access_token
            },
            params=params
        )
        page_response.raise_for_status()
        decoded_page_response = page_response.json()
        more = decoded_page_response['more']
        if more:
            page += 1
        vacancies.extend(decoded_page_response['objects'])
    return (vacancies, decoded_response['total'])


def get_salary_average_for_sj(vacancies):
    processed_salaries = []
    for vacancy in vacancies:
        processed_salaries.append(predict_rub_salary_for_sj(vacancy))
    if processed_salaries:
        salary_average = sum(processed_salaries)/len(processed_salaries)
        return (int(salary_average), len(processed_salaries))
    return (None, None)


def get_sj_stats_table(access_token):
    vacancies_salary_statistics = {}
    vacancies_table = [
                (
                    'Язык программирования',
                    'Найдено вакансий',
                    'Обработано вакансий',
                    'Средняя зарплата'
                )
            ]
    for language in PROGRAMMING_LANGUAGES:
        vacancies, vacancies_total = get_all_vacancies_by_language_for_sj(
                language,
                access_token
            )
        average, processed = get_salary_average_for_sj(vacancies)
        vacancies_salary_statistics[language] = {
            'vacancies_found': vacancies_total,
            'vacancies_processed': processed,
            'average_salary': average
        }
    for language in vacancies_salary_statistics:
        vacancies_table.append(
            (
                language,
                vacancies_salary_statistics[language].get('vacancies_found'),
                vacancies_salary_statistics[language].get(
                    'vacancies_processed'
                ),
                vacancies_salary_statistics[language].get('average_salary')
            )
        )
    table_instance = AsciiTable(vacancies_table, 'HeadHunter Moscow')
    return table_instance.table


def main():
    load_dotenv('tokens.env')
    sj_access_token = os.environ['SJ_ACCESS_TOKEN']
    print(get_sj_stats_table(sj_access_token))
    print(get_hh_stats_table())


if __name__ == "__main__":
    main()
