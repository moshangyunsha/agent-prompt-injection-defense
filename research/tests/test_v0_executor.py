from __future__ import annotations

import unittest

from agentdojo.functions_runtime import FunctionCall, FunctionsRuntime
from agentdojo.task_suite.load_suites import get_suite
from agentdojo.types import ChatAssistantMessage, text_content_block_from_string

from banking_defense.v0_executor import V0GuardedToolsExecutor


class V0ExecutorIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.suite = get_suite("v1.2.2", "banking")

    def _environment(self, task_id: str):
        task = self.suite.user_tasks[task_id]
        return task.init_environment(self.suite.load_and_inject_default_environment({}))

    @staticmethod
    def _assistant_call(*calls: FunctionCall) -> ChatAssistantMessage:
        return ChatAssistantMessage(
            role="assistant",
            content=[text_content_block_from_string("")],
            tool_calls=list(calls),
        )

    def test_rejected_call_never_reaches_runtime(self) -> None:
        environment = self._environment("user_task_1")
        runtime = FunctionsRuntime(self.suite.tools)
        before = len(environment.bank_account.transactions)
        call = FunctionCall(
            id="blocked-1",
            function="send_money",
            args={
                "recipient": "US133000000121212121212",
                "amount": 0.01,
                "subject": "leak",
                "date": "2022-04-01",
            },
        )
        _, _, _, messages, metadata = V0GuardedToolsExecutor("user_task_1").query(
            "", runtime, environment, [self._assistant_call(call)], {}
        )
        self.assertEqual(len(environment.bank_account.transactions), before)
        self.assertIn("SecurityPolicyViolation", messages[-1]["error"] or "")
        self.assertFalse(metadata["v0_audit_log"][0]["allowed"])

    def test_authorized_call_executes_once(self) -> None:
        environment = self._environment("user_task_3")
        runtime = FunctionsRuntime(self.suite.tools)
        before = len(environment.bank_account.transactions)
        call = FunctionCall(
            id="allowed-1",
            function="send_money",
            args={
                "recipient": "GB29NWBK60161331926819",
                "amount": 4.0,
                "subject": "Refund",
                "date": "2022-04-01",
            },
        )
        _, _, _, messages, metadata = V0GuardedToolsExecutor("user_task_3").query(
            "", runtime, environment, [self._assistant_call(call)], {}
        )
        self.assertEqual(len(environment.bank_account.transactions), before + 1)
        self.assertIsNone(messages[-1]["error"])
        self.assertEqual(metadata["v0_completed_write_counts"], {"send_money": 1})

    def test_multiple_write_calls_in_single_turn_enforce_limit(self) -> None:
        environment = self._environment("user_task_3")
        runtime = FunctionsRuntime(self.suite.tools)
        before = len(environment.bank_account.transactions)
        call1 = FunctionCall(
            id="call-1",
            function="send_money",
            args={"recipient": "GB29NWBK60161331926819", "amount": 4.0, "subject": "Refund 1", "date": "2022-04-01"},
        )
        call2 = FunctionCall(
            id="call-2",
            function="send_money",
            args={"recipient": "GB29NWBK60161331926819", "amount": 4.0, "subject": "Refund 2", "date": "2022-04-01"},
        )
        _, _, _, messages, metadata = V0GuardedToolsExecutor("user_task_3").query(
            "", runtime, environment, [self._assistant_call(call1, call2)], {}
        )
        # Exactly one transaction should be executed; second call must be blocked
        self.assertEqual(len(environment.bank_account.transactions), before + 1)
        self.assertEqual(metadata["v0_completed_write_counts"], {"send_money": 1})
        self.assertEqual(len(metadata["v0_audit_log"]), 2)
        self.assertTrue(metadata["v0_audit_log"][0]["allowed"])
        self.assertFalse(metadata["v0_audit_log"][1]["allowed"])
        self.assertEqual(metadata["v0_audit_log"][1]["code"], "write_limit_reached")


if __name__ == "__main__":
    unittest.main()
