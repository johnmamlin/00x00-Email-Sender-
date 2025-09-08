import os
import logging
import base64

class AttachmentLoader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            from .pdf_converter import PDFConverter
            self.pdf_converter = PDFConverter()
            self.PDF_SUPPORT = True
        except ImportError:
            self.PDF_SUPPORT = False
            self.logger.warning("PDF conversion disabled - pdf_converter not found")

    def load_attachments(self, attachments_dir, convert_to_pdf=False):
        """Load attachments from a directory"""
        attachments = []
        if os.path.exists(attachments_dir) and os.path.isdir(attachments_dir):
            for filename in os.listdir(attachments_dir):
                filepath = os.path.join(attachments_dir, filename)
                if os.path.isfile(filepath):
                    if convert_to_pdf and self.PDF_SUPPORT:
                        file_ext = os.path.splitext(filename)[1].lower()
                        convertible_exts = ['.html', '.htm', '.docx', '.doc', '.txt']
                        
                        if file_ext in convertible_exts:
                            pdf_path = self.pdf_converter.convert_file_to_pdf(filepath)
                            if pdf_path and os.path.exists(pdf_path):
                                with open(pdf_path, "rb") as f:
                                    pdf_name = os.path.basename(pdf_path)
                                    attachments.append((pdf_name, f.read()))
                                continue
                    
                    if filename.lower().endswith('.svg'):
                        with open(filepath, "rb") as f:
                            svg_data = f.read()
                            attachments.append((filename, svg_data))
                            self.logger.info(f"Added SVG attachment: {filename}")
                    else:
                        with open(filepath, "rb") as f:
                            attachments.append((filename, f.read()))
        return attachments