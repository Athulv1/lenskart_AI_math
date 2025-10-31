#!/usr/bin/env python3
"""
Gemini Image to JSON Converter
Takes a layout image and converts it to specific JSON format using Gemini API
"""

import google.generativeai as genai
import os
import json
from PIL import Image
from datetime import datetime

def load_merchmix_data(merchmix_path):
    """Load merchmix JSON data from file."""
    try:
        with open(merchmix_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading merchmix file: {e}")
        return None

def load_layout_image(image_path):
    """Load the layout image for analysis."""
    try:
        image = Image.open(image_path)
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        print(f"📸 Loaded layout image: {image.size[0]}x{image.size[1]} pixels")
        return image
    except Exception as e:
        print(f"❌ Error loading layout image: {e}")
        return None

def create_enhanced_json_conversion_prompt(merchmix_data=None):
    """Create enhanced JSON conversion prompt with optional merchmix validation."""
    
    base_prompt = """
# IMAGE TO JSON CONVERSION TASK

Analyze the provided optical store layout image and convert it to the EXACT JSON format specified below.

## YOUR TASK:
1. **IDENTIFY ALL FIXTURES**: Examine the layout image and identify each fixture/element
2. **DETERMINE POSITIONS**: Calculate the center coordinates for each fixture (normalized 0-1)
3. **ESTIMATE SIZES**: Determine width and height for each fixture (normalized 0-1)
4. **CLASSIFY FIXTURES**: Identify fixture types (vc_fixture_large, Euro_centre, screen_55, mirrors, etc.)"""

    # Add merchmix validation section if data is provided
    if merchmix_data:
        merch_min = merchmix_data.get('merch_mix_min', {})
        merch_max = merchmix_data.get('merch_mix_max', {})
        
        merchmix_section = f"""
5. **MERCHMIX VALIDATION**: Count detected fixtures and validate against requirements

## MERCHMIX REQUIREMENTS FOR VALIDATION:
**Store Information:**
- Project: {merchmix_data.get('name', 'Unknown')}
- Total Carpet Area: {merchmix_data.get('total_carpet_area', 'Not specified')} sq ft

**Required Fixture Counts (Minimum):**
- JJ Eye Fixtures: {merch_min.get('JJ_Eye', 0)}
- VC Eye Fixtures: {merch_min.get('VC_Eye', 0)}
- VC Sun Fixtures: {merch_min.get('VC_Sun', 0)}
- Clinic Units: {merch_min.get('CL', 0)}
- Tentpole Displays: {merch_min.get('Tentpole', 0)}"""
        
        base_prompt += merchmix_section

    # Continue with JSON format specification
    json_format = f"""

## REQUIRED JSON FORMAT:
```json
{{
  "project_id": "gemini-image-to-json-{datetime.now().strftime('%Y%m%d')}",
  "project_name": "Gemini Generated Layout from Image Analysis",
  "created_at": "{datetime.now().isoformat()}+05:30","""
    
    if merchmix_data:
        json_format += """
  "generated_with_merchmix": true,
  "merchmix_compliance": {
    "total_fixtures_detected": 0,
    "compliance_score": 0.0,
    "recommendations": []
  },"""

    json_format += """
  "room_measurements": {
    "floor_polygon": [
      { "x": 0.0, "y": 0.0 },
      { "x": 1.0, "y": 0.0 },
      { "x": 1.0, "y": 1.0 },
      { "x": 0.0, "y": 1.0 }
    ],
    "fixtures": [
      {
        "id": "fixture_1",
        "type": "vc_fixture_large",
        "center": { "x": 0.5, "y": 0.3 },
        "size": { "width": 0.1, "height": 0.05 },
        "rotation": 0.0
      }
    ]
  }
}
```

## COORDINATE SYSTEM:
- **X-axis**: 0.0 (left edge) to 1.0 (right edge)
- **Y-axis**: 0.0 (top edge) to 1.0 (bottom edge)

## FIXTURE TYPES TO IDENTIFY:
- vc_fixture_large, vc_fixture_medium, vc_fixture_small
- jj_fixture_large, jj_fixture_medium, jj_fixture_small
- Euro_centre, screen_55, mirror, ROC_clinic

## CRITICAL REQUIREMENTS:
- **OUTPUT ONLY JSON**: Provide ONLY the JSON response, no additional text
- **ACCURATE COORDINATES**: Use precise normalized coordinates (0.0 to 1.0)
- **ALL FIXTURES**: Include every visible fixture in the image
- **VALID JSON**: Ensure the output is properly formatted JSON"""

    if merchmix_data:
        json_format += """
- **MERCHMIX COMPLIANCE**: Include merchmix_compliance section with actual fixture counts"""

    json_format += """

Analyze the layout image and provide the complete JSON response:
"""
    
    return base_prompt + json_format

def create_json_conversion_prompt():
    """Create the prompt for converting image to JSON format."""
    conversion_prompt = """
# IMAGE TO JSON CONVERSION TASK

Analyze the provided optical store layout image and convert it to the EXACT JSON format specified below.

## YOUR TASK:
1. **IDENTIFY ALL FIXTURES**: Examine the layout image and identify each fixture/element
2. **DETERMINE POSITIONS**: Calculate the center coordinates for each fixture (normalized 0-1)
3. **ESTIMATE SIZES**: Determine width and height for each fixture (normalized 0-1)
4. **CLASSIFY FIXTURES**: Identify fixture types (vc_fixture_large, Euro_centre, screen_55, mirrors, etc.)

## REQUIRED JSON FORMAT:
```json
{
  "project_id": "gemini-image-to-json-YYYYMMDD",
  "project_name": "Gemini Generated Layout from Image Analysis",
  "created_at": "YYYY-MM-DDTHH:MM:SS+05:30",
  "room_measurements": {
    "floor_polygon": [
      { "x": 0.0, "y": 0.0 },
      { "x": 1.0, "y": 0.0 },
      { "x": 1.0, "y": 1.0 },
      { "x": 0.0, "y": 1.0 }
    ],
    "fixtures": [
      {
        "name": "fixture_type_name",
        "center": { "x": 0.0, "y": 0.0 },
        "size": { "width": 0.0, "height": 0.0 },
        "rotation": 0
      }
    ]
  },
  "rotation": 0.0
}
```

## COORDINATE SYSTEM:
- **X-axis**: 0.0 (left edge) to 1.0 (right edge)
- **Y-axis**: 0.0 (top edge) to 1.0 (bottom edge)
- **Center**: Center point of each fixture
- **Size**: Width and height of each fixture

## FIXTURE TYPES TO IDENTIFY:
- vc_fixture_large, vc_fixture_medium, vc_fixture_small
- jj_fixture_large, jj_fixture_medium, jj_fixture_small
- Euro_centre, euro_centre
- screen_55, screen
- mirror, mirror_different
- ROC_clinic, regular_clinic
- staff_rack, repair_table
- discussion_table, pos_ar
- sofa, bench

## CRITICAL REQUIREMENTS:
- **OUTPUT ONLY JSON**: Provide ONLY the JSON response, no additional text
- **ACCURATE COORDINATES**: Use precise normalized coordinates (0.0 to 1.0)
- **ALL FIXTURES**: Include every visible fixture in the image
- **CORRECT FORMAT**: Follow the exact JSON structure provided
- **VALID JSON**: Ensure the output is properly formatted JSON

Analyze the layout image and provide the complete JSON response:
"""
    return conversion_prompt

def convert_image_to_json(image_path, output_path, api_key, merchmix_path=None):
    """Convert layout image to JSON using Gemini API with optional merchmix support."""
    
    # Configure API
    genai.configure(api_key=api_key)
    
    # Load image
    layout_image = load_layout_image(image_path)
    if layout_image is None:
        return False
    
    # Load merchmix data if provided
    merchmix_data = None
    if merchmix_path and os.path.exists(merchmix_path):
        print(f"📊 Loading merchmix data: {merchmix_path}")
        merchmix_data = load_merchmix_data(merchmix_path)
        if merchmix_data:
            print(f"✅ Merchmix loaded - Store: {merchmix_data.get('name', 'Unknown')}")
        else:
            print("⚠️ Failed to load merchmix data, proceeding without it")
    else:
        print("📋 No merchmix data provided, using standard conversion")
    
    # Create enhanced conversion prompt with merchmix data
    conversion_prompt = create_enhanced_json_conversion_prompt(merchmix_data)
    
    try:
        print("🚀 Initializing Gemini 2.5 Pro for image analysis...")
        model = genai.GenerativeModel('gemini-2.5-pro')
        print("✅ Model initialized successfully")
        
        print("🔍 Analyzing layout image for JSON conversion...")
        print(f"📸 Input: {image_path}")
        if merchmix_data:
            print(f"📊 Merchmix: {merchmix_path} (Store: {merchmix_data.get('name', 'Unknown')})")
        print(f"📋 Target: JSON format conversion")
        
        # Analyze image and convert to JSON
        response = model.generate_content([conversion_prompt, layout_image])
        
        if hasattr(response, 'text') and response.text:
            response_text = response.text.strip()
            print(f"📝 Received response ({len(response_text)} characters)")
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                
                try:
                    # Parse and validate JSON
                    layout_data = json.loads(json_text)
                    print(f"✅ Valid JSON parsed successfully")
                    
                    # Update metadata
                    layout_data["project_id"] = f"gemini-image-to-json-{datetime.now().strftime('%Y%m%d')}"
                    layout_data["project_name"] = "Gemini Generated Layout from Image Analysis"
                    layout_data["created_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+05:30")
                    
                    # Count fixtures
                    fixture_count = len(layout_data.get("room_measurements", {}).get("fixtures", []))
                    print(f"📊 Identified {fixture_count} fixtures")
                    
                    # Create output directory if needed
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Save JSON file
                    with open(output_path, 'w') as f:
                        json.dump(layout_data, f, indent=2)
                    
                    print(f"✅ JSON saved: {output_path}")
                    print(f"📦 Project ID: {layout_data['project_id']}")
                    print(f"📅 Created: {layout_data['created_at']}")
                    
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"📝 Raw response: {response_text[:500]}...")
                    return False
            else:
                print("❌ No valid JSON found in response")
                print(f"📝 Response: {response_text[:200]}...")
                return False
        else:
            print("❌ No text response received")
            return False
            
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False

