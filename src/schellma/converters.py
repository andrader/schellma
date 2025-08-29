"""JSON Schema to TypeScript conversion utilities."""

from pydantic import BaseModel

from .constants import (
    DEFAULT_INDENT,
    DEFINITION_SEPARATOR,
    DEFS_PREFIX,
    EMPTY_LINE,
    ENUM_VALUE_TEMPLATE,
    OBJECT_OPEN_BRACE,
    TS_ANY_ARRAY_TYPE,
    TS_ANY_TYPE,
    TS_ARRAY_TEMPLATE,
    TS_INDEX_SIGNATURE_ANY,
    TS_INDEX_SIGNATURE_TEMPLATE,
    TS_NULL_TYPE,
    TS_OBJECT_TYPE,
    TS_TUPLE_TEMPLATE,
    TS_TYPE_MAPPINGS,
    TS_UNION_SEPARATOR,
)
from .exceptions import CircularReferenceError, ConversionError, InvalidSchemaError
from .logging import get_logger

logger = get_logger()


class SchemaConverter:
    """Converts JSON Schema to TypeScript-like type definitions."""

    def __init__(
        self,
        schema: dict,
        define_types: bool = True,
        indent: int | bool | None = DEFAULT_INDENT,
    ):
        """Initialize the converter with schema and configuration.

        Args:
            schema: JSON Schema dictionary
            define_types: If True, define reused types separately
            indent: Indentation configuration
        """
        self.schema = schema
        self.define_types = define_types
        self.indent = indent
        self.type_definitions: list[str] = []
        self.visited_refs: set[str] = set()
        self.ref_stack: set[str] = set()

    def convert(self) -> str:
        """Convert the schema to TypeScript-like type definition.

        Returns:
            A string representation of the TypeScript-like type definition

        Raises:
            InvalidSchemaError: If the schema is invalid or malformed
            ConversionError: If conversion fails for any reason
            CircularReferenceError: If circular references are detected
        """
        logger.debug(
            f"Converting JSON schema to TypeScript (define_types={self.define_types}, indent={self.indent})"
        )

        if not isinstance(self.schema, dict):
            logger.error(f"Invalid schema type: {type(self.schema).__name__}")
            raise InvalidSchemaError(
                f"Schema must be a dictionary, got {type(self.schema).__name__}"
            )

        if not self.schema:
            logger.error("Empty schema provided")
            raise InvalidSchemaError("Schema cannot be empty")

        # Handle definitions if define_types is True
        if self.define_types and "$defs" in self.schema:
            self._process_definitions()

        # Convert main schema
        try:
            main_type = self._convert_json_schema_type(self.schema, 1)
        except CircularReferenceError:
            raise
        except Exception as e:
            raise ConversionError(f"Failed to convert main schema: {e}") from e

        # Combine results
        result_parts = []
        if self.type_definitions:
            result_parts.extend(self.type_definitions)
            result_parts.append(EMPTY_LINE)

        result_parts.append(main_type)
        return DEFINITION_SEPARATOR.join(result_parts)

    def _process_definitions(self) -> None:
        """Process schema definitions when define_types is True."""
        defs = self.schema["$defs"]
        if not isinstance(defs, dict):
            raise InvalidSchemaError("$defs must be a dictionary")

        for def_name, def_schema in defs.items():
            if not isinstance(def_name, str):
                raise InvalidSchemaError(
                    f"Definition name must be a string, got {type(def_name).__name__}"
                )

            if not isinstance(def_schema, dict):
                raise InvalidSchemaError(
                    f"Definition schema for '{def_name}' must be a dictionary"
                )

            if def_schema.get("type") == "object":
                try:
                    self._process_object_definition(def_name, def_schema)
                except Exception as e:
                    raise ConversionError(
                        f"Failed to convert definition '{def_name}': {e}"
                    ) from e

    def _process_object_definition(self, def_name: str, def_schema: dict) -> None:
        """Process an object type definition."""
        _, comment_prefix, property_template, close_brace = _create_indent_formatter(
            self.indent, 1
        )

        lines = [f"{def_name} {{"]
        properties = def_schema.get("properties", {})

        if not isinstance(properties, dict):
            raise ConversionError(
                f"Properties for definition '{def_name}' must be a dictionary"
            )

        for prop_name, prop_schema in properties.items():
            if not isinstance(prop_name, str):
                raise ConversionError(
                    f"Property name must be a string, got {type(prop_name).__name__}"
                )

            # Add description as comment if available
            if "description" in prop_schema and isinstance(
                prop_schema["description"], str
            ):
                lines.append(f"{comment_prefix}{prop_schema['description']}")

            # Convert type
            prop_type = self._convert_json_schema_type(prop_schema, 2)
            lines.append(property_template.format(name=prop_name, type=prop_type))

        lines.append(close_brace)
        self.type_definitions.append("\n".join(lines))

    def _convert_reference(self, json_type: dict, level: int = 1) -> str:
        """Handle $ref (references to definitions)."""
        ref_path = json_type["$ref"]
        if not isinstance(ref_path, str):
            raise ConversionError(
                f"$ref must be a string, got {type(ref_path).__name__}"
            )

        if ref_path.startswith(DEFS_PREFIX):
            type_name = ref_path.replace(DEFS_PREFIX, "")

            # Check for circular references
            if ref_path in self.ref_stack:
                logger.warning(f"Circular reference detected: {ref_path}")
                raise CircularReferenceError(f"Circular reference detected: {ref_path}")

            self.ref_stack.add(ref_path)
            try:
                result = (
                    type_name
                    if self.define_types
                    else self._convert_definition_inline(type_name, level)
                )
                self.visited_refs.add(ref_path)
                return result
            finally:
                self.ref_stack.discard(ref_path)
        else:
            raise ConversionError(f"Unsupported reference format: {ref_path}")

    def _convert_string_type(self, json_type: dict, level: int = 1) -> str:
        """Convert string type, handling enums."""
        if "enum" in json_type:
            enum_values = [
                ENUM_VALUE_TEMPLATE.format(value=val) for val in json_type["enum"]
            ]
            return TS_UNION_SEPARATOR.join(enum_values)
        return TS_TYPE_MAPPINGS["string"]

    def _convert_array_type(self, json_type: dict, level: int = 1) -> str:
        """Convert array type, handling tuples and regular arrays."""
        if "prefixItems" in json_type:
            prefix_items = json_type["prefixItems"]
            if not isinstance(prefix_items, list):
                raise ConversionError("prefixItems must be a list")

            try:
                prefix_types = [
                    self._convert_json_schema_type(item, level) for item in prefix_items
                ]
                return TS_TUPLE_TEMPLATE.format(types=", ".join(prefix_types))
            except Exception as e:
                raise ConversionError(f"Failed to convert tuple items: {e}") from e
        elif "items" in json_type:
            try:
                item_type = self._convert_json_schema_type(json_type["items"], level)
                return TS_ARRAY_TEMPLATE.format(type=item_type)
            except Exception as e:
                raise ConversionError(f"Failed to convert array items: {e}") from e
        return TS_ANY_ARRAY_TYPE

    def _convert_object_type(self, json_type: dict, level: int = 1) -> str:
        """Convert object type, handling properties and additionalProperties."""
        if "properties" in json_type:
            try:
                return self._convert_object_properties(json_type, level)
            except CircularReferenceError:
                raise
            except Exception as e:
                raise ConversionError(
                    f"Failed to convert object properties: {e}"
                ) from e
        elif "additionalProperties" in json_type:
            return self._convert_additional_properties(json_type, level)
        return TS_OBJECT_TYPE

    def _convert_additional_properties(self, json_type: dict, level: int = 1) -> str:
        """Convert additionalProperties to TypeScript index signature."""
        additional_props = json_type["additionalProperties"]
        if additional_props is True:
            return TS_INDEX_SIGNATURE_ANY
        elif isinstance(additional_props, dict):
            try:
                value_type = self._convert_json_schema_type(additional_props, level)
                # Handle multiline object definitions
                if "\n" in value_type and value_type.startswith(OBJECT_OPEN_BRACE):
                    lines = value_type.strip().split("\n")
                    if len(lines) > 1:
                        inner_content = "\n".join(lines[1:-1])
                        return f"{{ [key: string]: {{\n{inner_content}\n  }} }}"

                return TS_INDEX_SIGNATURE_TEMPLATE.format(type=value_type)
            except Exception as e:
                raise ConversionError(
                    f"Failed to convert additionalProperties: {e}"
                ) from e
        else:
            raise ConversionError(
                f"Invalid additionalProperties value: {additional_props}"
            )

    def _convert_union_types(self, json_type: dict, level: int = 1) -> str:
        """Convert anyOf, oneOf union types."""
        if "anyOf" in json_type:
            return self._convert_any_of(json_type["anyOf"], level)
        elif "oneOf" in json_type:
            return self._convert_one_of(json_type["oneOf"], level)
        return TS_ANY_TYPE

    def _convert_any_of(self, any_of_list: list, level: int = 1) -> str:
        """Convert anyOf to TypeScript union type."""
        if not isinstance(any_of_list, list):
            raise ConversionError("anyOf must be a list")

        types = []
        has_null = False
        try:
            for t in any_of_list:
                if not isinstance(t, dict):
                    raise ConversionError("anyOf items must be dictionaries")
                if t.get("type") == "null":
                    has_null = True
                else:
                    types.append(self._convert_json_schema_type(t, level))

            if has_null and len(types) == 1:
                return f"{types[0]}{TS_UNION_SEPARATOR}{TS_NULL_TYPE}"
            elif has_null:
                return TS_UNION_SEPARATOR.join(types + [TS_NULL_TYPE])
            else:
                return TS_UNION_SEPARATOR.join(types)
        except Exception as e:
            raise ConversionError(f"Failed to convert anyOf: {e}") from e

    def _convert_one_of(self, one_of_list: list, level: int = 1) -> str:
        """Convert oneOf to TypeScript union type."""
        if not isinstance(one_of_list, list):
            raise ConversionError("oneOf must be a list")

        try:
            types = [self._convert_json_schema_type(t, level) for t in one_of_list]
            return TS_UNION_SEPARATOR.join(types)
        except Exception as e:
            raise ConversionError(f"Failed to convert oneOf: {e}") from e

    def _convert_json_schema_type(self, json_type: dict, level: int = 1) -> str:
        """Convert a JSON Schema type to TypeScript type."""
        if not isinstance(json_type, dict):
            raise ConversionError(
                f"Type definition must be a dictionary, got {type(json_type).__name__}"
            )

        # Handle $ref (references to definitions)
        if "$ref" in json_type:
            return self._convert_reference(json_type, level)

        # Handle type field
        json_type_name = json_type.get("type")

        if json_type_name == "string":
            return self._convert_string_type(json_type, level)
        elif json_type_name == "integer":
            return TS_TYPE_MAPPINGS["integer"]
        elif json_type_name == "number":
            return TS_TYPE_MAPPINGS["number"]
        elif json_type_name == "boolean":
            return TS_TYPE_MAPPINGS["boolean"]
        elif json_type_name == "array":
            return self._convert_array_type(json_type, level)
        elif json_type_name == "object":
            return self._convert_object_type(json_type, level)
        elif json_type_name is None:
            return self._convert_union_types(json_type, level)

        return TS_ANY_TYPE

    def _convert_object_properties(self, obj_schema: dict, level: int = 1) -> str:
        """Convert object properties to TypeScript object type."""
        if not isinstance(obj_schema, dict):
            raise ConversionError(
                f"Object schema must be a dictionary, got {type(obj_schema).__name__}"
            )

        # Create indentation formatter for this level
        property_indent, comment_prefix, property_template, close_brace = (
            _create_indent_formatter(self.indent, level)
        )

        lines = [OBJECT_OPEN_BRACE]
        properties = obj_schema.get("properties", {})

        if not isinstance(properties, dict):
            raise ConversionError("properties must be a dictionary")

        for prop_name, prop_schema in properties.items():
            if not isinstance(prop_name, str):
                raise ConversionError(
                    f"Property name must be a string, got {type(prop_name).__name__}"
                )

            if not isinstance(prop_schema, dict):
                raise ConversionError(
                    f"Property schema for '{prop_name}' must be a dictionary"
                )

            # Add description as comment if available
            if "description" in prop_schema:
                description = prop_schema["description"]
                if isinstance(description, str):
                    lines.append(f"{comment_prefix}{description}")

            # Convert type
            try:
                prop_type = self._convert_json_schema_type(prop_schema, level + 1)
                lines.append(property_template.format(name=prop_name, type=prop_type))
            except CircularReferenceError:
                raise
            except Exception as e:
                raise ConversionError(
                    f"Failed to convert property '{prop_name}': {e}"
                ) from e

        lines.append(close_brace)
        return "\n".join(lines)

    def _convert_definition_inline(self, def_name: str, level: int = 1) -> str:
        """Convert a definition inline (when define_types=False)."""
        if not isinstance(def_name, str):
            raise ConversionError(
                f"Definition name must be a string, got {type(def_name).__name__}"
            )

        if "$defs" in self.schema:
            defs = self.schema["$defs"]
            if not isinstance(defs, dict):
                raise ConversionError("$defs must be a dictionary")

            if def_name in defs:
                try:
                    return self._convert_json_schema_type(defs[def_name], level)
                except CircularReferenceError:
                    raise
                except Exception as e:
                    raise ConversionError(
                        f"Failed to convert definition '{def_name}': {e}"
                    ) from e

        raise ConversionError(f"Definition '{def_name}' not found in schema")


