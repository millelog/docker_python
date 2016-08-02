import sqlite3
import subprocess
import sys
import os
from datetime import datetime

class class_database(object):
        """This class will do all read and writes to the class database"""
        def __init__(self):
                self.db_path = "/data/cgrb/database.sqlite"
                self.ctn = 'classes'
                self.ptn = 'ports'
                self.class_name = 'class_name'
                self.instructor = 'instructor'
                self.inuse = 'inuse'
                self.port = 'port'
                self.conn = self.get_connection()
                self.create_class_table()
                self.create_port_table()

        def get_connection(self):
                """try a connection to the database path"""
                try:
                        self.conn = sqlite3.connect(self.db_path)
                except sqlite3.Error:
                        print("Error connecting to database")

        def create_class_table(self):
                self.get_connection()
                c = self.conn.cursor()
                #Create the table with the proper initial columns
                c.execute('''CREATE TABLE IF NOT EXISTS '{ctn}' (
                        '{cn}' {tf} PRIMARY KEY,
                        '{p}' {num},
                        '{i}' {tf});'''\
                        .format(ctn=self.ctn, p=self.port, cn=self.class_name, tf='TEXT', num='INTEGER', i=self.instructor))
                self.commit_db()

        def create_port_table(self):
                #connect to database
                self.get_connection()
                c = self.conn.cursor()
                #create the port table
                c.execute('''CREATE TABLE IF NOT EXISTS '{ptn}' (
                        '{p}' {num} PRIMARY KEY,
                        '{iu}' {num});'''\
                        .format(ptn=self.ptn, iu=self.inuse, p=self.port, num='INTEGER'))
                #commit to database
                self.commit_db()

        def insert_class(self, port, class_name, instructor):
                #connect to database
                self.get_connection()
                c=self.conn.cursor()
                #insert the parameters into their columns
                c.execute("INSERT OR REPLACE INTO '{ctn}' ('{p}', '{cn}', '{i}') VALUES ('{pv}', '{cnv}', '{iv}');".\
                        format(ctn=self.ctn, p=self.port, cn=self.class_name, i=self.instructor, pv=port, cnv=class_name, iv=instructor))
                c.execute("INSERT OR REPLACE INTO '{ptn}' ('{p}', '{iu}') VALUES ('{pv}', '{iuv}');".\
                        format(ptn=self.ptn, p=self.port, iu=self.inuse, pv=port, iuv=1))
                #Log class creation
                self.log(" : added to database : "+class_name+" - Instructor: "+instructor+" - Port: "+port)
                #commit info to database
                self.commit_db()

        def remove_class(self, class_name, port):
                #connect to database
                self.get_connection()
                c = self.conn.cursor()
                #command string to delete from class table
                sql = """
                        DELETE FROM {ctn}
                        WHERE {cn} = '{name}';
                """.format(ctn=self.self.ctn, cn=self.class_name, name=class_name)
                c.execute(sql)
                #command string to set port use table
                sql="INSERT OR REPLACE INTO '{ptn}' ('{iu}') VALUES ('{iuv}') WHERE {p} = '{pv}';".\
                        format(ptn=self.ptn, iu=self.inuse, iuv=0, p=self.port, pv=port)
                c.execute(sql)
                #log this removal
                self.log(" : removd from database : "+class_name+" : "+port+" is now free")
                #Commit to database
                self.commit_db()

        def log(self, string):
                with open("/data/log.txt", "a") as log:
                        log.write(str(datetime.now())++string)

        def commit_db(self):
                """commit database changes in info and close the connection"""
                self.conn.commit()
                self.conn.close()