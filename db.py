import psycopg2 as psy

def get_connection():
    return psy.connect(
        host = "localhost",
        database = "bloodtestreport",
        user = "postgres", 
        password = "P@ssw0rd"
        )
# cursor = con.cursor()