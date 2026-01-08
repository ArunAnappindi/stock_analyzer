"""
JSON formatter for programmatic output.
"""

import json
from typing import Dict, Any
from src.models import AnalysisResult


class JsonFormatter:
    """Formatter that produces JSON output."""

    def format(self, result: AnalysisResult) -> str:
        """
        Format the analysis result as JSON.

        Args:
            result: AnalysisResult to format

        Returns:
            JSON string
        """
        # Convert to dict using Pydantic's model_dump
        data = result.model_dump(mode='json')

        # Pretty print JSON
        return json.dumps(data, indent=2, default=str)

    def format_to_dict(self, result: AnalysisResult) -> Dict[str, Any]:
        """
        Format the analysis result as a dictionary.

        Args:
            result: AnalysisResult to format

        Returns:
            Dictionary representation
        """
        return result.model_dump(mode='json')
