""" Example to use SQLite
"""

from logzero import logger
from utils import MySqlite
from utils import FileInfo # for get_dir_file_list_in_folder and file_info

class FileInfoSqlite(object):
    """ Check file info and store to SQLite database
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

    def dir_info(self, filedir = None):
        """ Get directory file information
        """
        dirlist, filelist = FileInfo().get_dir_file_list_in_folder(thisdir=filedir)
        datalist=[]
        for f in filelist:
            status, f_info = FileInfo().file_info(thisfile=f)
            if not status:
                logger.error(f"Failed to get file info for '{f}'")
                exit()
            data = tuple(f_info)
            datalist.append(data)
        return datalist

logger.info("Start working...")
db = '../test.db'
table = 'disk1'
tbl_str_list = ['NAME', 'PATH', 'FILESIZE', 'CHANGETIME', 'REL_NAME']
table_structure=' TEXT, '.join(tbl_str_list)
table_structure = f"{table_structure} TEXT"
table_header=', '.join(tbl_str_list[:-1])
fis = FileInfoSqlite(db=db)
fis.table_check(table=table, drop_if_exist=True,
    table_structure=table_structure
    )
mydir = r'C:\Users\LukeDu\Documents\code\sqlite'
datalist = fis.dir_info(filedir=mydir)
logger.debug(datalist)
fis.import_data(table=table, datalist=datalist, header=table_header)
# ms = MySqlite(db = db)
# logger.debug(f"Note: {ms}")
# tables = ms.tables()
# logger.info(f"We already have tables: {tables}")
# logger.debug(f"Table disk1 exists: {ms.table_exist(table='disk1')}")
# qry = 'select count(*) from disk1'
# out = ms.execute(qry)
# logger.info(f"Table disk1 have records number: {out}")