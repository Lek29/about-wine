import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import date
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import argparse


def write_correctly_year(date):
    if date % 10 == 1 and date % 100 != 11:
        return f'{date} год'
    elif date % 10 in [2, 3, 4] and date % 100 not in [12, 13, 14]:
        return f'{date} года'
    else:
        return f'{date} лет'


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description='Введите путь до файла'
    )
    parser.add_argument(
        '-f', '--file',
        help='Введите путь до файла',
        default=os.getenv('WINE_DEFAULT_PATH'),
    )
    args = parser.parse_args()
    file_name = args.file
    if not file_name:
        print('Ошибка. Укажите путь к файлу')
        return

    file_path = Path(file_name)
    new_df = pd.read_excel(file_path)
    wines_range_not_nan = new_df.fillna(0)
    converted_wines_range = wines_range_not_nan.to_dict(orient='records')

    grouped_type_drink = defaultdict(list)
    for wine in converted_wines_range:
        drink_type = wine['Категория']
        grouped_type_drink[drink_type].append(wine)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    foundation_year = 1920
    year_now = date.today().year

    difference_year = year_now - foundation_year
    rendered_page = template.render(
        difference_age_message=f'Уже {write_correctly_year(difference_year)} с вами',
        grouped_wines=grouped_type_drink
    )

    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
