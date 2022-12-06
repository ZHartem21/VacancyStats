import os

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

HH_VACANCIES_URL = 'https://api.hh.ru/vacancies/'
SJ_VACANCIES_URL = 'https://api.superjob.ru/2.0/vacancies/'
PROGRAMMING_LANGUAGES = ['Python', 'Javascript', 'Java', 'Ruby', 'PHP', 'C++',
                         'C#', 'Swift', 'Go', 'Shell']


def predict_rub_salary(vacancy):
    if not vacancy['salary']:
        return None
    salary = vacancy['salary']
    if not salary['currency'] == 'RUR':
        return None
    if salary['from'] and not salary['to']:
        salary_approximation = salary['from'] * 1.2
        return salary_approximation
    if not salary['from'] and salary['to']:
        salary_approximation = salary['to'] * 0.8
        return salary_approximation
    if salary['from'] and salary['to']:
        salary_approximation = (vacancy['salary']['from'] +
                                vacancy['salary']['to']) / 2
        return salary_approximation
    return None


def get_all_vacancies_by_language(language):
    response = requests.get(
        HH_VACANCIES_URL,
        params={
            'text': f'Программист {language}',
            'area': 1,
        }
    )
    response.raise_for_status()
    vacancies = []
    page = response.json().get('page')
    pages = response.json().get('pages')
    while page < pages:
        page_response = requests.get(
            HH_VACANCIES_URL,
            params={
                'text': f'Программист {language}',
                'area': 1,
                'page': page
            }
        )
        page_response.raise_for_status()
        page += 1
        for vacancy in page_response.json().get('items'):
            vacancies.append(vacancy)
    return vacancies


def get_vacancies_stats_by_languages(languages):
    vacancies_by_language = {}
    for language in languages:
        response = requests.get(
            HH_VACANCIES_URL,
            params={
                'text': f'Программист {language}',
                'area': 1,
            }
        )
        response.raise_for_status()
        vacancies_by_language[language] = {
            'vacancies_found': response.json().get('found'),
            'vacancies_processed': get_number_of_processed_salaries(response),
            'average_salary': get_salary_average(response)
        }
    print(vacancies_by_language)


def get_number_of_vacancies_found(language):
    response = requests.get(
        HH_VACANCIES_URL,
        params={
            'text': f'Программист {language}',
            'area': 1,
        }
    )
    response.raise_for_status()
    return response.json().get('found')


def get_number_of_processed_salaries(vacancies):
    processed_salaries = []
    for vacancy in vacancies:
        if predict_rub_salary(vacancy):
            processed_salaries.append(predict_rub_salary(vacancy))
    return len(processed_salaries)


def get_salary_average(vacancies):
    processed_salaries = []
    for vacancy in vacancies:
        if predict_rub_salary(vacancy):
            processed_salaries.append(predict_rub_salary(vacancy))
    salary_average = sum(processed_salaries)/len(processed_salaries)

    return int(salary_average)


def get_hh_stats_table():
    vacancies_salary_statistics = {}
    table_data = [
        (
            'Язык программирования',
            'Найдено вакансий',
            'Обработано вакансий',
            'Средняя зарплата'
        )
    ]
    for language in PROGRAMMING_LANGUAGES:
        vacancies = get_all_vacancies_by_language(language)
        vacancies_salary_statistics[language] = {
            'vacancies_found': get_number_of_vacancies_found(language),
            'vacancies_processed': get_number_of_processed_salaries(vacancies),
            'average_salary': get_salary_average(vacancies)
        }
    for language in vacancies_salary_statistics:
        table_data.append(
            (
                language,
                vacancies_salary_statistics[language].get('vacancies_found'),
                vacancies_salary_statistics[language].get(
                    'vacancies_processed'
                ),
                vacancies_salary_statistics[language].get('average_salary')
            )
        )
    table_instance = AsciiTable(table_data, 'HeadHunter Moscow')
    return table_instance


