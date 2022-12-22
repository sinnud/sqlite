""" Example to use SQLite
"""

from logzero import logger

from utils import FileSync

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
"""
import os
from utils import MySqlite, FileSync
db = '../test.db'
ms = MySqlite(db=db)
mydir = os.path.realpath(r'C:\Users\LukeDu\Downloads')
datalist = FileSync().dir_info(filedir=mydir)
logger.debug(f"Got dir info of {mydir} into list.")
tbl_str_list = ['NAME', 'PATH', 'FILESIZE', 'CHANGETIME', 'REL_NAME']
header=', '.join(tbl_str_list[:-1])
fieldcnt = len(header.split(','))
wildlist = ['?'] * fieldcnt
wildstr = ', '.join(wildlist)
qry = f"INSERT INTO disk1 ({header}) VALUES({wildstr})"
ms.import_from_datalist(qry, datalist)
logger.debug(f"SQLite: {mydir} imported")
"""