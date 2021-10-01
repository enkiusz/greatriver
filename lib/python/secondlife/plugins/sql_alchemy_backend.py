#!/usr/bin/env python3

from structlog import get_logger
import logging
from pathlib import Path
from collections import defaultdict
from copy import deepcopy

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

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id} container_cell_id={self.container_cell_id} props={self.props}>'


class LogEntry(Base):
    __tablename__ = 'log_entries'

    cell_id = Column(String, ForeignKey('cells.id'), primary_key=True)
    idx = Column(Integer, primary_key=True)
    ts = Column(Float)
    entry = Column(JSON)

    cell = relationship('Cell', back_populates='log_entries')

    def __repr__(self):
        return f'<{self.__class__.__name__} cell_id={self.cell_id} idx={self.idx} ts={self.ts} entry={self.entry}>'


class Extra(Base):
    __tablename__ = 'extras'

    cell_id = Column(String, ForeignKey('cells.id'), primary_key=True)
    name = Column(String, primary_key=True)
    props = Column(JSON)
    ref = Column(String)
    content = Column(LargeBinary)

    cell = relationship('Cell', back_populates='extras')

    def __repr__(self):
        return f'<{self.__class__.__name__} cell_id={self.cell_id} name={self.name} props={self.props} ref={self.ref} content={len(self.content)} bytes>'  # noqa


class SQLAlchemy(CellDB):
    def __init__(self, dsn=None, **kwargs):
        super().__init__()

        self.config = kwargs['config']
        self.dsn = dsn
        self.engine = create_engine(self.dsn, echo=True if self.config.loglevel == 'DEBUG' else False, future=True)
        self.session = Session(self.engine)

        log.debug('backend setup', engine=self.engine)

    def __repr__(self):
        return f'SQLAlchemy/{repr(self.engine)}'

    def init(self):
        log.info('creating celldb', engine=self.engine)

        Base.metadata.create_all(self.engine)

    def _build_infoset(self, cell, log_entries: list, extras: list) -> Infoset:
        log.debug('building infoset', cell_row=cell, log_entries=log_entries, extras=extras)
        id = cell.id

        infoset = Infoset()
        infoset.put('.id', cell.id)
        infoset.put('.extra', [])
        infoset.put('.log', [])

        infoset.put('.props', deepcopy(cell.props))

        if hasattr(self, '_container_cache'):

            # Synthesize path from cache
            if cell.container_cell_id is not None:
                parts = [ '' ]
                p = self._container_cache[cell.id]
                while p is not None:
                    parts.append(p)
                    p = self._container_cache[p]

                infoset.put('.path', '/'.join(parts))
            else:
                infoset.put('.path', '/')

        else:

            # Synthesize path from database
            if cell.container_cell_id is not None:
                parts = [ '' ]
                p = self.session.execute( select(Cell).where(Cell.id == cell.container_cell_id)).first()[0]
                while p.container_cell_id is not None:
                    parts.append(p.continer_cell_id)
                    p = self.session.execute( select(Cell).where(Cell.id == p.container_cell_id)).first()[0]

                infoset.put('.path', '/'.join(parts))
            else:
                infoset.put('.path', '/')

        for e in sorted(log_entries, key=lambda e: e.idx):
            if e.ts is not None:
                e.entry.update({ 'ts': e.ts })

            infoset.fetch('.log').append(deepcopy(e.entry))

        for extra in extras:
            # TODO: Restore mtime and ctime from props
            infoset.fetch('.extra').append({
                'name': extra.name,
                'props': deepcopy(extra.props),
                'ref': extra.ref,
                'content': deepcopy(extra.content)
            })

        # Bind the state variables
        for (path, statevar_class) in v1.state_vars.items():
            infoset.put(f'.state.{path}', statevar_class(cell=infoset))

        return infoset

    def fetch(self, id: str) -> Infoset:
        log.info('fetching infoset', id=id)

        cell = self.session.execute( select(Cell).where(Cell.id == id) ).first()
        if cell is None:
            return None
        cell = cell[0]

        return self._build_infoset(cell, cell.log_entries, cell.extras)

    def put(self, infoset: Infoset):

        props = infoset.fetch('.props')
        cell_id = infoset.fetch('.id')

        container_cell_id = None
        if infoset.fetch('.path') is not None:
            parent_container = Path(infoset.fetch('.path')).name
            if parent_container:
                container_cell_id = parent_container

        self.session.merge( Cell(id=cell_id, container_cell_id=container_cell_id, props=props) )

        log_entries = infoset.fetch('.log')
        for idx in range(len(log_entries)):
            ts = log_entries[idx].get('ts', None)
            self.session.merge( LogEntry(cell_id=cell_id, idx=idx, ts=ts, entry=log_entries[idx]) )

        for extra in infoset.fetch('.extra'):
            self.session.merge( Extra(cell_id=cell_id, name=extra['name'],
                props=extra['props'], ref=extra['ref'], content=extra['content']) )

        self.session.flush()
        self.session.commit()

    def find(self) -> Infoset:

        # FIXME:
        # A better way needs to be developed for handling the task of quickly loading all information from the DB.
        # Using the ORM directly is too slow.
        #
        #
        # The caches will be invalidated with any changes performed on the infosets and as such are only useful
        # in a simple load all -> modify -> save all kind of workflow
        #

        # Build caches first for quicker access
        # - logs cache holds all logs
        # - extras cache holds all extras
        # - container cache holds all container cell IDs (used to synthesize paths)
        self._logs_cache = defaultdict(list)
        self._extras_cache = defaultdict(list)
        self._container_cache = defaultdict(lambda: None)

        # Fetch and cache all logs
        for e in self.session.execute( select(LogEntry) ):
            e = e[0]
            self._logs_cache[e.cell_id].append(e)

        log.info('cached all logs', count=len(self._logs_cache.keys()))

        # Fetch and cache all extras
        for e in self.session.execute( select(Extra) ):
            e = e[0]
            self._extras_cache[e.cell_id].append(e)

        log.info('cached all extras', count=len(self._extras_cache.keys()))

        # Fetch and cache all container cell IDs
        for cell in self.session.execute( select(Cell) ):
            cell = cell[0]
            if cell.container_cell_id is not None:
                self._container_cache[cell.id] = cell.container_cell_id

        log.info('cached all container IDs', count=len(self._container_cache.keys()))

        for cell in self.session.execute( select(Cell) ):
            cell = cell[0]
            yield self._build_infoset(cell, self._logs_cache[cell.id], self._extras_cache[cell.id])


v1.register_celldb_backend('sql-alchemy', SQLAlchemy)
