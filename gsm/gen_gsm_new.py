import openai
import json
import numpy as np
import random
from tqdm import tqdm
import argparse

def construct_message(agents, question, idx):
    if len(agents) == 0:
        return {"role": "user", "content": "Can you double check that your answer is correct. Please reiterate your answer, with your final answer a single numerical number, in the form \\boxed{{answer}}."}

    prefix_string = "These are the solutions to the problem from other agents: "

    for agent in agents:
        agent_response = agent[idx]["content"]
        response = "\n\n One agent solution: ```{}```".format(agent_response)

        prefix_string = prefix_string + response

    prefix_string = prefix_string + """\n\n Using the solutions from other agents as additional information, can you provide your answer to the math problem? \n The original math problem is {}. Your final answer should be a single numerical number, in the form \\boxed{{answer}}, at the end of your response.""".format(question)
    return {"role": "user", "content": prefix_string}


def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}


def read_jsonl(path: str):
    with open(path) as fh:
        return [json.loads(line) for line in fh.readlines() if line]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run experiments with different parameters')
    parser.add_argument('--agents', type=int, default=3, help='Number of agents')
    parser.add_argument('--rounds', type=int, default=2, help='Number of rounds')
    parser.add_argument('--num_of_questions', type=int, default=10, help='Number of questions to process')
    parser.add_argument('--temperatures', nargs='+', type=float, help='List of temperatures for each agent')

    args = parser.parse_args()

    agents = args.agents
    rounds = args.rounds
    num_of_questions = args.num_of_questions
    temperatures = args.temperatures
    print(temperatures)

    questions = read_jsonl("data/test.jsonl")
    random.seed(42)
    generated_description = {}
    random.shuffle(questions)

    for data in tqdm(questions[:num_of_questions]):
        question = data['question']
        answer = data['answer']

        agent_contexts = [[{"role": "user", "content": """Can you solve the following math problem? {} Explain your reasoning. Your final answer should be a single numerical number, in the form \\boxed{{answer}}, at the end of your response. """.format(question)}] for agent in range(agents)]

        for round in range(rounds):
            for i, agent_context in enumerate(agent_contexts):
                if round != 0:
                    agent_contexts_other = agent_contexts[:i] + agent_contexts[i+1:]
                    message = construct_message(agent_contexts_other, question, 2*round - 1)
                    agent_context.append(message)

                completion = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=agent_context,
                            temperature = temperatures[i],
                            n=1)

                assistant_message = construct_assistant_message(completion)
                # print(assistant_message)
                agent_context.append(assistant_message)

        generated_description[question] = (agent_contexts, answer)
    json.dump(generated_description, open("gsm_{}_{}_{}.json".format(agents, rounds, str(temperatures)), "w"), indent=4)

# import pdb
# pdb.set_trace()
# print(answer)
# print(agent_context)