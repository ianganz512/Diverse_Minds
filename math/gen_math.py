import openai
import json
import numpy as np
import time
import pickle
from tqdm import tqdm
import os

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


def generate_answer(answer_context, temperature, modelstring):
    try:
        completion = openai.ChatCompletion.create(
                  temperature=temperature,
                  model=modelstring,
                  messages=answer_context,
                  max_tokens=500,
                  n=1)
    except Exception as e:
        print(f"{e}")
        time.sleep(20)
        return generate_answer(answer_context, temperature, modelstring)

    return completion


def construct_message(agents, question, idx):

    # Use introspection in the case in which there are no other agents.
    if len(agents) == 0:
        return {"role": "user", "content": "Can you verify that your answer is correct. Please reiterate your answer, making sure to state your answer at the end of the response."}

    prefix_string = "These are the recent/updated opinions from other agents: "

    for agent in agents:
        agent_response = agent[idx]["content"]
        response = "\n\n One agent response: ```{}```".format(agent_response)

        prefix_string = prefix_string + response

    prefix_string = prefix_string + "\n\n Use these opinions carefully as additional advice, can you provide an updated answer? Make sure to state your answer at the end of the response.".format(question)
    return {"role": "user", "content": prefix_string}


def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}

def parse_answer(sentence):
    parts = sentence.split(" ")

    for part in parts[::-1]:
        try:
            answer = float(part)
            return answer
        except:
            continue


def most_frequent(List):
    counter = 0
    num = List[0]

    for i in List:
        current_frequency = List.count(i)
        if current_frequency > counter:
            counter = current_frequency
            num = i

    return num


if __name__ == "__main__":
    answer = parse_answer("My answer is the same as the other agents and AI language model: the result of 12+28*19+6 is 550.")

    agents = 1
    rounds = 2

    # temperature_sets = [[0.4, 0.7, 1], [0.5, 0.7, 0.9], [0.6, 0.7, 0.8], [0.7, 0.7, 0.7]]
    temperature_sets = [[0.7]]

    modelstring = "gpt-3.5-turbo"

    evaluation_round = 1000

    for temperature in temperature_sets:
        scores = [] 
        generated_description = {}
        np.random.seed(42)
        for round in tqdm(range(evaluation_round)):
            a, b, c, d, e, f = np.random.randint(0, 30, size=6)

            answer = a + b * c + d - e * f
            agent_contexts = [[{"role": "user", "content": """What is the result of {}+{}*{}+{}-{}*{}? Make sure to state your answer at the end of the response.""".format(a, b, c, d, e, f)}] for agent in range(agents)]

            content = agent_contexts[0][0]['content']
            question_prompt = "We seek to find the result of {}+{}*{}+{}-{}*{}?".format(a, b, c, d, e, f)

            for round in range(rounds):
                for i, agent_context in enumerate(agent_contexts):

                    if round != 0:
                        agent_contexts_other = agent_contexts[:i] + agent_contexts[i+1:]
                        message = construct_message(agent_contexts_other, question_prompt, 2*round - 1)
                        agent_context.append(message)

                        print("message: ", message)

                    completion = generate_answer(agent_context, temperature[i], modelstring)

                    assistant_message = construct_assistant_message(completion)
                    agent_context.append(assistant_message)
                    print(completion)

            text_answers = []

            for agent_context in agent_contexts:
                text_answer = string =  agent_context[-1]['content']
                text_answer = text_answer.replace(",", ".")
                text_answer = parse_answer(text_answer)

                if text_answer is None:
                    continue

                text_answers.append(text_answer)

            score = -1

            try:
                text_answer = most_frequent(text_answers)
                if text_answer == answer:
                    scores.append(1)
                    score = 1
                else:
                    scores.append(0)
                    score = 0
                generated_description[f"{a} + {b} * {c} + {d} - {e} * {f}"] = (agent_contexts, str(answer), score)
            except:
                generated_description[f"{a} + {b} * {c} + {d} - {e} * {f}"] = (agent_contexts, str(answer), score)
                continue

            print("performance:", np.mean(scores), np.std(scores) / (len(scores) ** 0.5))

        agent_temperature_string = "_temperature"
        for temp in temperature:
            agent_temperature_string += "_" + str(temp)
        #pickle.dump(generated_description, open(("math_agents{}_rounds{}".format(agents, rounds))+agent_temperature_string+".p", "wb"))

        foldername = f"{evaluation_round}_examples"
        # create the folder if it does not exist
        if not os.path.exists(foldername):
            os.makedirs(foldername)
        filename = f"{foldername}/agents{agents}_rounds{rounds}_temperature{agent_temperature_string}_evaluationRound_{evaluation_round}_model_{modelstring}"
        with open(filename + ".json", "w") as json_file:
            json.dump(generated_description, json_file, indent=4)
        with open(filename + ".txt", "w") as txt_file:
            txt_file.write("performance:" + str(np.mean(scores)) + " " + str( np.std(scores) / (len(scores) ** 0.5)))




