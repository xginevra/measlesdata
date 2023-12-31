import json
import sqlite3
from fhir.resources.bundle import Bundle
import pathlib


def create_table(cursor):
    # Drop the table if it exists
    cursor.execute('DROP TABLE IF EXISTS measles_data;')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measles_data(
            id INTEGER PRIMARY KEY,
            location TEXT,
            population INT,
            cases INT,
            vaccination_rate DECIMAL,
            cases_100000 DECIMAL
        );
    ''')


def insert_data(cursor, location, data):
    location = location.split("/")[1]
    population = int(data['Population'])
    cases = int(data['Measles Cases'])
    if "Vaccination Rate" in data:
        vacation_r = float(data['Vaccination Rate'])
    else:
        vacation_r = "N.A"
    if 'Per 100,000' in data:
        cases_100000 = float(data['Per 100,000'])
    else:
        cases_100000 = "N.A"
    cursor.execute('''
        INSERT INTO measles_data (location, population, cases, vaccination_rate, cases_100000)
        VALUES (?, ?, ?, ?, ?);
    ''', (location, population, cases, vacation_r, cases_100000))
    # Add more parameters and placeholders as needed


def main():
    # Replace 'your_database_file.db' with your desired database file name
    database_file = 'data_for_web_application.db'

    # Connect to the SQLite database
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    # Create the table if it doesn't exist
    create_table(cursor)

    # Insert data into the table
    # Read data from the JSON file
    filename = pathlib.Path("measles_statistics_fhir.json")
    pat = Bundle.parse_file(filename)
    for obs in pat.entry:
        location = obs.resource.subject.reference
        data_dict = {}
        for compons in obs.resource.component:
            data_dict[compons.code.text] = compons.valueQuantity.value

        insert_data(cursor, location, data_dict)

    # Commit the changes and close the connection
    connection.commit()
    connection.close()


if __name__ == "__main__":
    main()
