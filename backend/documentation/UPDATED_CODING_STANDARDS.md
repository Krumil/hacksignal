# Hackathon Monitor - Updated Coding Standards

## File Organization Guidelines

-   Keep each file ≤ 400 logical lines
-   Every logical concern should be in its own module/package with clear interfaces
-   Use semantic naming for files and functions
-   Group related functionality together
-   Use the documentation folder when adding .md files

## Code Quality Requirements

-   **Unit Test Pass Rate**: ≥ 95%
-   **Public API Documentation Coverage**: ≥ 80% (docstrings required)
-   **Error Handling**: Fail fast with clear exceptions; never silently pass
-   **Pure Functions**: Prefer pure functions; isolate I/O at boundaries
-   **LLM Call Validation**: Always validate structured outputs and implement fallbacks

## Structured Outputs Standards

### Pydantic Model Guidelines

All data models must follow these patterns:

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class ExampleEnum(str, Enum):
    """Use string enums for constrained choices."""
    option_a = "Option A"
    option_b = "Option B"

class ExampleModel(BaseModel):
    """Descriptive model docstring.

    All models must include comprehensive field descriptions.
    """
    required_field: str = Field(description="Clear description of field purpose and constraints")
    optional_field: Optional[int] = Field(default=None, description="Optional field description")
    enum_field: ExampleEnum = Field(description="Enum field with default value")
    list_field: List[str] = Field(description="List field with item type description")
```

### LLM Integration Patterns

#### Structured Output Functions

```python
def generate_with_llm(input_data: Dict) -> Optional[PydanticModel]:
    """Generate structured data using LLM with validation and fallback.

    Args:
        input_data: Input data for LLM processing

    Returns:
        Validated Pydantic model or None if generation/validation fails

    Raises:
        ValidationError: When generated data fails validation
        APIError: When LLM API call fails
    """
    try:
        # 1. Validate input
        if not _validate_input(input_data):
            return None

        # 2. Call structured output API
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[...],
            response_format=PydanticModel,
            temperature=0.7
        )

        # 3. Extract and validate result
        result = completion.choices[0].message.parsed

        if result and _validate_business_logic(result):
            return result
        else:
            print(f"Generated data failed validation")
            return None

    except Exception as e:
        print(f"Error in LLM generation: {e}")
        return None
```

#### Fallback Implementation

```python
def transform_with_fallback(data: Dict) -> Dict:
    """Main transformation function with LLM-first, fallback-second pattern.

    Args:
        data: Input data to transform

    Returns:
        Transformed data dictionary
    """
    # Try structured LLM generation first
    llm_result = generate_with_llm(data)

    if llm_result:
        return _convert_to_output_format(llm_result)

    # Fallback to rule-based generation
    print(f"LLM generation failed, using fallback")
    return _generate_fallback(data)
```

## Function Documentation Standards

Every public function must include a docstring with:

```python
def example_function(arg1: str, arg2: int) -> dict:
    """Brief description of function purpose.

    Args:
        arg1: Description of first argument
        arg2: Description of second argument

    Returns:
        Description of return value and structure

    Raises:
        SpecificException: When this error condition occurs
        ValidationError: When data validation fails
    """
```

### LLM Function Documentation

LLM-related functions require additional documentation:

```python
def llm_function(prompt: str, model_class: Type[BaseModel]) -> Optional[BaseModel]:
    """LLM function with structured output.

    Args:
        prompt: Input prompt for LLM
        model_class: Pydantic model class for structured output

    Returns:
        Validated model instance or None if generation fails

    Raises:
        APIError: When OpenAI API call fails
        ValidationError: When output doesn't match schema

    Notes:
        - Requires OPENAI_API_KEY environment variable
        - Falls back to rule-based generation on failure
        - Uses gpt-4o model for structured outputs
    """
```

## Testing Requirements

### Standard Testing

-   **Tests alongside code**: Treat red → green cycle as mandatory
-   **Test file naming**: `test_[module_name].py`
-   **Unit tests required for**: All public functions, error handling, edge cases

### Structured Outputs Testing

Additional testing requirements for LLM integration:

```python
def test_structured_generation_success():
    """Test successful structured output generation."""
    # Test with valid input
    result = generate_with_llm(valid_input)
    assert result is not None
    assert isinstance(result, ExpectedModel)
    assert result.required_field is not None

def test_structured_generation_fallback():
    """Test fallback when LLM generation fails."""
    # Mock API failure
    with patch('openai.OpenAI') as mock_client:
        mock_client.side_effect = Exception("API Error")
        result = transform_with_fallback(test_data)
        assert result is not None  # Should use fallback
        assert 'reasoning' in result  # Should indicate fallback used

def test_validation_failure():
    """Test handling of invalid LLM outputs."""
    # Test with invalid structured output
    with patch('client.beta.chat.completions.parse') as mock_parse:
        mock_parse.return_value.choices[0].message.parsed = invalid_model
        result = generate_with_llm(test_input)
        assert result is None  # Should fail validation

@pytest.mark.integration
def test_api_key_missing():
    """Test graceful handling of missing API key."""
    with patch.dict(os.environ, {}, clear=True):
        result = transform_with_fallback(test_data)
        assert result is not None  # Should use fallback
```

### Critical Test Cases

Each module must include tests for:

**hackathon_transformer.py**:

-   Structured output generation with valid inputs
-   Validation of all Pydantic model fields
-   Fallback behavior when LLM fails
-   API key missing scenarios
-   Business logic validation (prize ranges, durations, etc.)
-   Batch processing with mixed success/failure cases

**Existing modules** (ingestion.py, scoring.py, etc.):

-   [Previous requirements remain the same]

## Error Handling Standards

### LLM-Specific Error Handling

```python
# Good: Specific exception types with context
try:
    result = client.beta.chat.completions.parse(...)
