#!/usr.bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Club(Base):
    """A club of gamer organizing sessions of games around numerous tables"""
    __tablename__ = 'club'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    create_id = Column(Integer, ForeignKey('gamer.id'))
    modify_id = Column(Integer, ForeignKey('gamer.id'))
    active = Column(Boolean, default=True)
    name = Column(String(255))
    description = Column(Text)
    address = Column(Text)
    # gps_coord

    creator = relationship('Gamer', foreign_keys=[create_id])
    modifier = relationship('Gamer', foreign_keys=[modify_id])

    def __repr__(self):
        return (self.name and self.name or u'Club [%i]' % self.id)

class Gamer(Base):
    """ A Gamer and/or a user in a club"""
    __tablename__ = 'gamer'

    id = Column(Integer, primary_key=True)
    created = Column(Integer, default=datetime.now)
    modified = Column(Integer, default=datetime.now, onupdate=datetime.now)
    create_id = Column(Integer, ForeignKey('gamer.id'))
    modify_id = Column(Integer, ForeignKey('gamer.id'))
    active = Column(Boolean, default=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    surname = Column(String(50))
    login = Column(String(50))
    last_login = Column(DateTime)
    birthdate = Column(Date)
    #password

    creator = relationship('Gamer', foreign_keys=[create_id])
    modifier = relationship('Gamer', foreign_keys=[modify_id])

    def __repr__(self):
        if self.surname:
            result = self.surname
        elif self.last_name:
            result = u'%s %s'.strip() % (self.last_name,self.first_name or '')
        elif self.login:
            result = self.login
        else:
            result = u'Gamer [%i]' % self.id
        return result
    
    @property
    def age(self):
        if self.birthdate:
            result = 18
        else:
            result = 0
        return result

class GameSession(Base):
    """ A Game Session where gamers can play many games with others"""
    __tablename__ = 'gamesession'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    create_id = Column(Integer, ForeignKey('gamer.id'))
    modify_id = Column(Integer, ForeignKey('gamer.id'))
    active = Column(Boolean,default=True)
    name = Column(String, nullable=False)
    begin = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    type = Column(String(20)) # current values = Soiree/Week-End
    state = Column(String(20)) # current values = possible/confirmed/done/cancel
    club_id = Column(Integer, ForeignKey('club.id'))

    creator = relationship('Gamer', foreign_keys=[create_id])
    modifier = relationship('Gamer', foreign_keys=[modify_id])

    @property
    def duration_in_seconds(self):
        if self.end and self.begin:
            delta = self.end - self.begin
            return delta.days * 24 * 60 * 60 + delta.seconds
        else:
	    return 0

    @property
    def duration(self):
        if self.end - self.begin:
            delta = self.end - self.begin
            seconds = delta.seconds
            hours = delta.seconds % (60*60)
            seconds = seconds - (hours*60*60)
            minutes = delta.seconds % 60
            seconds = seconds - (minutes*60)
            return (delta.days,hours,minutes,seconds)
        else:
            return (0,0,0,0)

if __name__ == '__main__':
    engine = create_engine('sqlite:///gamesess_test1.db', echo=False)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    now = datetime.now()
    
    admin = Gamer(
        last_name=u'Administrator',
        first_name=u'',
        surname=u'Admin',
        login=u'admin')
    session.add(admin)
    session.commit()
    admin_id = admin.id
    print admin_id

    club_manager = Gamer(
        last_name = u'VANDERMEER',
        first_name = u'Philippe',
        surname = u'Philmer',
        login = u'philmer.vdm@gmail.com',
        create_id = admin_id)
    session.add(club_manager)
    session.commit()
    cmanager_id = club_manager.id

    gamer = Gamer(
        last_name = u'SELECK',
        first_name = u'Vincianne',
        surname = u'',
        login = u'vinci.seleck@gmail.com',
        create_id = cmanager_id)
    session.add(gamer)
    session.commit()
    gamer_a = gamer.id

    gamer = Gamer(
        last_name = u'VANDERMEER',
        first_name = u'Sylvain',
        surname = u'',
        login = u'sylvain.vdm@gmail.com',
        create_id = cmanager_id)
    session.add(gamer)
    session.commit()
    gamer_b = gamer.id

    gamer = Gamer(
        last_name = u'VANDERMEER',
        first_name = u'Simon',
        surname = u'',
        login = u'simon.deuxrys@gmail.com',
        create_id = cmanager_id)
    session.add(gamer)
    session.commit()
    gamer_c = gamer.id

    mormont = Club(
        name = u'Bibliothèque de Mormont',
        description = u'''Séances de jeu tous les derniers vendredis du mois.\n
                          De 20h00 à 24h00. Enfants bienvenus.
                       ''',
        address = u'Mormont',
        create_id = admin.id)
    session.add(mormont)
    session.commit()
    mormont_id = mormont.id

    prec = GameSession(
       name = u"Soirée du 21/4/2017 à Mormont",
       begin = datetime(2017,4,21,20,0,0),
       end = datetime(2017,4,21,23,59,59),
       #club_id = mormont_id
       create_id = admin.id)
    session.add(prec)
    session.commit()
    prec_id = prec.id

    next = GameSession(
        name = u"Soirée du 26/5/2017 à Mormont"
        begin = datetime(2017,5,26,20,0,0)
        end = datetime(2017,5,26,23,59,59)
        create_id = admin.id)
    session.add(next)
    session.commit()
    next_id = next.id

    club = session.query(Club).first()
    print club.id
    print club.name

    gamers = session.query(Gamer).all()
    for gamer in gamers:
        print gamer.id
        print gamer
        print '-------------'
