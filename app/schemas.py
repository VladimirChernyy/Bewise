from pydantic import BaseModel


class QuestionRequest(BaseModel):
    questions_num: int
