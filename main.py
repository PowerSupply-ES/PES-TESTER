from fastapi import FastAPI, HTTPException, Response, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schema import Session, AnswerTable, QuestionTable, ProblemTable
from tester import *
import os
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


def decode_token(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token = token.credentials
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 필요합니다.")
    
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_ENCODED, algorithms=[ALGORITHM], options={"verify_signature": False})
        print(token, JWT_SECRET_ENCODED, ALGORITHM)
        print(decoded_token)
        return decoded_token
    except jwt.ExpiredSignatureError:
        return JSONResponse(content={"ERROR" :"토큰이 만료되었습니다."}, status_code=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return JSONResponse(content={"ERROR" :"유효하지 않은 토큰입니다."}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.get("/info")
async def get_info(current_user: dict = Depends(decode_token)):
    return current_user


# 코드 제출 엔드포인트
@app.post("/api2/submit/{problem_id}")
async def submit_code(request: Request, problem_id: int, userinfo: dict = Depends(decode_token)):
    """submit c code

    Args:
        problem_id (int): _description_
        member_name (str): _description_

    Raises:
        he: _description_

    Returns:
        _type_: _description_
    """
    user = userinfo["memberEmail"]
    file_name = f"./answerData/{user}_{problem_id}.c"
    content = await request.body()
    with open(file_name, "w") as output_file:
        output_file.write(content.decode())
    try:
        res = code_tester(file_name, problem_id)
        if res == 100:
            return JSONResponse(content={"detail" : res}, status_code=status.HTTP_201_CREATED)
        else:
            return JSONResponse(content={"detail" : res}, status_code=status.HTTP_202_ACCEPTED)
        
    except FileNotFoundError:
        return JSONResponse(content={"ERROR" : "can't get problem"}, status_code=status.HTTP_404_NOT_FOUND)
    except HTTPException as he:
        return he


@app.get("/api2/question/{problem_id}")
async def get_code(problem_id: int, userinfo: dict = Depends(decode_token)):
    """get c code

    Args:
        problem_id (int): problem_id
        member_name (str): member_name

    Returns:
        _dict_: {detail : c_code}
    """
    user = userinfo["memberEmail"]
    file_name = f"./answerData/{user}_{problem_id}.c"
    try:
        with open(file_name, 'r', encoding='UTF8') as file:
            data = file.read()
            
            return {"code" : data}

    except HTTPException as he:
        raise he


# 문제 타이틀
@app.get("/api2/problemtitle/{problem_id}")
async def read_main(problem_id: int):
    """get problem title

    Args:
        problem_id (int): problem_id

    Returns:
        _dict_: {problemId, problemTitle, problemScore}
    """
    session = Session()
    prob = session.query(ProblemTable).filter_by(problem_id={problem_id}).first()
    session.close()
    return {"problemId" :problem_id, "problemTitle" : prob.problem_title, "problemScore" : prob.problem_score}


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

    uvicorn.run(app, host="0.0.0.0", port=8000)
