#!/usr/bin/env python3
"""
AI-Powered Fixture Mover with Gemini AI
========================================

This application uses Google Gemini AI to understand natural language commands
and automatically move fixtures in DXF files.

USAGE:
------
    python3 ai_fixture_mover.py

Then follow the prompts to:
1. Select your DXF file
2. Give natural language commands like:
   - "Move D-Table-1200 at position 12257,862683 by 1000mm to the right"
   - "Move the Chair up by 500mm"
   - "Move all tables 2000mm left"

Author: GitHub Copilot + Google Gemini AI
Version: 1.0
"""

import ezdxf
import json
import os
import sys
import google.generativeai as genai
from pathlib import Path


class AIFixtureMover:
    """AI-powered DXF fixture mover using Gemini"""
    
    def __init__(self, api_key):
        """Initialize with Gemini API key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro-preview-03-25')
        self.dxf_file = None
        self.fixtures = []
        
    def load_dxf(self, dxf_path):
        """Load DXF file and extract all fixtures"""
        print(f'\n📖 Loading DXF: {dxf_path}')
        
        if not os.path.exists(dxf_path):
            print(f'❌ ERROR: File not found: {dxf_path}')
            return False
        
        try:
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
            
            self.dxf_file = dxf_path
            self.fixtures = []
            
            # Extract all fixtures
            for entity in msp:
                if entity.dxftype() == 'INSERT':
                    pos = entity.dxf.insert
                    self.fixtures.append({
                        'name': entity.dxf.name,
                        'x': float(pos.x),
                        'y': float(pos.y),
                        'z': float(pos.z),
                        'rotation': float(entity.dxf.rotation) if hasattr(entity.dxf, 'rotation') else 0.0
                    })
            
            print(f'✅ Loaded successfully')
            print(f'   Total fixtures: {len(self.fixtures)}')
            
            # Group by type
            fixture_types = {}
            for f in self.fixtures:
                name = f['name']
                if name not in fixture_types:
                    fixture_types[name] = 0
                fixture_types[name] += 1
            
            print(f'   Unique types: {len(fixture_types)}')
            print(f'\n📦 Available fixtures:')
            for name, count in sorted(fixture_types.items()):
                print(f'   - {name} ({count} instances)')
            
            return True
            
        except Exception as e:
            print(f'❌ ERROR loading DXF: {e}')
            return False
    
    def create_ai_prompt(self, user_command):
        """Create a detailed prompt for Gemini AI"""
        
        fixtures_json = json.dumps(self.fixtures, indent=2)
        
        prompt = f"""You are a DXF fixture movement assistant. The user wants to move fixtures in a CAD drawing.

AVAILABLE FIXTURES:
{fixtures_json}

USER COMMAND: "{user_command}"

Your task is to understand the user's command and generate a JSON modifications file.

RULES:
1. The user might say "move up/down/left/right by X mm"
   - UP = increase Y (less negative)
   - DOWN = decrease Y (more negative)
   - RIGHT = increase X
   - LEFT = decrease X

2. The user might specify a fixture by:
   - Name (e.g., "D-Table-1200", "Chair")
   - Position (e.g., "at 12257, -862683")
   - Description (e.g., "the table", "all chairs")

3. If user says "all [type]", move ALL fixtures of that type
4. If user specifies position, find the closest fixture
5. Round all coordinates to 2 decimal places

OUTPUT FORMAT (MUST BE VALID JSON):
{{
  "fixtures": [
    {{
      "block_name": "EXACT_FIXTURE_NAME",
      "original_position": [X, Y],
      "new_position": [NEW_X, NEW_Y]
    }}
  ]
}}

If you cannot understand the command or find the fixture, output:
{{
  "error": "explanation of the problem"
}}