except openai.APIError as e:
    logger.error(f"OpenAI API error: {e}")
    return None
except ValidationError as e:
    logger.error(f"Structured output validation failed: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error in LLM generation: {e}")
    return None

# Bad: Generic exception catching
try:
    result = client.beta.chat.completions.parse(...)
except Exception:
    return None
```

### Validation Patterns

```python
def _validate_business_logic(data: PydanticModel) -> bool:
    """Validate business logic constraints beyond schema validation.

    Args:
        data: Pydantic model instance

    Returns:
        True if data passes business validation
    """
    try:
        # Check ranges
        if not (5000 <= data.prizePool <= 250000):
            return False

        # Check consistency
        if data.duration > 21 and data.prizePool < 20000:
            return False  # Long events should have higher prizes

        return True

    except Exception as e:
        logger.error(f"Business validation error: {e}")
        return False
```

## Configuration Management

### API Key Management

```python
# Good: Centralized API key handling
def get_openai_client() -> Optional[openai.OpenAI]:
    """Get OpenAI client with proper error handling."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.warning("OPENAI_API_KEY not found, LLM features disabled")
        return None
    return openai.OpenAI(api_key=api_key)

# Bad: Direct API key access in business logic
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Don't do this
```

### Model Configuration

```python
# config.json updates
{
    "llm": {
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_retries": 3,
        "timeout": 30
    },
    "validation": {
        "prize_pool_min": 5000,
        "prize_pool_max": 250000,
        "duration_min": 3,
        "duration_max": 21
    }
}
```

## Performance Considerations

### LLM Call Optimization

-   **Batch processing**: Group multiple operations when possible
-   **Caching**: Cache LLM results for identical inputs
-   **Rate limiting**: Respect API rate limits with exponential backoff
-   **Cost monitoring**: Log token usage and API costs

```python
# Good: Efficient batch processing
def process_tweets_batch(tweets: List[Dict]) -> List[Dict]:
    """Process tweets in batches with rate limiting."""
    results = []
    for tweet in tweets:
        try:
            result = transform_tweet_to_hackathon(tweet)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to process tweet {tweet.get('id', 'unknown')}: {e}")
            continue

        # Rate limiting
        time.sleep(0.1)  # Prevent hitting rate limits

    return results
```

## Security Guidelines

### Enhanced API Security

-   **Never commit API keys**: Use environment variables only
-   **Key rotation**: Support API key rotation without code changes
-   **Least privilege**: Use API keys with minimal required permissions
-   **Audit logging**: Log all LLM API calls (without sensitive data)

```python
# Good: Secure API key handling
@functools.lru_cache(maxsize=1)
def get_api_client():
    """Get cached API client with validation."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or len(api_key) < 10:
        raise ValueError("Invalid or missing OPENAI_API_KEY")
    return openai.OpenAI(api_key=api_key)
```

### Data Privacy

-   **Input sanitization**: Remove PII from LLM prompts
-   **Output filtering**: Validate LLM outputs don't contain sensitive data
-   **Audit trail**: Log what data is sent to external APIs

## Code Style Guidelines

### Type Hints for LLM Code

```python
from typing import Optional, Dict, List, Type, Union
from pydantic import BaseModel

# All LLM functions must have complete type hints
def generate_structured_data(
    input_data: Dict[str, Any],
    model_class: Type[BaseModel],
    temperature: float = 0.7
) -> Optional[BaseModel]:
    """Generate structured data with type safety."""
    pass
```

### Naming Conventions

-   **LLM functions**: Prefix with `generate_` or `llm_`
-   **Validation functions**: Prefix with `validate_` or `_validate_`
-   **Fallback functions**: Suffix with `_fallback`
-   **Pydantic models**: Use descriptive names ending in `Data` or `Model`

## Version Control Standards

-   Use semantic commit messages
-   Tag releases with semantic versioning
-   Update CHANGELOG.md for each release
-   **LLM changes**: Clearly mark commits that modify LLM prompts or models
-   **Breaking changes**: Increment major version for Pydantic model changes

## CI/CD Requirements

### Enhanced Testing Pipeline

-   Standard unit tests must pass (≥95% coverage)
-   **LLM integration tests**: Run with mock responses
-   **API key tests**: Verify graceful handling of missing keys
-   **Performance tests**: Monitor LLM call latency and costs
-   **Validation tests**: Ensure all Pydantic models work correctly

```bash
# Required test commands
python -m pytest                           # Standard tests
python test_structured_transformer.py      # Structured outputs tests
python -m pytest --integration            # Integration tests (with API keys)
```

## Monitoring and Observability

### LLM-Specific Monitoring

-   **Token usage tracking**: Monitor and alert on high usage
-   **Error rate monitoring**: Track LLM API failures
-   **Fallback usage**: Monitor how often fallbacks are used
-   **Response quality**: Track validation failure rates

```python
# Example monitoring
@functools.wraps(func)
def monitor_llm_call(func):
    """Decorator to monitor LLM API calls."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            metrics.increment('llm.calls.success')
            return result
        except Exception as e:
            metrics.increment('llm.calls.failure')
            metrics.increment(f'llm.calls.failure.{type(e).__name__}')
            raise
        finally:
            duration = time.time() - start_time
            metrics.timing('llm.calls.duration', duration)
    return wrapper
```

This updated coding standard incorporates all the new patterns from our structured outputs implementation while maintaining compatibility with existing code.