def predict_rub_salary_for_superJob(vacancy):
    if not vacancy['currency'] == 'rub':
        return None
    if vacancy['payment_from'] and not vacancy['payment_to']:
        salary_approximation = vacancy['payment_from'] * 1.2
        return salary_approximation
    if not vacancy['payment_from'] and vacancy['payment_to']:
        salary_approximation = vacancy['payment_to'] * 0.8
        return salary_approximation
    if vacancy['payment_from'] and vacancy['payment_to']:
        salary_approximation = (vacancy['payment_from'] +
                                vacancy['payment_to']) / 2
        return salary_approximation
    return None


def get_all_vacancies_by_language_for_superjob(language, access_token):
    response = requests.get(
        SJ_VACANCIES_URL,
        headers={
            'X-Api-App-Id': access_token
        },
        params={
            'catalogues': 48,
            'keyword': language,
            'town': 4,
        }
    )
    response.raise_for_status()
    vacancies = []
    for vacancy in response.json()['objects']:
        vacancies.append(vacancy)
    more = response.json()['more']
    page = 1
    while more:
        page_response = requests.get(
            SJ_VACANCIES_URL,
            headers={
                'X-Api-App-Id': access_token
            },
            params={
                'catalogues': 48,
                'keyword': language,
                'town': 4,
                'page': page
            }
        )
        page_response.raise_for_status()
        more = page_response.json()['more']
        if more:
            page += 1
        for vacancy in page_response.json()['objects']:
            vacancies.append(vacancy)
    return vacancies


def get_number_of_vacancies_found_for_superjob(language, access_token):
    response = requests.get(
        SJ_VACANCIES_URL,
        headers={
            'X-Api-App-Id': access_token
        },
        params={
            'catalogues': 48,
            'keyword': language,
            'town': 4,
        }
    )
    response.raise_for_status()
    return response.json().get('total')


def get_number_of_processed_salaries_for_superjob(vacancies):
    processed_salaries = []
    for vacancy in vacancies:
        if predict_rub_salary_for_superJob(vacancy):
            processed_salaries.append(predict_rub_salary_for_superJob(vacancy))
    if processed_salaries:
        return len(processed_salaries)
    return None


def get_salary_average_for_superjob(vacancies):
    processed_salaries = []
    for vacancy in vacancies:
        if predict_rub_salary_for_superJob(vacancy):
            processed_salaries.append(predict_rub_salary_for_superJob(vacancy))
    if processed_salaries:
        salary_average = sum(processed_salaries)/len(processed_salaries)
        return int(salary_average)
    return None


def get_sj_stats_table(access_token):
    vacancies_salary_statistics = {}
    table_data = [
                (
                    'Язык программирования',
                    'Найдено вакансий',
                    'Обработано вакансий',
                    'Средняя зарплата'
                )
            ]
    for language in PROGRAMMING_LANGUAGES:
        vacancies = get_all_vacancies_by_language_for_superjob(
                language,
                access_token
            )
        vacancies_salary_statistics[language] = {
            'vacancies_found': get_number_of_vacancies_found_for_superjob(
                language,
                access_token
            ),
            'vacancies_processed':
            get_number_of_processed_salaries_for_superjob(vacancies),
            'average_salary': get_salary_average_for_superjob(vacancies)
        }
    for language in vacancies_salary_statistics:
        table_data.append(
            (
                language,
                vacancies_salary_statistics[language].get('vacancies_found'),
                vacancies_salary_statistics[language].get(
                    'vacancies_processed'
                ),
                vacancies_salary_statistics[language].get('average_salary')
            )
        )
    table_instance = AsciiTable(table_data, 'HeadHunter Moscow')
    return table_instance.table


def main():
    load_dotenv('tokens.env')
    sj_access_token = os.environ['SJ_ACCESS_TOKEN']
    print(get_sj_stats_table(sj_access_token))
    print(get_hh_stats_table())


if __name__ == "__main__":
    main()