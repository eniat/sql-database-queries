import mysql.connector
from mysql.connector import Error
import csv
import plotly.graph_objects as go
import plotly.io as pio

def create_mysql_connection(host_name, user_name, user_password):
    """
    Creates and returns a MySQL connection.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='',
            password=''
        )
        if connection.is_connected():
            print("Connected to MySQL")
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None


def create_database(connection, db_name):
    """
    Creates a database if it doesn't already exist.
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists.")
        cursor.close()
    except Error as e:
        print(f"Error: '{e}'")


def create_tables(connection, db_name):
    """
    Creates 'User_Accounts','Uploads' and 'Messenger' tables with specified attributes and relationships.
    """
    try:
        connection.database = db_name
        cursor = connection.cursor()

        # Create User_Accounts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS User_Accounts (
            username varchar(50) NOT NULL,
            email varchar(50),
            date_of_birth DATE,
            mobile_number varchar(50),
            PRIMARY KEY(username)
        )
        """)

        # Create Uploads table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Uploads (
            upload_number INT,
            username varchar(50) NOT NULL,
            caption TEXT,
            date_of_upload DATE,
            likes INT,
            PRIMARY KEY(upload_number),
            FOREIGN KEY (username) REFERENCES User_Accounts(username) ON DELETE CASCADE
        )
        """)

        # Create Messenger table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Messenger (
            message_ID varchar(50) NOT NULL,
            username varchar(50) NOT NULL,
            message_content TEXT,
            sent_on DATE,
            received BOOLEAN,
            receiver TEXT,
            PRIMARY KEY(message_ID),
            FOREIGN KEY (username) REFERENCES User_Accounts(username) ON DELETE CASCADE
        )
        """)

        print("Tables 'User_Accounts','Uploads' and 'Messenger' created or already exist.")
        cursor.close()
    except Error as e:
        print(f"Error: '{e}'")


def populate_table_from_csv(connection, csv_file_path, table_name):
    """
    Populates a specified table from a CSV file.
    """
    try:
        cursor = connection.cursor()
        with open(csv_file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row

            # Define insert query based on table
            if table_name == 'User_Accounts':
                insert_query = """
                INSERT INTO User_Accounts (username, email, date_of_birth, mobile_number)
                VALUES (%s, %s, %s, %s)
                """
            elif table_name == 'Uploads':
                insert_query = """
                INSERT INTO Uploads (upload_number, username, caption, date_of_upload, likes)
                VALUES (%s, %s, %s, %s, %s)
                """
            elif table_name == 'Messenger':
                insert_query = """
                INSERT INTO Messenger (message_ID, username, message_content, sent_on, received, receiver)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

            # Insert each row from CSV into the table
            for row in csv_reader:
                cursor.execute(insert_query, row)

        connection.commit()
        print(f"Data from '{csv_file_path}' inserted successfully into '{table_name}' table.")
        cursor.close()
    except Error as e:
        print(f"Error: '{table_name}' '{e}'")


def print_captions_of_uploads(connection):
    """
    Prints the caption of uploads with 100 likes from the uploads table
    """
    try:
        cursor = connection.cursor()
        query = """
        SELECT caption 
        FROM Uploads 
        WHERE likes = 100"""
        cursor.execute(query)
        captions = cursor.fetchall()
        print("Captions from uploads with 100 likes in 'Uploads':")
        for caption in captions:
            print(caption[0])
        cursor.close()
    except Error as e:
        print(f"Error: '{e}'")


def print_usernames_active_on_date(connection):
    """
    Prints the username's that uploaded on or sent a message on 3/12/2023
    """
    try:
        cursor = connection.cursor()
        query = """
        SELECT DISTINCT username
        FROM (
            SELECT username FROM Uploads WHERE date_of_upload = '2023-12-03'
            UNION
            SELECT username FROM Messenger WHERE sent_on = '2023-12-03'
        ) AS combined_usernames;
        """
        cursor.execute(query)
        usernames = cursor.fetchall()
        print("Username's that uploaded on or sent a message on 3/12/2023 in 'Uploads' and 'Messenger':")
        for username in usernames:
            print(username[0])
        cursor.close()
    except Error as e:
        print(f"Error: '{e}'")


