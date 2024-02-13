from fastapi import FastAPI, HTTPException, Response, status, Request
import subprocess
import json
import ctypes
import os
import uuid
import random
from fastapi.middleware.cors import CORSMiddleware
from schema import Session, AnswerTable, QuestionTable

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 오는 요청을 허용합니다. 실제 배포에서는 구체적인 도메인을 명시하세요.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드를 허용합니다.
    allow_headers=["*"],  # 모든 HTTP 헤더를 허용합니다.
)


def open_prob(problem_id):
    file_path = f"./problems/prob{problem_id}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="파일을 찾을 수 없습니다.")
    with open(f"./problems/prob{problem_id}.json", 'r', encoding='UTF8') as file:
        return json.load(file)


def compile_c_code(file_name, jdata):
    try:
        # 컴파일 명령어 실행
        lib_path = f"{uuid.uuid4().hex}.so"
        result = subprocess.run(['gcc', '-shared', '-o', lib_path, file_name], capture_output=True, text=True)
        
        # 컴파일 에러 시 원인 return
        if result.returncode != 0:
            return (result.stderr.strip())
        lib = ctypes.CDLL(f"./{lib_path}")
        total = len(jdata["inputs"])
        for idx, inp in enumerate(jdata["inputs"]):
            if jdata["outputs"][idx] != lib.pes(*inp):
                del lib
                os.remove(lib_path)
                return int(idx / total * 100)
        del lib
        os.remove(lib_path)
        return 1
    
    except Exception as e:
        return "HARD ERROR :" + {e}
    


# 코드 제출 엔드포인트
@app.post("/api2/submit/{problem_id}/{member_name}")
async def submit_code(request: Request, problem_id: int, member_name: str):

    file_name = f"./answerData/{member_name}_{problem_id}.c"
    try:
        jdata = open_prob(problem_id)
        
        data = await request.json()
        with open(file_name, 'w') as file:
            file.write(data.get("code"))
        result = compile_c_code(file_name, jdata)
        
        if result == 1:
            try:
                session = Session()
                check = session.query(AnswerTable).filter_by(problem_id=problem_id).first()
                if not check:
                    questions = session.query(QuestionTable).filter_by(problem_id=problem_id).all()
                    choices = random.sample(questions, 2)
                    addanswer = AnswerTable(member_email=member_name, problem_id=problem_id, 
                                                question_fst=choices[0].question_id, question_sec=choices[1].question_id, 
                                                final_score=10) # 임시로 10점
                    session.add(addanswer)
                    session.commit()
                        
                answerid = session.query(AnswerTable).filter_by(problem_id=problem_id).first().answer_id
                return {"answerid" : answerid}
            except:
                session.rollback()
                raise
            finally:
                session.close()
                
        else:
            return {"detail" : result}

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



# 메인 페이지
@app.get("/api2/problem/{problem_id}")
async def read_main(request: Request, problem_id: int):
    try:
        jdata = open_prob(problem_id)

        return {"problem_id": problem_id, 
        "title" : jdata["title"], "context" : jdata["context"],
        "sample_inputs" : jdata["sampleInputs"], "sample_outputs" : jdata["sampleOutputs"]}

    except HTTPException as he:
        raise he

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
