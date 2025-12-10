#!/usr/bin/env python3
"""
AI Pipeline Integration for Django Backend
Integrates the complete AI pipeline (VTN → Gemini → JSON → Merger) with Django
"""

import os
import sys
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class AILayoutPipelineIntegrator:
    """Integrates the complete AI pipeline with Django backend"""
    
    def __init__(self):
        # AI Pipeline paths
        self.ai_pipeline_root = "/home/athul/json"
        self.main_orchestrator = f"{self.ai_pipeline_root}/main_orchestrator.py"
        self.venv_path = "/home/athul/json/lenskart_backend/venv"
        
        # Default wall JSON (can be project-specific later)
        self.default_wall_json = f"{self.ai_pipeline_root}/input_wall_json/White_filed_Bangalore.json"
        
        # Validate paths
        self._validate_setup()
    
    def _validate_setup(self):
        """Validate that AI pipeline is properly set up"""
        required_paths = [
            self.main_orchestrator,
            self.default_wall_json,
            f"{self.venv_path}/bin/activate"
        ]
        
        for path in required_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"AI Pipeline dependency missing: {path}")
        
        logger.info("✅ AI Pipeline setup validated")
    
    def process_image_with_ai(self, image_path, project_name=None, ai_prompt=None, merchmix_json=None):
        """
        Process a floorplan image using the complete AI pipeline
        
        Args:
            image_path (str): Path to the input floorplan image
            project_name (str): Name for the project (used in output directory)
            ai_prompt (str): Optional custom AI prompt (not used yet, for future)
            merchmix_json (str): Optional merchmix configuration
        
        Returns:
            dict: Results containing output paths and metadata
        """
        try:
            logger.info(f"🤖 Starting AI pipeline processing for: {image_path}")
            
            # Generate unique output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_safe_name = project_name.replace(" ", "_") if project_name else "ai_layout"
            output_dir = f"ai_outputs/{project_safe_name}_{timestamp}"
            
            # Prepare command
            cmd = self._build_ai_command(image_path, output_dir, merchmix_json)
            
            # Execute AI pipeline
            result = self._execute_ai_pipeline(cmd, timeout=300)  # 5 minute timeout
            
            if result["success"]:
                # Process results
                results = self._process_ai_results(output_dir, result["stdout"])
                logger.info(f"✅ AI pipeline completed successfully")
                return results
            else:
                logger.error(f"❌ AI pipeline failed: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"],
                    "stderr": result["stderr"]
                }
                
        except Exception as e:
            logger.exception(f"❌ Error in AI pipeline processing: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_ai_command(self, image_path, output_dir, merchmix_json=None):
        """Build the AI pipeline command"""
        # Base command with virtual environment activation
        cmd = [
            "bash", "-c",
            f"cd {self.ai_pipeline_root} && "
            f"source {self.venv_path}/bin/activate && "
            f"python3 {self.main_orchestrator} "
            f"--image \"{image_path}\" "
            f"--wall-json \"{self.default_wall_json}\" "
            f"--output-dir \"{output_dir}\""
        ]
        
        # Add merchmix if provided
        if merchmix_json and os.path.exists(merchmix_json):
            cmd[2] += f" --merchmix \"{merchmix_json}\""
        
        return cmd
    
    def _execute_ai_pipeline(self, cmd, timeout=300):
        """Execute the AI pipeline command"""
        try:
            logger.info(f"🚀 Executing AI pipeline...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.ai_pipeline_root
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "success": False,
                    "error": f"Pipeline failed with return code {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "AI pipeline timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_ai_results(self, output_dir, stdout):
        """Process AI pipeline results and extract output files"""
        results = {
            "success": True,
            "output_directory": output_dir,
            "files": {},
            "metadata": {}
        }
        
        # Parse stdout for output directory
        actual_output_dir = None
        for line in stdout.split('\n'):
            if "Output Directory:" in line:
                actual_output_dir = line.split("Output Directory:")[-1].strip()
                break
            elif "Results available in:" in line:
                actual_output_dir = line.split("Results available in:")[-1].strip()
                break
        
        if actual_output_dir:
            full_output_path = f"{self.ai_pipeline_root}/{actual_output_dir}"
            results["output_directory"] = full_output_path
            
            # Find output files
            self._find_output_files(full_output_path, results)
            
            # Extract metadata from stdout
            self._extract_metadata(stdout, results)
        
        return results
    
    def _find_output_files(self, output_dir, results):
        """Find and catalog output files"""
        if not os.path.exists(output_dir):
            logger.warning(f"Output directory not found: {output_dir}")
            return
        
        # Look for specific file types
        file_patterns = {
            "merged_layout_json": "merged_layout_*.json",
            "merged_layout_dxf": "merged_layout_*.dxf",
            "vtn_output": "vtn_output/floorplan_*_layout.png",
            "gemini_image": "gemini_optimized/gemini_25_improved_layout_*.png",
            "fixture_layout": "fixture_layout.json",
            "pipeline_summary": "pipeline_summary.json"
        }
        
        import glob
        for file_type, pattern in file_patterns.items():
            full_pattern = f"{output_dir}/**/{pattern}"
            matches = glob.glob(full_pattern, recursive=True)
            if matches:
                # Use the latest file if multiple matches
                latest_file = max(matches, key=os.path.getctime)
                results["files"][file_type] = latest_file
                logger.info(f"📄 Found {file_type}: {os.path.basename(latest_file)}")
    
    def _extract_metadata(self, stdout, results):
        """Extract metadata from pipeline output"""
        metadata = {}
        
        # Extract duration
        for line in stdout.split('\n'):
            if "Total Duration:" in line:
                duration = line.split("Total Duration:")[-1].strip()
                metadata["duration"] = duration
            elif "Pipeline completed successfully!" in line:
                metadata["status"] = "completed"
            elif "Generated size:" in line and "pixels" in line:
                size_info = line.split("Generated size:")[-1].strip()
                metadata["gemini_image_size"] = size_info
            elif "Identified" in line and "fixtures" in line:
                fixtures_info = line.split("Identified")[-1].split("fixtures")[0].strip()
                metadata["fixtures_count"] = fixtures_info
        
        results["metadata"] = metadata
    
    def copy_result_to_django_media(self, ai_result, django_media_root):
        """Copy AI pipeline results to Django media directory"""
        if not ai_result.get("success"):
            return None
        
        files = ai_result.get("files", {})
        copied_files = {}
        
        # Create AI results directory in media
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ai_media_dir = os.path.join(django_media_root, f"ai_results/{timestamp}")
        os.makedirs(ai_media_dir, exist_ok=True)
        
        # Copy important files
        files_to_copy = ["merged_layout_dxf", "merged_layout_json", "gemini_image"]
        
        for file_type in files_to_copy:
            if file_type in files and os.path.exists(files[file_type]):
                source_file = files[file_type]
                filename = os.path.basename(source_file)
                dest_file = os.path.join(ai_media_dir, filename)
                
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_files[file_type] = dest_file
                    logger.info(f"📁 Copied {file_type} to Django media")
                except Exception as e:
                    logger.error(f"❌ Failed to copy {file_type}: {e}")
        
        return copied_files if copied_files else None