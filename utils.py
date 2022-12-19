""" Some functions to use
"""
import os
from datetime import datetime
from logzero import logger
import sqlite3
import glob
class MySqlite(object):
    """ Interface to SQLite
    """
    def __init__(self,
    db = None,
    ):
        self.db = db
        self.conn = None # sqlite3.connect(self.db)
        logger.debug(f"Connect to SQLite database '{self.db}'...")

    def __repr__(self):
        """ It could be represented
        """
        return f"SQLite: Database='{self.db}'"

    def __del__(self):
        """ destruction
        """
        if self.conn:
            self.conn.close()
            logger.debug(f"Connection to database '{self.db}' closed")

    def connect(self):
        """ Connect with auto commit
        """
        # self.conn = sqlite3.connect(self.db, autocommit=True)
        self.conn = sqlite3.connect(self.db, isolation_level=None)

    def execute(self, query):
        """ execute query
        return array instead of cursor
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        return [x for x in cursor.execute(query)]

    def tables(self):
        """ List tables in database
        """
        qry = '''
        SELECT name FROM sqlite_schema
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        '''
        return [x[0] for x in self.execute(qry)]

    def drop_table(self, table = None):
        """ List tables in database
        """
        qry = f'DROP TABLE {table}'
        self.execute(qry)

    def table_exist(self, table = None):
        """ List tables in database
        """
        qry = f'''
        SELECT name FROM sqlite_schema
        WHERE type = 'table'
        AND name = '{table}'
        '''
        if len(self.execute(qry)) == 0:
            return False
        else:
            return True        

    def import_from_datalist(self, query, datalist):
        """ import data list into table using query
        Sample query is: "INSERT INTO person (name, age) VALUES(?, ?)"
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.executemany(query, datalist)

class FileInfo(object):
    """ Create file information
    """
    def get_dir_file_list_in_folder(self, thisdir=None):
        dirlist=list()
        filelist=list()
        checklist=glob.glob(f"{thisdir}/*")
        for elm in checklist:
            if os.path.isdir(elm):
                dirlist.append(elm)
            else:
                filelist.append(elm)
        return dirlist, filelist

    def file_info(self, thisfile=None):
        if not os.path.exists(thisfile):
            logger.error(f"{thisfile} does NOT exist!!!")
            return False, None
        if os.path.isdir(thisfile):
            logger.error(f"{thisfile} is directory, NOT file!!!")
            return False, None
        
        path, fn=os.path.split(thisfile)
        st=os.stat(thisfile)
        dt=datetime.fromtimestamp(st.st_ctime)
        dt_fmt=dt.strftime("%Y-%m-%d %H:%M:%S")
        return True, [fn, path, str(st.st_size), dt_fmt]