from fastapi import FastAPI, HTTPException, Response, status, Request
import subprocess
import json
import ctypes
import os
import uuid
import random
from fastapi.middleware.cors import CORSMiddleware
from schema import Session, AnswerTable, QuestionTable
from tester import *

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 오는 요청을 허용합니다. 실제 배포에서는 구체적인 도메인을 명시하세요.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드를 허용합니다.
    allow_headers=["*"],  # 모든 HTTP 헤더를 허용합니다.
)


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
