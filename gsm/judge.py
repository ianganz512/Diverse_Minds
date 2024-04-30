import openai
def judge(agent_contexts: list, question: str) -> dict:
    agents = len(agent_contexts)
    rounds = len(agent_contexts[0])//2
    prompt = f"""
There are {agents} agents who debated with each other for {rounds} to solve a math problem: {question}. Here are their debates recorded:
"""
    for round in range(rounds):
        round_prompt = f"ROUND {round+1}:\n"
        for i, agent_context in enumerate(agent_contexts):
            for j, agent in enumerate(agent_context):
                round_prompt += f"AGENT {j+1}: {agent['content']}\n"
        prompt += round_prompt
    prompt += f"You are a judge who need to decide the final answer to the math problem from their debates. Your final answer should be a single numerical number, in the form \\boxed{{answer}}, at the end of your response."
    messages = [
        {"role": "user", "content": prompt}
    ]
    completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature = 0.7,
                n=1)
    return completion.choices[0].message
