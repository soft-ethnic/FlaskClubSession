#!/usr.bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, date
from datetime import timedelta

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,relationship,backref
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
# import six

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
    public = Column(Boolean, default=False)
    # gps_coord

    creator = relationship('Gamer', foreign_keys=[create_id])
    modifier = relationship('Gamer', foreign_keys=[modify_id])

    def __repr__(self):
        return (self.name and self.name or u'Club [%i]' % self.id)

class Gamer(Base):
    """ A Gamer and/or a user in a club.
        Also serves as USERS database for Flask-Login
    """
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
    password_hashed = Column(String(128))
    email = Column(String(255))
    
    creator = relationship('Gamer', foreign_keys=[create_id])
    modifier = relationship('Gamer', foreign_keys=[modify_id])

    def __repr__(self):
        return self._get_name()

    def _get_name(self):
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
            result = 77
        return result
        
    @property
    def password(self):
        raise AttributeError(u'Password is not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hashed = generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password_hashed,password)

    # Flask-Login methods and properties
    def get_id(self):
        return str(self.id)
    @property
    def is_active(self):
        return self.active
    @property
    def is_anonymous(self):
        return False
    @property
    def is_authenticated(self):
        return True
        
class GamerClub(Base):
    """ A Club can have many manager and more users"""
    __tablename__ = 'gamerclub'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    create_id = Column(Integer, ForeignKey('gamer.id'))
    modify_id = Column(Integer, ForeignKey('gamer.id'))
    active = Column(Boolean,default=True)
    role = Column(String(50)) ## manager/user
    club_id = Column(Integer, ForeignKey('club.id'))
    gamer_id = Column(Integer, ForeignKey('gamer.id'))

    creator = relationship('Gamer', foreign_keys=[create_id])
    modifier = relationship('Gamer', foreign_keys=[modify_id])
    gamer = relationship('Gamer', foreign_keys=[gamer_id])

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

class GameTable(Base):
    """A table groups gamers around a game"""
    __tablename__ = 'gametable'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    create_id = Column(Integer, ForeignKey('gamer.id'))
    modify_id = Column(Integer, ForeignKey('gamer.id'))
    active = Column(Boolean, default=True)
    name = Column(String(255))
    description = Column(Text)
    begin = Column(DateTime)
    end = Column(DateTime)
    min_part = Column(Integer)
    max_part = Column(Integer)
    type = Column(String(50)) # proposition, confirmé
    game_id = Column(Integer,ForeignKey('game.id'))
    session_id = Column(Integer,ForeignKey('gamesession.id'))

    creator = relationship('Gamer', foreign_keys=[create_id])
    modifier = relationship('Gamer', foreign_keys=[modify_id])

    def __repr__(self):
        return (self.name and self.name or u'Table [%i]' % self.id)

class Game(Base):
    """A game is a proposed game : can be a game or a scenario"""
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    create_id = Column(Integer, ForeignKey('gamer.id'))
    modify_id = Column(Integer, ForeignKey('gamer.id'))
    active = Column(Boolean, default=True)
    name = Column(String(255))
    parts = Column(String(200)) # can be a range "2-5" or a list of possibilities : "2; 4"
    parent_id = Column(Integer,ForeignKey('game.id'))
    average_duration = Column(Integer) # in minutes
    
    creator = relationship('Gamer', foreign_keys=[create_id])
    modifier = relationship('Gamer', foreign_keys=[modify_id])
    #parent = relationship('Game', remote_side=[id])
    children = relationship('Game', backref=backref('parent', remote_side=[id]))

    def __repr__(self):
        return (self.name and self.name or u'Game [%i]' % self.id)

    @property
    def parts_as_list(self):
        if ';' in self.parts:
            ranges = self.parts.split(';')
        else:
            ranges = [self.parts,]
        result = []
        for srange in ranges:
            if srange.count('-') == 1:
                (sbegin,send) = srange.split('-')
                begin = int(sbegin)
                end = int(send)
                if begin > end:
                    (begin,end) = (end,begin)
                value = begin
                while value <= end:
                    if value not in result:
                        result.append(value)
                    value += 1
            elif srange.count('-') > 1:
                pass
            else:
                value = int(srange.strip())
                if value not in result:
                    result.append(value)
        return result

class Attendance(Base):
    """An attendance is a participation or a possible participation of a gamer to a table"""
    __tablename__ = 'attendance'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    modified = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    create_id = Column(Integer, ForeignKey('gamer.id'))
    modify_id = Column(Integer, ForeignKey('gamer.id'))
    active = Column(Boolean, default=True)
    name = Column(String(50)) ## possible, confirmé, initiateur
    table_id = Column(Integer,ForeignKey('gametable.id'))
    gamer_id = Column(Integer,ForeignKey('gamer.id'))
    
    creator = relationship('Gamer', foreign_keys=[create_id])
    modifier = relationship('Gamer', foreign_keys=[modify_id])
    gamer = relationship('Gamer', foreign_keys=[gamer_id,])

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
        login=u'admin',
        password=u'admin',
        email='dev@soft-ethnic.be')
    session.add(admin)
    session.commit()
    admin_id = admin.id
    print(admin_id)
    print(admin.password_hashed)

    club_manager = Gamer(
        last_name = u'VANDERMEER',
        first_name = u'Philippe',
        surname = u'Philmer',
        login = u'philmer.vdm@gmail.com',
        password=u'philmer',
        create_id = admin_id,
        birthdate = date(1966,2,17),
        email='philmer.vdm@gmail.com')
    session.add(club_manager)
    session.commit()
    cmanager_id = club_manager.id
    print(club_manager.password_hashed)

    gamer = Gamer(
        last_name = u'SELECK',
        first_name = u'Vincianne',
        surname = u'',
        login = u'vinci.seleck@gmail.com',
        password=u'vincianne',
        create_id = cmanager_id)
    session.add(gamer)
    session.commit()
    gamer_a = gamer.id

    gamer = Gamer(
        last_name = u'VANDERMEER',
        first_name = u'Sylvain',
        surname = u'',
        login = u'sylvain.vdm@gmail.com',
        password=u'sylvain',
        create_id = cmanager_id)
    session.add(gamer)
    session.commit()
    gamer_b = gamer.id

    gamer = Gamer(
        last_name = u'VANDERMEER',
        first_name = u'Simon',
        surname = u'',
        login = u'simon.deuxrys@gmail.com',
        password=u'simon',
        create_id = cmanager_id)
    session.add(gamer)
    session.commit()
    gamer_c = gamer.id

    gamer = Gamer(
        last_name = u'ANONYMOUS',
        first_name = u'Thomas',
        surname = u'',
        login = u'thomas.anonymous@gmail.com',
        password=u'thomas',
        create_id = cmanager_id)
    session.add(gamer)
    session.commit()
    gamer_thomas_id = gamer.id

    mormont = Club(
        name = u'Bibliothèque de Mormont',
        description = u'''Séances de jeu tous les derniers vendredis du mois.\n
                          De 20h00 à 24h00. Enfants bienvenus.
                       ''',
        address = u'Mormont',
        public = True,
        create_id = admin.id)
    session.add(mormont)
    session.commit()
    mormont_id = mormont.id

    thomas = Club(
        name = u'Thomas and Co',
        description = u'''Séances assez disparates mais souvent consacrées à d enouveaux jeux. Joueurs expérimentés et avides de nouveautés.
                       ''',
        address = u'Liège',
        public = True,
        create_id = admin.id)
    session.add(thomas)
    session.commit()
    thomas_club_id = thomas.id

    thomas_thomas = GamerClub(
        role = 'manager',
        gamer_id = gamer_thomas_id,
        club_id = thomas_club_id,
        create_id = admin.id)
    session.add(thomas_thomas)
    session.commit()

    philmer_mormont = GamerClub(
        role = 'manager',
        gamer_id = cmanager_id,
        club_id = mormont_id,
        create_id = admin.id)
    session.add(philmer_mormont)
    session.commit()
    sylvain_mormont = GamerClub(
        role = 'user',
        gamer_id = gamer_b,
        club_id = mormont_id,
        create_id = admin.id)
    session.add(sylvain_mormont)
    session.commit()
    simon_mormont = GamerClub(
        role = 'user',
        gamer_id = gamer_c,
        club_id = mormont_id,
        create_id = admin.id)
    session.add(simon_mormont)
    session.commit()
    
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
        name = u"Soirée du 26/5/2017 à Mormont",
        begin = datetime(2017,5,26,20,0,0),
        end = datetime(2017,5,26,23,59,59),
        create_id = admin.id)
    session.add(next)
    session.commit()
    next_id = next.id

    sw = Game(
        name = u'Small World',
        parts = '2-4',
        average_duration=150)
    session.add(sw)
    session.commit()
    sw_id = sw.id
    
    swu = Game(
        name = u'Small World Underground',
        parts = '2-4',
        parent_id = sw_id,
        average_duration=180)
    session.add(swu)
    session.commit()
    swu_id = swu.id
    
    adr = Game(
        name = u"Les Aventuriers du Rail",
        parts = '2-4',
        average_duration = 150)
    session.add(adr)
    session.commit()
    adr_id = adr.id
    
    adr_inde = Game(
        name = u"Les Aventuriers du Rail - carte Inde",
        parts = '2-4',
        average_duration = 120,
        parent_id = adr_id)
    session.add(adr_inde)
    session.commit()

    adr_suisse = Game(
        name = u"Les Aventuriers du Rail - carte Suisse",
        parts = '2-4',
        average_duration = 150,
        parent_id = adr_id)
    session.add(adr_suisse)
    session.commit()
    adr_suisse_id = adr_suisse.id

    toi = Game(
        name = u"Tide Of Iron - L'aube d'acier",
        parts = '2;4',
        average_duration = 300)
    session.add(toi)
    session.commit()
    
    table_adr_suisse = GameTable(
        name = u"Première partie aux Aventuriers du Rail - carte Suisse",
        min_part = 3,
        max_part = 4,
        begin = datetime(2017,5,26,20,0,0),
        end = datetime(2017,5,26,22,0,0),
        type = u'Proposition',
        game_id = adr_suisse_id,
        session_id = next_id)
    session.add(table_adr_suisse)
    session.commit()
    table1_id = table_adr_suisse.id
    
    table_sw = GameTable(
        name = u"Small World en test",
        min_part = 3,
        max_part = 4,
        begin = datetime(2017,5,26,20,0,0),
        end = datetime(2017,5,26,22,30,0),
        type = u'Proposition',
        game_id = sw_id,
        session_id = next_id)
    session.add(table_sw)
    session.commit()
    table2_id = table_sw.id
    
    att_adr_suisse = Attendance(
        name = 'initiateur',
        table_id = table1_id,
        gamer_id = cmanager_id)
    session.add(att_adr_suisse)
    session.commit()
    
    att_sw = Attendance(
        name = 'initiateur',
        table_id = table2_id,
        gamer_id = cmanager_id)
    session.add(att_sw)
    session.commit()
    
    att2_sw = Attendance(
        name = 'possible',
        table_id = table2_id,
        gamer_id = gamer_b)
    session.add(att2_sw)
    session.commit()
    
    club = session.query(Club).first()
    print(club.id)
    print(club.name)

    gamers = session.query(Gamer).all()
    for gamer in gamers:
        print(gamer.id)
        print(gamer)
        print('-------------')

    games = session.query(Game).all()
    for game in games:
        print(game.id)
        print(game)
        print(game.parts_as_list)
        print(game.parent)
        print(game.children)
        print('-------------')

    tables = session.query(GameTable).all()
    for table in tables:
        print(table.id)
        print(table.name)
        print(table.creator)
        
    atts = session.query(Attendance).all()
    for att in atts:
        print(att.id)
        print(att.name)
        print(att.gamer)
        print(att.gamer.age)