#!/usr/bin/env python3

from structlog import get_logger
import logging
from pathlib import Path

from sqlalchemy import select, create_engine, Table, Column, Integer, String, LargeBinary, Float, JSON, ForeignKey
from sqlalchemy.orm import Session, declarative_base, relationship

from secondlife.plugins.api import v1
from secondlife.infoset import Infoset
from secondlife.celldb import CellDB

log = get_logger()

Base = declarative_base()
class Cell(Base):
    __tablename__ = 'cells'

    id = Column(String, primary_key=True)
    container_cell_id = Column(String, ForeignKey('cells.id'), nullable=True)
    props = Column(JSON)

    log_entries = relationship('LogEntry', back_populates='cell')
    extras = relationship('Extra', back_populates='cell')

class LogEntry(Base):
    __tablename__ = 'log_entries'

    cell_id = Column(String, ForeignKey('cells.id'), primary_key=True)
    idx = Column(Integer, primary_key=True)
    ts = Column(Float)
    entry = Column(JSON)

    cell = relationship('Cell', back_populates='log_entries')

class Extra(Base):
    __tablename__ = 'extras'

    cell_id = Column(String, ForeignKey('cells.id'), primary_key=True)
    name = Column(String, primary_key=True)
    props = Column(JSON)
    ref = Column(String)
    content = Column(LargeBinary)
    
    cell = relationship('Cell', back_populates='extras')

class SQLAlchemy(CellDB):
    def __init__(self, dsn=None, **kwargs):
        super().__init__()

        self.config = kwargs['config']
        self.dsn = dsn
        self.engine = create_engine(self.dsn, echo=True if self.config.loglevel == 'DEBUG' else False, future=True)

        log.debug('backend setup', engine=self.engine)

    def __repr__(self):
        return f'SQLAlchemy/{repr(self.engine)}'

    def init(self):
        log.info('creating celldb', engine=self.engine)

        Base.metadata.create_all(self.engine)
    
    def fetch(self, id: str) -> Infoset:
        log.info('fetching infoset', id=id)

        infoset = Infoset()
        infoset.put('.id', id)
        infoset.put('.extra', [])
        infoset.put('.log', [])

        with Session(self.engine) as session:

            cell = session.execute( select(Cell).where(Cell.id==id) ).first()
            if cell is None:
                return None

            cell = cell[0]
                
            infoset.put('.props', cell.props)

            # Synthesize path
            if cell.container_cell_id is not None:
                parts = [ '', cell.container_cell_id ]
                p = session.execute( select(Cell).where(Cell.id==cell.container_cell_id)).first()[0]
                while p.container_cell_id is not None:
                    parts.append(p.continer_cell_id)
                    p = session.execute( select(Cell).where(Cell.id == p.container_cell_id)).first()[0]
                
                infoset.put('.path', '/'.join(parts))
            else:
                infoset.put('.path', '/')

            for e in sorted(cell.log_entries, key=lambda e: e.idx):
                if e.ts is not None:
                    e.entry.update({ 'ts': e.ts })
                
                infoset.fetch('.log').append(e.entry)

            for extra in cell.extras:
                # TODO: Restore mtime and ctime from props
                infoset.fetch('.extra').append({
                    'name': extra.name,
                    'props': extra.props,
                    'ref': extra.ref,
                    'content': extra.content
                })

        # Bind the state variables
        for (path, statevar_class) in v1.state_vars.items():
            infoset.put(f'.state.{path}', statevar_class(cell=infoset))

        return infoset

    def put(self, infoset: Infoset):

        props = infoset.fetch('.props')
        cell_id = infoset.fetch('.id')

        container_cell_id = None
        if infoset.fetch('.path') is not None:
            parent_container = Path(infoset.fetch('.path')).name
            if parent_container:
                container_cell_id = parent_container

        with Session(self.engine) as session:
            session.merge( Cell(id=cell_id, container_cell_id=container_cell_id, props=props) )

            log_entries = infoset.fetch('.log')
            for idx in range(len(log_entries)):
                ts = log_entries[idx].pop('ts', None)
                session.merge( LogEntry(cell_id=cell_id, idx=idx, ts=ts, entry=log_entries[idx]) )

            for extra in infoset.fetch('.extra'):
                session.merge( Extra(cell_id=cell_id, name=extra['name'], 
                    props=extra['props'], ref=extra['ref'], content=extra['content']) )

            session.flush()
            session.commit()

    def find(self) -> Infoset: # Generator

        with Session(self.engine) as session:

            for cell in session.execute( select(Cell) ):
                yield self.fetch(cell[0].id)

v1.register_celldb_backend('sql-alchemy', SQLAlchemy)