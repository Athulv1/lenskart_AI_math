#!/usr/bin/env python3
"""
Main Layout Pipeline Orchestrator
Integrates 4 Apps: VTN Model → Gemini Image Gen → Gemini JSON → JSON Merger
Complete end-to-end optical store layout generation pipeline
"""

import os
import sys
import subprocess
import argparse
import glob
import time
from datetime import datetime
from pathlib import Path
import json

class LayoutPipelineOrchestrator:
    """Main orchestrator for the complete layout generation pipeline"""
    
    def __init__(self, input_image, input_wall_json=None, merchmix_json=None, base_output_dir="pipeline_outputs"):
        self.input_image = os.path.abspath(input_image)
        self.input_wall_json = os.path.abspath(input_wall_json) if input_wall_json else None
        self.merchmix_json = os.path.abspath(merchmix_json) if merchmix_json else None
        self.base_output_dir = base_output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"{base_output_dir}/run_{self.timestamp}"
        
        # Pipeline paths
        self.vtn_checkpoint = "/home/athul/json/config/vtn_enhanced_500epoch/checkpoints/best.pt"
        self.prompt_file = "/home/athul/json/config/prompt.txt"
        
        # App scripts
        self.app1_script = "/home/athul/json/scripts/5_inference.py"
        self.app2_script = "/home/athul/json/scripts/gemini_25_layout_generator.py"
        self.app3_script = "/home/athul/json/scripts/gemini_image_to_json.py"
        self.app4_script = "/home/athul/json/scripts/merge_layouts.py"
        
        # Intermediate file paths (to be auto-detected)
        self.vtn_output_path = None
        self.gemini_image_path = None
        self.fixture_json_path = None
        self.final_output_path = None
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup pipeline logging"""
        os.makedirs(self.output_dir, exist_ok=True)
        self.log_file = f"{self.output_dir}/pipeline_log.txt"
        
        def log_message(message, level="INFO"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}"
            print(log_entry)
            with open(self.log_file, 'a') as f:
                f.write(log_entry + "\n")
        
        self.log = log_message
    
    def validate_dependencies(self):
        """Validate all required files and dependencies exist"""
        self.log("🔍 Validating pipeline dependencies...")
        
        required_files = {
            "Input Image": self.input_image,
            "VTN Checkpoint": self.vtn_checkpoint,
            "Prompt File": self.prompt_file,
            "App 1 (VTN)": self.app1_script,
            "App 2 (Gemini Gen)": self.app2_script,
            "App 3 (Gemini JSON)": self.app3_script,
            "App 4 (Merger)": self.app4_script
        }
        
        # Add input wall JSON to validation if provided
        if self.input_wall_json:
            required_files["Input Wall JSON"] = self.input_wall_json
        
        missing_files = []
        for name, path in required_files.items():
            if not os.path.exists(path):
                missing_files.append(f"{name}: {path}")
                self.log(f"❌ Missing: {name} at {path}", "ERROR")
            else:
                self.log(f"✅ Found: {name}")
        
        if missing_files:
            self.log(f"❌ Pipeline validation failed. Missing {len(missing_files)} required files.", "ERROR")
            return False
        
        self.log("✅ All dependencies validated successfully")
        return True
    
    def find_latest_file(self, directory, pattern="*.png", description="file"):
        """Find the most recently created file matching pattern in directory"""
        search_path = os.path.join(directory, pattern)
        files = glob.glob(search_path)
        
        if not files:
            self.log(f"❌ No {description} found in {directory} matching {pattern}", "ERROR")
            return None
        
        # Get the most recent file
        latest_file = max(files, key=os.path.getctime)
        self.log(f"📁 Auto-detected latest {description}: {latest_file}")
        return latest_file
    
    def run_app1_vtn_model(self):
        """App 1: Run VTN inference to generate initial layout"""
        self.log("🚀 Starting App 1: VTN Model Inference...")
        
        # Prepare VTN output directory
        vtn_output_dir = f"{self.output_dir}/vtn_output"
        os.makedirs(vtn_output_dir, exist_ok=True)
        
        # Build VTN command
        vtn_command = [
            "python3", self.app1_script,
            "--checkpoint", self.vtn_checkpoint,
            "--image", self.input_image,
            "--out_dir", vtn_output_dir,
            "--top_p", "0.95",
            "--temperature", "0.9"
        ]
        
        self.log(f"📋 VTN Command: {' '.join(vtn_command)}")
        
        try:
            # Run VTN inference
            result = subprocess.run(vtn_command, capture_output=True, text=True, cwd="/home/athul/json")
            
            if result.returncode != 0:
                self.log(f"❌ App 1 (VTN) failed with return code {result.returncode}", "ERROR")
                self.log(f"STDOUT: {result.stdout}", "ERROR")
                self.log(f"STDERR: {result.stderr}", "ERROR")
                return False
            
            self.log("✅ App 1 (VTN) completed successfully")
            self.log(f"VTN Output: {result.stdout}")
            
            # Auto-detect VTN output file
            self.vtn_output_path = self.find_latest_file(vtn_output_dir, "*.png", "VTN output image")
            
            if not self.vtn_output_path:
                self.log("❌ Could not find VTN output image", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ App 1 (VTN) exception: {str(e)}", "ERROR")
            return False
    
    def run_app2_gemini_image_gen(self):
        """App 2: Run Gemini image generation using VTN output + prompt + merchmix"""
        self.log("🚀 Starting App 2: Gemini Image Generation...")
        
        if not self.vtn_output_path:
            self.log("❌ No VTN output available for App 2", "ERROR")
            return False
        
        # Prepare Gemini output directory
        gemini_output_dir = f"{self.output_dir}/gemini_optimized"
        os.makedirs(gemini_output_dir, exist_ok=True)
        
        try:
            # Build enhanced Gemini command with merchmix support
            gemini_command = ["python3", self.app2_script, self.vtn_output_path]
            
            # Add merchmix parameter if available
            if self.merchmix_json and os.path.exists(self.merchmix_json):
                gemini_command.extend(["--merchmix", self.merchmix_json])
                self.log(f"📊 Including merchmix data: {self.merchmix_json}")
            else:
                self.log("📋 No merchmix data provided, using standard generation")
            
            self.log(f"📋 Gemini Command: {' '.join(gemini_command)}")
            
            result = subprocess.run(gemini_command, capture_output=True, text=True, cwd="/home/athul/json")
            
            if result.returncode != 0:
                self.log(f"❌ App 2 (Gemini Gen) failed with return code {result.returncode}", "ERROR")
                self.log(f"STDOUT: {result.stdout}", "ERROR")
                self.log(f"STDERR: {result.stderr}", "ERROR")
                return False
            
            self.log("✅ App 2 (Gemini Gen) completed successfully")
            self.log(f"Gemini Output: {result.stdout}")
            
            # Auto-detect Gemini output file
            gemini_dir = "/home/athul/json/outputs/gemini_25_optimized"
            self.gemini_image_path = self.find_latest_file(gemini_dir, "*.png", "Gemini generated image")
            
            if not self.gemini_image_path:
                self.log("❌ Could not find Gemini output image", "ERROR")
                return False
            
            # Copy to our output directory for organization
            import shutil
            gemini_copy_path = f"{gemini_output_dir}/{os.path.basename(self.gemini_image_path)}"
            shutil.copy2(self.gemini_image_path, gemini_copy_path)
            self.log(f"📁 Copied Gemini image to: {gemini_copy_path}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ App 2 (Gemini Gen) exception: {str(e)}", "ERROR")
            return False
    
    def run_app3_gemini_json_conversion(self):
        """App 3: Convert Gemini image to JSON format with merchmix validation"""
        self.log("🚀 Starting App 3: Gemini JSON Conversion...")
        
        if not self.gemini_image_path:
            self.log("❌ No Gemini image available for App 3", "ERROR")
            return False
        
        try:
            # Build enhanced JSON conversion command with merchmix support
            fixture_json_output = os.path.join(self.output_dir, "fixture_layout.json")
            json_command = [
                "python3", self.app3_script,
                "--input-image", self.gemini_image_path,
                "--output-json", fixture_json_output
            ]
            
            # Add merchmix parameter if available
            if self.merchmix_json and os.path.exists(self.merchmix_json):
                json_command.extend(["--merchmix", self.merchmix_json])
                self.log(f"📊 Including merchmix validation: {self.merchmix_json}")
            else:
                self.log("📋 No merchmix data provided, using standard conversion")
            
            self.log(f"📋 JSON Command: {' '.join(json_command)}")
            
            result = subprocess.run(json_command, capture_output=True, text=True, cwd="/home/athul/json")
            
            if result.returncode != 0:
                self.log(f"❌ App 3 (Gemini JSON) failed with return code {result.returncode}", "ERROR")
                self.log(f"STDOUT: {result.stdout}", "ERROR")
                self.log(f"STDERR: {result.stderr}", "ERROR")
                return False
            
            self.log("✅ App 3 (Gemini JSON) completed successfully")
            self.log(f"JSON Output: {result.stdout}")
            
            # Check if fixture_layout.json was created in our output directory
            fixture_json_output = os.path.join(self.output_dir, "fixture_layout.json")
            
            if not os.path.exists(fixture_json_output):
                self.log("❌ fixture_layout.json was not created in output directory", "ERROR")
                return False
            
            self.fixture_json_path = fixture_json_output
            
            return True
            
        except Exception as e:
            self.log(f"❌ App 3 (Gemini JSON) exception: {str(e)}", "ERROR")
            return False
    
    def run_app4_json_merger(self):
        """App 4: Merge wall layout and fixture layout JSONs"""
        self.log("🚀 Starting App 4: JSON Layout Merger...")
        
        if not self.fixture_json_path or not os.path.exists(self.fixture_json_path):
            self.log("❌ No fixture JSON available for App 4", "ERROR")
            return False
        
        try:
            # Prepare final output path
            final_output_filename = f"merged_layout_{self.timestamp}.json"
            final_output_path = f"{self.output_dir}/{final_output_filename}"
            
            # --- SPATIAL AWARENESS FIX: Use input wall JSON when available ---
            if self.input_wall_json:
                # Use the provided input wall JSON for spatial accuracy
                wall_json_path = self.input_wall_json
                self.log(f"🎯 Using input wall JSON for spatial accuracy: {wall_json_path}")
            else:
                # Fallback to default wall_layout.json
                wall_json_path = "wall_layout.json"
                self.log(f"📐 Using default wall layout JSON")
            
            absolute_fixture_json_path = os.path.abspath(self.fixture_json_path)

            merge_command = [
                "python3", self.app4_script,
                wall_json_path,               # Use input wall JSON for spatial accuracy
                absolute_fixture_json_path,   # Use fixture JSON from App 3
                final_output_filename
            ]
            # --- END OF SPATIAL AWARENESS FIX ---
            
            self.log(f"📋 Merge Command: {' '.join(merge_command)}")
            
            result = subprocess.run(merge_command, capture_output=True, text=True, 
                                  cwd="/home/athul/json")
            
            if result.returncode != 0:
                self.log(f"❌ App 4 (JSON Merger) failed with return code {result.returncode}", "ERROR")
                self.log(f"STDOUT: {result.stdout}", "ERROR")
                self.log(f"STDERR: {result.stderr}", "ERROR")
                return False
            
            self.log("✅ App 4 (JSON Merger) completed successfully")
            self.log(f"Merge Output: {result.stdout}")
            
            # Check if final output was created and copy it
            merger_output = f"/home/athul/json/{final_output_filename}"
            
            if os.path.exists(merger_output):
                import shutil
                shutil.copy2(merger_output, final_output_path)
                self.final_output_path = final_output_path
                self.log(f"📁 Final output saved: {final_output_path}")
                return True
            else:
                self.log("❌ Merged layout JSON was not created", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"❌ App 4 (JSON Merger) exception: {str(e)}", "ERROR")
            return False
    
    def create_pipeline_summary(self):
        """Create a summary of the complete pipeline run"""
        summary_path = f"{self.output_dir}/pipeline_summary.json"
        
        summary = {
            "pipeline_run": {
                "timestamp": self.timestamp,
                "input_image": self.input_image,
                "output_directory": self.output_dir,
                "success": bool(self.final_output_path),
                "final_output": self.final_output_path
            },
            "app_outputs": {
                "app1_vtn_output": self.vtn_output_path,
                "app2_gemini_image": self.gemini_image_path,
                "app3_fixture_json": self.fixture_json_path,
                "app4_final_merged": self.final_output_path
            },
            "pipeline_configuration": {
                "vtn_checkpoint": self.vtn_checkpoint,
                "prompt_file": self.prompt_file,
                "input_wall_json": self.input_wall_json,
                "vtn_parameters": {
                    "top_p": 0.95,
                    "temperature": 0.9
                }
            }
        }
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.log(f"📋 Pipeline summary saved: {summary_path}")
        return summary_path
    
    def run_complete_pipeline(self):
        """Execute the complete 4-app pipeline"""
        start_time = time.time()
        
        self.log("=" * 80)
        self.log("🚀 STARTING COMPLETE LAYOUT GENERATION PIPELINE")
        self.log("=" * 80)
        self.log(f"📸 Input Image: {self.input_image}")
        self.log(f"📁 Output Directory: {self.output_dir}")
        self.log(f"🕐 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 80)
        
        # Step 0: Validate dependencies
        if not self.validate_dependencies():
            self.log("❌ Pipeline aborted due to missing dependencies", "ERROR")
            return False
        
        # Step 1: VTN Model
        self.log("\n" + "="*50)
        self.log("📱 STEP 1/4: VTN Model Inference")
        self.log("="*50)
        if not self.run_app1_vtn_model():
            self.log("❌ Pipeline failed at Step 1 (VTN Model)", "ERROR")
            return False
        
        # Step 2: Gemini Image Generation
        self.log("\n" + "="*50)
        self.log("🎨 STEP 2/4: Gemini Image Generation")
        self.log("="*50)
        if not self.run_app2_gemini_image_gen():
            self.log("❌ Pipeline failed at Step 2 (Gemini Image Gen)", "ERROR")
            return False
        
        # Step 3: Gemini JSON Conversion
        self.log("\n" + "="*50)
        self.log("📋 STEP 3/4: Gemini JSON Conversion")
        self.log("="*50)
        if not self.run_app3_gemini_json_conversion():
            self.log("❌ Pipeline failed at Step 3 (Gemini JSON)", "ERROR")
            return False
        
        # Step 4: JSON Merger
        self.log("\n" + "="*50)
        self.log("🔗 STEP 4/4: JSON Layout Merger")
        self.log("="*50)
        if not self.run_app4_json_merger():
            self.log("❌ Pipeline failed at Step 4 (JSON Merger)", "ERROR")
            return False
        
        # Pipeline Completion
        end_time = time.time()
        duration = end_time - start_time
        
        self.log("\n" + "="*80)
        self.log("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        self.log("="*80)
        self.log(f"⏱️  Total Duration: {duration:.2f} seconds")
        self.log(f"📁 Output Directory: {self.output_dir}")
        self.log(f"📄 Final Result: {self.final_output_path}")
        self.log("="*80)
        
        # Create summary
        summary_path = self.create_pipeline_summary()
        
        return True

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Complete Layout Generation Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main_orchestrator.py --image "/path/to/floorplan.png"
  python3 main_orchestrator.py --image "data/sample.png" --output-dir "my_results"
  python3 main_orchestrator.py --image "data/kolanchery.png" --wall-json "input_wall_json/kolanchery.json"
  python3 main_orchestrator.py --image "data/sample.png" --merchmix "merchmix.json"
        """
    )
    
    parser.add_argument(
        "--image", 
        required=True,
        help="Path to input floor plan image"
    )
    
    parser.add_argument(
        "--wall-json",
        help="Path to input wall coordinates JSON file for spatial accuracy"
    )
    
    parser.add_argument(
        "--merchmix",
        help="Path to merchmix.json file for fixture requirements and compliance validation"
    )
    
    parser.add_argument(
        "--output-dir",
        default="pipeline_outputs",
        help="Base output directory (default: pipeline_outputs)"
    )
    
    args = parser.parse_args()
    
    # Validate input image exists
    if not os.path.exists(args.image):
        print(f"❌ Error: Input image not found: {args.image}")
        return 1
    
    # Validate wall JSON if provided
    if args.wall_json and not os.path.exists(args.wall_json):
        print(f"❌ Error: Wall JSON not found: {args.wall_json}")
        return 1
    
    # Validate merchmix JSON if provided
    if args.merchmix and not os.path.exists(args.merchmix):
        print(f"❌ Error: Merchmix JSON not found: {args.merchmix}")
        return 1
    
    # Initialize and run pipeline
    try:
        orchestrator = LayoutPipelineOrchestrator(
            input_image=args.image, 
            input_wall_json=args.wall_json, 
            merchmix_json=args.merchmix,
            base_output_dir=args.output_dir
        )
        success = orchestrator.run_complete_pipeline()
        
        if success:
            print(f"\n✅ Pipeline completed successfully!")
            print(f"📁 Results available in: {orchestrator.output_dir}")
            print(f"📄 Final output: {orchestrator.final_output_path}")
            if args.merchmix:
                print(f"📊 Enhanced with merchmix requirements")
            return 0
        else:
            print(f"\n❌ Pipeline failed. Check logs in: {orchestrator.output_dir}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Pipeline interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Pipeline crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())