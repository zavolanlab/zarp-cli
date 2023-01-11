"""Handle initialization mode."""

from enum import Enum
from json import JSONDecodeError
import logging
from os.path import expandvars
from pathlib import Path
import sys
from typing import (
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

import jsonref  # type: ignore
from pydantic import (  # pylint: disable=E0611
    BaseModel,
    ValidationError,
)
from yaml import (
    safe_dump,
    YAMLError,
)

from zarp.config import enums
from zarp.config.models import InitConfig
from zarp.config.parser import ConfigParser

LOGGER = logging.getLogger(__name__)


class Initializer:
    """Handler for app initialization.

    Attributes:
        config: Configuration model instance.
    """

    def __init__(self) -> None:
        """Class constructor."""
        self.config: InitConfig = InitConfig()

    def set_from_file(self, config_file: Path) -> None:
        """Set configuration based on configuration file contents.

        Args:
            config_file: Path to YAML file containing the initialization
                configuration.

        Raises:
            ValueError: Contents are not valid YAML.
        """
        if config_file.is_file():
            config_dict = ConfigParser.parse_yaml(path=config_file)
            try:
                self.config = InitConfig(**config_dict)
            except (TypeError, ValidationError) as exc:
                raise ValueError(
                    "configuration file contains invalid arguments: "
                    f"{config_file}"
                ) from exc

    def set_from_user_input(self):  # pylint: disable=R0912,R0915
        """Update configuration based on user input."""
        sys.stdout.write(
            """
Please enter an argument for each parameter or accept the default (in brackets)
by pressing <ENTER>. Refer to the documentation to find out what a given
parameter means.

For parameters that accept only particular arguments, valid choices are listed
in braces.

If you do not want to provide a default, enter 'None', but note that in these
cases, ZARP-cli may fall back to system defaults to ensure flawless operation.

Parameters for which you can supply multiple values are marked with an
asterisk. For these, the query will be repeated until you press <ENTER> without
having entered a value. Make sure to enter only _one_ value per query.

"""
        )
        schema_full = jsonref.loads(InitConfig.schema_json())
        for config_group in schema_full["properties"]:  # type: ignore
            for param, default in getattr(self.config, config_group):
                schema = schema_full["properties"][  # type: ignore
                    config_group
                ]["allOf"][0]["properties"][
                    param
                ]  # type: ignore
                choices: List = []
                user_inputs: List = []
                default = self._format_default(value=default)
                param_type, param_class, item_type = self._get_param_type(
                    schema=schema,  # type: ignore
                )
                if param_class is not None and (
                    param_type == "enum" or item_type == "enum"
                ):
                    choices = [item.value for item in param_class]
                prompt = self._generate_prompt(
                    param=param,
                    default=default,
                    choices=choices,
                    multi=param_type == "array",
                )
                while True:
                    sys.stdout.write(prompt)
                    # handle user input
                    user_input: Optional[
                        Union[float, int, List, Path, str]
                    ] = str(input())
                    # default
                    if user_input == "":
                        user_input = default
                        break
                    # none
                    if user_input == "None":
                        user_input = None
                    # choices
                    elif len(choices) > 0 and user_input not in choices:
                        sys.stdout.write("invalid choice\n")
                        continue
                    # path
                    elif param_type == "path":
                        try:
                            user_input = (
                                Path(expandvars(user_input))
                                .expanduser()
                                .resolve()
                            )
                        except RuntimeError:
                            sys.stdout.write("path could not be resolved\n")
                            continue
                    # array
                    elif param_type == "array":
                        user_inputs.append(user_input)
                        user_input = list(set(user_inputs))
                    # integer
                    elif param_type == "integer":
                        try:
                            user_input = int(user_input)
                        except (TypeError, ValueError):
                            sys.stdout.write("not an integer\n")
                            continue
                    # float
                    elif param_type == "number":
                        try:
                            user_input = float(user_input)
                        except (TypeError, ValueError):
                            sys.stdout.write("not a number\n")
                            continue
                    # update value with user input
                    try:
                        setattr(
                            getattr(self.config, config_group),
                            param,
                            user_input,
                        )
                    except ValidationError:
                        del user_inputs[-1]
                        sys.stdout.write(f"invalid format: {user_input}\n")
                        continue
                    # continue for arrays
                    if param_type == "array":
                        continue
                    break

        LOGGER.debug(f"USER INPUT: {self.config}")

    @staticmethod
    def write_yaml(contents: BaseModel, path: Path) -> None:
        """Write Pydantic model to YAML file.

        Args:
            contents: `:mod:Pydantic` model to be written.
            path: Path to YAML output file.

        Raises:
            OSError: File could not be written.
            ValueError: Contents are not valid YAML.
        """
        if not path.is_file():
            path.parent.absolute().mkdir(
                parents=True,
                exist_ok=True,
            )
        try:
            with open(path, "w", encoding="utf-8") as _file:
                try:
                    safe_dump(jsonref.loads(contents.json()), _file)
                except (JSONDecodeError, YAMLError) as exc:
                    raise ValueError(
                        f"contents are not valid YAML: {contents}"
                    ) from exc
        except OSError as exc:
            raise OSError(f"file could not be written: {path}") from exc

    @staticmethod
    def _get_param_type(
        schema: Mapping,
    ) -> Tuple[Optional[str], Optional[Type[Enum]], Optional[str]]:
        """Return type of property based on schema.

        Only implemented and tested for determining types relevant for this
        class.

        Args:
            schema: Dictionary representation of JSON schema.

        Returns:
            Type name of property as string. Currently supports at least
                the basic types `array`, `integer`, `string`, as well as the
                referenced type `enum`. For the latter, also the class is
                returned. For type `array`, also the type of the items is
                returned. In case these are of type `enum`, the returned class
                refers to the item type. For type `string`, if `format` is set,
                then that is returned.
        """
        _type: Optional[str] = None
        _class: Optional[Type[Enum]] = None
        _type_item: Optional[str] = None
        # basic types
        try:
            _type = schema["format"]
        except KeyError:
            try:
                _type = schema["type"]
            except KeyError:
                pass
        # referenced types
        try:
            ref_props = schema["allOf"][0]
            if "enum" in list(ref_props):
                _type = "enum"
                _class = getattr(enums, ref_props["title"])
        except KeyError:
            pass
        # array item types
        if _type == "array":
            try:
                _type_item = schema["items"]["format"]
            except KeyError:
                try:
                    _type_item = schema["items"]["type"]
                except KeyError:
                    pass
            if "enum" in list(schema["items"]):
                _type_item = "enum"
                _class = getattr(enums, schema["items"]["title"])
        return (_type, _class, _type_item)

    @staticmethod
    def _format_default(
        value: Optional[Union[Enum, int, List, str]],
    ) -> Optional[Union[int, List, str]]:
        """Format default value.

        Args:
            Value to format.

        Returns:
            Formatted default value.
        """
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, list) and len(value) == 0:
            return None
        return value

    @staticmethod
    def _generate_prompt(
        param: str,
        default: Optional[Union[int, List, str]] = None,
        choices: Optional[Sequence[str]] = None,
        multi: bool = False,
    ) -> str:
        """Compile prompt for user input.

        Args:
            param: Name of the query parameter.
            default: Default value of the query parameter.
            choices: List of available options.
            multi: Whether query parameter can be answered multiple times.

        Returns:
            Formatted prompt string.
        """
        if choices is None:
            choices = []
        asterisk = "*" if multi else ""
        choices_clean: str = ""
        param_clean = param.capitalize().replace("_", " ")
        if len(choices) != 0:
            choices_clean = f" {{{','.join(choices)}}}"
        default_clean: str = str(default)
        if isinstance(default, list):
            default_clean = ",".join(default)
        return f"{param_clean} [{default_clean}]{choices_clean}{asterisk}: "
