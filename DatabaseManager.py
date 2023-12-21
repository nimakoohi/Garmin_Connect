import mysql.connector

class DatabaseManager:
    def __init__(self, config):
        self.host = config['Database']['host']
        self.user = config['Database']['user']
        self.password = config['Database']['password']
        self.db = config['Database']['database']

    def establish_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db,
                charset='utf8mb4',
            )

            print("Connected to MySQL!")

            self.cursor = self.connection.cursor()

            self.create_tables()

            return True
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return False

    def create_tables(self):
        create_tables_query = """
        DROP TABLE IF EXISTS ActivityData;

        CREATE TABLE IF NOT EXISTS ActivityData (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Time DATETIME,
            Distance FLOAT,
            Heart_Rate FLOAT,
            Speed FLOAT,
            Cadance INT,
            Altitude_Meters FLOAT
        )
        """

        for statement in create_tables_query.split(';'):
            if statement.strip():
                self.cursor.execute(statement)

        self.connection.commit()

    def close_connection(self):
        if self.connection:
            self.connection.close()

# Example Usage:
# config = {'Database': {'host': 'localhost', 'user': 'username', 'password': 'password', 'database': 'dbname'}}
# db = DatabaseManager(config)
# db.establish_connection()
# # Perform database operations
# db.close_connection()
