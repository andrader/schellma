import re
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    try:
        from openai.types import ChatCompletion  # type: ignore[import-not-found]
    except ImportError:
        ChatCompletion = Any

CompletionOrStr: TypeAlias = str | Any

T = TypeVar("T", bound=BaseModel)

_PATTERN = r"```(?:json|typescript)?\s*(.*?)\s*```"
_COMPILED_PATTERN = re.compile(_PATTERN, re.DOTALL)


def clean_content(content: str) -> str:
    """Clean LLM response content by extracting from code blocks and stripping whitespace.

    Removes markdown code block markers (```json, ```typescript, or plain ```)
    from the content and strips leading/trailing whitespace.

    Args:
        content: Raw content string that may contain code block markers

    Returns:
        Cleaned content string with code block markers removed and whitespace stripped

    Example:
        >>> content = "```json\\n{\"name\": \"John\"}\\n```"
        >>> clean_content(content)
        '{"name": "John"}'
    """
    # Extract content from code blocks
    match = _COMPILED_PATTERN.search(content)
    if match:
        content = match.group(1)
    content = content.strip()
    return content


def parse_completion(completion: CompletionOrStr, model: type[T]) -> T:
    """Parse LLM completion response into a Pydantic model.

    Extracts JSON content from either a string or OpenAI ChatCompletion object,
    cleans it by removing code block markers, and validates it against the provided model.

    Args:
        completion: Either a string containing JSON or an OpenAI ChatCompletion object
        model: Pydantic model class to validate the JSON against

    Returns:
        Validated instance of the provided Pydantic model

    Example:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     name: str
        ...     age: int
        >>> json_str = '{"name": "John", "age": 30}'
        >>> user = parse_completion(json_str, User)
        >>> user.name
        'John'
    """
    if isinstance(completion, str):
        content = completion
    else:
        content = completion.choices[0].message.content

    cleaned_content = clean_content(content)
    return model.model_validate_json(cleaned_content)
