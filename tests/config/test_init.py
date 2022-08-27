"""Unit tests for ``:mod:zarp.config.init``."""

from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
)

import jsonref
from pydantic import (
    BaseModel,
    EmailStr,
)
import pytest

from tests.utils import (
    MultiMocker,
    RaiseError,
)
from zarp.config.enums import (
    OutputFileGroups,
    ExecModes,
)
from zarp.config.init import Initializer
from zarp.config.models import InitConfig


class TestInitializer:
    """Test ``cls:zarp.config.init.Initializer`` class."""

    def test_init(self):
        """Test class initialization."""
        initializer = Initializer()
        assert hasattr(initializer, "config")

    def test_set_from_file_valid(self, tmpdir):
        """Test method `.set_from_file()` with valid file."""
        initializer: Initializer = Initializer()
        exec_mode_before_update: Optional[
            ExecModes
        ] = initializer.config.run.execution_mode
        config_file: Path = Path(tmpdir / "config_file")
        test_config: InitConfig = InitConfig()
        test_config.run.execution_mode = ExecModes.DRY_RUN
        initializer.write_yaml(
            contents=test_config,
            path=config_file,
        )
        initializer.set_from_file(config_file=config_file)
        assert exec_mode_before_update == ExecModes.RUN
        assert initializer.config.run.execution_mode == ExecModes.DRY_RUN.value

    def test_set_from_file_invalid(self, tmpdir):
        """Test method `.set_from_file()` with invalid file."""
        initializer: Initializer = Initializer()
        config_file: Path = Path(tmpdir / "config_file")
        with open(config_file, "w", encoding="utf-8") as _file:
            _file.write("INVALID")
        with pytest.raises(ValueError):
            initializer.set_from_file(config_file=config_file)

    def test_set_from_user_input_use_defaults(self, monkeypatch):
        """Test method `.set_from_user_input()` with default inputs."""
        initializer: Initializer = Initializer()
        monkeypatch.setattr("builtins.input", lambda: "")
        initializer.set_from_user_input()

    def test_set_from_user_input_string(self, monkeypatch):
        """Test method `.set_from_user_input()` with string input."""

        class InitUser(BaseModel):
            author: str = "author"

        class InitConfig(BaseModel):
            user: InitUser = InitUser()

        schema: Dict = jsonref.loads(InitConfig().schema_json())
        initializer: Initializer = Initializer()
        monkeypatch.setattr("jsonref.loads", lambda *args: schema)
        monkeypatch.setattr("builtins.input", lambda: "new_author")
        setattr(initializer, "config", InitConfig())
        initializer.set_from_user_input()
        assert initializer.config.user.author == "new_author"

    def test_set_from_user_input_none(self, monkeypatch):
        """Test method `.set_from_user_input()` with input `None`."""

        class InitUser(BaseModel):
            author: str = "author"

        class InitConfig(BaseModel):
            user: InitUser = InitUser()

        schema: Dict = jsonref.loads(InitConfig().schema_json())
        initializer: Initializer = Initializer()
        monkeypatch.setattr("jsonref.loads", lambda *args: schema)
        monkeypatch.setattr("builtins.input", lambda: "None")
        setattr(initializer, "config", InitConfig())
        initializer.set_from_user_input()
        assert initializer.config.user.author is None

    def test_set_from_user_input_choices(self, monkeypatch):
        """Test method `.set_from_user_input()` with input choices."""

        class InitRun(BaseModel):
            execution_mode: ExecModes = ExecModes.RUN

        class InitConfig(BaseModel):
            run: InitRun = InitRun()

        mocker: MultiMocker = MultiMocker(
            [
                "NOT_VALID",
                "DRY_RUN",
            ]
        )
        schema: Dict = jsonref.loads(InitConfig().schema_json())
        initializer: Initializer = Initializer()
        monkeypatch.setattr("jsonref.loads", lambda *args: schema)
        monkeypatch.setattr("builtins.input", mocker)
        setattr(initializer, "config", InitConfig())
        initializer.set_from_user_input()
        assert initializer.config.run.execution_mode == "DRY_RUN"

    def test_set_from_user_input_path(self, tmpdir, monkeypatch):
        """Test method `.set_from_user_input()` with path input."""

        class InitRun(BaseModel):
            working_directory: Path = Path.cwd()

        class InitConfig(BaseModel):
            run: InitRun = InitRun()

        mocker: MultiMocker = MultiMocker(
            [
                f"~{Path(tmpdir).name}",
                "$HOME",
            ]
        )
        schema: Dict = jsonref.loads(InitConfig().schema_json())
        initializer: Initializer = Initializer()
        monkeypatch.setattr("jsonref.loads", lambda *args: schema)
        monkeypatch.setattr("builtins.input", mocker)
        setattr(initializer, "config", InitConfig())
        initializer.set_from_user_input()
        assert initializer.config.run.working_directory == Path.home()

    def test_set_from_user_input_array(self, tmpdir, monkeypatch):
        """Test method `.set_from_user_input()` with array input."""

        class InitUser(BaseModel):
            affiliations: List[str] = ["affiliation"]

        class InitConfig(BaseModel):
            user: InitUser = InitUser()

        mocker: MultiMocker = MultiMocker(
            [
                "affiliation_1",
                "affiliation_2",
                "affiliation_2",
                "",
            ]
        )
        schema: Dict = jsonref.loads(InitConfig().schema_json())
        initializer: Initializer = Initializer()
        monkeypatch.setattr("jsonref.loads", lambda *args: schema)
        monkeypatch.setattr("builtins.input", mocker)
        setattr(initializer, "config", InitConfig())
        initializer.set_from_user_input()
        config = initializer.config.user
        assert "affiliation_1" in config.affiliations  # type: ignore
        assert "affiliation_2" in config.affiliations  # type: ignore
        assert len(config.affiliations) == 2  # type: ignore

    def test_set_from_user_input_integer(self, monkeypatch):
        """Test method `.set_from_user_input()` with integer input."""

        class InitRun(BaseModel):
            cores: int = 1

        class InitConfig(BaseModel):
            run: InitRun = InitRun()

        mocker: MultiMocker = MultiMocker(
            [
                "NOT_INT",
                "4",
            ]
        )
        schema: Dict = jsonref.loads(InitConfig().schema_json())
        initializer: Initializer = Initializer()
        monkeypatch.setattr("jsonref.loads", lambda *args: schema)
        monkeypatch.setattr("builtins.input", mocker)
        setattr(initializer, "config", InitConfig())
        initializer.set_from_user_input()
        assert initializer.config.run.cores == 4

    def test_set_from_user_input_float(self, monkeypatch):
        """Test method `.set_from_user_input()` with float input."""

        class InitSample(BaseModel):
            fragment_length_distribution_mean: float = 500.0

        class InitConfig(BaseModel):
            sample: InitSample = InitSample()

        mocker: MultiMocker = MultiMocker(
            [
                "NOT_FLOAT",
                "3.0",
            ]
        )
        schema: Dict = jsonref.loads(InitConfig().schema_json())
        initializer: Initializer = Initializer()
        monkeypatch.setattr("jsonref.loads", lambda *args: schema)
        monkeypatch.setattr("builtins.input", mocker)
        setattr(initializer, "config", InitConfig())
        initializer.set_from_user_input()
        assert (
            initializer.config.sample.fragment_length_distribution_mean == 3.0
        )

    def test_set_from_user_input_format_str(self, tmpdir, monkeypatch):
        """Test method `.set_from_user_input()` with formatted string input."""

        class InitUser(BaseModel):
            emails: Optional[List[EmailStr]] = None

            class Config:
                validate_assignment = True

        class InitConfig(BaseModel):
            user: InitUser = InitUser()

        mocker: MultiMocker = MultiMocker(
            [
                "email_1@some.org",
                "NOT_EMAIL",
                "email_2@some.org",
                "",
            ]
        )
        schema = jsonref.loads(InitConfig().schema_json())
        initializer: Initializer = Initializer()
        monkeypatch.setattr("jsonref.loads", lambda *args: schema)
        monkeypatch.setattr("builtins.input", mocker)
        setattr(initializer, "config", InitConfig())
        initializer.set_from_user_input()
        config = initializer.config.user
        assert "email_1@some.org" in config.emails  # type: ignore
        assert "email_2@some.org" in config.emails  # type: ignore
        assert len(config.emails) == 2  # type: ignore

    def test_write_yaml_valid_yaml(self, tmpdir):
        """Test method `.write_yaml()` with valid YAML contents."""
        initializer: Initializer = Initializer()
        config_file: Path = Path(tmpdir / "config_file")
        Initializer.write_yaml(
            contents=initializer.config,
            path=config_file,
        )
        assert config_file.is_file()

    def test_write_yaml_invalid_yaml(self, monkeypatch, tmpdir):
        """Test method `.write_yaml()` with invalid YAML contents."""
        config_file: Path = Path(tmpdir / "config_file")
        monkeypatch.setattr("pydantic.BaseModel.json", lambda _: "not_json")
        with pytest.raises(ValueError):
            Initializer.write_yaml(
                contents=InitConfig(),
                path=config_file,
            )

    def test_write_yaml_not_writable(self, monkeypatch, tmpdir):
        """Test method `.write_yaml()` when output file is not writable."""
        config_file: Path = Path(tmpdir / "config_file")
        monkeypatch.setattr("builtins.open", RaiseError(exc=OSError))
        with pytest.raises(OSError):
            Initializer.write_yaml(
                contents=InitConfig(),
                path=config_file,
            )

    def test_get_param_type_basic(self):
        """Test method `._get_param_type()` with basic type."""
        group: str = "run"
        param: str = "cores"
        schema: Dict = jsonref.loads(InitConfig.schema_json())["properties"][
            group
        ]["allOf"][0]["properties"][param]
        ret = Initializer._get_param_type(schema=schema)
        assert ret[0] == "integer"
        assert ret[1] is None
        assert ret[2] is None

    def test_get_param_type_basic_format(self):
        """Test method `._get_param_type()` with formatted string."""
        group: str = "user"
        param: str = "emails"
        schema: Dict = jsonref.loads(InitConfig.schema_json())["properties"][
            group
        ]["allOf"][0]["properties"][param]["items"]
        ret = Initializer._get_param_type(schema=schema)
        assert ret[0] == "email"
        assert ret[1] is None
        assert ret[2] is None

    def test_get_param_type_referenced(self):
        """Test method `._get_param_type()` with referenced type."""
        group: str = "run"
        param: str = "execution_mode"
        schema: Dict = jsonref.loads(InitConfig.schema_json())["properties"][
            group
        ]["allOf"][0]["properties"][param]
        ret = Initializer._get_param_type(schema=schema)
        assert ret[0] == "enum"
        assert ret[1] == ExecModes
        assert ret[2] is None

    def test_get_param_type_array(self):
        """Test method `._get_param_type()` with array."""
        group: str = "user"
        param: str = "affiliations"
        schema: Dict = jsonref.loads(InitConfig.schema_json())["properties"][
            group
        ]["allOf"][0]["properties"][param]
        ret = Initializer._get_param_type(schema=schema)
        assert ret[0] == "array"
        assert ret[1] is None
        assert ret[2] == "string"

    def test_get_param_type_array_format(self):
        """Test method `._get_param_type()` with array of formatted strings."""
        group: str = "user"
        param: str = "emails"
        schema: Dict = jsonref.loads(InitConfig.schema_json())["properties"][
            group
        ]["allOf"][0]["properties"][param]
        ret = Initializer._get_param_type(schema=schema)
        assert ret[0] == "array"
        assert ret[1] is None
        assert ret[2] == "email"

    def test_get_param_type_array_enum(self):
        """Test method `._get_param_type()` with array of enums."""
        group: str = "run"
        param: str = "cleanup_strategy"
        schema: Dict = jsonref.loads(InitConfig.schema_json())["properties"][
            group
        ]["allOf"][0]["properties"][param]
        ret = Initializer._get_param_type(schema=schema)
        assert ret[0] == "array"
        assert ret[1] == OutputFileGroups
        assert ret[2] == "enum"

    def test_format_default_int(self):
        """Test method `._format_default()` with basic type."""
        ret = Initializer._format_default(value=0)
        assert ret == 0

    def test_format_default_enum(self):
        """Test method `._format_default()` with enum."""
        ret = Initializer._format_default(value=ExecModes.RUN)
        assert ret == "RUN"

    def test_format_default_empty_list(self):
        """Test method `._format_default()` with empty list."""
        ret = Initializer._format_default(value=[])
        assert ret is None

    def test_generate_prompt_only_param(self):
        """Test method `._generate_prompt()` with only parameter passed."""
        param: str = "my_param"
        ret = Initializer._generate_prompt(param=param)
        assert ret == "My param [None]: "

    def test_generate_prompt_default(self):
        """Test method `._generate_prompt()` with default passed."""
        param: str = "my_param"
        default: str = "my_value"
        ret = Initializer._generate_prompt(param=param, default=default)
        assert ret == "My param [my_value]: "

    def test_generate_prompt_choices(self):
        """Test method `._generate_prompt()` with choices passed."""
        param: str = "my_param"
        choices: List[str] = ["val_1", "val_2"]
        ret = Initializer._generate_prompt(param=param, choices=choices)
        assert ret == "My param [None] {val_1,val_2}: "

    def test_generate_prompt_multi(self):
        """Test method `._generate_prompt()` for multi query."""
        param: str = "my_param"
        multi: bool = True
        ret = Initializer._generate_prompt(param=param, multi=multi)
        assert ret == "My param [None]*: "

    def test_generate_prompt_all_args(self):
        """Test method `._generate_prompt()` with all arguments passed."""
        param: str = "my_param"
        default: str = "my_value"
        choices: List[str] = ["val_1", "val_2"]
        multi: bool = True
        ret = Initializer._generate_prompt(
            param=param,
            default=default,
            choices=choices,
            multi=multi,
        )
        assert ret == "My param [my_value] {val_1,val_2}*: "
