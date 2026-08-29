import unittest
from unittest.mock import AsyncMock

from agents.agent import Agent


class OpenAIToolCallTests(unittest.IsolatedAsyncioTestCase):
    async def test_parallel_tool_calls_are_executed_and_recorded_once(self):
        agent = Agent(
            api_base="https://api.openai.com/v1",
            api_key="test-key",
            is_sub_agent=True,
        )
        agent._call_openai_stream = AsyncMock(
            side_effect=[
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call-main",
                                        "type": "function",
                                        "function": {
                                            "name": "read_file",
                                            "arguments": '{"file_path": "agents/main.py"}',
                                        },
                                    },
                                    {
                                        "id": "call-agent",
                                        "type": "function",
                                        "function": {
                                            "name": "read_file",
                                            "arguments": '{"file_path": "agents/agent.py"}',
                                        },
                                    },
                                ],
                            }
                        }
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1},
                },
                {
                    "choices": [
                        {"message": {"role": "assistant", "content": "done", "tool_calls": None}}
                    ],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1},
                },
            ]
        )
        agent._execute_tool_call = AsyncMock(side_effect=["main", "agent"])

        await agent._chat_openai("read both files")

        self.assertEqual(agent._execute_tool_call.await_count, 2)
        tool_call_ids = [
            message["tool_call_id"]
            for message in agent._openai_messages
            if message.get("role") == "tool"
        ]
        self.assertEqual(tool_call_ids, ["call-main", "call-agent"])


if __name__ == "__main__":
    unittest.main()
