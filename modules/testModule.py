# pylint:disable=no-name-in-module,import-error
from asyncio import sleep
import re
from typing import Optional, cast

from jellyfish import jaro_winkler_similarity

from config import TEST_QUESTION_PREFIX, TEST_RESPONSE_PREFIX, test_response_message
from modules.module import IntegrationTest, Module, Response
from servicemodules.serviceConstants import Services
from utilities import get_question_id, is_test_response
from utilities.serviceutils import ServiceMessage
from utilities.utilities import is_bot_dev


class TestModule(Module):
    """
    This module is the only module that gets stampy to ask its self multiple questions
    In test mode, stampy only responds to itself, whereas in other modes stampy responds only to not itself
    """

    TEST_PREFIXES = {TEST_QUESTION_PREFIX, TEST_RESPONSE_PREFIX}
    TEST_MODULE_PROMPTS = {"test yourself", "test modules", "test module"}
    TEST_PHRASES = {TEST_RESPONSE_PREFIX} | TEST_MODULE_PROMPTS
    TEST_MODE_RESPONSE_MESSAGE = "I am running my integration test right now and I cannot handle your request until I am finished"
    SUPPORTED_SERVICES = [Services.DISCORD, Services.SLACK]

    def __init__(self):
        super().__init__()
        self.class_name = self.__str__()
        self.sent_test: list[IntegrationTest] = []

    def process_message(self, message: ServiceMessage):
        if not self.is_at_module(message):
            return Response()
        # If this is a message coming from an integration test,
        # add it to the dictionary and update output to the channel
        if is_test_response(message.clean_content):
            response_id = cast(int, get_question_id(message))
            self.log.info(
                self.class_name,
                clean_content=message.clean_content,
                response_id=response_id,
                is_at_me=self.is_at_me(message),
            )
            self.sent_test[response_id]["received_response"] = self.clean_test_prefixes(
                message, TEST_RESPONSE_PREFIX
            )
            return Response(
                confidence=8,
                text=test_response_message,
                why="this was a test",
            )

        # If Stampy is already running tests and this message is a request
        # to test himself, ignore it and reply accordingly
        if self.utils.test_mode:
            return Response(
                confidence=9,
                text=self.TEST_MODE_RESPONSE_MESSAGE,
                why="Test already running",
            )

        if message.channel.name != "talk-to-stampy":
            return Response(
                confidence=10,
                text="Testing is only allowed in #talk-to-stampy",
                why=f"{message.author.name} wanted to test me outside of the #talk-to-stampy channel which is prohibited!",
            )

        if not is_bot_dev(message.author):
            return Response(
                confidence=10,
                text=f"You are not a bot dev, {message.author.name}",
                why=f"{message.author.name} wanted to test me but they are not a bot dev",
            )

        # Otherwise, this is a request for Stampy to run integration tests
        lowercase_module_names = [
            module_name.lower() for module_name in self.utils.modules_dict
        ]
        if match := re.search(r"test module (\w+)", message.clean_content, re.I):
            parsed_module_name = match.group(1)
            if parsed_module_name.lower() not in lowercase_module_names:
                return Response(
                    confidence=10,
                    text=f'I don\'t have a module named "{parsed_module_name}"',
                    why=f'{message.author.name} asked me to test module "{parsed_module_name}" but I don\'t have such a module',
                )
            module_name = next(
                module_name
                for module_name in self.utils.modules_dict
                if module_name.lower() == parsed_module_name.lower()
            )
            modules_dict = {module_name: self.utils.modules_dict[module_name]}
        elif message.clean_content.strip().endswith("test module"):
            return Response(
                confidence=10,
                text="Yeah but what module?",
                why=f"{message.author.name} asked me to test a module but they didn't specify which one",
            )
        else:
            modules_dict = self.parse_module_dict(message)

        return Response(
            confidence=10,
            callback=self.run_integration_tests,
            args=[message],
            kwargs={"modules_dict": modules_dict},
        )

    def is_at_module(self, message: ServiceMessage) -> bool:
        if hasattr(message, "service"):
            if message.service not in self.SUPPORTED_SERVICES:
                return False
        return any(phrase in message.clean_content for phrase in self.TEST_PHRASES)

    def parse_module_dict(self, message: ServiceMessage) -> dict[str, Module]:
        text = message.clean_content
        if match := re.search(r"test modules ([\w\s]+)\n", text, re.I):
            module_name_candidates = match.group(1).lower().split()
            modules_dict = {
                module_name: module
                for module_name, module in self.utils.modules_dict.items()
                if module_name.lower() in module_name_candidates
            }
            return modules_dict
        return self.utils.modules_dict

    async def run_integration_tests(
        self, message: ServiceMessage, modules_dict: dict[str, Module]
    ) -> Response:
        """Run integration tests in all modules with test_cases"""

        # Set test mode to True and set message prefix
        self.utils.test_mode = True
        self.utils.message_prefix = TEST_RESPONSE_PREFIX

        # Run test_cases
        await self.send_test_questions(message, modules_dict)
        await sleep(3)  # Wait for test messages to go to discord and back to server

        # Evaluate tests and generate test message with the score (% of tests that passed)
        score = self.evaluate_test()
        test_message = f"The percentage of tests passed is {score:.2%}"

        # Get status messages and send them to the channel
        for question_number, question in enumerate(self.sent_test):
            test_status_message = (
                f"QUESTION # {question_number}: {question['result']}\n"
                f"The sent message was '{question['question'][:200]}'\n"
                f"the expected message was '{question['expected_response'][:200]}'\n"
                f"the received message was '{question['received_response'][:200]}'\n\n\n"
            )
            await message.channel.send(test_status_message)

        await sleep(3)

        # Delete all test from memory
        self.sent_test.clear()

        # Reset test mode and message_prefix
        self.utils.test_mode = False
        self.utils.message_prefix = ""
        return Response(confidence=10, text=test_message, why="this was a test")

    async def send_test_questions(
        self, message: ServiceMessage, modules_dict: dict[str, Module]
    ) -> None:
        question_id = 0
        for module_name, module in modules_dict.items():
            if hasattr(module, "test_cases"):
                self.log.info(self.class_name, msg=f"testing module {module_name}")
                for test_case in cast(
                    list[IntegrationTest], getattr(module, "test_cases")
                ):
                    test_message = (
                        f"{TEST_QUESTION_PREFIX}{question_id}: {test_case['question']}"
                    )
                    test_case["question"] = test_message
                    self.sent_test.append(test_case)
                    question_id += 1
                    await message.channel.send(test_message)
                    await sleep(test_case["test_wait_time"])
            else:
                self.sent_test.append(
                    self.create_integration_test(
                        question=f"Developers didn't write test for {module}",
                        expected_response="NEVER RECEIVED A RESPONSE",
                    )
                )
                question_id += 1

    def evaluate_test(self) -> float:
        passed_tests_count = 0
        for question in self.sent_test:
            # Removing random whitespace errors
            received_response = question["received_response"].strip()

            # Evaluate regex test
            if question["expected_regex"]:
                question["expected_response"] = "RegEx: " + question["expected_regex"]
                if re.search(question["expected_regex"], received_response):
                    passed_tests_count += 1
                    question["result"] = "PASSED"
                else:
                    question["result"] = "FAILED"

            # Evaluate "normal" test
            elif question["minimum_allowed_similarity"] == 1.0:
                if question["expected_response"] == received_response:
                    passed_tests_count += 1
                    question["result"] = "PASSED"
                else:
                    question["result"] = "FAILED"

            # Evaluate test which allows less-than-perfect-similarity
            else:
                text_similarity = jaro_winkler_similarity(
                    question["expected_response"], received_response
                )
                if text_similarity >= question["minimum_allowed_similarity"]:
                    passed_tests_count += 1
                    question["result"] = "PASSED"
                else:
                    question["result"] = "FAILED"

        score = passed_tests_count / len(self.sent_test)
        return score

    def __str__(self):
        return "TestModule"

    @property
    def test_cases(self):
        return [
            self.create_integration_test(
                question=prompt, expected_response=self.TEST_MODE_RESPONSE_MESSAGE
            )
            for prompt in self.TEST_MODULE_PROMPTS
        ]
