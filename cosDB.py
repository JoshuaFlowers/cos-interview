import MySQLdb

class cosDB:

    def __init__(self):
        # Define the database credentials
        self.host = 'localhost'
        self.user = 'cos'
        self.password = 'cos_pass'
        self.db = 'chiefofstaff'

    def connect(self):
        """Establish a connection to the database and return the connection object."""
        try:
            conn = MySQLdb.connect(host=self.host,
                                   user=self.user,
                                   passwd=self.password,
                                   db=self.db)
            return conn
        except MySQLdb.Error as e:
            print(f"Error {e.args[0]}: {e.args[1]}")
            return None

    def insert_user(self, email, authorized, token, last_authenticated):
        """Insert a new user into the users table."""
        conn = self.connect()
        if conn is None:
            return False

        cursor = conn.cursor()

        try:
            insert_query = """
                    INSERT INTO users
                    (email, authorized, token, last_authenticated)
                    VALUES (%s, %s, %s, %d)"
                    ON DUPLICATE KEY UPDATE
                    authorized = VALUES(authorized),
                    token = VALUES(token),
                    last_authenticated = VALUES(last_authenticated)
                    """
            cursor.execute(insert_query, (email, authorized, token, last_authenticated))
            conn.commit()
            return True
        except MySQLdb.Error as e:
            print(f"Error {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user(self, email):
        """Fetch a user based on the email provided."""
        conn = self.connect()
        if conn is None:
            return None

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)  # This will return the result as a dictionary

        try:
            select_query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(select_query, (email,))
            user = cursor.fetchone()  # fetch one record
            return user
        except MySQLdb.Error as e:
            print(f"Error {e.args[0]}: {e.args[1]}")
            return None
        finally:
            cursor.close()
            conn.close()
