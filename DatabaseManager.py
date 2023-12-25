import mysql.connector

class DatabaseManager:
    def __init__(self, config):
        self.host = config['Database']['host']
        self.user = config['Database']['user']
        self.password = config['Database']['password']
        self.db = config['Database']['database']

    def establish_connection(self):
        try:
            print(f"Connecting to MySQL with host={self.host}, user={self.user}, database={self.db}")
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
            print(f"Failed to establish connection. Details: {self.host}, {self.user}, {self.db}")
            return False

    def create_tables(self):
        create_tables_query = """
        CREATE TABLE IF NOT EXISTS Run_Name (
            id INT AUTO_INCREMENT PRIMARY KEY,
            run_name VARCHAR(255)
        );

        CREATE TABLE IF NOT EXISTS ActivityData (
            id INT AUTO_INCREMENT PRIMARY KEY,
            run_name_id INT,
            Time DATETIME,
            Distance FLOAT,
            Heart_Rate FLOAT,
            Speed TIME,
            Cadance INT,
            Altitude_Meters FLOAT,
            FOREIGN KEY (run_name_id) REFERENCES Run_Name(id)
        );
        """

        try:
            for statement in create_tables_query.split(';'):
                if statement.strip():
                    self.cursor.execute(statement)

            self.connection.commit()
            print("Tables created successfully.")
        except mysql.connector.Error as e:
            print(f"Error creating tables: {e}")

    def close_connection(self):
        print("close connection")
        if self.connection:
            self.connection.close()

# Example Usage:
# config = {'Database': {'host': 'localhost', 'user': 'username', 'password': 'password', 'database': 'dbname'}}
# db = DatabaseManager(config)
# db.establish_connection()
# # Perform database operations
# db.close_connection()
