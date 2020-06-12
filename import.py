import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create table books if not exists
db.execute("CREATE TABLE IF NOT EXISTS books(id serial PRIMARY KEY NOT NULL,isbn VARCHAR (10) UNIQUE NOT NULL, title VARCHAR (40) NOT NULL, author VARCHAR (40) NOT NULL, year TEXT )")
db.commit()

def main():
    f = open("books.csv")
    t = open("books.csv")
    reader = csv.reader(f)
    total = csv.reader(t)
    lines = len(list(total)) - 1
    print(f"{lines} in the csv")
    number = 0
    next(reader)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"{number} / {lines}  Adding book {title} by {author}.")
        number = number + 1
    db.commit()
    print(f"{number} books added")

if __name__ == "__main__":
    main()
