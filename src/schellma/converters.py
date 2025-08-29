"""JSON Schema to ScheLLMa conversion utilities."""

from typing import Any

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
from .logger import get_logger

logger = get_logger()


class SchemaConverter:
    """Converts JSON Schema to ScheLLMa type definitions."""

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
        """Convert the schema to ScheLLMa type definition.

        Returns:
            A string representation of the ScheLLMa type definition

        Raises:
            InvalidSchemaError: If the schema is invalid or malformed
            ConversionError: If conversion fails for any reason
            CircularReferenceError: If circular references are detected
        """
        logger.debug(
            f"Converting JSON schema to ScheLLMa (define_types={self.define_types}, indent={self.indent})"
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
        required_fields = set(def_schema.get("required", []))

        if not isinstance(properties, dict):
            raise ConversionError(
                f"Properties for definition '{def_name}' must be a dictionary"
            )

        for prop_name, prop_schema in properties.items():
            if not isinstance(prop_name, str):
                raise ConversionError(
                    f"Property name must be a string, got {type(prop_name).__name__}"
                )

            # Build comment with description and default value
            comment_parts = []

            # Add description if available
            if "description" in prop_schema and isinstance(
                prop_schema["description"], str
            ):
                comment_parts.append(prop_schema["description"])

            # Add default value if available
            if "default" in prop_schema:
                default_value = self._format_default_value(prop_schema["default"])
                comment_parts.append(f"default: {default_value}")

            # Add constraints if available
            constraints = self._format_constraints(prop_schema)
            if constraints:
                comment_parts.extend(constraints)

            # Add examples if available
            examples = self._format_examples(prop_schema)
            if examples:
                comment_parts.append(examples)

            # Add required/optional status
            is_required = prop_name in required_fields
            if is_required:
                comment_parts.append("required")
            else:
                comment_parts.append("optional")

            # Add combined comment if we have any parts
            if comment_parts:
                lines.append(f"{comment_prefix}{', '.join(comment_parts)}")

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
        """Convert array type, handling tuples, regular arrays, and contains constraints."""
        # Handle tuple types with prefixItems
        if "prefixItems" in json_type:
            prefix_items = json_type["prefixItems"]
            if not isinstance(prefix_items, list):
                raise ConversionError("prefixItems must be a list")

            try:
                prefix_types = [
                    self._convert_json_schema_type(item, level) for item in prefix_items
                ]

                # Check if there are additional items allowed
                if "items" in json_type:
                    additional_type = self._convert_json_schema_type(
                        json_type["items"], level
                    )
                    # For tuples with additional items, show as tuple with spread
                    tuple_base = TS_TUPLE_TEMPLATE.format(types=", ".join(prefix_types))
                    return f"{tuple_base[:-1]}, ...{additional_type}[]]"
                else:
                    return TS_TUPLE_TEMPLATE.format(types=", ".join(prefix_types))
            except Exception as e:
                raise ConversionError(f"Failed to convert tuple items: {e}") from e

        # Handle regular arrays with items
        elif "items" in json_type:
            try:
                item_type = self._convert_json_schema_type(json_type["items"], level)
                return TS_ARRAY_TEMPLATE.format(type=item_type)
            except Exception as e:
                raise ConversionError(f"Failed to convert array items: {e}") from e

        # Handle arrays with contains constraint but no items
        elif "contains" in json_type:
            try:
                contains_type = self._convert_json_schema_type(
                    json_type["contains"], level
                )
                return TS_ARRAY_TEMPLATE.format(type=contains_type)
            except Exception:
                # Fallback to any[] if contains conversion fails
                return TS_ANY_ARRAY_TYPE

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
        """Convert additionalProperties to ScheLLMa index signature."""
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
        """Convert anyOf, oneOf, allOf union types."""
        if "anyOf" in json_type:
            return self._convert_any_of(json_type["anyOf"], level)
        elif "oneOf" in json_type:
            discriminator = json_type.get("discriminator")
            if discriminator is not None and not isinstance(discriminator, dict):
                discriminator = None
            return self._convert_one_of(json_type["oneOf"], level, discriminator)
        elif "allOf" in json_type:
            return self._convert_all_of(json_type["allOf"], level)
        return TS_ANY_TYPE

    def _convert_any_of(self, any_of_list: list, level: int = 1) -> str:
        """Convert anyOf to ScheLLMa union type."""
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

    def _convert_one_of(
        self, one_of_list: list, level: int = 1, discriminator: dict | None = None
    ) -> str:
        """Convert oneOf to ScheLLMa union type with optional discriminator support."""
        if not isinstance(one_of_list, list):
            raise ConversionError("oneOf must be a list")

        try:
            types = []
            for t in one_of_list:
                converted_type = self._convert_json_schema_type(t, level)

                # Add discriminator information if available
                if discriminator and "$ref" in t:
                    ref_name = t["$ref"].replace("#/$defs/", "")
                    property_name = discriminator.get("propertyName", "type")
                    mapping = discriminator.get("mapping", {})

                    # Find the discriminator value for this type
                    discriminator_value = None
                    for value, ref_path in mapping.items():
                        if ref_path.endswith(ref_name):
                            discriminator_value = value
                            break

                    if discriminator_value:
                        # Add comment about the discriminator
                        converted_type = f'{converted_type} // {property_name}: "{discriminator_value}"'

                types.append(converted_type)

            return TS_UNION_SEPARATOR.join(types)
        except Exception as e:
            raise ConversionError(f"Failed to convert oneOf: {e}") from e

    def _convert_all_of(self, all_of_list: list, level: int = 1) -> str:
        """Convert allOf to ScheLLMa intersection-like type."""
        if not isinstance(all_of_list, list):
            raise ConversionError("allOf must be a list")

        try:
            # For allOf, we need to merge all the schemas into one object
            merged_properties = {}
            merged_required = set()
            descriptions = []

            for schema in all_of_list:
                if not isinstance(schema, dict):
                    raise ConversionError("allOf items must be dictionaries")

                # Collect properties from each schema
                if "properties" in schema:
                    merged_properties.update(schema["properties"])

                # Collect required fields
                if "required" in schema:
                    merged_required.update(schema["required"])

                # Collect descriptions for the intersection comment
                if "description" in schema:
                    descriptions.append(schema["description"])

            # Create a merged schema
            merged_schema = {
                "type": "object",
                "properties": merged_properties,
                "required": list(merged_required),
            }

            # Convert the merged schema
            result = self._convert_object_type(merged_schema, level)

            # Add intersection comment if we have descriptions
            if descriptions:
                intersection_comment = f"// Intersection of: {', '.join(descriptions)}"
                lines = result.split("\n")
                lines.insert(1, f"  {intersection_comment}")
                result = "\n".join(lines)

            return result

        except Exception as e:
            raise ConversionError(f"Failed to convert allOf: {e}") from e

    def _convert_json_schema_type(self, json_type: dict, level: int = 1) -> str:
        """Convert a JSON Schema type to ScheLLMa type."""
        if not isinstance(json_type, dict):
            raise ConversionError(
                f"Type definition must be a dictionary, got {type(json_type).__name__}"
            )

        # Handle $ref (references to definitions)
        if "$ref" in json_type:
            return self._convert_reference(json_type, level)

        # Handle union types first (allOf, anyOf, oneOf) before checking type
        if any(key in json_type for key in ["allOf", "anyOf", "oneOf"]):
            return self._convert_union_types(json_type, level)

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
        """Convert object properties to ScheLLMa object type."""
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
        required_fields = set(obj_schema.get("required", []))

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

            # Build comment with description and default value
            comment_parts = []

            # Add description if available
            if "description" in prop_schema:
                description = prop_schema["description"]
                if isinstance(description, str):
                    comment_parts.append(description)

            # Add default value if available
            if "default" in prop_schema:
                default_value = self._format_default_value(prop_schema["default"])
                comment_parts.append(f"default: {default_value}")

            # Add constraints if available
            constraints = self._format_constraints(prop_schema)
            if constraints:
                comment_parts.extend(constraints)

            # Add examples if available
            examples = self._format_examples(prop_schema)
            if examples:
                comment_parts.append(examples)

            # Add required/optional status
            is_required = prop_name in required_fields
            if is_required:
                comment_parts.append("required")
            else:
                comment_parts.append("optional")

            # Add combined comment if we have any parts
            if comment_parts:
                lines.append(f"{comment_prefix}{', '.join(comment_parts)}")

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

    def _format_default_value(self, default_value: Any) -> str:
        """Format default value for human-readable display in comments.

        Args:
            default_value: The default value from the JSON schema

        Returns:
            A formatted string representation of the default value
        """
        if default_value is None:
            return "null"
        elif isinstance(default_value, bool):
            return "true" if default_value else "false"
        elif isinstance(default_value, str):
            return f'"{default_value}"'
        elif isinstance(default_value, int | float):
            return str(default_value)
        elif isinstance(default_value, list):
            if not default_value:
                return "[]"
            # Format list items
            formatted_items = [
                self._format_default_value(item) for item in default_value
            ]
            return f"[{', '.join(formatted_items)}]"
        elif isinstance(default_value, dict):
            if not default_value:
                return "{}"
            # Format dict items
            formatted_items = [
                f'"{key}": {self._format_default_value(value)}'
                for key, value in default_value.items()
            ]
            return f"{{ {', '.join(formatted_items)} }}"
        else:
            # Fallback for other types
            return str(default_value)

    def _format_constraints(self, schema: dict) -> list[str]:
        """Format field constraints for human-readable display in comments.

        Args:
            schema: The property schema dictionary

        Returns:
            A list of formatted constraint strings
        """
        constraints = []

        # Handle anyOf/oneOf unions (like nullable types with constraints)
        if "anyOf" in schema:
            # Look for constraints in the non-null type
            for any_of_item in schema["anyOf"]:
                if any_of_item.get("type") != "null":
                    # Recursively get constraints from the non-null type
                    sub_constraints = self._format_constraints(any_of_item)
                    constraints.extend(sub_constraints)
            return constraints
        elif "oneOf" in schema:
            # Similar handling for oneOf
            for one_of_item in schema["oneOf"]:
                if one_of_item.get("type") != "null":
                    sub_constraints = self._format_constraints(one_of_item)
                    constraints.extend(sub_constraints)
            return constraints

        # String constraints
        if schema.get("type") == "string":
            # Length constraints
            if "minLength" in schema and "maxLength" in schema:
                constraints.append(
                    f"length: {schema['minLength']}-{schema['maxLength']}"
                )
            elif "minLength" in schema:
                constraints.append(f"minLength: {schema['minLength']}")
            elif "maxLength" in schema:
                constraints.append(f"maxLength: {schema['maxLength']}")

            # Pattern constraint
            if "pattern" in schema:
                pattern = schema["pattern"]
                # Try to make common patterns more readable
                if pattern == r"^[^@]+@[^@]+\.[^@]+$":
                    constraints.append("format: email")
                elif pattern == r"^\+?1?\d{9,15}$":
                    constraints.append("format: phone")
                elif pattern == r"^[a-zA-Z0-9_]+$":
                    constraints.append("pattern: alphanumeric and underscore only")
                else:
                    constraints.append(f"pattern: {pattern}")

        # Numeric constraints (integer and number)
        elif schema.get("type") in ["integer", "number"]:
            # Range constraints
            if "minimum" in schema and "maximum" in schema:
                constraints.append(f"range: {schema['minimum']}-{schema['maximum']}")
            elif "minimum" in schema:
                constraints.append(f"minimum: {schema['minimum']}")
            elif "maximum" in schema:
                constraints.append(f"maximum: {schema['maximum']}")

            # Exclusive constraints (gt/lt in Pydantic become exclusiveMinimum/exclusiveMaximum)
            if "exclusiveMinimum" in schema:
                constraints.append(f"exclusiveMinimum: {schema['exclusiveMinimum']}")
            if "exclusiveMaximum" in schema:
                constraints.append(f"exclusiveMaximum: {schema['exclusiveMaximum']}")

            # Multiple constraint
            if "multipleOf" in schema:
                multiple = schema["multipleOf"]
                if multiple == 0.05:
                    constraints.append("multipleOf: 0.05 (5% increments)")
                elif multiple == 1:
                    constraints.append("multipleOf: 1 (integers only)")
                else:
                    constraints.append(f"multipleOf: {multiple}")

        # Array constraints
        elif schema.get("type") == "array":
            # Item count constraints
            if "minItems" in schema and "maxItems" in schema:
                constraints.append(f"items: {schema['minItems']}-{schema['maxItems']}")
            elif "minItems" in schema:
                constraints.append(f"minItems: {schema['minItems']}")
            elif "maxItems" in schema:
                constraints.append(f"maxItems: {schema['maxItems']}")

            # Unique items constraint
            if schema.get("uniqueItems"):
                constraints.append("uniqueItems: true")

            # Contains constraints
            if "contains" in schema:
                contains_constraint = self._format_contains_constraint(schema)
                if contains_constraint:
                    constraints.append(contains_constraint)

            # MinContains/MaxContains constraints
            if "minContains" in schema and "maxContains" in schema:
                constraints.append(
                    f"contains: {schema['minContains']}-{schema['maxContains']} items"
                )
            elif "minContains" in schema:
                constraints.append(f"minContains: {schema['minContains']}")
            elif "maxContains" in schema:
                constraints.append(f"maxContains: {schema['maxContains']}")

        # Handle not constraints
        if "not" in schema:
            not_constraint = self._format_not_constraint(schema["not"])
            if not_constraint:
                constraints.append(not_constraint)

        return constraints

    def _format_not_constraint(self, not_schema: dict) -> str:
        """Format not constraint for human-readable display.

        Args:
            not_schema: The not constraint schema

        Returns:
            A formatted string representation of the not constraint
        """
        if not isinstance(not_schema, dict):
            return ""

        # Handle enum exclusions
        if "enum" in not_schema:
            excluded_values = not_schema["enum"]
            if isinstance(excluded_values, list) and excluded_values:
                formatted_values = [
                    self._format_default_value(val) for val in excluded_values
                ]
                if len(formatted_values) == 1:
                    return f"not: {formatted_values[0]}"
                else:
                    return f"not: {', '.join(formatted_values)}"

        # Handle type exclusions
        if "type" in not_schema:
            excluded_type = not_schema["type"]
            return f"not: {excluded_type}"

        # Handle more complex not constraints
        if "properties" in not_schema:
            return "not: specific object pattern"

        return "not: specific constraint"

    def _format_contains_constraint(self, schema: dict) -> str:
        """Format contains constraint for human-readable display.

        Args:
            schema: The array schema with contains constraint

        Returns:
            A formatted string representation of the contains constraint
        """
        contains_schema = schema.get("contains", {})
        if not isinstance(contains_schema, dict):
            return ""

        # Handle type-based contains
        if "type" in contains_schema:
            contains_type = contains_schema["type"]

            # Add pattern information if available
            if "pattern" in contains_schema:
                pattern = contains_schema["pattern"]
                if pattern == "^required_":
                    return f"contains: {contains_type} starting with 'required_'"
                elif pattern == "^tag:":
                    return f"contains: {contains_type} starting with 'tag:'"
                else:
                    return f"contains: {contains_type} matching pattern {pattern}"

            return f"contains: {contains_type}"

        # Handle enum-based contains
        if "enum" in contains_schema:
            enum_values = contains_schema["enum"]
            if isinstance(enum_values, list) and enum_values:
                formatted_values = [
                    self._format_default_value(val) for val in enum_values
                ]
                return f"contains: one of {', '.join(formatted_values)}"

        # Handle const-based contains
        if "const" in contains_schema:
            const_value = self._format_default_value(contains_schema["const"])
            return f"contains: {const_value}"

        return "contains: specific item"

    def _format_examples(self, schema: dict) -> str:
        """Format examples for human-readable display in comments.

        Args:
            schema: The property schema dictionary

        Returns:
            A formatted string representation of examples, or empty string if none
        """
        # Handle anyOf/oneOf unions (like nullable types with examples)
        if "anyOf" in schema:
            # Look for examples in the non-null type
            for any_of_item in schema["anyOf"]:
                if any_of_item.get("type") != "null":
                    examples = self._format_examples(any_of_item)
                    if examples:
                        return examples
        elif "oneOf" in schema:
            # Similar handling for oneOf
            for one_of_item in schema["oneOf"]:
                if one_of_item.get("type") != "null":
                    examples = self._format_examples(one_of_item)
                    if examples:
                        return examples

        # Check for examples at the current level
        if "examples" not in schema:
            return ""

        examples_list = schema["examples"]
        if not isinstance(examples_list, list) or not examples_list:
            return ""

        # Format examples based on type and quantity
        if len(examples_list) == 1:
            # Single example
            formatted_example = self._format_default_value(examples_list[0])
            return f"example: {formatted_example}"
        else:
            # Multiple examples - show first few
            max_examples = 3  # Limit to avoid overly long comments
            formatted_examples = [
                self._format_default_value(ex) for ex in examples_list[:max_examples]
            ]
            examples_str = ", ".join(formatted_examples)
            if len(examples_list) > max_examples:
                examples_str += ", ..."
            return f"examples: {examples_str}"


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


def json_schema_to_schellma(
    schema: dict, define_types: bool = True, indent: int | bool | None = DEFAULT_INDENT
) -> str:
    """Convert a JSON Schema to ScheLLMa type definition string.

    Args:
        schema: JSON Schema dictionary from model.model_json_schema()
        define_types: If True, define reused types separately to avoid repetition
        indent: Indentation configuration:
            - False/None/0: No indentation (compact format)
            - int: Number of spaces per indentation level (default: 2)

    Returns:
        A string representation of the ScheLLMa type definition

    Raises:
        InvalidSchemaError: If the schema is invalid or malformed
        ConversionError: If conversion fails for any reason
        CircularReferenceError: If circular references are detected
    """
    converter = SchemaConverter(schema, define_types, indent)
    return converter.convert()


def pydantic_to_schellma(
    model_class: type[BaseModel],
    define_types: bool = False,
    indent: int | bool | None = DEFAULT_INDENT,
) -> str:
    """Convert a Pydantic model to a ScheLLMa type definition string.

    Args:
        model_class: A Pydantic BaseModel class
        define_types: If True, define reused types separately to avoid repetition
        indent: Indentation configuration:
            - False/None/0: No indentation (compact format)
            - int: Number of spaces per indentation level (default: 2)

    Returns:
        A string representation of the ScheLLMa type definition

    Raises:
        InvalidSchemaError: If the model is invalid
        ConversionError: If conversion fails for any reason
        CircularReferenceError: If circular references are detected
    """
    logger.debug(
        f"Converting Pydantic model {getattr(model_class, '__name__', str(model_class))} to ScheLLMa"
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

    return json_schema_to_schellma(schema, define_types, indent)


def schellma(
    obj: dict | type[BaseModel],
    define_types: bool = False,
    indent: int | bool | None = DEFAULT_INDENT,
) -> str:
    """Convert a JSON Schema dictionary or Pydantic model to a ScheLLMa type definition string.

    Args:
        obj: A JSON Schema dictionary or Pydantic model
        define_types: If True, define reused types separately to avoid repetition
        indent: Indentation configuration:
            - False/None/0: No indentation (compact format)
            - int: Number of spaces per indentation level (default: 2)

    Returns:
        A string representation of the ScheLLMa type definition

    Raises:
        InvalidSchemaError: If the model is invalid
        ConversionError: If conversion fails for any reason
        CircularReferenceError: If circular references are detected
    """
    if isinstance(obj, type) and issubclass(obj, BaseModel):
        return pydantic_to_schellma(obj, define_types, indent)
    elif isinstance(obj, dict):
        return json_schema_to_schellma(obj, define_types, indent)
    else:
        raise InvalidSchemaError(f"Invalid object type: {type(obj).__name__}")