def _create_indent_formatter(
    indent: int | bool | None, level: int = 1
) -> tuple[str, str, str, str]:
    """Create indentation formatting strings based on indent parameter and nesting level.

    Args:
        indent: Indentation configuration
            - False/None/0: No indentation
            - int: Number of spaces per level (default 2)
        level: Nesting level (1 = top level, 2 = nested, etc.)

    Returns:
        Tuple of (property_indent, comment_prefix, property_template, close_brace)
    """
    if indent is False or indent is None or indent == 0:
        # No indentation - compact format
        return "", "// ", '"{name}": {type},', "}"

    # Use specified number of spaces (default 2)
    base_spaces = indent if isinstance(indent, int) and indent > 0 else DEFAULT_INDENT
    total_spaces = base_spaces * level
    property_indent = " " * total_spaces
    comment_prefix = f"{property_indent}// "
    property_template = f'{property_indent}"{{name}}": {{type}},'

    # Close brace should be at the parent level (one level less indentation)
    close_indent = " " * (base_spaces * (level - 1)) if level > 1 else ""
    close_brace = f"{close_indent}}}"

    return property_indent, comment_prefix, property_template, close_brace


def json_schema_to_llm(
    schema: dict, define_types: bool = True, indent: int | bool | None = DEFAULT_INDENT
) -> str:
    """Convert a JSON Schema to TypeScript-like type definition string.

    Args:
        schema: JSON Schema dictionary from model.model_json_schema()
        define_types: If True, define reused types separately to avoid repetition
        indent: Indentation configuration:
            - False/None/0: No indentation (compact format)
            - int: Number of spaces per indentation level (default: 2)

    Returns:
        A string representation of the TypeScript-like type definition

    Raises:
        InvalidSchemaError: If the schema is invalid or malformed
        ConversionError: If conversion fails for any reason
        CircularReferenceError: If circular references are detected
    """
    converter = SchemaConverter(schema, define_types, indent)
    return converter.convert()


