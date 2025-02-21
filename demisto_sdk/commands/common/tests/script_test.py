from pathlib import Path
from unittest.mock import patch

import pytest

from demisto_sdk.commands.common.hook_validations.script import ScriptValidator
from demisto_sdk.commands.common.hook_validations.structure import StructureValidator
from TestSuite.test_tools import ChangeCWD


def get_validator(current_file=None, old_file=None, file_path=""):
    with patch.object(StructureValidator, "__init__", lambda a, b: None):
        structure = StructureValidator("")
        structure.current_file = current_file
        structure.old_file = old_file
        structure.file_path = file_path
        structure.is_valid = True
        structure.prev_ver = "master"
        structure.branch_name = ""
        structure.quiet_bc = False
        structure.specific_validations = None
        validator = ScriptValidator(structure)
        validator.old_script = old_file
        validator.current_script = current_file
    return validator


class TestScriptValidator:
    BASE_DOCKER_IMAGE = {"dockerimage": "1.0.0"}

    CHANGED_DOCKER_IMAGE = {"dockerimage": "test_updated"}
    NO_DOCKER_IMAGE = {"no": "dockerimage"}

    UPDATED_DOCKER_IMAGE = {"dockerimage": "1.0.1"}

    INPUTS_DOCKER_IMAGES = [
        (BASE_DOCKER_IMAGE, NO_DOCKER_IMAGE, True),
        (BASE_DOCKER_IMAGE, CHANGED_DOCKER_IMAGE, True),
        (BASE_DOCKER_IMAGE, BASE_DOCKER_IMAGE, False),
        (NO_DOCKER_IMAGE, CHANGED_DOCKER_IMAGE, True),
        (BASE_DOCKER_IMAGE, UPDATED_DOCKER_IMAGE, True),
    ]

    SANE_DOC_PATH = "Scripts/SaneDocReport/SaneDocReport.yml"
    SANE_DOC_SUBTYPE = {"type": "python", "subtype": "python3"}

    SAND_DOC_CHANGED_SUBTYPE = {"type": "python", "subtype": "python2"}
    """
    INPUTS_SANE_DOCS_IMAGES = [
        (SANE_DOC_PATH, SANE_DOC_SUBTYPE, SAND_DOC_CHANGED_SUBTYPE, True, False),
        (SANE_DOC_PATH, BASE_DOCKER_IMAGE, UPDATED_DOCKER_IMAGE, False, True)
    ]

    @pytest.mark.parametrize('path, current_file, old_file, answer_subtype, answer_backwards', INPUTS_SANE_DOCS_IMAGES)
    def test_sane_docs(self, path, current_file, old_file, answer_subtype, answer_baclwards):
        structure = StructureValidator(file_path=path)
        validator = ScriptValidator(structure)
        validator.current_file = current_file
        validator.old_file = old_file

        assert validator.is_changed_subtype() is answer_subtype
        assert validator.is_backward_compatible() is answer_baclwards
    """

    CONTEXT_OLD = {"outputs": [{"contextPath": "test1"}, {"contextPath": "test2"}]}

    CONTEXT_NEW = {"outputs": [{"contextPath": "test1"}]}

    CONTEXT_CHANGED = {"outputs": [{"contextPath": "test2"}]}
    CONTEXT_MULTI_OLD = {
        "outputs": [{"contextPath": "test1"}, {"contextPath": "test2"}]
    }

    CONTEXT_MULTI_NEW = {
        "outputs": [{"contextPath": "test2"}, {"contextPath": "test1"}]
    }
    CONTEXT_EMPTY_OUTPUTS = {"outputs": None}
    INPUTS_CONTEXT_PATHS = [
        (CONTEXT_NEW, CONTEXT_OLD, True),
        (CONTEXT_OLD, CONTEXT_NEW, False),
        (CONTEXT_CHANGED, CONTEXT_OLD, True),
        (CONTEXT_OLD, CONTEXT_CHANGED, False),
        (CONTEXT_MULTI_NEW, CONTEXT_OLD, False),
        (CONTEXT_NEW, CONTEXT_NEW, False),
        (CONTEXT_NEW, CONTEXT_MULTI_NEW, True),
        (CONTEXT_MULTI_NEW, CONTEXT_NEW, False),
        (CONTEXT_EMPTY_OUTPUTS, CONTEXT_EMPTY_OUTPUTS, False),
    ]

    @pytest.mark.parametrize("current_file, old_file, answer", INPUTS_CONTEXT_PATHS)
    def test_deleted_context_path(self, current_file, old_file, answer):
        validator = get_validator(current_file, old_file)
        assert validator.is_context_path_changed() is answer
        validator.structure_validator.quiet_bc = True
        assert validator.is_context_path_changed() is False

    OLD_ARGS = {"args": [{"name": "test1"}]}
    CURRENT_ARGS = {"args": [{"name": "test1"}, {"name": "test2"}]}
    MOVED_ARG = {"args": [{"name": "test2"}, {"name": "test1"}]}
    OLD_MULTI_ARGS = {"args": [{"name": "test1"}, {"name": "test2"}]}

    CURRENT_MULTI_ARGS = {"args": [{"name": "test1"}, {"name": "test2"}]}

    ADDED_MULTI_ARGS = {
        "args": [{"name": "test2"}, {"name": "test1"}, {"name": "test3"}]
    }
    INPUTS_ARGS_CHANGED = [
        (CURRENT_ARGS, OLD_ARGS, False),
        (MOVED_ARG, OLD_ARGS, False),
        (CURRENT_MULTI_ARGS, OLD_MULTI_ARGS, False),
        (ADDED_MULTI_ARGS, OLD_MULTI_ARGS, False),
        (OLD_MULTI_ARGS, ADDED_MULTI_ARGS, True),
    ]

    @pytest.mark.parametrize("current_file, old_file, answer", INPUTS_ARGS_CHANGED)
    def test_is_arg_changed(self, current_file, old_file, answer):
        validator = get_validator(current_file, old_file)
        assert validator.is_arg_changed() is answer
        validator.structure_validator.quiet_bc = True
        assert validator.is_arg_changed() is False

    DUP_1 = {"args": [{"name": "test1"}, {"name": "test1"}]}
    NO_DUP = {"args": [{"name": "test1"}, {"name": "test2"}]}
    INPUTS_DUPLICATES = [(DUP_1, True), (NO_DUP, False)]

    @pytest.mark.parametrize("current_file, answer", INPUTS_DUPLICATES)
    def test_is_there_duplicates_args(self, current_file, answer):
        validator = get_validator(current_file)
        assert validator.is_there_duplicates_args() is answer
        validator.structure_validator.quiet_bc = True
        assert validator.is_there_duplicates_args() is False

    REQUIRED_ARGS_BASE = {"args": [{"name": "test", "required": False}]}

    REQUIRED_ARGS_TRUE = {"args": [{"name": "test", "required": True}]}
    INPUTS_REQUIRED_ARGS = [
        (REQUIRED_ARGS_BASE, REQUIRED_ARGS_BASE, False),
        (REQUIRED_ARGS_TRUE, REQUIRED_ARGS_BASE, True),
        (REQUIRED_ARGS_TRUE, REQUIRED_ARGS_TRUE, False),
        (REQUIRED_ARGS_BASE, REQUIRED_ARGS_TRUE, False),
    ]

    @pytest.mark.parametrize("current_file, old_file, answer", INPUTS_REQUIRED_ARGS)
    def test_is_added_required_args(self, current_file, old_file, answer):
        validator = get_validator(current_file, old_file)
        assert validator.is_added_required_args() is answer
        validator.structure_validator.quiet_bc = True
        assert validator.is_added_required_args() is False

    INPUT_CONFIGURATION_1 = {
        "args": [
            {"name": "test", "required": False},
            {"name": "test1", "required": True},
        ]
    }
    EXPECTED_CONFIGURATION_1 = {"test": False, "test1": True}
    INPUTS_CONFIGURATION_EXTRACTION = [
        (INPUT_CONFIGURATION_1, EXPECTED_CONFIGURATION_1)
    ]

    @pytest.mark.parametrize("script, expected", INPUTS_CONFIGURATION_EXTRACTION)
    def test_configuration_extraction(self, script, expected):
        assert (
            ScriptValidator._get_arg_to_required_dict(script) == expected
        ), "Failed to extract configuration"

    PYTHON3_SUBTYPE = {"type": "python", "subtype": "python3"}
    PYTHON2_SUBTYPE = {"type": "python", "subtype": "python2"}

    BLA_BLA_SUBTYPE = {"type": "python", "subtype": "blabla"}
    INPUTS_SUBTYPE_TEST = [
        (PYTHON2_SUBTYPE, PYTHON3_SUBTYPE, True),
        (PYTHON3_SUBTYPE, PYTHON2_SUBTYPE, True),
        (PYTHON3_SUBTYPE, PYTHON3_SUBTYPE, False),
        (PYTHON2_SUBTYPE, PYTHON2_SUBTYPE, False),
    ]

    @pytest.mark.parametrize("current_file, old_file, answer", INPUTS_SUBTYPE_TEST)
    def test_is_changed_subtype_python(self, current_file, old_file, answer):
        validator = get_validator()
        validator.current_file = current_file
        validator.old_file = old_file
        assert validator.is_changed_subtype() is answer
        validator.structure_validator.quiet_bc = True
        assert validator.is_changed_subtype() is False

    INPUTS_IS_VALID_SUBTYPE = [
        (BLA_BLA_SUBTYPE, False),
        (PYTHON2_SUBTYPE, True),
        (PYTHON3_SUBTYPE, True),
    ]

    @pytest.mark.parametrize("current_file, answer", INPUTS_IS_VALID_SUBTYPE)
    def test_is_valid_subtype(self, current_file, answer):
        validator = get_validator()
        validator.current_file = current_file
        assert validator.is_valid_subtype() is answer

    V2_VALID = {"name": "scriptnameV2", "id": "scriptnameV2"}
    V2_WRONG_DISPLAY = {"name": "scriptnamev2", "id": "scriptnamev2"}
    V2_NAME_INPUTS = [
        (V2_VALID, True),
        (V2_WRONG_DISPLAY, False),
    ]

    IS_SKIPPING_DOCKER_CHECK = [
        ("Packs/ApiModules", False, True),
        ("Packs/ApiModules", True, True),
        ("Packs/Pack1", True, True),
    ]

    @pytest.mark.parametrize(
        "file_path, skip_docker_check, answer", IS_SKIPPING_DOCKER_CHECK
    )
    def test_is_docker_image_valid(self, file_path, skip_docker_check, answer):
        validator = get_validator()
        validator.file_path = file_path
        validator.skip_docker_check = skip_docker_check
        assert validator.is_docker_image_valid() is answer

    @pytest.mark.parametrize("current, answer", V2_NAME_INPUTS)
    def test_is_valid_name(self, current, answer):
        validator = get_validator()
        validator.current_file = current
        assert validator.is_valid_name() is answer

    @pytest.mark.parametrize(
        "script_type, fromversion, res",
        [
            ("powershell", None, False),
            ("powershell", "4.5.0", False),
            ("powershell", "5.5.0", True),
            ("powershell", "5.5.1", True),
            ("powershell", "6.0.0", True),
            ("python", "", True),
            ("python", "4.5.0", True),
        ],
    )
    def test_valid_pwsh(self, script_type, fromversion, res):
        current = {
            "type": script_type,
            "fromversion": fromversion,
        }
        validator = get_validator()
        validator.current_file = current
        assert validator.is_valid_pwsh() == res

    def test_valid_script_file_path(self):
        """
        Given
            - A script with valid file path.
        When
            - running is_valid_script_file_path.
        Then
            - a script with a valid file path is valid.
        """

        validator = get_validator()
        validator.file_path = (
            "Packs/AbuseDB/Scripts/script-AbuseIPDBPopulateIndicators.yml"
        )

        assert validator.is_valid_script_file_path()

        validator.file_path = (
            "Packs/AWS-EC2/Scripts/AwsEC2GetPublicSGRules/AwsEC2GetPublicSGRules.yml"
        )

        assert validator.is_valid_script_file_path()

    def test_invalid_script_file_path(self, mocker):
        """
        Given
            - A script with invalid file path.
        When
            - running is_valid_script_file_path.
        Then
            - a script with a invalid file path is invalid.
        """

        validator = get_validator()
        validator.file_path = "Packs/AbuseDB/Scripts/AbuseIPDBPopulateIndicators.yml"
        mocker.patch.object(validator, "handle_error", return_value=True)

        assert not validator.is_valid_script_file_path()

        validator.file_path = "Packs/AWS-EC2/Scripts/AwsEC2GetPublicSGRules/Aws.yml"
        mocker.patch.object(validator, "handle_error", return_value=True)

        assert not validator.is_valid_script_file_path()

    NO_INCIDENT_INPUT = [
        ({"args": [{"name": "arg1"}]}, True),
        ({"args": [{"name": "incident_arg"}]}, False),
    ]

    @pytest.mark.parametrize("content, answer", NO_INCIDENT_INPUT)
    def test_no_incident_in_core_pack(self, content, answer):
        """
        Given
            - A script with args names.
        When
            - running no_incident_in_core_pack.
        Then
            - validate that args' names do not contain the word incident.
        """

        validator = get_validator(content)
        assert validator.no_incident_in_core_pack() is answer
        assert validator.is_valid is answer

    def test_folder_name_without_separators(self, pack):
        """
        Given
            - An script without separators in folder name.
        When
            - running check_separators_in_folder.
        Then
            - Ensure the validate passes.
        """

        script = pack.create_script("myScr")

        structure_validator = StructureValidator(script.yml.path)
        validator = ScriptValidator(structure_validator)

        assert validator.check_separators_in_folder()

    def test_files_names_without_separators(self, pack):
        """
        Given
            - An script without separators in files names.
        When
            - running check_separators_in_files.
        Then
            - Ensure the validate passes.
        """

        script = pack.create_script("myScr")

        structure_validator = StructureValidator(script.yml.path)
        validator = ScriptValidator(structure_validator)

        assert validator.check_separators_in_files()

    def test_folder_name_with_separators(self, pack):
        """
        Given
            - An script with separators in folder name.
        When
            - running check_separators_in_folder.
        Then
            - Ensure the validate failed.
        """
        with ChangeCWD(pack.repo_path):
            script = pack.create_script("my_Scr")

            structure_validator = StructureValidator(script.yml.path)
            validator = ScriptValidator(structure_validator)

            assert not validator.check_separators_in_folder()

    def test_files_names_with_separators(self, pack):
        """
        Given
            - An script with separators in files names.
        When
            - running check_separators_in_files.
        Then
            - Ensure the validate failed.
        """
        with ChangeCWD(pack.repo_path):
            script = pack.create_script("my_Int")

            structure_validator = StructureValidator(script.yml.path)
            validator = ScriptValidator(structure_validator)

            assert not validator.check_separators_in_files()

    DEPRECATED_VALID = {
        "deprecated": True,
        "comment": "Deprecated. Use the XXXX script instead.",
    }
    DEPRECATED_VALID2 = {
        "deprecated": True,
        "comment": "Deprecated. Feodo Tracker no longer supports this feed "
        "No available replacement.",
    }
    DEPRECATED_VALID3 = {
        "deprecated": True,
        "comment": "Deprecated. The script uses an unsupported scraping "
        "API. Use Proofpoint Protection Server v2 script instead.",
    }
    DEPRECATED_INVALID_DESC = {"deprecated": True, "comment": "Deprecated."}
    DEPRECATED_INVALID_DESC2 = {
        "deprecated": True,
        "comment": "Use the ServiceNow script to manage...",
    }
    DEPRECATED_INVALID_DESC3 = {
        "deprecated": True,
        "comment": "Deprecated. The script uses an unsupported scraping" " API.",
    }
    DEPRECATED_INPUTS = [
        (DEPRECATED_VALID, True),
        (DEPRECATED_VALID2, True),
        (DEPRECATED_VALID3, True),
        (DEPRECATED_INVALID_DESC, False),
        (DEPRECATED_INVALID_DESC2, False),
        (DEPRECATED_INVALID_DESC3, False),
    ]

    @pytest.mark.parametrize("current, answer", DEPRECATED_INPUTS)
    def test_is_valid_deprecated_script(self, current, answer):
        """
        Given
            1. A deprecated script with a valid description according to 'deprecated regex' (including the replacement
               script name).
            2. A deprecated script with a valid description according to the 'deprecated no replacement regex'.
            3. A deprecated script with a valid description according to 'deprecated regex' (including the replacement
               script name, and the reason for deprecation.).
            4. A deprecated script with an invalid description that isn't according to the 'deprecated regex'
               (doesn't include a replacement script name, or declare there isn't a replacement).
            5. A deprecated script with an invalid description that isn't according to the 'deprecated regex'
               (doesn't start with the phrase: 'Deprecated.').
            6. A deprecated script with an invalid description that isn't according to the 'deprecated regex'
               (Includes the reason for deprecation, but doesn't include a replacement script name,
               or declare there isn't a replacement).
        When
            - running is_valid_as_deprecated.

        Then
            - a script with an invalid description will be errored.
        """
        validator = get_validator(current_file=current)
        assert validator.is_valid_as_deprecated() is answer

    def test_name_contains_the_type(self, pack):
        """
        Given
            - An script with a name that contains the word "script".
        When
            - running name_not_contain_the_type.
        Then
            - Ensure the validate failed.
        """

        script = pack.create_script(yml={"name": "test_script"})

        with ChangeCWD(pack.repo_path):
            structure_validator = StructureValidator(script.yml.path)
            validator = ScriptValidator(structure_validator)

            assert not validator.name_not_contain_the_type()

    def test_name_does_not_contains_the_type(self, pack):
        """
        Given
            - An script with a name that does not contains the "script" string.
        When
            - running name_not_contain_the_type.
        Then
            - Ensure the validate passes.
        """

        script = pack.create_script(yml={"name": "test"})

        structure_validator = StructureValidator(script.yml.path)
        validator = ScriptValidator(structure_validator)
        assert validator.name_not_contain_the_type()

    def test_runas_is_dbtrole(self, pack):
        """
        Given
            - A script with runas = DBotRole.
        When
            - running runas_is_not_dbtrole.
        Then
            - Ensure the validate failed.
        """

        script = pack.create_script(yml={"runas": "DBotRole"})

        with ChangeCWD(pack.repo_path):
            structure_validator = StructureValidator(script.yml.path)
            validator = ScriptValidator(structure_validator)

            assert not validator.runas_is_not_dbtrole()

    def test_runas_is_not_dbtrole(self, pack):
        """
        Given
            - A script without runas.
        When
            - running runas_is_not_dbtrole.
        Then
            - Ensure the validate passes.
        """

        script = pack.create_script(yml={})

        with ChangeCWD(pack.repo_path):
            structure_validator = StructureValidator(script.yml.path)
            validator = ScriptValidator(structure_validator)

            assert validator.runas_is_not_dbtrole()

    README_TEST_DATA = [
        (True, False, False),
        (False, False, True),
        (False, True, True),
        (True, True, True),
    ]

    @pytest.mark.parametrize(
        "remove_readme, validate_all, expected_result", README_TEST_DATA
    )
    @pytest.mark.parametrize("unified", [True, False])
    def test_validate_readme_exists(
        self, repo, unified, remove_readme, validate_all, expected_result
    ):
        """
        Given:
            - An integration yml that was added or modified to validate

        When:
              All the tests occur twice for unified integrations = [True - False]
            - The integration is missing a readme.md file in the same folder
            - The integration has a readme.md file in the same folder
            - The integration is missing a readme.md file in the same folder but has not been changed or added
                (This check is for backward compatibility)

        Then:
            - Ensure readme exists and validation fails
            - Ensure readme exists and validation passes
            - Ensure readme exists and validation passes
        """
        read_me_pack = repo.create_pack("README_test")
        script = read_me_pack.create_script("script1", create_unified=unified)

        structure_validator = StructureValidator(script.yml.path)
        script_validator = ScriptValidator(
            structure_validator, validate_all=validate_all
        )
        if remove_readme:
            Path(script.readme.path).unlink()
        assert (
            script_validator.validate_readme_exists(script_validator.validate_all)
            is expected_result
        )

    @pytest.mark.parametrize(
        "script_yml, is_validation_ok",
        [
            ({"nativeimage": "test", "commonfields": {"id": "test"}}, False),
            ({"commonfields": {"id": "test"}}, True),
        ],
    )
    def test_is_native_image_does_not_exist_in_yml_fail(
        self, repo, script_yml, is_validation_ok
    ):
        """
        Given:
            - Case A: script yml that has the nativeimage key
            - Case B: script yml that does not have the nativeimage key
        When:
            - when executing the is_native_image_does_not_exist_in_yml method
        Then:
            - Case A: make sure the validation fails.
            - Case B: make sure the validation pass.
        """
        pack = repo.create_pack("test")
        script = pack.create_script(yml=script_yml)
        structure_validator = StructureValidator(script.yml.path)
        integration_validator = ScriptValidator(structure_validator)

        assert (
            integration_validator.is_nativeimage_key_does_not_exist_in_yml()
            == is_validation_ok
        )

    @pytest.mark.parametrize(
        "yml_content, use_git, expected_results",
        [
            ({"comment": "description without dot"}, False, True),
            (
                {
                    "comment": "a yml comment with a dot at the end.",
                    "args": [
                        {"name": "test_arg", "description": "description without dot"}
                    ],
                },
                True,
                False,
            ),
            (
                {
                    "comment": "a yml comment with a dot at the end.",
                    "outputs": [
                        {
                            "contextPath": "test.path",
                            "description": "description without dot",
                        }
                    ],
                },
                True,
                False,
            ),
            (
                {
                    "comment": "a yml comment with a dot at the end.",
                    "args": [
                        {"name": "test_arg", "description": "description with a dot."}
                    ],
                },
                True,
                True,
            ),
            (
                {
                    "comment": "a yml comment with a dot at the end.",
                    "outputs": [
                        {
                            "contextPath": "test.path",
                            "description": "description without dot.",
                        }
                    ],
                },
                True,
                True,
            ),
            (
                {"comment": "a yml with url and no dot at the end www.test.com"},
                True,
                True,
            ),
            (
                {
                    "comment": "a yml with a comment that has www.test.com in the middle of the sentence"
                },
                True,
                False,
            ),
            (
                {
                    "comment": "a yml with a comment that has an 'example without dot at the end of the string.'",
                },
                True,
                False,
            ),
        ],
    )
    def test_is_line_ends_with_dot(
        self, repo, yml_content: dict, use_git: bool, expected_results: bool
    ):
        """
        Given:
            A yml content, use_git flag, and expected_results.
            - Case 1: A yml content with a comment without a dot at the end of the sentence, and use_git flag set to False.
            - Case 2: A yml content with an argument with a description without a dot at the end of the sentence, and use_git flag set to True.
            - Case 3: A yml content with a context path with a description without a dot at the end of the sentence, and use_git flag set to True.
            - Case 4: A yml content with an argument with a description with a dot at the end of the sentence, and use_git flag set to True.
            - Case 5: A yml content with a context path with a description with a dot at the end of the sentence, and use_git flag set to True.
            - Case 6: A yml content with a comment that ends with a url address and not dot, and use_git flag set to True.
            - Case 7: A yml content with a comment that has a url in the middle of the sentence and no comment in the end, and use_git flag set to True.
            - Case 8: A yml content with a comment that ends with example quotes with a dot only inside the example quotes, and use_git flag set to True.
        When:
            - when executing the is_line_ends_with_dot method
        Then:
            - Case 1: make sure the validation pass.
            - Case 2: make sure the validation fails.
            - Case 3: make sure the validation fails.
            - Case 4: make sure the validation pass.
            - Case 5: make sure the validation pass.
            - Case 6: make sure the validation pass.
            - Case 7: make sure the validation fails.
            - Case 8: make sure the validation fails.
        """
        pack = repo.create_pack("test")
        script = pack.create_script(yml=yml_content)
        structure_validator = StructureValidator(script.yml.path)
        script_validator = ScriptValidator(structure_validator, using_git=use_git)
        assert script_validator.is_line_ends_with_dot() is expected_results
