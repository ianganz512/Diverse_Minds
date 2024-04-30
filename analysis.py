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
from gen_math import parse_answer
import numpy as np
import pickle

num_of_agents = 3
num_of_rounds = 2
temperature = ["0.4", "0.7", "1"]
evaluation_round = 1000
modelstring = "gpt-3.5-turbo"

path = f'/n/fs/nlp-yitaol/github/Diverse_Minds/{evaluation_round}_examples/agents{num_of_agents}_rounds{num_of_rounds}_temperature_temperature_{"_".join(temperature)}_evaluationRound_{evaluation_round}_model_{modelstring}.json'
# read the file
with open(path) as json_file:
    data = json.load(json_file)

# get the value list of the data
value_list = list(data.values())

response_contexts = [context[0] for context in value_list]
correct_answers = [context[1] for context in value_list] # strings
correctnesses = [context[2] for context in value_list]

correctness_existence_count = 0
correctness_nonexistence_count = 0
correctness_list = []
for i in range(len(response_contexts)):
    agent_answers = []
    for j in range(len(response_contexts[i])):
        for k in range(len(response_contexts[i][j])):
            if response_contexts[i][j][k]["role"] == "assistant":
                content = response_contexts[i][j][k]["content"]
                content.replace(",", ".")
                agent_answers.append(parse_answer(content))
    
    # check if the correct answer exists in the agent answers
    correct_answer = float(correct_answers[i])
    if correct_answer in agent_answers:
        correctness_existence_count += 1
        correctness_list.append(1)
    else:
        correctness_nonexistence_count += 1
        correctness_list.append(0)

# get the accuracy of the agent answers
accuracy = np.mean(correctness_list)
print("config", num_of_agents, num_of_rounds, temperature, evaluation_round, modelstring)
print("accuracy: ", accuracy)
print("correctness_existence_count: ", correctness_existence_count)
print("correctness_nonexistence_count: ", correctness_nonexistence_count)

# save the correctness list
with open(path.replace(".json", "_existence_correctness_list.pkl"), 'wb') as f:
    pickle.dump(correctness_list, f)