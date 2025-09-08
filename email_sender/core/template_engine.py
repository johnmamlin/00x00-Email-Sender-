# In template_engine.py
import os
import glob
import random
import logging

logger = logging.getLogger(__name__)  

def load_template_from_folder(templates_dir, template_name=None):
    """Load a template from templates directory"""
    if not os.path.exists(templates_dir) or not os.path.isdir(templates_dir):
        logger.error(f"Templates directory not found: {templates_dir}")
        return None
        
    if template_name:
        template_path = os.path.join(templates_dir, template_name)
        if os.path.exists(template_path) and os.path.isfile(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logger.error(f"Template not found: {template_path}")
            return None
            
    html_files = glob.glob(os.path.join(templates_dir, "*.html")) + \
                 glob.glob(os.path.join(templates_dir, "*.htm"))
    if not html_files:
        logger.error(f"No HTML templates found in: {templates_dir}")
        return None
        
    template_path = random.choice(html_files)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"Loaded template: {template_path}")
            return content
    except Exception as e:
        logger.error(f"Error loading template {template_path}: {e}")
        return None