def main():
    import argparse
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Convert Gemini generated layout image to JSON format')
    parser.add_argument('--input-image', type=str, help='Path to input layout image')
    parser.add_argument('--output-json', type=str, help='Path to output JSON file')
    parser.add_argument('--merchmix', type=str, help='Path to merchmix.json file')
    
    args = parser.parse_args()
    
    # Configuration
    api_key = "AIzaSyDYivSaB99eiXW__eYF_WprJsa8qCZGQ2M"
    
    # Use command line arguments if provided, otherwise use defaults
    if args.input_image:
        input_image = args.input_image
    else:
        # Try to auto-detect latest Gemini output
        opt_dir = "/home/athul/json/outputs/gemini_25_optimized"
        if os.path.exists(opt_dir):
            import glob
            png_files = glob.glob(os.path.join(opt_dir, "*.png"))
            if png_files:
                latest_file = max(png_files, key=os.path.getctime)
                print(f"🔄 Using latest file: {latest_file}")
                input_image = latest_file
            else:
                print("❌ No PNG files found")
                return 1
        else:
            print(f"❌ Directory not found: {opt_dir}")
            return 1
    
    if args.output_json:
        output_json = args.output_json
    else:
        output_json = "/home/athul/json/outputs/fixture_layout.json"
    
    merchmix_path = args.merchmix
    
    print("🎯 GEMINI IMAGE TO JSON CONVERTER")
    print("=" * 50)
    print(f"📸 Input Image: {input_image}")
    print(f"📄 Output JSON: {output_json}")
    if merchmix_path:
        print(f"📊 Merchmix File: {merchmix_path}")
    print("=" * 50)
    
    # Validate input image exists
    if not os.path.exists(input_image):
        print(f"❌ Input image not found: {input_image}")
        return 1
    
    if merchmix_path and not os.path.exists(merchmix_path):
        print(f"❌ Merchmix file not found: {merchmix_path}")
        return 1
    
    # Convert image to JSON with merchmix support
    success = convert_image_to_json(input_image, output_json, api_key, merchmix_path)
    
    if success:
        print(f"\n🎉 SUCCESS! Image converted to JSON format")
        print(f"📸 Source: {input_image}")
        print(f"📄 Output: {output_json}")
        print(f"🤖 Model: Gemini 2.5 Pro")
        if merchmix_path:
            print(f"📊 Enhanced with merchmix validation")
        return 0
    else:
        print(f"\n❌ Failed to convert image to JSON")
        return 1

if __name__ == "__main__":
    exit(main())
