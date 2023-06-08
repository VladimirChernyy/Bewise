import logging
from typing import Union

import requests
from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm.session import Session

from database import get_db
from models import Question
from schemas import QuestionRequest

logging.basicConfig(
    filename='main.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s'
)

ENDPOINT = 'https://jservice.io/api/random?count='

app = FastAPI()


def get_response(questions_num):
    """Получаем json от внешнего API."""
    response = requests.get(f'{ENDPOINT}{questions_num}')
    if response.status_code is status.HTTP_200_OK:
        return response
    message = f'Неверный ответ сервера {response.status_code} != 200'
    logging.error(message)
    raise HTTPException(status_code=response.status_code)


def check_questions(data: dict, db: Session) -> bool:
    """Проверка вопроса на наличие в базе данных и добовление."""
    db_questions = False
    for item in data:
        questions = db.query(Question).filter_by(
            question=item["question"]).first()
        if not questions:
            new_question = Question(question=item["question"],
                                    answer=item["answer"])
            db.add(new_question)
            db.commit()
            db.refresh(new_question)
            logging.debug('Вопрос добавлен в базу данных')
            db_questions = False
        else:
            logging.debug('Вопрос существует в базе данных')
            db_questions = True
            continue
    return db_questions


@app.post("/questions/")
def get_questions(request: QuestionRequest,
                  db: Session = Depends(get_db)) -> Union[str, None]:
    """Запрос вопроса от внешенего сервиса,
    получение предпоследнего сохраненного вопроса из базы данных"""
    questions_num = request.questions_num
    while True:
        try:
            response = get_response(questions_num)
            data = response.json()
            db_question = check_questions(data, db)
            if db_question:
                continue
            previous_record = db.query(Question.question).order_by(
                desc(Question.id)).limit(1).offset(1).scalar()
            return previous_record

        except HTTPException as error:
            message = f'Неверный ответ от внешнего эндпоинта {error}'
            logging.error(message)

        except Exception as error:
            message = f'Сбой в работе приложения {error}'
            logging.critical(message)
            raise error
