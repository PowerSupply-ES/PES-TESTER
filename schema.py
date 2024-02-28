from sqlalchemy import create_engine, Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

engin = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engin)
Base = declarative_base()


class MemberTable(Base):
    __tablename__ = 'member_table'

    member_email = Column(String(255), primary_key=True)
    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    member_beak_id = Column(String(255))
    member_gen = Column(Integer)
    member_major = Column(String(255))
    member_name = Column(String(255))
    member_phone = Column(String(255), unique=True)
    member_pw = Column(String(255))
    member_status = Column(String(255))

    answers = relationship("AnswerTable", back_populates="member")
    comments = relationship("CommentTable", back_populates="member")


class AnswerTable(Base):
    __tablename__ = 'answer_table'

    answer_id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    answer_fst = Column(String(255))
    answer_sec = Column(String(255))
    answer_state = Column(String(255))
    final_score = Column(Integer, nullable=False)
    member_email = Column(String(255), ForeignKey('member_table.member_email'))
    problem_id = Column(Integer, ForeignKey('problem_table.problem_id'))
    question_fst = Column(Integer, ForeignKey('question_table.question_id'))
    question_sec = Column(Integer, ForeignKey('question_table.question_id'))

    member = relationship("MemberTable", back_populates="answers")
    problem = relationship("ProblemTable", back_populates="answers")
    question_fst_rel = relationship("QuestionTable", foreign_keys=[question_fst], back_populates="answer_fst_rel")
    question_sec_rel = relationship("QuestionTable", foreign_keys=[question_sec], back_populates="answer_sec_rel")

    comments = relationship("CommentTable", back_populates="answer")

class CommentTable(Base):
    __tablename__ = 'comment_table'

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    comment_content = Column(String(255))
    comment_pass_fail = Column(Integer, nullable=False)
    answer_id = Column(Integer, ForeignKey('answer_table.answer_id'))
    member_email = Column(String(255), ForeignKey('member_table.member_email'))

    answer = relationship("AnswerTable", back_populates="comments")
    member = relationship("MemberTable", back_populates="comments")
    


class ProblemTable(Base):
    __tablename__ = 'problem_table'

    problem_id = Column(Integer, primary_key=True)
    problem_score = Column(Integer, nullable=False)
    problem_title = Column(String(255))

    answers = relationship("AnswerTable", back_populates="problem")
    questions = relationship("QuestionTable", back_populates="problem")

class QuestionTable(Base):
    __tablename__ = 'question_table'

    question_id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(Integer, ForeignKey('problem_table.problem_id'))
    question_content = Column(String(255))
    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())

    problem = relationship("ProblemTable", back_populates="questions")
    answer_fst_rel = relationship("AnswerTable", foreign_keys=[AnswerTable.question_fst], back_populates="question_fst_rel")
    answer_sec_rel = relationship("AnswerTable", foreign_keys=[AnswerTable.question_sec], back_populates="question_sec_rel")


if __name__ == "__main__":
    session = Session()
    print("PROBLEMTANLE")
    user = session.query(ProblemTable).filter_by(problem_id=1).first()
    print(user.problem_title)
    session.close()

"""
# 단일 레코드 조회
user = session.query(User).filter_by(id=1).first()
print(user.name, user.age)

# 모든 레코드 조회
users = session.query(User).all()
for user in users:
    print(user.name, user.age)

# 특정 레코드 수정
user = session.query(User).filter_by(id=1).first()
user.age = 35
session.commit()

# 특정 레코드 삭제
user = session.query(User).filter_by(id=1).first()
session.delete(user)
session.commit()

# 모든 레코드 삭제
session.query(User).delete()
session.commit()

"""