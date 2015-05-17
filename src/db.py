import cx_Oracle


class Db():
    def __init__(self, db_connection='ukrtel/ukrtel@bill'):
        try:
            self.conn = cx_Oracle.connect(db_connection)
            self.curr = self.conn.cursor()
        except cx_Oracle.DatabaseError as (strerror):
            print "DB connection error: {0}".format(strerror)
            print "DB connection:", db_connection
            raise

if __name__ == '__main__':
    pass
