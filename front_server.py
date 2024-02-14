from fastapi import FastAPI, HTTPException, status, Request
import json
import os


app = FastAPI()

def open_prob(problem_id):
    file_path = f"./problems/prob{problem_id}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="파일을 찾을 수 없습니다.")
    with open(f"./problems/prob{problem_id}.json", 'r', encoding='UTF8') as file:
        return json.load(file)


# 코드 제출 엔드포인트
@app.post("/api2/submit/{problem_id}/{user_name}")
async def submit_code(request: Request, problem_id: int, user_name: str):

    file_name = f"{user_name}_{problem_id}.c"
    try:
        data = await request.json()
        with open(file_name, 'w') as file:
            file.write(data.get("code"))

        return {"detail" : "success!!"}

    except HTTPException as he:
        raise he


@app.get("/api2/question/{answer_id}/{user_name}")
async def get_code(request: Request, answer_id: int, user_name: str):

    file_name = f"{user_name}_{answer_id}.c"
    try:
        with open(file_name, 'r', encoding='UTF8') as file:
            data = file.read()
            return {"detail" : data}

    except HTTPException as he:
        raise he

# 문제 타이틀
@app.get("/api2/problemtitle/{problem_id}")
async def get_title(request: Request, problem_id: int):
    return {"problem_id" : problem_id, "problemTitle" : "임시 타이틀입니다!", "problemScore" : 10}

# 문제 보기
@app.get("/api2/problem/{problem_id}")
async def get_problem(request: Request, problem_id: int):
    try:
        jdata = open_prob(problem_id)

        return {"problem_id": problem_id, 
        "context" : jdata["context"],
        "sample_inputs" : jdata["sampleInputs"], "sample_outputs" : jdata["sampleOutputs"]}

    except HTTPException as he:
        raise he

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)