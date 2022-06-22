import logging
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

DATABASE = {
   'drivername': 'sqlite',
   'database': '/app/app.db'
}

def drop_table(table_name):
   engine = create_engine(URL(**DATABASE))
   base = declarative_base()
   metadata = MetaData(engine, reflect=True)
   table = metadata.tables.get(table_name)
   if table is not None:
       logging.info(f'Deleting {table_name} table')
       base.metadata.drop_all(engine, [table], checkfirst=True)

drop_table('user')