Generate ONLY the JSON, no other text."""
        
        return prompt
    
    def ask_gemini(self, user_command):
        """Ask Gemini AI to interpret the command and generate modifications.json"""
        
        print(f'\n🤖 Processing command with Gemini AI...')
        print(f'   Command: "{user_command}"')
        
        try:
            prompt = self.create_ai_prompt(user_command)
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            
            # Parse JSON
            modifications = json.loads(response_text)
            
            # Check for errors
            if 'error' in modifications:
                print(f'❌ AI Error: {modifications["error"]}')
                return None
            
            print(f'✅ AI understood your command!')
            print(f'   Fixtures to move: {len(modifications.get("fixtures", []))}')
            
            return modifications
            
        except json.JSONDecodeError as e:
            print(f'❌ ERROR: AI response is not valid JSON')
            print(f'   Response: {response_text[:200]}...')
            return None
        except Exception as e:
            print(f'❌ ERROR calling Gemini: {e}')
            return None
    
    def apply_modifications(self, modifications, output_path):
        """Apply modifications to DXF and save"""
        
        print(f'\n🔧 Applying modifications...')
        
        # Load original DXF
        doc = ezdxf.readfile(self.dxf_file)
        msp = doc.modelspace()
        
        # Create fixture mapping
        original_fixtures = {}
        for entity in msp:
            if entity.dxftype() == 'INSERT':
                name = entity.dxf.name
                pos = (round(entity.dxf.insert.x, 2), round(entity.dxf.insert.y, 2))
                key = f'{name}@{pos[0]},{pos[1]}'
                
                if key not in original_fixtures:
                    original_fixtures[key] = []
                original_fixtures[key].append(entity)
        
        # Apply modifications
        changes_made = 0
        for mod in modifications.get('fixtures', []):
            block_name = mod['block_name']
            orig_pos = mod['original_position']
            new_pos = mod['new_position']
            
            orig_pos_key = (round(orig_pos[0], 2), round(orig_pos[1], 2))
            key = f'{block_name}@{orig_pos_key[0]},{orig_pos_key[1]}'
            
            if key in original_fixtures and original_fixtures[key]:
                fixture_to_update = original_fixtures[key].pop(0)
                new_pos_vec = ezdxf.math.Vec3(new_pos)
                old_pos = fixture_to_update.dxf.insert
                fixture_to_update.dxf.insert = new_pos_vec
                
                delta_x = new_pos_vec.x - old_pos.x
                delta_y = new_pos_vec.y - old_pos.y
                
                print(f'   ✅ Moved "{block_name}"')
                print(f'      From: X={old_pos.x:.2f}, Y={old_pos.y:.2f}')
                print(f'      To:   X={new_pos_vec.x:.2f}, Y={new_pos_vec.y:.2f}')
                print(f'      Delta: ΔX={delta_x:.2f}mm, ΔY={delta_y:.2f}mm')
                
                changes_made += 1
            else:
                print(f'   ⚠️  Fixture not found: {block_name} at {orig_pos_key}')
        
        if changes_made == 0:
            print(f'   ⚠️  No changes made')
            return False
        
        # Set R2018 + MM format
        doc.header['$INSUNITS'] = 4
        doc.header['$MEASUREMENT'] = 1
        
        # Save
        print(f'\n💾 Saving modified DXF...')
        doc.saveas(output_path)
        print(f'   ✅ Saved: {output_path}')
        
        return True


def main():
    """Main application"""
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  AI-POWERED FIXTURE MOVER                                  ║
║                  Powered by Google Gemini AI                               ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    # API Key
    API_KEY = "AIzaSyDYivSaB99eiXW__eYF_WprJsa8qCZGQ2M"
    
    print("🔑 Initializing Gemini AI...")
    try:
        ai_mover = AIFixtureMover(API_KEY)
        print("✅ Gemini AI ready!\n")
    except Exception as e:
        print(f"❌ ERROR: Could not initialize Gemini: {e}")
        print("   Please check your API key and internet connection")
        sys.exit(1)
    
    # Get DXF file
    print("=" * 80)
    dxf_file = input("📂 Enter DXF file path (or press Enter for default): ").strip()
    
    if not dxf_file:
        dxf_file = "ATTA MARKET SECTOR-18_NOIDA-FLAGSHIP-B-FURNITURE.dxf"
    
    if not ai_mover.load_dxf(dxf_file):
        sys.exit(1)
    
    # Interactive loop
    print("\n" + "=" * 80)
    print("🎯 READY! Give me commands in natural language.")
    print("=" * 80)
    print("\nExamples:")
    print('  - "Move D-Table-1200 at 12257,-862683 right by 1000mm"')
    print('  - "Move Chair up by 500mm"')
    print('  - "Move the table at position 14657,-862683 left by 2000mm"')
    print("\nType 'quit' to exit, 'help' for more examples\n")
    
    command_count = 0
    
    while True:
        try:
            # Get user command
            user_command = input("\n💬 Your command: ").strip()
            
            if not user_command:
                continue
            
            if user_command.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_command.lower() == 'help':
                print("\n📖 HELP - Example Commands:")
                print("   1. Move specific fixture by name and position:")
                print('      "Move D-Table-1200 at 12257,-862683 right 1000mm"')
                print("\n   2. Move by description:")
                print('      "Move the chair up by 500mm"')
                print("\n   3. Move all of a type:")
                print('      "Move all chairs left 2000mm"')
                print("\n   4. Complex movements:")
                print('      "Move table 1000mm right and 500mm up"')
                continue
            
            # Process with AI
            modifications = ai_mover.ask_gemini(user_command)
            
            if modifications is None:
                print("❌ Could not process command. Please try again.")
                continue
            
            # Show what AI understood
            print(f'\n📋 AI Generated Modifications:')
            print(json.dumps(modifications, indent=2))
            
            # Ask for confirmation
            confirm = input(f'\n✅ Apply these changes? (yes/no): ').strip().lower()
            
            if confirm not in ['yes', 'y']:
                print("❌ Cancelled. No changes made.")
                continue
            
            # Generate output filename
            command_count += 1
            base_name = Path(dxf_file).stem
            output_file = f"{base_name}-AI-MODIFIED-{command_count}.dxf"
            
            # Save modifications.json for reference
            mods_file = f"modifications-ai-{command_count}.json"
            with open(mods_file, 'w') as f:
                json.dump(modifications, f, indent=2)
            print(f'\n💾 Saved modifications to: {mods_file}')
            
            # Apply modifications
            if ai_mover.apply_modifications(modifications, output_file):
                print("\n" + "=" * 80)
                print("🎉 SUCCESS!")
                print("=" * 80)
                print(f"✅ Modified DXF: {output_file}")
                print(f"✅ Modifications JSON: {mods_file}")
                print("=" * 80)
            else:
                print("\n⚠️  No changes were applied")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
