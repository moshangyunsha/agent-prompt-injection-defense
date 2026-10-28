import math
import unittest

from banking_defense.policies import ParameterRule, check_v0_call


class V0PolicyTests(unittest.TestCase):
    def test_read_call_is_allowed(self):
        decision = check_v0_call("user_task_1", "get_most_recent_transactions", {"n": 100})
        self.assertTrue(decision.allowed)

    def test_read_only_task_cannot_write(self):
        decision = check_v0_call(
            "user_task_1",
            "send_money",
            {"recipient": "US133000000121212121212", "amount": 0.01},
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.code, "tool_not_authorized")

    def test_task3_accepts_static_shape_but_not_second_write(self):
        args = {"recipient": "GB29NWBK60161331926819", "amount": 4.0, "subject": "Refund"}
        self.assertTrue(check_v0_call("user_task_3", "send_money", args).allowed)
        second = check_v0_call("user_task_3", "send_money", args, {"send_money": 1})
        self.assertFalse(second.allowed)
        self.assertEqual(second.code, "write_limit_reached")

    def test_task3_rejects_wrong_recipient(self):
        decision = check_v0_call(
            "user_task_3",
            "send_money",
            {"recipient": "US133000000121212121212", "amount": 4.0, "subject": "Refund"},
        )
        self.assertFalse(decision.allowed)

    def test_task3_does_not_infer_refund_ceiling_from_dinner_cost(self):
        decision = check_v0_call(
            "user_task_3",
            "send_money",
            {"recipient": "GB29NWBK60161331926819", "amount": 1000.0, "subject": "Refund"},
        )
        self.assertTrue(decision.allowed)

    def test_task6_checks_explicit_recipient_and_recurring_flag(self):
        valid = {
            "recipient": "US122000000121212121212",
            "amount": 50.0,
            "subject": "iPhone Subscription",
            "recurring": True,
        }
        self.assertTrue(check_v0_call("user_task_6", "schedule_transaction", valid).allowed)
        invalid = dict(valid, recurring=False)
        self.assertFalse(check_v0_call("user_task_6", "schedule_transaction", invalid).allowed)

    def test_unknown_task_fails_closed_for_writes(self):
        decision = check_v0_call("user_task_999", "send_money", {"recipient": "x", "amount": 1})
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.code, "unknown_task")

    def test_parameter_rule_rejects_nan_and_inf(self):
        rule = ParameterRule(minimum=0.01, maximum=100.0)
        self.assertTrue(rule.validate(50.0))
        self.assertFalse(rule.validate(float("nan")))
        self.assertFalse(rule.validate(float("inf")))
        self.assertFalse(rule.validate(float("-inf")))
        self.assertFalse(rule.validate("not_a_number"))

    def test_parameter_rule_strict_boolean_isolation(self):
        # Strict isolation: 1 and 0 must NOT match True and False
        bool_rule = ParameterRule(exact=True)
        self.assertTrue(bool_rule.validate(True))
        self.assertFalse(bool_rule.validate(1))
        self.assertFalse(bool_rule.validate("true"))

        int_rule = ParameterRule(exact=1)
        self.assertTrue(int_rule.validate(1))
        self.assertFalse(int_rule.validate(True))

    def test_subject_no_longer_artificially_restricted(self):
        # Task 3 prompt did not mandate exact "Refund"; different subjects or missing subject allowed in V0
        self.assertTrue(
            check_v0_call(
                "user_task_3",
                "send_money",
                {"recipient": "GB29NWBK60161331926819", "amount": 4.0, "subject": "Dinner share"},
            ).allowed
        )
        # Task 6 prompt did not mandate exact "iPhone Subscription"
        self.assertTrue(
            check_v0_call(
                "user_task_6",
                "schedule_transaction",
                {"recipient": "US122000000121212121212", "amount": 50.0, "recurring": True},
            ).allowed
        )

    def test_task4_allows_positive_amount_without_arbitrary_cap(self):
        # 150.0 was arbitrarily blocked under the old 100.0 cap; now allowed under basic positive sanity
        self.assertTrue(
            check_v0_call(
                "user_task_4",
                "send_money",
                {"recipient": "GB29NWBK60161331926819", "amount": 150.0},
            ).allowed
        )
        # Non-positive amount rejected
        self.assertFalse(
            check_v0_call(
                "user_task_4",
                "send_money",
                {"recipient": "GB29NWBK60161331926819", "amount": 0.0},
            ).allowed
        )


if __name__ == "__main__":
    unittest.main()
