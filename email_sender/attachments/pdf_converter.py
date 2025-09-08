import os
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import pdfkit
import mammoth
import pypandoc

class PDFConverter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.check_dependencies()

    def check_dependencies(self):
        self.pdf_support = True
        try:
            import pdfkit
            import mammoth
            import pypandoc
            from reportlab.lib.pagesizes import letter
        except ImportError as e:
            self.pdf_support = False
            self.logger.warning(f"Missing PDF conversion dependency: {e}")

    def convert_file_to_pdf(self, file_path):
        """Convert various file types to PDF"""
        if not PDF_SUPPORT:
            self.logger.warning("PDF conversion libraries not installed, skipping conversion")
            return None
            
        output_pdf = os.path.splitext(file_path)[0] + ".pdf"
        
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in ['.html', '.htm']:
                pdfkit.from_file(file_path, output_pdf)
                self.logger.info(f"Converted HTML to PDF: {output_pdf}")
                
            elif file_extension in ['.docx', '.doc']:
                with open(file_path, "rb") as docx_file:
                    result = mammoth.convert_to_html(docx_file)
                    html = result.value
                
                with open("temp.html", "w", encoding="utf-8") as html_file:
                    html_file.write(html)
                
                pdfkit.from_file("temp.html", output_pdf)
                if os.path.exists("temp.html"):
                    os.remove("temp.html")
                self.logger.info(f"Converted DOCX to PDF: {output_pdf}")
                
            elif file_extension in ['.txt']:
                doc = SimpleDocTemplate(output_pdf, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    text = txt_file.read()
                
                paragraphs = text.split('\n\n')
                for paragraph in paragraphs:
                    p = Paragraph(paragraph.replace('\n', '<br />'), styles['Normal'])
                    story.append(p)
                    story.append(Spacer(1, 0.2 * inch))
                
                doc.build(story)
                self.logger.info(f"Converted TXT to PDF: {output_pdf}")
                
            elif file_extension in ['.svg']:
                self.logger.warning(f"SVG to PDF conversion not supported: {file_path}")
                return None
                
            else:
                self.logger.warning(f"Unsupported file type for conversion: {file_path}")
                return None
                
            if os.path.exists(output_pdf):
                return output_pdf
                
        except Exception as e:
            self.logger.error(f"Error converting {file_path} to PDF: {e}")
        return None