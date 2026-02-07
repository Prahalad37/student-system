from celery import shared_task
from django.template.loader import get_template
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from .models import ExamScore, StudyMaterial

@shared_task
def generate_marksheet_pdf_task(score_id):
    """
    This task runs in the background. 
    It generates the PDF and saves it to the database 
    so the user can download it later.
    """
    try:
        # 1. Fetch Data
        score = ExamScore.objects.get(id=score_id)
        
        # 2. Calculate Logic (Same as before)
        total_obtained = score.maths + score.physics + score.chemistry + score.english + score.computer
        percentage = round((total_obtained / 500) * 100, 2)
        
        context = {
            'score': score, 'student': score.student, 
            'total_obtained': total_obtained, 'percentage': percentage,
            'school': score.student.school
        }

        # 3. Render HTML
        template = get_template('marksheet_pdf.html')
        html = template.render(context)

        # 4. Generate PDF
        pdf_file = ContentFile(b'')
        pisa_status = pisa.CreatePDF(html, dest=pdf_file)

        if not pisa_status.err:
            # Save the PDF to the model field
            filename = f"Report_{score.student.firstname}_{score.exam_name}.pdf"
            score.generated_report.save(filename, pdf_file)
            score.save()
            
            print(f"✅ PDF Saved to Database: {filename}")
            return f"Saved: {filename}"
            
    except ExamScore.DoesNotExist:
        return "Error: Score not found"
