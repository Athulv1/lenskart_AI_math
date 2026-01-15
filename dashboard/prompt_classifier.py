"""
Prompt Classifier for AI-Powered Fixture Operations
====================================================

Classifies user prompts into simple or complex operations to route them
to the appropriate processing pipeline (Direct AI vs Math Model + AI).

Author: Lenskart Development Team
Version: 1.0
Date: January 13, 2026
"""

import re
from typing import Dict, List, Optional


class PromptClassifier:
    """Classifies user prompts into simple or complex operations"""
    
    # Simple operation keywords (direct transformations)
    SIMPLE_KEYWORDS = [
        "move", "shift", "drag", "relocate", "reposition",
        "rotate", "turn", "spin", "angle",
        "by", "mm", "cm", "m", "meter", "millimeter",
        "left", "right", "up", "down", "north", "south", "east", "west"
    ]
    
    # Complex operation keywords (requires mathematical model)
    COMPLEX_KEYWORDS = [
        "rearrange", "reorganize", "optimize", "layout", "restructure",
        "add", "insert", "create", "new", "place", "put",
        "remove", "delete", "clear", "eliminate", "take out",
        "all", "entire", "whole", "every", "complete",
        "boh", "back of house", "backhouse", "backup house",
        "clinic", "clinics", "eye test", "examination",
        "fixtures", "furniture", "items",
        "section", "zone", "area", "region",
        "floor", "wall", "screen", "table", "chair"
    ]
    
    # Simple operation patterns (regex)
    SIMPLE_PATTERNS = [
        r"move\s+\w+\s+(left|right|up|down|by)",
        r"rotate\s+\w+\s+\d+",
        r"shift\s+\w+\s+\d+\s?(mm|cm|m)",
        r"(left|right|up|down)\s+by\s+\d+",
        r"turn\s+\w+\s+(clockwise|counterclockwise|anticlockwise)",
        r"drag\s+\w+\s+to\s+\d+,\s?\d+",
    ]
    
    # Complex operation patterns (regex)
    COMPLEX_PATTERNS = [
        r"(rearrange|reorganize|optimize)\s+(boh|clinic|fixtures?|layout)",
        r"add\s+\d+\s+(clinic|table|screen|fixture|chair)",
        r"remove\s+all\s+\w+",
        r"(delete|clear)\s+(all|entire|every)",
        r"place\s+\d+\s+\w+\s+in",
        r"create\s+(new|\d+)\s+\w+",
        r"optimize\s+(space|layout|arrangement)",
    ]
    
    # Fixture type keywords
    FIXTURE_TYPES = [
        "clinic", "table", "chair", "screen", "mirror", "shelf",
        "bench", "sofa", "toilet", "pos", "counter", "rack",
        "dispenser", "euro_centre", "discussion_table"
    ]
    
    def __init__(self):
        """Initialize the classifier"""
        self.simple_keywords = [kw.lower() for kw in self.SIMPLE_KEYWORDS]
        self.complex_keywords = [kw.lower() for kw in self.COMPLEX_KEYWORDS]
        
    def classify(self, prompt: str) -> Dict:
        """
        Classify a user prompt into operation type.
        
        Args:
            prompt: User's natural language prompt
            
        Returns:
            Dictionary containing:
            - operation_type: 'simple' or 'complex'
            - intent: The main action (move, rotate, rearrange, add, remove)
            - confidence: Confidence score (0.0 - 1.0)
            - fixtures_affected: List of fixture names/types mentioned
            - requires_math_model: Boolean flag
            - reasoning: Explanation of classification
        """
        prompt_lower = prompt.lower().strip()
        
        # Extract fixtures mentioned
        fixtures_affected = self._extract_fixtures(prompt_lower)
        
        # Check for simple patterns first (highest priority)
        simple_score = self._calculate_simple_score(prompt_lower)
        
        # Check for complex patterns
        complex_score = self._calculate_complex_score(prompt_lower)
        
        # Determine operation type
        if simple_score > complex_score and simple_score >= 0.5:
            operation_type = "simple"
            requires_math_model = False
            confidence = simple_score
            intent = self._extract_simple_intent(prompt_lower)
            reasoning = f"Detected simple operation pattern with {len(fixtures_affected)} fixture(s)"
        else:
            operation_type = "complex"
            requires_math_model = True
            confidence = complex_score
            intent = self._extract_complex_intent(prompt_lower)
            reasoning = f"Detected complex operation requiring mathematical model"
        
        # Special case: if multiple fixtures or numeric additions/removals, force complex
        if self._has_multiple_fixture_changes(prompt_lower):
            operation_type = "complex"
            requires_math_model = True
            confidence = max(confidence, 0.8)
            reasoning = "Multiple fixture changes detected, using mathematical model"
        
        return {
            "operation_type": operation_type,
            "intent": intent,
            "confidence": confidence,
            "fixtures_affected": fixtures_affected,
            "requires_math_model": requires_math_model,
            "reasoning": reasoning,
            "original_prompt": prompt
        }
    
    def _calculate_simple_score(self, prompt: str) -> float:
        """Calculate confidence score for simple operations"""
        score = 0.0
        total_checks = 0
        
        # Check for simple keywords
        keyword_matches = sum(1 for kw in self.simple_keywords if kw in prompt)
        if keyword_matches > 0:
            score += min(keyword_matches / 3, 0.5)  # Max 0.5 from keywords
        total_checks += 1
        
        # Check for simple patterns
        pattern_matches = sum(1 for pattern in self.SIMPLE_PATTERNS 
                            if re.search(pattern, prompt, re.IGNORECASE))
        if pattern_matches > 0:
            score += 0.5  # 0.5 from pattern match
        total_checks += 1
        
        # Check for specific distance/angle values
        if re.search(r'\d+\s?(mm|cm|m|degree|°)', prompt):
            score += 0.3
        total_checks += 1
        
        # Penalize if complex keywords present
        complex_keyword_matches = sum(1 for kw in self.complex_keywords if kw in prompt)
        if complex_keyword_matches > 2:
            score -= 0.4
        
        return max(0.0, min(1.0, score))
    
    def _calculate_complex_score(self, prompt: str) -> float:
        """Calculate confidence score for complex operations"""
        score = 0.0
        
        # Check for complex keywords
        keyword_matches = sum(1 for kw in self.complex_keywords if kw in prompt)
        if keyword_matches > 0:
            score += min(keyword_matches / 3, 0.5)  # Max 0.5 from keywords
        
        # Check for complex patterns
        pattern_matches = sum(1 for pattern in self.COMPLEX_PATTERNS 
                            if re.search(pattern, prompt, re.IGNORECASE))
        if pattern_matches > 0:
            score += 0.6  # 0.6 from pattern match
        
        # Check for multiple fixture operations
        if re.search(r'(add|remove|delete)\s+\d+', prompt):
            score += 0.3
        
        # Check for section/zone mentions
        if any(word in prompt for word in ['section', 'zone', 'area', 'all', 'entire']):
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _extract_simple_intent(self, prompt: str) -> str:
        """Extract the primary intent for simple operations"""
        if any(word in prompt for word in ['move', 'shift', 'relocate', 'drag']):
            return "move"
        elif any(word in prompt for word in ['rotate', 'turn', 'spin']):
            return "rotate"
        else:
            return "transform"
    
    def _extract_complex_intent(self, prompt: str) -> str:
        """Extract the primary intent for complex operations"""
        if any(word in prompt for word in ['rearrange', 'reorganize', 'optimize']):
            return "rearrange"
        elif any(word in prompt for word in ['add', 'insert', 'create', 'new', 'place']):
            return "add"
        elif any(word in prompt for word in ['remove', 'delete', 'clear']):
            return "remove"
        else:
            return "optimize"
    
    def _extract_fixtures(self, prompt: str) -> List[str]:
        """Extract fixture names/types from prompt"""
        fixtures = []
        
        # Check for specific fixture types
        for fixture_type in self.FIXTURE_TYPES:
            if fixture_type in prompt:
                fixtures.append(fixture_type)
        
        # Check for fixture names with patterns like "clinic_1", "table-123"
        fixture_patterns = re.findall(r'\b[a-z_]+[-_]?\d*\b', prompt)
        for match in fixture_patterns:
            if len(match) > 3 and match not in self.simple_keywords:
                fixtures.append(match)
        
        return list(set(fixtures))  # Remove duplicates
    
    def _has_multiple_fixture_changes(self, prompt: str) -> bool:
        """Check if prompt involves multiple fixture additions/removals"""
        # Check for numeric quantities
        numeric_changes = re.findall(r'(add|remove|delete|place)\s+(\d+)', prompt)
        if numeric_changes:
            for _, num in numeric_changes:
                if int(num) > 1:
                    return True
        
        # Check for "all" or "entire" keywords
        if any(word in prompt for word in ['all', 'entire', 'whole', 'every']):
            return True
        
        return False
    
    def get_classification_summary(self, classification: Dict) -> str:
        """Generate a human-readable summary of the classification"""
        summary = f"""
Classification Result:
----------------------
Operation Type: {classification['operation_type'].upper()}
Intent: {classification['intent']}
Confidence: {classification['confidence']:.2%}
Requires Math Model: {'Yes' if classification['requires_math_model'] else 'No'}
Fixtures Affected: {', '.join(classification['fixtures_affected']) if classification['fixtures_affected'] else 'None identified'}
Reasoning: {classification['reasoning']}
"""
        return summary


# Example usage and testing
if __name__ == "__main__":
    classifier = PromptClassifier()
    
    # Test cases
    test_prompts = [
        "Move clinic_1 left by 500mm",
        "Rotate Euro_centre 90 degrees",
        "Rearrange back of house",
        "Add 2 more clinics",
        "Remove all screens",
        "Optimize floor fixtures layout",
        "Shift table up 1000mm",
        "Delete entire BOH section"
    ]
    
    print("=" * 70)
    print("PROMPT CLASSIFIER TEST RESULTS")
    print("=" * 70)
    
    for prompt in test_prompts:
        result = classifier.classify(prompt)
        print(f"\nPrompt: \"{prompt}\"")
        print(f"  Type: {result['operation_type']} | Intent: {result['intent']} | Confidence: {result['confidence']:.2%}")
        print(f"  Math Model: {result['requires_math_model']} | Fixtures: {result['fixtures_affected']}")
        print(f"  Reasoning: {result['reasoning']}")