def pydantic_to_llm(
    model_class: type[BaseModel],
    define_types: bool = False,
    indent: int | bool | None = DEFAULT_INDENT,
) -> str:
    """Convert a Pydantic model to a TypeScript-like type definition string.

    Args:
        model_class: A Pydantic BaseModel class
        define_types: If True, define reused types separately to avoid repetition
        indent: Indentation configuration:
            - False/None/0: No indentation (compact format)
            - int: Number of spaces per indentation level (default: 2)

    Returns:
        A string representation of the TypeScript-like type definition

    Raises:
        InvalidSchemaError: If the model is invalid
        ConversionError: If conversion fails for any reason
        CircularReferenceError: If circular references are detected
    """
    logger.debug(
        f"Converting Pydantic model {getattr(model_class, '__name__', str(model_class))} to TypeScript"
    )

    if not isinstance(model_class, type):
        logger.error(f"Invalid model class type: {type(model_class).__name__}")
        raise InvalidSchemaError(
            f"model_class must be a class, got {type(model_class).__name__}"
        )

    # Check if it's a BaseModel subclass
    try:
        if not issubclass(model_class, BaseModel):
            raise InvalidSchemaError(
                f"model_class must be a BaseModel subclass, got {model_class.__name__}"
            )
    except TypeError as e:
        raise InvalidSchemaError(
            f"model_class must be a class, got {type(model_class).__name__}"
        ) from e

    try:
        schema = model_class.model_json_schema()
    except Exception as e:
        raise InvalidSchemaError(
            f"Failed to generate JSON schema from model: {e}"
        ) from e

    return json_schema_to_llm(schema, define_types, indent)


def to_llm(
    obj: dict | type[BaseModel],
    define_types: bool = False,
    indent: int | bool | None = DEFAULT_INDENT,
) -> str:
    """Convert a JSON Schema dictionary or Pydantic model to a TypeScript-like type definition string.

    Args:
        obj: A JSON Schema dictionary or Pydantic model
        define_types: If True, define reused types separately to avoid repetition
        indent: Indentation configuration:
            - False/None/0: No indentation (compact format)
            - int: Number of spaces per indentation level (default: 2)

    Returns:
        A string representation of the TypeScript-like type definition

    Raises:
        InvalidSchemaError: If the model is invalid
        ConversionError: If conversion fails for any reason
        CircularReferenceError: If circular references are detected
    """
    if isinstance(obj, type) and issubclass(obj, BaseModel):
        return pydantic_to_llm(obj, define_types, indent)
    elif isinstance(obj, dict):
        return json_schema_to_llm(obj, define_types, indent)
    else:
        raise InvalidSchemaError(f"Invalid object type: {type(obj).__name__}")
