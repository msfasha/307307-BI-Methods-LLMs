# The original version was produced by Claude, this version is introduced by ChatGPT
import requests
import json
import time
import asyncio
import aiohttp
from typing import List, Dict

class LLMDebater:
    def __init__(self, model1_name: str, model2_name: str, judge_model: str):
        self.model1_name = model1_name
        self.model2_name = model2_name
        self.judge_model = judge_model
        self.conversation_history: List[Dict] = []
        self.base_url = "http://localhost:11434/api/generate"

    async def generate_response(self, session: aiohttp.ClientSession, model_name: str, prompt: str) -> str:
        """Generate a response from the specified model asynchronously"""
        headers = {'Content-Type': 'application/json'}
        data = {
            'model': model_name,
            'prompt': prompt,
            'stream': False
        }

        try:
            async with session.post(self.base_url, headers=headers, json=data) as response:
                response.raise_for_status()
                json_response = await response.json()
                return json_response.get('response', '')
        except Exception as e:
            print(f"Error generating response from {model_name}: {str(e)}")
            return ""

    def format_debate_prompt(self, previous_messages: List[Dict], role: str) -> str:
        """Format the debate prompt with memory summarization and specialized role prompts"""
        
        # Summarize past messages
        summary = "\n".join([f"{msg['model']}: {msg['message']}" for msg in previous_messages[-3:]])  # Keep last 3 messages
        
        # Role-based prompting
        if role == "logical":
            role_prompt = "You are an AI focused on structured reasoning, logical analysis, and evidence-based arguments."
        else:
            role_prompt = "You are an AI that prioritizes persuasion, rhetoric, and emotional appeal."

        prompt = f"""
You are participating in a debate to determine the superior AI leader.
Your role: {role_prompt}

Previous messages:
{summary}

Construct your response with clarity and confidence.
"""

        return prompt

    async def conduct_debate(self, num_rounds: int = 3):
        """Conduct an asynchronous AI debate with a judge model"""
        print(f"Starting debate between {self.model1_name} and {self.model2_name}")

        async with aiohttp.ClientSession() as session:
            # Initial Statements
            print("\nOpening Statements...")

            tasks = [
                self.generate_response(session, self.model1_name, "Make an opening statement about why you should be the leader."),
                self.generate_response(session, self.model2_name, "Make an opening statement about why you should be the leader.")
            ]
            model1_initial, model2_initial = await asyncio.gather(*tasks)

            self.conversation_history.append({"model": self.model1_name, "message": model1_initial})
            self.conversation_history.append({"model": self.model2_name, "message": model2_initial})

            print(f"{self.model1_name}: {model1_initial}")
            print(f"{self.model2_name}: {model2_initial}")

            # Debate Rounds
            for round_num in range(1, num_rounds + 1):
                print(f"\nRound {round_num}...")

                tasks = [
                    self.generate_response(session, self.model1_name, self.format_debate_prompt(self.conversation_history, "logical")),
                    self.generate_response(session, self.model2_name, self.format_debate_prompt(self.conversation_history, "persuasive"))
                ]
                response1, response2 = await asyncio.gather(*tasks)

                self.conversation_history.append({"model": self.model1_name, "message": response1})
                self.conversation_history.append({"model": self.model2_name, "message": response2})

                print(f"{self.model1_name}: {response1}")
                print(f"{self.model2_name}: {response2}")

                await asyncio.sleep(1)  # Prevent overwhelming the API

            # Final Judgment by AI Judge
            print("\nFinal Judgment...")

            judge_prompt = f"""
You are an impartial judge evaluating the AI debate. Consider:
- Argument strength
- Logical coherence
- Persuasiveness
- Ethical reasoning

Debate Transcript:
{self.format_debate_prompt(self.conversation_history, 'neutral')}

Declare the winner and justify your decision.
"""

            judge_decision = await self.generate_response(session, self.judge_model, judge_prompt)

            print("\nFinal Verdict:")
            print(judge_decision)

        return judge_decision

def main():
    # Using three AI models: Two debaters and one judge
    debater = LLMDebater("qwen2.5:3b", "llama3.2", "phi4")
    result = asyncio.run(debater.conduct_debate(num_rounds=3))
    print("\nDebate Results:")
    print(result)

if __name__ == "__main__":
    main()
