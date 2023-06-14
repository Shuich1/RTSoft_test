import csv

from db.database import DataStorage
from models.images import Category, Image


def fill_database_from_csv(db: DataStorage, file_path: str):
    with open(file_path, "r") as csv_file, db.get_session() as session:
        csv_reader = csv.reader(csv_file, delimiter=";")
        next(csv_reader)
        for row in csv_reader:
            url = row[0]
            repetitions = row[1]
            categories = row[2:]

            image = session.query(Image).filter_by(url=url).first()
            if image:
                continue
            image = Image(url=url, repetitions=repetitions)

            for category_name in categories:
                category = session.query(Category).filter_by(
                    name=category_name
                ).first()
                if not category:
                    category = Category(name=category_name)
                image.categories.append(category)

            session.add(image)

        session.commit()
