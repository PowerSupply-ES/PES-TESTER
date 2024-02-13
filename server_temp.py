import os
import uuid
import subprocess
import json


def open_prob(problem_id):
    file_path = f"./problems/prob{problem_id}.json"
    if not os.path.exists(file_path):
        return "NONE"
    with open(f"./problems/prob{problem_id}.json", 'r', encoding='UTF8') as file:
        return json.load(file)


def check_main_function(file_path):
    # C 파일 읽기
    with open(file_path, "r", encoding='utf-8') as f:
        c_code = f.read()

    # main 함수 검사
    if "int main(" in c_code or "void main(" in c_code:
        if "scanf_s":
            return 1 #scanf_s, main 컴파일러
        return 2 # main 컴파일러
    else:
        return 3 # 함수 컴파일러


def compile_c_code(file_name, jdata):
    try:
        # 컴파일 명령어 실행
        lib_path = f"{uuid.uuid4().hex}.so"
        result = subprocess.run(['gcc', '-shared', '-o', lib_path, file_name], capture_output=True, text=True)
        
        # 컴파일 에러 시 원인 return
        if result.returncode != 0:
            return (result.stderr.strip())

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
        return "HARD ERROR :" + str(e)


def compile_func(cdata, jdata):
    try:
        result = subprocess.run([cdata] + list(map(str, jdata)), capture_output=True, text=True)
        return result.stdout.strip()
        
    except Exception as e:
        return "HARD ERROR :" + str(e)

def compile_main(cdata, jdata, check):
    try:
        if check == 1:
            insert = " ".join(map(str, jdata)) + "\n"
            print("insert: ", insert)
            result = subprocess.run([cdata], input=insert.encode("utf-8"), stdout=subprocess.PIPE, universal_newlines=True)
            print("temp: ", result.stdout)
            result.stdout.flush()
            return result.stdout
        else:
            result = subprocess.run([cdata], capture_output=True, text=True)
            return result.stdout.strip()
        
    except Exception as e:
        return "HARD ERROR :" + str(e)



c_file_path = "./answerData/1.c"
prob = open_prob("1")

lib_path = f"./{uuid.uuid4().hex}.so"



check = check_main_function(c_file_path)
if check < 3:
    print("C 파일에 main 함수가 존재합니다.")
    result = subprocess.run(['gcc', '-o', lib_path, c_file_path], stdout=subprocess.PIPE)
    for input_data, output_data in zip(prob["inputs"], prob["outputs"]):
        actual_output = compile_main(lib_path, input_data, check)
        print(output_data, actual_output)

else:
    print("C 파일에 main 함수가 존재하지 않습니다.")
    result = subprocess.run(['gcc', '-o', lib_path, "-I", "problems", c_file_path, "./problems/main.c", "./problems/pes.h"], stdout=subprocess.PIPE)
    for input_data, output_data in zip(prob["inputs"], prob["outputs"]):
        actual_output = compile_func(lib_path, input_data)
        print(output_data, actual_output)
