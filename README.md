# sqlite

## Purpose
- Collect file information and store to database (SQLite 3)
- Compare two portable drive to sync them

## Design
- File `utils.py` includes two Python classes:
  - Class `MySqlite` as interface to SQLite database
  - Class `FileInfo` to obtain file information
- File `sqlite.py` includes usage of tools in `utils.py`
  - Class `FileInfoSqlite` calls two classes above
  - The main part just call the above class