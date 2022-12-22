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