def print_email_with_no_message_recieved(connection):
    """
    Prints the email of users who have messages that aren't recieved
    """
    try:
        cursor = connection.cursor()
        query = """
        SELECT DISTINCT u.email
        FROM User_Accounts u
        JOIN Messenger m ON u.username = m.username
        WHERE m.received = FALSE;
        """
        cursor.execute(query)
        usernames = cursor.fetchall()
        print("Emails that have a message not recieved in 'User_Accounts' and 'Messenger':")
        for username in usernames:
            print(username[0])
        cursor.close()
    except Error as e:
        print(f"Error: '{e}'")


def print_amount_of_accounts(connection):
    """
    Prints the amount of accounts
    """
    try:
        cursor = connection.cursor()
        query = """
        SELECT COUNT(username) 
        FROM User_Accounts;
        """
        cursor.execute(query)
        amount = cursor.fetchone()[0]
        print("Amount of unique accounts in 'User_Accounts':")
        print(amount)
        cursor.close()
    except Error as e:
        print(f"Error: '{e}'")


def print_DOB_of_most_liked(connection):
    """
    Prints the date of birth of the username that's linked to the most liked upload
    """
    try:
        cursor = connection.cursor()
        query = """
        SELECT u.date_of_birth
        FROM User_Accounts u
        JOIN Uploads u2 ON u.username = u2.username
        WHERE u2.likes = (
            SELECT MAX(likes) FROM Uploads
        )
        LIMIT 1;
        """
        cursor.execute(query)
        DOB = cursor.fetchone()[0]
        print("DOB from 'User_Accounts' of username with most liked upload from 'Uploads':")
        print(DOB)
        cursor.close()
    except Error as e:
        print(f"Error: '{e}'")


def create_likes_chart(conn):
    """Queries likes from uploads and displays a bar chart."""
    cursor = conn.cursor()
    cursor.execute("SELECT likes FROM Uploads;")

    # Fetch all rows of the query result
    data = cursor.fetchall()

    # Check if data is None or empty
    if data is None or len(data) == 0:
        print("No data found in the Uploads table. Exiting.")
        return

    # Extract likes values
    likes_values = [row[0] for row in data]

    # Create a frequency dictionary for likes values
    value_counts = {}
    for value in likes_values:
        value_counts[value] = value_counts.get(value, 0) + 1

    # Convert the dictionary to two lists: one for the values and one for the counts
    values = list(value_counts.keys())
    counts = list(value_counts.values())

    # Create a bar chart using Plotly
    bar_chart = go.Figure(data=[
        go.Bar(
            x=values,
            y=counts,
            text=counts,  # Display the count on top of each bar
            textposition='auto',
            marker=dict(color='red')
        )
    ])

    # Update layout for better appearance
    bar_chart.update_layout(
        title="Bar Chart of likes",
        xaxis_title="likes",
        yaxis_title="amount",
        template="plotly_dark"
    )

    # Display the bar chart in a web browser (default renderer)
    bar_chart.show()


def main():
    # MySQL connection details
    host_name = ""
    user_name = ""
    user_password = ""

    # Database name
    db_name = "socialmedia_database"

    # File paths for CSVs
    user_accounts_csv = "user_accounts.csv"
    uploads_csv = "uploads.csv"
    messenger_csv = "messenger.csv"

    # Create MySQL connection
    connection = create_mysql_connection(host_name, user_name, user_password)

    if connection:
        try:
            # Step 1: Create the database
            create_database(connection, db_name)

            # Step 2: Create the tables in the database
            create_tables(connection, db_name)

            # Step 3: Populate tables with data from the CSV files

            populate_table_from_csv(connection, user_accounts_csv, "User_Accounts")
            populate_table_from_csv(connection, uploads_csv, "Uploads")
            populate_table_from_csv(connection, messenger_csv, "Messenger")

            # Step 4: Execute queries and print results
            print_captions_of_uploads(connection)
            print_usernames_active_on_date(connection)
            print_email_with_no_message_recieved(connection)
            print_amount_of_accounts(connection)
            print_DOB_of_most_liked(connection)
            create_likes_chart(connection)


        finally:
            # Step 5: Close the MySQL connection
            connection.close()
            print("MySQL connection closed.")
    else:
        print("Failed to connect to MySQL")


# Run the main function
if __name__ == "__main__":
    main()