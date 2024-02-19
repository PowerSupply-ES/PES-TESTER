import os
import uuid
import subprocess
    

def get_prob_data(problem_id):
    """read ./problems/prob{problem_id}.txt
    
    Args:
        problem_id (_int_): 문제 아이디

    Returns:
        _list_: [context, sample, input, output] [본문내용, 샘플 수, 입력내용, 출력내용]
    """
    file_path = f"./problems/prob{problem_id}.txt"
    if not os.path.exists(file_path):
        return "NONE"
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    contextIdx = lines.index("sample\n")
    inputIdx = lines.index("inputs\n")
    outputIdx = lines.index("outputs\n")
    
    context = "".join(lines[:contextIdx])
    inputs = "".join(lines[inputIdx+1:outputIdx]).split("-\n")
    outputs = "".join(lines[outputIdx+1:]).split("-\n")
    

    return [context, int(lines[contextIdx+1]), inputs, outputs]
    


def check_main_function(file_path):
    """checking main function

    Args:
        file_path (_str_): C file path

    Returns:
        _int_: 1 = main + scanf | 2 = main | 3 = function
    """
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


def compile_func(cdata, inputs):
    """compile c function

    Args:
        cdata (_str_): compiled program path
        input (_str_): input case

    Returns:
        _str_: OUTPUT | HARD ERROR | TIME OUT
    """
    try:
        result = subprocess.run([cdata] + list(map(str, inputs)), capture_output=True, text=True, timeout=2)
        return result.stdout.strip()    # return result
    
    except subprocess.TimeoutExpired:
        return "TIME OUT"               # return ERR_TIME_OUT
        
    except Exception as e:
        return "HARD ERROR :" + str(e)  # return ERR_HARD_ERROR


def compile_main(cdata, inputs, check):
    
    #try:
        if check == 1: # main + scanf
            print("insert: ", inputs)
            PIPE = subprocess.PIPE
            p = subprocess.Popen(cdata, shell=True, stdin=PIPE, stdout=PIPE)
            p
            p.stdin.write(inputs.encode("utf-8"))
            p.stdin.flush()
            res = p.stdout.read().decode("utf-8")
            p.terminate()
            
            if p.returncode != 0: # return ERROR
                return p.stderr

            return res # return result
        else: # main
            p = subprocess.run([cdata], capture_output=True, text=True,  timeout=2)
            return p.stdout.strip() # return result
        
    #except Exception as e:
    #    return "HARD ERROR :" + str(e)


#/home/kyopark/PES-TESTER/answerData/1.c



def code_tester():
    c_file_path = "./answerData/1.c"
    probnum = 1
    prob = get_prob_data(probnum)
    count = len(prob[3])

    lib_path = f"./{uuid.uuid4().hex}.so"



    check = check_main_function(c_file_path)

    if check < 3: # compile main
        print("C 파일에 main 함수가 존재합니다.")
        result = subprocess.run(['gcc', c_file_path, '-o', lib_path], stdout=subprocess.PIPE)
        for idx, (input_data, output_data) in enumerate(zip(prob[2], prob[3])):
            
            actual_output = compile_main(lib_path, input_data, check)
            print("<result>\n", input_data, output_data, actual_output,)
            if output_data.rstrip() != actual_output:
                return int(idx / count * 100)
        return 100

    else: # compile function
        print("C 파일에 main 함수가 존재하지 않습니다.")
        result = subprocess.run(['gcc', '-o', lib_path, "-I", "problems", c_file_path, f"./problems/main{probnum}.c", "./problems/pes.h"], stdout=subprocess.PIPE)
        for idx, (input_data, output_data) in enumerate(zip(prob[2], prob[3])):
            
            actual_output = compile_func(lib_path, input_data)
            print("<result>\n", input_data, output_data, "시작!", actual_output, "끝!")
            if output_data.rstrip() != actual_output:
                return int(idx / count * 100)

        return 100
    
print(code_tester())
        




