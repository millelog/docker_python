import sqlite3
import subprocess
import sys
import os
import logger as log


class class_database(object):
        """This class will do all read and writes to the class database"""
        def __init__(self):
                #Variables that refer to columns and names of the database to lower the chance of spelling errors
                self.db_path = "/data/cgrb/database.sqlite"
                self.ctn = 'classes'
                self.ptn = 'ports'
                self.class_name = 'class_name'
                self.instructor = 'instructor'
                self.inuse = 'inuse'
                self.port = 'port'
                self.conn = self.get_connection()
                self.create_port_table()
                self.create_class_table()
                

        def get_connection(self):
                """try a connection to the database path"""
                try:
                        self.conn = sqlite3.connect(self.db_path)
                except sqlite3.Error:
                        print("Error connecting to database")

                return self.conn.cursor()

        def create_class_table(self):
                c = self.get_connection()
                c.execute("PRAGMA foreign_keys = ON;")
                #Create the table with the proper initial columns
                c.execute('''CREATE TABLE IF NOT EXISTS '{ctn}' (
                        {host} {tf} NOT NULL,
                        {p} {num} NOT NULL,
                        {cn} {tf} PRIMARY KEY,
                        {hrname} {tf},
                        {i} {tf},
                        {first} {tf},
                        {last} {tf},
                        {email} {tf},
                        FOREIGN KEY({host}) REFERENCES {ptn}({host}),
                        FOREIGN KEY({p}) REFERENCES {ptn}({p}));'''\
                        .format(ctn=self.ctn, p=self.port, cn=self.class_name, hrname='readable_name', host='host', tf='TEXT', num='INTEGER', 
                                i=self.instructor, first='first', last='last', email='email', ptn=self.ptn))
                self.commit_db()

        def populate_port_table(self, hv):
                c = self.get_connection()
                #Add 100 ports as not in use for the given host name
                for i in range(8001, 8101):
                        sql="INSERT OR IGNORE INTO {ptn} VALUES ('{hv}', '{pv}', '{iuv}');".\
                                format(ptn=self.ptn, hv=hv, pv=i, iuv=0)
                        c.execute(sql)
                self.commit_db()

        def create_port_table(self):
                #connect to database
                c = self.get_connection()
                #create the port table
                c.execute('''CREATE TABLE IF NOT EXISTS '{ptn}' (
                        '{host}' {text} NOT NULL,
                        '{p}' {num} NOT NULL,
                        '{iu}' {num},
                        PRIMARY KEY ({host}, {p})
                        );'''\
                        .format(ptn=self.ptn, host='host', text='TEXT', iu=self.inuse, p=self.port, num='INTEGER'))
                #commit to database
                self.commit_db()

        def insert_class(self, host, port, class_name, readable_name, instructor, first, last, email):
                #connect to database
                c=self.get_connection()
                sql = "INSERT OR REPLACE INTO {ctn} VALUES ('{hv}', '{pv}', '{cnv}', '{rnv}', '{iv}', '{fv}', '{lv}', '{ev}');".\
                        format(ctn=self.ctn, pv=port, hv=host, cnv=class_name, rnv=readable_name, iv=instructor, fv=first, lv=last, ev=email)
                #insert the parameters into their columns
                c.execute(sql)
                sql="UPDATE {ptn} SET {iu} = '{iuv}' WHERE {h}='{hv}' AND {p}='{pv}';".\
                        format(ptn=self.ptn, h='host', p=self.port, iu=self.inuse, hv=host, pv=port, iuv=1)
                c.execute(sql)
                #Log class creation
                log.log(" : added to database : "+class_name+" - Instructor: "+instructor+" - Host: "+host+" - Port: "+str(port))
                #commit info to database
                self.commit_db()
        
        def get_instructor_info(self, class_name):
                '''Returns a dict of the isntructors first, last and email'''
                c = self.get_connection()
                #Define the dictionaries
                info = {'first': '', 'last': '', 'email': ''}
                #Returns a tuple of the columns notated where class name is the same as the parameter
                for row in c.execute("SELECT {first}, {last}, {email}, {rname} FROM {ctn} WHERE {cn} = \'{class_name}\';".\
                        format(first='first', last='last', email='email', rname='readable_name', ctn=self.ctn, cn= self.class_name, class_name=class_name)):
                        info = {
                                'first': row[0].capitalize(),
                                'last': row[1].capitalize(),
                                'email': row[2],
                                'class_name': row[3]
                        }
                return info
                 

        def get_class_names(self):
                #connect to the database
                c = self.get_connection()
                #get class names
                names = list()
                for row in c.execute("SELECT {class_name} FROM {ctn};".\
                        format(class_name=self.class_name, ctn=self.ctn)):
                        names.append(row[0].rstrip())
                return names

        def get_unique_hosts(self):
                c=self.get_connection()
                hosts = [None]
                #For all the lines in the ports database
                for row in c.execute("SELECT {host} FROM {ptn};".\
                        format(host='host', ptn=self.ptn)):
                        #Unique part
                        if not row[0].rstrip() == hosts[0]:
                                hosts.append(row[0].rstrip())
                return hosts

        def remove_class(self, class_name):
                #connect to database
                c=self.get_connection()
                #Get port of class_name
                sql = "SELECT {p} FROM {ctn} WHERE {cn} = \'{name}\';".\
                        format(p=self.port, ctn=self.ctn, cn=self.class_name, name=class_name)

		# execute returns a tuple of tuples, turn it into a list 
                ports = c.execute(sql).fetchall()
		#If no available ports
                if not ports:
                        log.log("There are no avaibale ports for "+class_name+" and the program quit without finishing")
                        exit(2)

                remove_ports = list()
                for port in ports:
                        remove_ports.append(port[0])
                for port in remove_ports:
                        #command string to set port use table
                        sql="UPDATE {ptn} SET {iu}= {iuv} WHERE {p} = {pv};".\
                               format(ptn=self.ptn, iu=self.inuse, iuv=0, p=self.port, pv=port)
                        c.execute(sql)
                        #log this removal
                        log.log(" : removed from database : "+class_name+" : "+str(port)+" is now free")
                
                #command string to delete from class table
                sql = "DELETE FROM {ctn} WHERE {cn} = \'{name}\';".\
                        format(ctn=self.ctn, cn=self.class_name, name=class_name)
                c.execute(sql)
                
                
                #Commit to database
                self.commit_db()

        def print_ports(self):
                c = self.get_connection()
                sql = "SELECT {p}, * FROM {ptn} ORDER BY {p};".format(p=self.port, ptn=self.ptn)
                for row in c.exvimecute(sql):
                        print(row)

        def print_classes(self):
                c = self.get_connection()
                sql = "SELECT {c}, * FROM {ctn} ORDER BY {c}".format(c=self.class_name, ctn=self.ctn)
                for row in c.execute(sql):
                        print(row)

        
        def get_available_ports(self, host):
                c=self.get_connection()
                ports=[]
                #Select ports of the given host name that are not in use
                for row in c.execute("SELECT {port} FROM {ptn} WHERE {h} = '{hv}' AND {iu} = '{iuv}';".\
                format(port=self.port, ptn=self.ptn, h='host', hv=host, iu=self.inuse, iuv=0)):
                        ports.append(row[0])

                sql = 'UPDATE {ptn} SET {iu}={iuv} WHERE {p} = {pv};'.\
                        format(ptn=self.ptn, iu=self.inuse, iuv=1, p=self.port, pv=ports[0])
                c.execute(sql)
                self.commit_db()
                return ports

        def get_first_available_port(self, host):
                return self.get_available_ports(host)[0]

        

        def commit_db(self):
                """commit database changes in info and close the connection"""
                self.conn.commit()
                self.conn.close()
