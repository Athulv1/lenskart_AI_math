import os
import sys
import logging

logger = logging.getLogger("app")

# This function should be called once from api.py before importing any FreeCAD modules
def setup_freecad_environment():
    """Setup FreeCAD environment paths consistently across the application"""
    logger.info("Setting up FreeCAD environment paths...")
    
    # Clear any previous FreeCAD paths to avoid conflicts
    freecad_paths = [p for p in sys.path if 'freecad' in p.lower() or 'FreeCAD' in p]
    for p in freecad_paths:
        if p in sys.path:
            sys.path.remove(p)
    
    # Add FreeCAD paths based on platform detection
    if os.path.exists('/Applications/FreeCAD.app'):
        # MacOS path
        sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib/')  
        sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib/python3.11/site-packages')
        logger.info("Added MacOS FreeCAD paths")
    else:
        # Linux path - add multiple potential paths
        linux_paths = [
            '/usr/lib/freecad-python3/lib/',
            '/usr/lib/freecad-python3/lib/python3/dist-packages',
            '/usr/lib/freecad/lib/',
            '/usr/share/freecad/Mod/',
            '/usr/local/lib/freecad/lib/',
        ]
        
        for path in linux_paths:
            if os.path.exists(path):
                sys.path.insert(0, path)
                logger.info(f"Added Linux FreeCAD path: {path}")
    
    # Add the current directory to path to ensure local modules can be found
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        logger.info(f"Added current directory to path: {current_dir}")
    
    # Log the resulting path for debugging
    logger.info(f"Updated sys.path: {sys.path}")
    
    return True
