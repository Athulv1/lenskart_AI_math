#!/usr/bin/env python3
"""
Gemini 2.5 Flash Image Generation for Layout Enhancement
Takes floor plan + prompt.txt and generates improved layout image
"""

import google.generativeai as genai
import os
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime

def load_merch_mix_file(merch_mix_path):
    """Load the merchandise mix JSON data from file."""
    try:
        import json
        with open(merch_mix_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading merchandise mix file: {e}")
        return None

def load_prompt_file(prompt_path):
    """Load the ultra-strict prompt from file."""
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error loading prompt file: {e}")
        return None

def prepare_floor_plan_image(image_path):
    """Load and prepare floor plan image for Gemini API."""
    try:
        image = Image.open(image_path)
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        print(f"📸 Loaded floor plan: {image.size[0]}x{image.size[1]} pixels")
        return image
    except Exception as e:
        print(f"❌ Error loading floor plan: {e}")
        return None

def create_enhanced_image_generation_prompt(ultra_strict_prompt, merchmix_data=None):
    """Create enhanced prompt combining prompt.txt + merchmix.json requirements."""
    
    # Base prompt from prompt.txt
    enhanced_prompt = f"""
# OPTICAL STORE LAYOUT IMAGE GENERATION TASK

Based on the provided floor plan image, generate a NEW, IMPROVED optical store layout image that strictly follows ALL the ultra-strict rules below.

## CRITICAL REQUIREMENTS:
- **GENERATE AN IMAGE**: Output must be a visual layout image, not text
- **STRICT COMPLIANCE**: Follow EVERY rule from the complete prompt below
- **PROFESSIONAL LAYOUT**: Clean, organized, visually balanced fixture placement
- **ENTRANCE PROTECTION**: Clear entrance zones (bottom area of floor plan)
- **FIXTURE ALIGNMENT**: Perfect geometric alignment and spacing
- **VISUAL QUALITY**: High-resolution, professional store layout visualization

## COMPLETE ULTRA-STRICT OPTICAL STORE LAYOUT RULES:
{ultra_strict_prompt}"""
    
    # Add merchmix-specific requirements if available
    if merchmix_data:
        merch_min = merchmix_data.get('merch_mix_min', {})
        merch_max = merchmix_data.get('merch_mix_max', {})
        
        merchmix_section = f"""

## **MERCHANDISE MIX REQUIREMENTS - MANDATORY COMPLIANCE**

### **STORE SPECIFICATIONS:**
- Total Carpet Area: {merchmix_data.get('total_carpet_area', 'Not specified')} sq ft
- Floor Level: {merchmix_data.get('floor_level', 'Not specified')}
- Main Entrance: {merchmix_data.get('main_entrance_direction', 'Not specified')}
- Project: {merchmix_data.get('name', 'Unknown')}

### **FIXTURE COUNT REQUIREMENTS (STRICT COMPLIANCE REQUIRED):**

**MINIMUM Requirements:**
- JJ Eye Fixtures: {merch_min.get('JJ_Eye', 0)}
- JJ Sun Fixtures: {merch_min.get('JJ_Sun', 0)}
- VC Eye Fixtures: {merch_min.get('VC_Eye', 0)}
- VC Sun Fixtures: {merch_min.get('VC_Sun', 0)}
- VC Kids Fixtures: {merch_min.get('VC_Kids', 0)}
- Clinic Units (CL): {merch_min.get('CL', 0)}
- Tentpole Displays: {merch_min.get('Tentpole', 0)}
- Hustlr Displays: {merch_min.get('Hustlr', 0)}
- Reading Glasses: {merch_min.get('Reading_Glasses', 0)}

**MAXIMUM Allowed:**
- JJ Eye Fixtures: {merch_max.get('JJ_Eye', 0)}
- JJ Sun Fixtures: {merch_max.get('JJ_Sun', 0)}
- VC Eye Fixtures: {merch_max.get('VC_Eye', 0)}
- VC Sun Fixtures: {merch_max.get('VC_Sun', 0)}
- VC Kids Fixtures: {merch_max.get('VC_Kids', 0)}
- Clinic Units (CL): {merch_max.get('CL', 0)}
- Tentpole Displays: {merch_max.get('Tentpole', 0)}
- Hustlr Displays: {merch_max.get('Hustlr', 0)}

### **CRITICAL MERCHMIX VALIDATION RULES:**
1. **FIXTURE COUNT COMPLIANCE**: MUST include AT LEAST the minimum fixture counts specified above
2. **MAXIMUM LIMITS**: MUST NOT exceed maximum fixture counts
3. **HIGH-VALUE PRIORITY**: Prioritize placement of Tentpole and Hustlr displays in prime locations
4. **BALANCED DISTRIBUTION**: Ensure optimal fixture mix ratios across store area
5. **CATEGORY BALANCE**: Maintain proper balance between Eye, Sun, and specialty fixtures"""
        
        enhanced_prompt += merchmix_section
    
    # Add generation instructions
    generation_instructions = f"""

## GENERATION INSTRUCTION:
Using the input floor plan image and ALL rules above (including merchmix requirements), generate a NEW improved optical store layout image that achieves 100% compliance with all specified rules.

The output should be a high-quality layout image showing:
- Properly positioned fixtures according to base rules AND merchmix requirements
- Correct fixture counts as specified in merchmix data
- Clear entrance area (bottom of layout)
- Professional alignment and spacing
- Organized fixture groupings by category
- Visual balance and clean presentation
- Optimal placement of high-value fixtures (Tentpole, Hustlr)

GENERATE THE IMPROVED LAYOUT IMAGE NOW."""
    
    enhanced_prompt += generation_instructions
    return enhanced_prompt

def create_image_generation_prompt(ultra_strict_prompt):
    """Legacy function for backward compatibility."""
    return create_enhanced_image_generation_prompt(ultra_strict_prompt, None)

def generate_improved_layout_image(floor_plan_path, prompt_path, output_dir, api_key, merchmix_path=None):
    """Generate improved layout image using Gemini 2.5 Flash Image Preview with optional merchmix support."""
    
    # Configure API
    genai.configure(api_key=api_key)
    
    # Load inputs
    print("📋 Loading inputs...")
    ultra_strict_prompt = load_prompt_file(prompt_path)
    if not ultra_strict_prompt:
        return None
    
    # Load merchmix data if provided
    merchmix_data = None
    if merchmix_path and os.path.exists(merchmix_path):
        print(f"📊 Loading merchmix data: {merchmix_path}")
        merchmix_data = load_merch_mix_file(merchmix_path)
        if merchmix_data:
            print(f"✅ Merchmix loaded - Store: {merchmix_data.get('name', 'Unknown')}")
        else:
            print("⚠️ Failed to load merchmix data, proceeding without it")
    else:
        print("📋 No merchmix data provided, using standard generation")
    
    floor_plan_image = prepare_floor_plan_image(floor_plan_path)
    if floor_plan_image is None:
        return None
    
    # Create enhanced generation prompt with merchmix data
    image_prompt = create_enhanced_image_generation_prompt(ultra_strict_prompt, merchmix_data)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print("🚀 Initializing Gemini 2.5 Flash Image Preview...")
        model = genai.GenerativeModel('gemini-2.5-flash-image-preview')
        print("✅ Model initialized successfully")
        
        print("🎨 Generating improved layout image...")
        print(f"📸 Input: {floor_plan_path}")
        print(f"📋 Prompt: {prompt_path} ({len(ultra_strict_prompt)} characters)")
        if merchmix_data:
            print(f"📊 Merchmix: {merchmix_path} (Store: {merchmix_data.get('name', 'Unknown')})")
        
        # Generate content with floor plan + enhanced prompt
        response = model.generate_content([image_prompt, floor_plan_image])
        
        print("🔍 Processing response...")
        
        if hasattr(response, 'parts') and response.parts:
            print(f"📦 Found {len(response.parts)} response parts")
            
            for i, part in enumerate(response.parts):
                if hasattr(part, 'inline_data') and part.inline_data:
                    print(f"🎯 IMAGE DATA FOUND! (Part {i+1})")
                    print(f"📊 MIME type: {part.inline_data.mime_type}")
                    
                    try:
                        # Extract image data
                        image_data = part.inline_data.data
                        
                        # Handle the image data
                        if isinstance(image_data, bytes):
                            generated_image = Image.open(BytesIO(image_data))
                        else:
                            image_bytes = base64.b64decode(image_data)
                            generated_image = Image.open(BytesIO(image_bytes))
                        
                        # Save the generated image
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_filename = f"gemini_25_improved_layout_{timestamp}.png"
                        output_path = os.path.join(output_dir, output_filename)
                        
                        generated_image.save(output_path)
                        
                        print(f"✅ Improved layout saved: {output_path}")
                        print(f"📐 Generated size: {generated_image.size}")
                        
                        # Save metadata
                        metadata = {
                            "generation_metadata": {
                                "generated_on": datetime.now().isoformat(),
                                "input_floor_plan": floor_plan_path,
                                "ultra_strict_prompt": prompt_path,
                                "gemini_model": "gemini-2.5-flash-image-preview",
                                "generation_type": "FLOOR_PLAN_TO_IMPROVED_LAYOUT",
                                "output_image": output_path,
                                "image_size": f"{generated_image.size[0]}x{generated_image.size[1]}",
                                "prompt_size_chars": len(ultra_strict_prompt)
                            }
                        }
                        
                        import json
                        metadata_path = output_path.replace('.png', '_metadata.json')
                        with open(metadata_path, 'w') as f:
                            json.dump(metadata, f, indent=2)
                        
                        print(f"📋 Metadata saved: {metadata_path}")
                        
                        return output_path
                        
                    except Exception as decode_error:
                        print(f"❌ Image decode error: {decode_error}")
                        return None
                
                elif hasattr(part, 'text') and part.text:
                    print(f"📝 Text response (Part {i+1}): {part.text[:100]}...")
        
        # Check for direct text response
        if hasattr(response, 'text') and response.text:
            print(f"📝 Direct text response: {response.text[:100]}...")
            print("⚠️  Received text instead of image")
            
        return None
        
    except Exception as e:
        print(f"❌ Error during image generation: {e}")
        return None

def main():
    import sys
    import argparse
    
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Generate improved layout image using Gemini 2.5 Flash')
    parser.add_argument('floor_plan', nargs='?', help='Path to floor plan image')
    parser.add_argument('--merchmix', type=str, help='Path to merchmix.json file')
    parser.add_argument('--prompt', type=str, help='Path to prompt.txt file')
    parser.add_argument('--output', type=str, help='Output directory')
    
    args = parser.parse_args()
    
    # Configuration
    api_key = "AIzaSyDYivSaB99eiXW__eYF_WprJsa8qCZGQ2M"
    
    # Determine floor plan path
    if args.floor_plan:
        floor_plan_path = args.floor_plan
        print(f"📸 Using provided image: {floor_plan_path}")
    elif len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        floor_plan_path = sys.argv[1]
        print(f"📸 Using VTN generated image: {floor_plan_path}")
    else:
        # Fallback to default floor plan
        floor_plan_path = "/home/athul/json/2025.06.08_APPROVED LAYOUT PLAN-Model-5-ground_layout.png"
        print(f"📸 Using default floor plan: {floor_plan_path}")
    
    # Set other paths
    prompt_path = args.prompt or "/home/athul/json/config/prompt.txt"
    output_dir = args.output or "/home/athul/json/outputs/gemini_25_optimized"
    merchmix_path = args.merchmix
    
    print("🎯 GEMINI 2.5 FLASH IMAGE LAYOUT GENERATION")
    print("=" * 60)
    print(f"📸 Floor Plan: {floor_plan_path}")
    print(f"📋 Prompt File: {prompt_path}")
    if merchmix_path:
        print(f"📊 Merchmix File: {merchmix_path}")
    print(f"📁 Output Dir: {output_dir}")
    print("=" * 60)
    
    # Validate inputs
    if not os.path.exists(floor_plan_path):
        print(f"❌ Floor plan not found: {floor_plan_path}")
        return 1
    
    if not os.path.exists(prompt_path):
        print(f"❌ Prompt file not found: {prompt_path}")
        return 1
    
    if merchmix_path and not os.path.exists(merchmix_path):
        print(f"❌ Merchmix file not found: {merchmix_path}")
        return 1
    
    # Generate improved layout with merchmix support
    result = generate_improved_layout_image(
        floor_plan_path,
        prompt_path,
        output_dir,
        api_key,
        merchmix_path
    )
    
    if result:
        print(f"\n🎉 SUCCESS! Improved layout generated:")
        print(f"📸 Output: {result}")
        print(f"🤖 Model: Gemini 2.5 Flash Image Preview")
        print(f"📋 Using complete ultra-strict prompt ({os.path.getsize(prompt_path)} bytes)")
        if merchmix_path:
            print(f"📊 Enhanced with merchmix requirements")
        return 0
    else:
        print(f"\n❌ Failed to generate improved layout image")
        return 1

if __name__ == "__main__":
    exit(main())
