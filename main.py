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
    params = {
            'text': f'Программист {language}',
            'area': HH_MOSCOW_ID,
    }
    response = requests.get(
        HH_VACANCIES_URL,
        params=params
    )
    response.raise_for_status()
    decoded_response = response.json()
    vacancies = []
    page = decoded_response.get('page')
    pages = decoded_response.get('pages')
    while page < pages:
        current_page = {'page': page}
        params.update(current_page)
        page_response = requests.get(
            HH_VACANCIES_URL,
            params=params
        )
        page_response.raise_for_status()
        decoded_page_response = page_response.json()
        page += 1
        vacancies.extend(decoded_page_response.get('items'))
    return [vacancies, decoded_response.get('found')]


def get_vacancies_stats_by_languages(languages):
    vacancies_by_language = {}
    for language in languages:
        response = requests.get(
            HH_VACANCIES_URL,
            params={
                'text': f'Программист {language}',
                'area': HH_MOSCOW_ID,
            }
        )
        response.raise_for_status()
        vacancies_by_language[language] = {
            'vacancies_found': response.json().get('found'),
            'vacancies_processed': get_number_of_processed_salaries(response),
            'average_salary': get_salary_average(response)
        }
    print(vacancies_by_language)


def get_number_of_processed_salaries(vacancies):
    processed_salaries = []
    for vacancy in vacancies:
        if predict_rub_salary(vacancy):
            processed_salaries.append(predict_rub_salary(vacancy))
    return len(processed_salaries)


def get_salary_average(vacancies):
    processed_salaries = []
    for vacancy in vacancies:
        processed_salaries.append(predict_rub_salary(vacancy))
    salary_average = sum(processed_salaries)/len(processed_salaries)

    return int(salary_average)


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
        vacancies_parsed_from_hh = get_all_vacancies_by_language(language)
        vacancies = vacancies_parsed_from_hh[0]
        vacancies_total = vacancies_parsed_from_hh[1]
        vacancies_salary_statistics[language] = {
            'vacancies_found': vacancies_total,
            'vacancies_processed': get_number_of_processed_salaries(vacancies),
            'average_salary': get_salary_average(vacancies)
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
        current_page = {'page': page}
        params.update(current_page)
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
    return [vacancies, decoded_response['total']]


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
        processed_salaries.append(predict_rub_salary_for_superJob(vacancy))
    if processed_salaries:
        salary_average = sum(processed_salaries)/len(processed_salaries)
        return int(salary_average)
    return None


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
        vacancies_parsed_from_sj = get_all_vacancies_by_language_for_superjob(
                language,
                access_token
            )
        vacancies = vacancies_parsed_from_sj[0]
        vacancies_total = vacancies_parsed_from_sj[1]
        vacancies_salary_statistics[language] = {
            'vacancies_found': vacancies_total,
            'vacancies_processed':
            get_number_of_processed_salaries_for_superjob(vacancies),
            'average_salary': get_salary_average_for_superjob(vacancies)
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
