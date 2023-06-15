import csv

from db.database import DataStorage
from models.images import Category, Image
from sqlalchemy import select


async def fill_database_from_csv(db: DataStorage, file_path: str):
    async with db.get_session() as session:
        with open(file_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            next(csv_reader)
            for row in csv_reader:
                url = row[0]
                repetitions = row[1]
                categories = row[2:]

                image = await session.execute(select(Image).filter_by(url=url))
                image = image.scalars().first()
                if image:
                    continue
                image = Image(url=url, repetitions=int(repetitions))
                for category_name in categories:
                    category = await session.execute(
                        select(Category).filter_by(name=category_name)
                    )
                    category = category.scalars().first()
                    if not category:
                        category = Category(name=category_name)
                    image.categories.append(category)

                session.add(image)

            await session.commit()
