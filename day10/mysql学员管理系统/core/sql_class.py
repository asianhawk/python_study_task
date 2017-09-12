# -*- coding: utf-8 -*-
__author__ = 'Mc.Lee'
import sys, os

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path)

from sqlalchemy import Column,String,create_engine,Integer,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship

import configparser


class DB_Control(object):
    def __init__(self):
        self.Get_Conf()
        #self.Conn()
        self.Tables = self.Table_Framework()

    def Conn(self):
        conn_str = '%s+pymysql://%s:%s@%s/%s'%(self.DB_TYPE,self.DB_USER,self.DB_PWD,self.DB_HOST,self.DB_NAME)
        self.Engine = create_engine(
            conn_str,
            encoding='utf8',
            echo=True
        )
        DB_BASE = declarative_base()
        Session_Class = sessionmaker(bind=self.Engine)
        self.Session = Session_Class()
        return DB_BASE

    def Get_Conf(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(path,'conf','config.ini'))
        self.DB_TYPE = config['DB']['type']
        self.DB_HOST = config['DB']['host']
        self.DB_USER = config['DB']['user']
        self.DB_PWD = config['DB']['pwd']
        self.DB_NAME = config['DB']['db_name']

    def Table_Framework(self):
        Base = self.Conn()
        class User(Base):
            __tablename__ = 'user'
            id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
            name = Column(String(32), nullable=False)
            pwd = Column(String(32), nullable=False)
            type_id = Column(Integer, ForeignKey('role_type.id'))
            type = relationship('Role_Type', backref='user_id')
            # type_id = relationship('Role_Tpye')
            # course_id = Column(Integer,ForeignKey('couesr.id'))
            qq = Column(String(32))
            email = Column(String(32))

            def __repr__(self):
                return '<User>name=%s,type=%s' % (self.name, self.type.name)

        class User_Course(Base):
            __tablename__ = 'user_course'
            id = Column(Integer, primary_key=True, autoincrement=True)
            user_id = Column(Integer, ForeignKey('user.id'))
            user = relationship('User', backref='courses', foreign_keys=[user_id])
            course_id = Column(Integer, ForeignKey('course.id'))
            course = relationship('Course',backref='user',foreign_keys=[course_id])
            pay_status = Column(String(32))



            def __repr__(self):
                return '<user_course>user:%s,course:%s'%(self.user.name,self.course.name)

        class Role_Type(Base):
            __tablename__ = 'role_type'
            id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
            name = Column(String(8), nullable=False)

            def __repr__(self):
                return '<role_type>%s:%s'%(self.id,self.name)

        class Course(Base):
            __tablename__ = 'course'
            id = Column(Integer, primary_key=True)
            name = Column(String(32), nullable=False)
            teacher_id = Column(Integer, ForeignKey('user.id'))
            #teacher = relationship('User',backref='')
            school_id = Column(Integer, ForeignKey('school.id'))

        class School(Base):
            __tablename__ = 'school'
            id = Column(Integer, primary_key=True)
            name = Column(String(32), nullable=False)
            address = Column(String(32), nullable=False)

        Base.metadata.create_all(self.Engine)
        table_dict = {
            'user':User,
            'user_courses':User_Course,
            'role_type':Role_Type,
            'course':Course,
            'school':School
        }
        #返回表结构对象字典
        return table_dict

    def Fields(self,table_name):
        '''
        根据表名返回字段
        :param table_name:
        :return:
        '''
        pass



    def Search_Data(self):
        #getattr(self.Table_Framework)
        #data = self.Session.query(table)

        pass



if __name__ == '__main__':
    db = DB_Control()
    print(db.Tables)
    table = db.Tables['role_type']
    print(table.__dict__.keys())
    #data = db.Session.query(table).filter(table.id <5 ).all()
    #print(data)

