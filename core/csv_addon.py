import csv
import logging
from pathlib import Path


def load_from_csv(file_name):
    with Path(file_name).open("r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_to_csv(file_name, data):
    file_path = Path(file_name)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "d_id",
                "siege_id",
            ],
        )
        writer.writeheader()
        writer.writerows(data)
        logging.info("Users saved")
