
import os
from docx import Document
from jinja2 import Environment, FileSystemLoader
import pandas as pd

def fill_word_template(excel_path, word_template_path, word_output_path):
  
    """
    Llena un plantilla de word con datos extraidos de un archivo excel, utilizando jinja2.

    Args:

    excel_path (str) : ruta del archivo de Excel
    word_template_path (str) : Ruta de la plantilla de word
    word_outh_path (str) : Ruta donde se guardara el documento word final.

    """
    df = pd.read_excel(excel_path)
    env = Environment(loader=FileSystemLoader(os.path.dirname(word_template_path)))
    template = env.get_template(os.path.basename(word_template_path))

    for index, row in df.iterrows():
        data = {
            'determinacion_causa': row['determinacion_causa'],
            'medidas_tomadas': row['medidas_tomadas'],
            'fecha_inicio': row['fecha_inicio'].strftime('%d/%m%Y'),
            'fecha_fin': row['fecha_fin'].strftime('%d/%m%Y')
        }
        document = Document(word_template_path)
        document.add_paragraph(template.render(data))
        document.save(f"{word_output_path}reporte_Ticket_{index+1}.docx")
        print(f"Ticket {index+1} generado exitosamente.")

if __name__ == "__main__":
    excel_path = os.path.abspath("media/pronatel/data/DataTicketsPronatel.xlsx")
    word_template_path = os.path.abspath("media/pronatel/plantilla/plantilla_word.docx")
    word_output_path = os.path.abspath("media/pronatel/reportes/")

    fill_word_template(excel_path, word_template_path, word_output_path)
















