from fastapi import FastAPI, HTTPException, Response, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schema import Session, AnswerTable, QuestionTable
from tester import *
import os
import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
import base64

JWT_SECRET = "PESprojectisgreatprojectanditsfunandinterestingproject"#os.environ.get('JWT_SECRET')
ALGORITHM = os.environ.get('ALGORITHM')

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 오는 요청을 허용합니다. 실제 배포에서는 구체적인 도메인을 명시하세요.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드를 허용합니다.
    allow_headers=["*"],  # 모든 HTTP 헤더를 허용합니다.
)


def decode_token(token: str): # ERROR
    #try:
        token = token.replace("Bearer ", "")
        print(token, base64.b64encode(JWT_SECRET.encode()), ALGORITHM)

        decoded_token = jwt.decode(token, base64.b64encode(JWT_SECRET.encode()), algorithms=[ALGORITHM])
        print(decoded_token)
        return decoded_token
    #except jwt.ExpiredSignatureError:
    #    raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    #except jwt.DecodeError:
    #    raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")


@app.get("/info")
async def get_info(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token = credentials.credentials
    decoded_token = decode_token(token)
    return decoded_token

# 코드 제출 엔드포인트
@app.post("/api2/submit/{problem_id}/{member_name}")
async def submit_code(request: Request, problem_id: int, member_name: str):

    file_name = f"./answerData/{member_name}_{problem_id}.c"
    try:
        return {"detail" : code_tester(file_name, problem_id)}
    
    except HTTPException as he:
        raise he


@app.get("/api2/answer/{problem_id}/{member_name}")
async def submit_code(request: Request, problem_id: int, member_name: str):

    file_name = f"{member_name}_{problem_id}.c"
    try:
        with open(file_name, 'r', encoding='UTF8') as file:
            data = file.read()
            return {"detail" : data}

    except HTTPException as he:
        raise he



# 문제 페이지
@app.get("/api2/problem/{problem_id}")
async def read_main(request: Request, problem_id: int):
    try:
        prob_data = get_prob_data(problem_id)
        sample = prob_data[1]
        return {"problem_id": problem_id, 
        "title" : "temp", "context" : prob_data[0],
        "sample_inputs" : prob_data[2][:sample], "sample_outputs" : prob_data[3][:sample]}

    except HTTPException as he:
        raise he

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
