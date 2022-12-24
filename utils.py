""" Some functions to use
Updates:
22DEC2022-LD accelerate executemany based on https://stackoverflow.com/questions/35013453/apsw-or-sqlite3-very-slow-insert-on-executemany
"""
import os
from datetime import datetime # timestamp
from logzero import logger # logger
import sqlite3 # Looks slow when import into table, any way to accelerate it?
import glob    # for getting file and folder info
import shutil  # for copy files
from inputimeout import inputimeout, TimeoutOccurred # time out for waiting inputs
from sys import exit

class MySqlite(object):
    """ Interface to SQLite
    """
    def __init__(self,
    db = None,
    ):
        self.db = db
        self.conn = None

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
        logger.debug(f"Connect to SQLite database '{self.db}'...")

    def execute(self, query):
        """ execute query
        return array instead of cursor
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        cursor.execute(query)
        try:
            rst = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            return cursor
        # logger.debug(f"Result length: {len(rst)}")
        return rst

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
        cursor.execute("BEGIN TRANSACTION;")
        cursor.executemany(query, datalist)
        cursor.execute("COMMIT;")

class FileInfo(object):
    """ Create file information
    """
    def get_dir_file_list_in_folder(self, thisdir=None):
        """ Just list sub-folders and files at current folder
        Do not work recursively
        """
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
        """ Get file size and timestamp
        """
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

class FileInfoSqlite(object):
    """ Check file info and store to SQLite database
    Assumption:
    - One folder only. SQLite table includes file information under this folder
    - Table structure: file name, file path, file size, file timestmap, and relative path
    - Each time drop table and create one (this is slow?)
    """
    def __init__(self, db = None, ):
        self.sqlite = MySqlite(db = db)

    def table_check(self, table = None, drop_if_exist = False, table_structure = None):
        """ Check table
        if not exist, create it
        """
        tblex = self.sqlite.table_exist(table=table)
        if tblex and drop_if_exist:
            self.sqlite.drop_table(table=table)
        elif tblex:
            return
        qry = f"CREATE TABLE {table} ({table_structure});"
        self.sqlite.execute(qry)

    def import_data(self, table = None, datalist = None, header = None):
        """ Import data into table
        The header argument list column name
        """
        fieldcnt = len(header.split(','))
        wildlist = ['?'] * fieldcnt
        wildstr = ', '.join(wildlist)
        qry = f"INSERT INTO {table} ({header}) VALUES({wildstr})"
        self.sqlite.import_from_datalist(query=qry, datalist=datalist)

    def compute_relname(self, table = None, prefix=None):
        """ Compute relative path for comparing
        """
        qry = f"update {table}"
        qry = f"{qry} set rel_name = replace(path, '{prefix}', '')||'\\'||name"
        self.sqlite.execute(qry)

    def compute_newfiles(self, table = None, tablebase = None):
        """ Compute relative path for comparing
        """
        qry = f"select a.REL_NAME from {table} a left join {tablebase} b on a.rel_name = b.REL_NAME where b.filesize is null"
        return [x[0] for x in self.sqlite.execute(qry)]

    def compute_updatedfiles(self, table = None, tablebase = None):
        """ Compute relative path for comparing
        """
        qry = f"select a.REL_NAME from {table} a join {tablebase} b on a.rel_name = b.REL_NAME where a.filesize != b.filesize"
        return [x[0] for x in self.sqlite.execute(qry)]

class ConfigOps(object):
    """ Read from config file
    Get first folder we need to handle
    Update config file

    config file line start with '#' as comment and historical log with timestamp
    """
    def __init__(self,
            config_file = None,
    ):
        self.config_file = config_file
        with open(self.config_file, 'r', encoding="utf-8") as f:
            self.config_lines = f.readlines()
        self.current_idx = None
    
    def get_first_folder(self):
        """ Get first non-comment line and record idx
        """
        folder = None
        for idx, line in enumerate(self.config_lines, start = 1):
            line = line.strip()
            if line.startswith('#'):
                continue
            folder = line
            self.current_idx = idx
            break
        if folder is None:
            logger.debug("Finished all folders in config file!!!")
        return folder
    
    def update_config_with_dirlist(self,
            newfilecnt = None,
            updatedfilecnt = None,
            dirlist = None,
    ):
        """ Using dirlist to update config file
        """
        with open(self.config_file, 'w', encoding="utf-8") as f:
            for idx, line in enumerate(self.config_lines, start = 1):
                line = line.strip()
                if idx == self.current_idx:
                    timestampstr = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                    f.write(f"# {line} -- synced {timestampstr}\n")
                    if newfilecnt == 0 and updatedfilecnt == 0:
                        continue
                    f.write(f"# ---- synced {newfilecnt} new files and {updatedfilecnt} updated files\n")
                else:
                    f.write(f"{line}\n")
            if dirlist is not None:
                for line in sorted(dirlist):
                    f.write(f"{line}\n")

class FileSync(object):
    """ Copy files
    """
    def __init__(self,
            config_file = None,
            waittime = None,
            src_tbl = 'disk1',
            src_prefix = r'\\wdmycloud',
            tgt_tbl = 'disk2',
            tgt_prefix = r'\\192.168.86.104\Public',
            table_structure = None,
            table_header = None,
    ):
        self.config_file = config_file
        self.waittime = waittime
        self.src_tbl = src_tbl
        self.src_prefix = src_prefix
        self.tgt_tbl = tgt_tbl
        self.tgt_prefix = tgt_prefix
        self.table_structure = table_structure
        self.table_header = table_header
        self.dirlist = None

    def folder_sync(self, db = None):
        """ Sync folder and all sub-folders using config file
        """
        co = ConfigOps(config_file=self.config_file)
        rel_dir = co.get_first_folder()
        while rel_dir is not None:
            newfilecnt, updatedfilecnt, dirlist = self.one_folder_sync(db=db, rel_dir=rel_dir)
            co.update_config_with_dirlist(newfilecnt=newfilecnt, updatedfilecnt=updatedfilecnt, dirlist=dirlist)
            co = ConfigOps(config_file=self.config_file)
            rel_dir = co.get_first_folder()

    def one_folder_sync(self, db = None, rel_dir = None):
        """ Sync one filder from config file
        """
        fis = FileInfoSqlite(db=db)
        fis.table_check(table=self.src_tbl, drop_if_exist=True,
            table_structure=self.table_structure)
        logger.debug(f"SQLite: prepared table {self.tgt_tbl}.")
        fis.table_check(table=self.tgt_tbl, drop_if_exist=True,
            table_structure=self.table_structure)
        logger.debug(f"SQLite: prepared table {self.tgt_tbl}.")

        src_dir = f"{self.src_prefix}{rel_dir}"
        datalist = self.dir_info(filedir=src_dir, store_src_dirlist = True)
        logger.debug(f"Got dir info of {src_dir} into list.")
        fis.import_data(table=self.src_tbl, datalist=datalist, header=self.table_header)
        logger.debug(f"SQLite: {self.src_tbl} imported")
        fis.compute_relname(table=self.src_tbl, prefix=self.src_prefix)
        logger.debug(f"SQLite: {self.src_tbl} rel name")
        
        tgt_dir = f"{self.tgt_prefix}{rel_dir}"
        if not os.path.isdir(tgt_dir):
            rst = self.target_create_folder(new_folder=tgt_dir)
            if not rst:
                logger.error(f"You stop creating target folder!!!")
                exit(1)
        datalist = self.dir_info(filedir=tgt_dir)
        logger.debug(f"Got dir info of {tgt_dir} into list.")
        fis.import_data(table=self.tgt_tbl, datalist=datalist, header=self.table_header)
        logger.debug(f"SQLite: {self.tgt_tbl} imported")
        fis.compute_relname(table=self.tgt_tbl, prefix=self.tgt_prefix)
        logger.debug(f"SQLite: {self.tgt_tbl} rel name")

        fl=fis.compute_newfiles(table=self.src_tbl, tablebase=self.tgt_tbl)
        str_fl = '\n'.join(fl)
        logger.debug(f"New files: {str_fl}")
        self.copy_file_in_list(filelist=fl, source_prefix=self.src_prefix, target_prefix=self.tgt_prefix)
        logger.debug(f"Synced new files.")
        newfilecnt = len(fl)

        fl=fis.compute_updatedfiles(table=self.src_tbl, tablebase=self.tgt_tbl)
        str_fl = '\n'.join(fl)
        logger.debug(f"Updated files: {str_fl}")
        self.copy_file_in_list(filelist=fl, source_prefix=self.src_prefix, target_prefix=self.tgt_prefix)
        logger.debug(f"Synced updated files.")
        updatedfilecnt = len(fl)

        return newfilecnt, updatedfilecnt, self.dirlist

    def promptcall(self):
        """ prompt with timeout
        """
        if self.waittime is None:
            return True
        try:
            y_or_n = inputimeout(prompt=f'[Create folder(Y, N)] (default Y wait for {self.waittime} seconds) >> ', timeout=self.waittime)
        except TimeoutOccurred:
            y_or_n = 'Y'
        if y_or_n == 'Y':
            return True
        return False

    def dir_info(self, filedir = None, store_src_dirlist = False):
        """ Get directory file information
        """
        dirlist, filelist = FileInfo().get_dir_file_list_in_folder(thisdir=filedir)
        if store_src_dirlist:
            self.dirlist = [x.replace(self.src_prefix, '') for x in dirlist]
        datalist=[]
        for f in filelist:
            status, f_info = FileInfo().file_info(thisfile=f)
            if not status:
                logger.error(f"Failed to get file info for '{f}'")
                exit()
            data = tuple(f_info) # use tuple considering `sqlite3.executemany` format
            datalist.append(data)
        return datalist

    def copy_file_in_list(self, filelist = None, source_prefix = None, target_prefix = None):
        """ Add prefix to each file and copy
        """
        for f in filelist:
            logger.debug(f"Sync {f}...")
            src = f"{source_prefix}{f}"
            tgt = f"{target_prefix}{f}"
            shutil.copy2(src, tgt)

    def target_create_folder(self, new_folder=None):
        """ Create target folder
        """
        if not self.promptcall():
            logger.debug(f"Do not create folder '{new_folder}'!!!")
            return False
        logger.debug(f"Start creating folder '{new_folder}'...")
        os.makedirs(new_folder, exist_ok=True)
        return True