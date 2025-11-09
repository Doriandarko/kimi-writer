"""
Writing samples library for the Kimi Multi-Agent Novel Writing System.

This module provides a preset writing samples library that users can select
to guide the writing style of their novels. Default is no sample (user can
customize or upload their own).
"""

from typing import Dict, List, Optional


# Preset writing samples (empty by default - user can add custom samples)
WRITING_SAMPLES: Dict[str, Dict[str, str]] = {
    # Example structure (to be filled by user):
    # "sample_id": {
    #     "name": "Author Name",
    #     "description": "Style description",
    #     "sample": "Sample text here...",
    #     "source": "Book title (year)"
    # }
}


def get_writing_sample(sample_id: str) -> Optional[str]:
    """
    Get writing sample text by ID.

    Args:
        sample_id: Sample identifier

    Returns:
        Sample text or None if not found
    """
    sample = WRITING_SAMPLES.get(sample_id)
    if sample:
        return sample.get('sample')
    return None


def list_available_samples() -> List[Dict[str, str]]:
    """
    Get list of available writing samples with metadata.

    Returns:
        List of sample metadata dictionaries (without full text)
    """
    samples = []
    for sample_id, sample_data in WRITING_SAMPLES.items():
        samples.append({
            'id': sample_id,
            'name': sample_data.get('name', 'Unknown'),
            'description': sample_data.get('description', ''),
            'source': sample_data.get('source', '')
        })
    return samples


def save_custom_sample(
    sample_id: str,
    name: str,
    sample_text: str,
    description: str = "",
    source: str = "Custom"
) -> str:
    """
    Save a custom writing sample.

    Args:
        sample_id: Unique identifier for the sample
        name: Display name for the sample
        sample_text: The actual sample text
        description: Description of the style
        source: Source attribution

    Returns:
        The sample_id
    """
    WRITING_SAMPLES[sample_id] = {
        'name': name,
        'description': description,
        'sample': sample_text,
        'source': source
    }
    return sample_id


def validate_sample_text(text: str) -> bool:
    """
    Validate that sample text meets minimum requirements.

    Args:
        text: Sample text to validate

    Returns:
        True if valid, False otherwise
    """
    if not text:
        return False

    # Minimum 100 characters
    if len(text) < 100:
        return False

    # Should have some substance (not just whitespace)
    if len(text.strip()) < 100:
        return False

    return True
