"""
Enhanced AI Pipeline with Mathematical Model Integration
=========================================================

Orchestrates the complete prompt → classification → processing → DXF flow.
Routes prompts to either direct AI processing or mathematical model + AI
based on complexity classification.

Author: Lenskart Development Team
Version: 1.0
Date: January 13, 2026
"""

import os
import json
import logging
from typing import Dict, Optional, Any
import ezdxf

from .prompt_classifier import PromptClassifier
from .math_model_integration import MathModelIntegration
from .ai_fixture_mover import AIFixtureMover

logger = logging.getLogger(__name__)


class EnhancedAIPipeline:
    """Orchestrates the complete prompt → position → DXF flow"""
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize the enhanced pipeline.
        
        Args:
            gemini_api_key: Google Gemini API key for AI processing
        """
        self.gemini_api_key = gemini_api_key
        self.classifier = PromptClassifier()
        self.ai_mover = AIFixtureMover(gemini_api_key) if gemini_api_key else None
        
        logger.info("Enhanced AI Pipeline initialized")
    
    def process_prompt(
        self,
        prompt: str,
        session_data: Dict
    ) -> Dict:
        """
        Main entry point for processing user prompts.
        
        Args:
            prompt: User's natural language prompt
            session_data: Current session data containing DXF and fixture info
            
        Returns:
            Dictionary with processing results:
            {
                'success': True/False,
                'operation_type': 'simple'/'complex',
                'fixtures': [...],
                'method': 'direct_ai'/'math_model',
                'error': 'error message if failed'
            }
        """
        logger.info(f"Processing prompt: {prompt}")
        
        try:
            # Step 1: Classify the prompt
            classification = self.classifier.classify(prompt)
            
            logger.info(f"Classification: {classification['operation_type']} "
                       f"({classification['confidence']:.2%} confidence)")
            logger.info(f"Reasoning: {classification['reasoning']}")
            
            # Step 2: Route to appropriate pipeline
            if classification['requires_math_model']:
                result = self._process_complex(prompt, session_data, classification)
            else:
                result = self._process_simple(prompt, session_data, classification)
            
            # Add classification info to result
            result['classification'] = classification
            result['operation_type'] = classification['operation_type']
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing prompt: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'fixtures': [],
                'operation_type': 'unknown'
            }
    
    def _process_simple(
        self,
        prompt: str,
        session_data: Dict,
        classification: Dict
    ) -> Dict:
        """
        Process simple operations using direct AI.
        
        Simple operations include:
        - Move fixture by specific amount
        - Rotate fixture
        - Single fixture transformations
        """
        logger.info("Processing simple operation with direct AI")
        
        if not self.ai_mover:
            return {
                'success': False,
                'error': 'AI service not available (API key missing)',
                'fixtures': [],
                'method': 'direct_ai'
            }
        
        try:
            # Load the DXF file for AI processing
            dxf_path = session_data.get('original_dxf')
            if not dxf_path or not os.path.exists(dxf_path):
                return {
                    'success': False,
                    'error': 'DXF file not found',
                    'fixtures': [],
                    'method': 'direct_ai'
                }
            
            # Load DXF to extract fixtures
            self.ai_mover.load_dxf(dxf_path)
            
            # Ask Gemini AI to process the command
            ai_result = self.ai_mover.ask_gemini(prompt)
            
            if not ai_result:
                return {
                    'success': False,
                    'error': 'AI processing returned no result',
                    'fixtures': [],
                    'method': 'direct_ai'
                }
            
            if isinstance(ai_result, dict) and 'error' in ai_result:
                return {
                    'success': False,
                    'error': ai_result.get('error', 'AI processing failed'),
                    'fixtures': [],
                    'method': 'direct_ai'
                }
            
            # Parse AI response into fixture modifications
            fixtures = ai_result.get('fixtures', [])
            
            return {
                'success': True,
                'fixtures': fixtures,
                'method': 'direct_ai',
                'ai_response': ai_result
            }
            
        except Exception as e:
            logger.error(f"Error in simple processing: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'fixtures': [],
                'method': 'direct_ai'
            }
    
    def _process_complex(
        self,
        prompt: str,
        session_data: Dict,
        classification: Dict
    ) -> Dict:
        """
        Process complex operations using mathematical model + AI refinement.
        
        Complex operations include:
        - Rearrange sections (BOH, clinic, etc.)
        - Add multiple fixtures
        - Remove multiple fixtures
        - Optimize entire layout
        """
        logger.info("Processing complex operation with mathematical model + AI")
        
        try:
            dxf_path = session_data.get('original_dxf')
            if not dxf_path or not os.path.exists(dxf_path):
                return {
                    'success': False,
                    'error': 'DXF file not found',
                    'fixtures': [],
                    'method': 'math_model'
                }
            
            # Step 1: Extract floor boundaries and fixtures
            json_data = session_data.get('json_data', {})
            logger.info(f"Session data keys: {list(session_data.keys())}")
            logger.info(f"JSON data keys: {list(json_data.keys()) if json_data else 'None'}")
            
            boundaries = self._extract_boundaries(json_data)
            fixtures = self._extract_fixtures(json_data)
            
            logger.info(f"Extracted boundaries: {boundaries}")
            logger.info(f"Extracted {len(fixtures)} fixtures: {list(fixtures.keys())[:5] if fixtures else 'None'}...")
            
            # Validate boundaries before passing to math model
            if not boundaries or not all(k in boundaries for k in ['min_x', 'max_x', 'min_y', 'max_y']):
                logger.error(f"Invalid boundaries extracted: {boundaries}")
                return {
                    'success': False,
                    'error': 'Could not extract floor boundaries from DXF',
                    'fixtures': [],
                    'method': 'math_model'
                }
            
            # Step 2: Initialize mathematical model
            math_model = MathModelIntegration(
                dxf_path=dxf_path,
                floor_boundaries=boundaries,
                session_id=session_data.get('session_id', 'unknown')
            )
            
            # Step 3: Get merch mix and room measurements if available
            merch_mix = session_data.get('merch_mix')
            room_measurements = session_data.get('room_measurements')
            
            # Step 4: Calculate optimal positions using mathematical model
            logger.info(f"Calculating positions for intent: {classification['intent']}")
            math_result = math_model.calculate_positions(
                operation=classification['intent'],
                fixtures=fixtures,
                merch_mix=merch_mix,
                room_measurements=room_measurements
            )
            
            logger.info(f"Math model result - placement_valid: {math_result.get('placement_valid')}, "
                       f"fixtures count: {len(math_result.get('fixtures', []))}")
            
            if not math_result.get('placement_valid'):
                logger.warning("Mathematical model returned invalid placement, falling back to AI")
                # Fallback to AI-only processing
                return self._process_simple(prompt, session_data, classification)
            
            # Math model succeeded - use its results
            fixtures_calculated = math_result.get('fixtures', [])
            
            if not fixtures_calculated:
                logger.warning("Math model returned no fixtures")
                return {
                    'success': False,
                    'error': 'Mathematical model returned no fixture positions',
                    'fixtures': [],
                    'method': 'math_model'
                }
            
            # Step 5: Optionally refine positions with AI (disabled for now to ensure math model works)
            # if self.ai_mover and self.gemini_api_key:
            #     refined_result = self._ai_refine_positions(
            #         prompt,
            #         math_result,
            #         session_data,
            #         boundaries
            #     )
            #     
            #     if refined_result.get('success'):
            #         fixtures_calculated = refined_result.get('fixtures', fixtures_calculated)
            
            # Cleanup temporary files
            math_model.cleanup()
            
            logger.info(f"Returning {len(fixtures_calculated)} fixtures from math model")
            
            return {
                'success': True,
                'fixtures': fixtures_calculated,
                'method': 'math_model_only',
                'warnings': math_result.get('warnings', [])
            }
            
        except Exception as e:
            logger.error(f"Error in complex processing: {e}", exc_info=True)
            
            # Return error instead of fallback (for debugging)
            return {
                'success': False,
                'error': f'Complex processing failed: {str(e)}',
                'fixtures': [],
                'method': 'math_model',
                'exception_type': type(e).__name__
            }
    
    def _ai_refine_positions(
        self,
        prompt: str,
        math_result: Dict,
        session_data: Dict,
        boundaries: Dict
    ) -> Dict:
        """
        Use Gemini AI to refine mathematically calculated positions.
        
        This allows AI to make minor aesthetic adjustments while staying
        within the constraints calculated by the mathematical model.
        """
        logger.info("Refining positions with AI")
        
        try:
            # Prepare the AI prompt
            fixtures_json = json.dumps(math_result.get('fixtures', []), indent=2)
            boundaries_json = json.dumps(boundaries, indent=2)
            
            ai_prompt = f"""You are a fixture placement assistant. I have calculated optimal positions 
