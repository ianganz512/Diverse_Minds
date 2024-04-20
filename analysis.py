import json

# read the file
with open('/n/fs/nlp-yitaol/github/Diverse_Minds/new_results/agents3_rounds2_temperature_temperature_0.7_0.7_0.7_evaluationRound_100_model_gpt-3.5-turbo.json') as json_file:
    data = json.load(json_file)

successful_count = 0
unsuccessful_count = 0
error_count = 0
# iterate over the data
for key, value in data.items():
    if value[2] == 0:
        unsuccessful_count += 1
    elif value[2] == 1:
        successful_count += 1
    else:
        error_count += 1

print("successful_count: ", successful_count)
print("unsuccessful_count: ", unsuccessful_count)
print("error_count: ", error_count)