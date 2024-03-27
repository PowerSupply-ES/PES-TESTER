from fastapi import FastAPI, HTTPException, Response, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schema import Session, manage_session, AnswerTable, QuestionTable, ProblemTable
from tester import *
import os
import random
import jwt
from fastapi.responses import JSONResponse
import base64

JWT_SECRET = os.environ.get('JWT_SECRET')
ALGORITHM = os.environ.get('ALGORITHM')
JWT_SECRET_ENCODED = base64.b64encode(JWT_SECRET.encode())

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 오는 요청을 허용합니다. 실제 배포에서는 구체적인 도메인을 명시하세요.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드를 허용합니다.
    allow_headers=["*"],  # 모든 HTTP 헤더를 허용합니다.
)


def decode_token(request):
    auth = request.cookies.get("Authorization")
    try:
        decode_auth = jwt.decode(auth, JWT_SECRET_ENCODED, algorithms=[ALGORITHM], options={"verify_signature": False})
        return decode_auth
    except (KeyError, jwt.ExpiredSignatureError, jwt.DecodeError):
        return HTTPException(content={"ERROR": "사용자 정보가 올바르지 않습니다."}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/info")
async def get_info(current_user: dict = Depends(decode_token)):
    return current_user


@app.post("/api2/submit/{problem_id}")
async def submit_code(request: Request, problem_id: int):
    """submit c code

    Args:
        problem_id (int): _description_
        member_name (str): _description_

    Raises:
        he: _description_

    Returns:
        _type_: _description_
    """
    session = None
    user = decode_token(request)["memberId"]
    
    file_name = f"./answerData/{user}_{problem_id}.c"
    content = await request.json()
    if content["code"][0] != "#" or content["code"].rstrip()[-1] != "}":
        return JSONResponse(content={"detail": "WARN : It's not a C code. I can't compile it!"}, status_code=status.HTTP_202_ACCEPTED)

    with open(file_name, "w") as output_file:
        output_file.write(content["code"])
    try:
        res = code_tester(file_name, problem_id)
        session = Session()
        if res == 100:
            check = session.query(AnswerTable).filter_by(problem_id=problem_id, member_id=user).first()
            if not check:
                questions = session.query(QuestionTable).filter_by(problem_id=problem_id).all()
                choices = random.sample(questions, 2)
                addanswer = AnswerTable(member_id=user, problem_id=problem_id, answer_state="question",
                                            question_fst=choices[0].question_id, question_sec=choices[1].question_id, 
                                            final_score=0) # 임시로 0점
                session.add(addanswer)
                session.commit()
            answerid = session.query(AnswerTable).filter_by(problem_id=problem_id, member_id=user).first().answer_id
            
            return JSONResponse(content={"answer_id": answerid, "detail": res}, status_code=status.HTTP_201_CREATED)
        else:
            return JSONResponse(content={"detail": res}, status_code=status.HTTP_202_ACCEPTED)
        
    except FileNotFoundError:
        session.rollback()
        return JSONResponse(content={"ERROR": "can't get problem"}, status_code=status.HTTP_404_NOT_FOUND)
    except HTTPException as he:
        session.rollback()
        return he
    finally:
        if session:
            session.close()


@app.get("/api2/question/{answer_id}")
async def get_code(request: Request, answer_id: int):
    """get c code

    Args:
        answer_id (int): problem_id
        member_name (str): member_name

    Returns:
        _dict_: {detail : c_code}
    """
    session = None
    session = Session()
    user = decode_token(request)["memberId"]    
    check = session.query(AnswerTable).filter_by(answer_id=answer_id).first()
    file_name = f"./answerData/{check.member_id}_{check.problem_id}.c"
    try:
        with open(file_name, 'r', encoding='UTF8') as file:
            data = file.read()
            
            return {"code" : data}

    except HTTPException as he:
        raise he
    finally:
        if session:
            session.close()

# 문제 타이틀
'''
@app.get("/api2/problemtitle/{problem_id}")
async def read_main(problem_id: int):
    """get problem title

    Args:
        problem_id (int): problem_id

    Returns:
        _dict_: {problemId, problemTitle, problemScore}
    """
    session = None
    session = Session()
    prob = session.query(ProblemTable).filter_by(problem_id=problem_id).first()
    session.close()
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return {"problemId": problem_id, "problemTitle": prob.problem_title, "problemScore": prob.problem_score}
'''


# 문제 보기
@app.get("/api2/problem/{problem_id}")
async def read_main(problem_id: int):
    """_summary_

    Args:
        request (Request): _description_
        problem_id (int): _description_

    Raises:
        he: _description_

    Returns:
        _dict_: {problemId, problemContent, sampleInputs, sampleOutputs}
    """
    try:
        prob_data = get_prob_data(problem_id)
        sample = prob_data[1]
        return {"problemId": problem_id, "problemContent" : prob_data[0],
        "sampleInputs" : prob_data[2][:sample], "sampleOutputs" : prob_data[3][:sample]}

    except HTTPException as he:
        raise he

if __name__ == "__main__":
    import uvicorn