for fixtures using mathematical constraints and design guidelines.

Please refine these positions based on the user's specific intent, but you MUST:
1. Stay within the floor boundaries
2. Maintain minimum spacing between fixtures (800mm)
3. Keep fixtures in their assigned zones
4. Only make minor adjustments (max 500mm from calculated position)

USER REQUEST: "{prompt}"

CALCULATED POSITIONS:
{fixtures_json}

FLOOR BOUNDARIES:
{boundaries_json}

Output ONLY valid JSON in this exact format:
{{
    "fixtures": [
        {{
            "block_name": "fixture_name",
            "original_position": [x, y],
            "new_position": [x, y],
            "reasoning": "why this position"
        }}
    ]
}}

If the calculated positions are already optimal, return them unchanged.
Do NOT add explanatory text, only the JSON."""

            # Ask Gemini AI
            response = self.ai_mover.model.generate_content(ai_prompt)
            response_text = response.text.strip()
            
            # Clean up response
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON response
            ai_result = json.loads(response_text)
            
            if 'fixtures' in ai_result and len(ai_result['fixtures']) > 0:
                # Validate positions are within boundaries
                validated_fixtures = []
                for fixture in ai_result['fixtures']:
                    new_pos = fixture.get('new_position', [])
                    if self._validate_position(new_pos, boundaries):
                        validated_fixtures.append(fixture)
                    else:
                        logger.warning(f"AI suggested invalid position for {fixture.get('block_name')}, "
                                     f"keeping math model position")
                        # Keep original math model position
                        for orig_fixture in math_result['fixtures']:
                            if orig_fixture['block_name'] == fixture['block_name']:
                                validated_fixtures.append(orig_fixture)
                                break
                
                return {
                    'success': True,
                    'fixtures': validated_fixtures,
                    'method': 'math_model_ai_refined'
                }
            else:
                # No valid fixtures from AI, return math model result
                return math_result
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return math_result
        except Exception as e:
            logger.error(f"Error in AI refinement: {e}")
            return math_result
    
    def _extract_boundaries(self, json_data: Dict) -> Dict:
        """
        Extract floor boundaries from JSON data.
        
        CRITICAL: Uses room_min/max values (from POLYLINE entities) for validation,
        NOT display boundaries which include fixture padding.
        """
        # First check for explicit boundaries dict
        boundaries = json_data.get('boundaries', {})
        
        # Check for room_min/max format (from DXF extraction)
        if not boundaries:
            room_min_x = json_data.get('room_min_x')
            room_max_x = json_data.get('room_max_x')
            room_min_y = json_data.get('room_min_y')
            room_max_y = json_data.get('room_max_y')
            
            # Only use if all values are present and not None
            if all(v is not None for v in [room_min_x, room_max_x, room_min_y, room_max_y]):
                boundaries = {
                    'min_x': room_min_x,
                    'max_x': room_max_x,
                    'min_y': room_min_y,
                    'max_y': room_max_y
                }
                logger.info(f"Using room boundaries: X=[{boundaries['min_x']:.0f}, {boundaries['max_x']:.0f}], Y=[{boundaries['min_y']:.0f}, {boundaries['max_y']:.0f}]")
        
        # Fallback: try min/max format
        if not boundaries and 'min_x' in json_data:
            boundaries = {
                'min_x': json_data.get('min_x', 0),
                'max_x': json_data.get('max_x', 10000),
                'min_y': json_data.get('min_y', 0),
                'max_y': json_data.get('max_y', 8000)
            }
        
        # Fallback: calculate from walls
        if not boundaries:
            walls = json_data.get('walls', [])
            if walls:
                xs = []
                ys = []
                for wall in walls:
                    if 'start' in wall:
                        xs.append(wall['start'][0])
                        ys.append(wall['start'][1])
                    if 'end' in wall:
                        xs.append(wall['end'][0])
                        ys.append(wall['end'][1])
                
                if xs and ys:
                    boundaries = {
                        'min_x': min(xs),
                        'max_x': max(xs),
                        'min_y': min(ys),
                        'max_y': max(ys)
                    }
        
        # Last resort: default boundaries
        if not boundaries:
            logger.warning("No boundaries found in JSON, using defaults")
            boundaries = {
                'min_x': 0,
                'max_x': 10000,
                'min_y': 0,
                'max_y': 8000
            }
        
        return boundaries
    
    def _extract_fixtures(self, json_data: Dict) -> Dict:
        """Extract fixtures from JSON data"""
        fixtures = {}
        
        # Try various possible fixture data structures
        blocks = json_data.get('blocks', [])
        if blocks:
            for block in blocks:
                # Handle if block is a string (block name) or dict
                if isinstance(block, str):
                    name = block
                    fixtures[name] = {
                        'type': 'floor',
                        'position': [0, 0],
                        'rotation': 0.0,
                        'layer': 'default'
                    }
                elif isinstance(block, dict):
                    name = block.get('name', f"fixture_{len(fixtures)}")
                    fixtures[name] = {
                        'type': block.get('type', 'floor'),
                        'position': block.get('position', [0, 0]),
                        'rotation': block.get('rotation', 0.0),
                        'layer': block.get('layer', 'default')
                    }
        
        # Also check for 'fixtures' key
        json_fixtures = json_data.get('fixtures', {})
        if isinstance(json_fixtures, dict):
            for fname, fdata in json_fixtures.items():
                if isinstance(fdata, dict):
                    fixtures[fname] = fdata
                else:
                    fixtures[fname] = {'type': 'floor', 'position': [0, 0]}
        elif isinstance(json_fixtures, list):
            for fixture in json_fixtures:
                if isinstance(fixture, dict):
                    name = fixture.get('name', f"fixture_{len(fixtures)}")
                    fixtures[name] = fixture
                elif isinstance(fixture, str):
                    fixtures[fixture] = {'type': 'floor', 'position': [0, 0]}
        
        return fixtures
    
    def _validate_position(self, position: list, boundaries: Dict) -> bool:
        """Validate that a position is within boundaries"""
        if not position or len(position) < 2:
            return False
        
        x, y = position[0], position[1]
        
        return (boundaries.get('min_x', 0) <= x <= boundaries.get('max_x', 10000) and
                boundaries.get('min_y', 0) <= y <= boundaries.get('max_y', 10000))


# Example usage and testing
if __name__ == "__main__":
    # Test the pipeline
    print("=" * 70)
    print("ENHANCED AI PIPELINE TEST")
    print("=" * 70)
    
    # Mock session data
    test_session = {
        'session_id': 'test_123',
        'original_dxf': '/tmp/test.dxf',
        'json_data': {
            'boundaries': {'min_x': 0, 'max_x': 10000, 'min_y': 0, 'max_y': 8000},
            'fixtures': {
                'clinic_1': {'type': 'clinic', 'position': [1000, 1000]},
                'table_1': {'type': 'floor', 'position': [5000, 3000]}
            }
        }
    }
    
    # Note: This would need a real API key to run
    # pipeline = EnhancedAIPipeline('your-api-key-here')
    
    test_prompts = [
        "Move clinic_1 left by 500mm",
        "Rearrange back of house",
        "Add 2 more clinics"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: '{prompt}'")
        print("-" * 70)
        # result = pipeline.process_prompt(prompt, test_session)
        # print(json.dumps(result, indent=2))
        print("(Test would run here with valid API key)")
