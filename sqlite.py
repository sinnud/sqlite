""" Example to use SQLite
"""

from logzero import logger
from utils import ConfigOps
from utils import FileSync # for copy_file_in_list

logger.info("Start working...")
db = 'd:/data/code4photo/test.db'
table = 'disk1'
tbl_str_list = ['NAME', 'PATH', 'FILESIZE', 'CHANGETIME', 'REL_NAME']
table_structure=' TEXT, '.join(tbl_str_list)
table_structure = f"{table_structure} TEXT"
table_header=', '.join(tbl_str_list[:-1])
config_file = 'd:/data/code4photo/synchist.txt'
fs = FileSync(config_file = config_file,
        table_structure=table_structure,
        table_header=table_header,
        waittime=3,
)
fs.folder_sync(db = db)
'''
fis = FileInfoSqlite(db=db)

mydir = r'\\wdmycloud\data\ydata\important\2021tax'
fis.table_check(table=table, drop_if_exist=True,
    table_structure=table_structure
    )
logger.debug("SQLite: prepared table disk1")
datalist = FileSync().dir_info(filedir=mydir)
logger.debug(f"Got dir info into list")
fis.import_data(table=table, datalist=datalist, header=table_header)
logger.debug("SQLite: disk1 imported")
table = 'disk2'
mydir = r'\\192.168.86.104\Public\data\ydata\important\2021tax'
fis.table_check(table=table, drop_if_exist=True,
    table_structure=table_structure
    )
logger.debug("SQLite: prepared table disk2")
datalist = FileSync().dir_info(filedir=mydir)
logger.debug(f"Got dir info into list")
fis.import_data(table=table, datalist=datalist, header=table_header)
logger.debug("SQLite: disk2 imported")
fis.compute_relname(table='disk1', prefix=r'\\wdmycloud')
logger.debug("SQLite: disk1 rel name")
fis.compute_relname(table='disk2', prefix=r'\\192.168.86.104\Public')
logger.debug("SQLite: disk2 rel name")

fl=fis.compute_newfiles(table='disk1', tablebase='disk2')
str_fl = '\n'.join(fl)
logger.debug(f"New files: {str_fl}")
FileSync().copy_file_in_list(filelist=fl, source_prefix=r'\\wdmycloud', target_prefix=r'\\192.168.86.104\Public')
logger.debug(f"Synced new files.")
fl=fis.compute_updatedfiles(table='disk1', tablebase='disk2')
str_fl = '\n'.join(fl)
logger.debug(f"Updated files: {str_fl}")
FileSync().copy_file_in_list(filelist=fl, source_prefix=r'\\wdmycloud', target_prefix=r'\\192.168.86.104\Public')
logger.debug(f"Synced Updated files.")

FileSync(waittime = 3).target_create_folder()
'''