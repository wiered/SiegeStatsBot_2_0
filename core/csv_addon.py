import csv
import logging


def load_from_csv(file_name):
    with open(file_name, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_to_csv(file_name, data):
    open(file_name, 'w').close()
    with open(file_name, 'w') as f:
        writer = csv.DictWriter(
            f, 
            fieldnames=[
                'name', 
                'd_id', 
                'siege_id',
                'rank'
            ]
            )
        writer.writeheader()
        writer.writerows(data)
        logging.info('Users saved')
