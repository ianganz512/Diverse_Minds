# codes for counting the correct, incorrect, and error responses in the evaluation results
# import json

# # read the file
# with open('/n/fs/nlp-yitaol/github/Diverse_Minds/new_results/agents3_rounds2_temperature_temperature_0.7_0.7_0.7_evaluationRound_100_model_gpt-3.5-turbo.json') as json_file:
#     data = json.load(json_file)

# successful_count = 0
# unsuccessful_count = 0
# error_count = 0
# # iterate over the data
# for key, value in data.items():
#     if value[2] == 0:
#         unsuccessful_count += 1
#     elif value[2] == 1:
#         successful_count += 1
#     else:
#         error_count += 1

# print("successful_count: ", successful_count)
# print("unsuccessful_count: ", unsuccessful_count)
# print("error_count: ", error_count)

# codes for analyzing the existence of the correct answer during debating

import json
import numpy as np
import pickle
import json
import openai
import numpy as np
import time
import re

def parse_bullets(sentence):
    bullets_preprocess = sentence.split("\n")
    bullets = []

    for bullet in bullets_preprocess:
        try:
            idx = bullet.find(next(filter(str.isalpha, bullet)))
        except:
            continue

        bullet = bullet[idx:]

        if len(bullet) != 0:
            bullets.append(bullet)

    return bullets


def parse_yes_no(string):
    """
    Parses a string containing "yes" or "no" and returns a boolean value.

    Args:
        string (str): The string to parse.

    Returns:
        bool: True if the string contains "yes", False if the string contains "no".

    Raises:
        ValueError: If the input string does not contain "yes" or "no".
    """
    if "yes" in string.lower():
        return True
    elif "no" in string.lower():
        return False
    else:
        return None


def solve_math_problems(input_str):
    pattern = r"\d+\.?\d*"

    matches = re.findall(pattern, input_str)
    if matches:
        return matches[-1]

    return None

def parse_answer(input_str):
    pattern = r"\{([0-9.,$]*)\}"
    matches = re.findall(pattern, input_str)

    solution = None

    for match_str in matches[::-1]:
        solution = re.sub(r"[^0-9.]", "", match_str)
        if solution:
            break

    return solution

# check the existence of correct answer in the debates
def compute_accuracy(gt, pred_solutions):
    answers = solve_math_problems(gt)

    if answers is None:
        return None

    if type(pred_solutions) == list:
        pred_answers = []

        for pred_solution in pred_solutions:
            pred_answer = parse_answer(pred_solution)

            if pred_answer is None:
                pred_answer = solve_math_problems(pred_solution)

            pred_answers.append(pred_answer)

        float_pred_answers = []
        # print("pred_answers: ", pred_answers)
        for answer in pred_answers:
            if answer is None:
                continue
            try:
                float_pred_answers.append(float(answer))
            except:
                print("answer: ", answer)
                continue
        # float_pred_answers = [float(answer) if answer is not None else 0 for answer in pred_answers]
        if float(answers) in float_pred_answers:
            return 1
        else:
            return 0
        # print("pred answer: ", pred_answer)
        # pred_answer = pred_answers[0]
        
    else:
        pred_answer = parse_answer(pred_solutions)
        if pred_answer is None:
            pred_answer = solve_math_problems(pred_solution)

    if pred_answer is None:
        return 1

    # try:
    if float(answers) == float(pred_answer):
        return 1
    else:
        return 0
    # except:
    #     import pdb
    #     pdb.set_trace()
    #     print(pred_solution)


def most_frequent(List):
    counter = 0
    num = List[0]

    for i in List:
        current_frequency = List.count(i)
        if current_frequency > counter:
            counter = current_frequency
            num = i

    return num


num_of_agents = 3
num_of_rounds = 2
temperature = [0.7, 0.7, 0.7]
evaluation_round = 500
modelstring = "gpt-3.5-turbo"


path = f'/n/fs/nlp-yitaol/github/Diverse_Minds/gsm/{evaluation_round}_examples/gsm_{num_of_agents}_{num_of_rounds}_{str(temperature)}.json'
# read the file
with open(path) as json_file:
    data = json.load(json_file)

# get the value list of the data
value_list = list(data.values())

response_contexts = [context[0] for context in value_list]
correct_answers = [context[1] for context in value_list] # strings

correctness_existence_count = 0
correctness_nonexistence_count = 0
correctness_list = []
for i in range(len(response_contexts)):
    agent_answers = []
    for j in range(len(response_contexts[i])):
        for k in range(len(response_contexts[i][j])):
            if response_contexts[i][j][k]["role"] == "assistant":
                # parse out the answer from the content
                content = response_contexts[i][j][k]["content"]
                content.replace(",", ".")
                agent_answers.append(content)
    accuracy = compute_accuracy(correct_answers[i], agent_answers)
    correctness_existence_count += accuracy
    correctness_nonexistence_count += 1 - accuracy
    correctness_list.append(accuracy)

# get the accuracy of the agent answers
score = np.mean(correctness_list)
print("config", num_of_agents, num_of_rounds, temperature, evaluation_round, modelstring)
print("accuracy: ", score)
print("correctness_existence_count: ", correctness_existence_count)
print("correctness_nonexistence_count: ", correctness_nonexistence_count)

# save the correctness list
with open(path.replace(".json", "_existence_correctness_list.pkl"), 'wb') as f:
    pickle.dump(correctness_list, f)