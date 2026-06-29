import os
import sys
import fitz  # PyMuPDF
import time

try:
    from docx2pdf import convert as docx_to_pdf
except ImportError:
    docx_to_pdf = None

# สำหรับ Excel และ PowerPoint
try:
    import win32com.client
    win32_client = win32com.client
except ImportError:
    win32_client = None

def convert_excel_to_pdf(input_path, output_path):
    if not win32_client:
        raise ImportError("กรุณาติดตั้ง pywin32 โดยรัน 'pip install pywin32'")
    excel = win32_client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    try:
        wb = excel.Workbooks.Open(os.path.abspath(input_path))
        # Type 0 is PDF
        wb.ExportAsFixedFormat(0, os.path.abspath(output_path))
        wb.Close(False)
    finally:
        excel.Quit()

def convert_ppt_to_pdf(input_path, output_path):
    if not win32_client:
        raise ImportError("กรุณาติดตั้ง pywin32 โดยรัน 'pip install pywin32'")
    powerpoint = win32_client.DispatchEx("Powerpoint.Application")
    # powerpoint.Visible = True # PowerPoint optimization
    try:
        deck = powerpoint.Presentations.Open(os.path.abspath(input_path), WithWindow=False)
        # Type 32 is PDF
        deck.SaveAs(os.path.abspath(output_path), 32)
        deck.Close()
    finally:
        powerpoint.Quit()

def process_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_folder = os.path.join(os.path.dirname(file_path), f"{base_name}_Pages")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    temp_pdf = os.path.join(output_folder, f"temp_{int(time.time())}.pdf")
    pdf_path = None

    try:
        if ext in ['.doc', '.docx']:
            print(f"กำลังแปลง Word -> PDF: {os.path.basename(file_path)}")
            if docx_to_pdf:
                docx_to_pdf(file_path, temp_pdf)
                pdf_path = temp_pdf
            else:
                print("[!] ผิดพลาด: ไม่พบไลบรารี docx2pdf")
                return

        elif ext in ['.xls', '.xlsx']:
            print(f"กำลังแปลง Excel -> PDF: {os.path.basename(file_path)}")
            convert_excel_to_pdf(file_path, temp_pdf)
            pdf_path = temp_pdf

        elif ext in ['.ppt', '.pptx']:
            print(f"กำลังแปลง PowerPoint -> PDF: {os.path.basename(file_path)}")
            convert_ppt_to_pdf(file_path, temp_pdf)
            pdf_path = temp_pdf

        elif ext == '.pdf':
            print(f"กำลังประมวลผล PDF: {os.path.basename(file_path)}")
            pdf_path = file_path
        else:
            print(f"[!] ไม่รองรับไฟล์นามสกุล: {ext}")
            return

        # แยกหน้า PDF ออกมาเป็นหน้าย่อยๆ
        if pdf_path and os.path.exists(pdf_path):
            doc = fitz.open(pdf_path)
            print(f"พบ {len(doc)} หน้า กำลังแยกหน้าเป็น PDF...")

            for page_num in range(len(doc)):
                # สร้าง PDF ใหม่สำหรับหน้าเดียว
                new_doc = fitz.open()
                # คัดลอกหน้าเฉพาะเจาะจงมา (รักษาความเป็นข้อความ/Vector ไว้)
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                output_filename = f"Page_{page_num + 1}.pdf"
                output_path = os.path.join(output_folder, output_filename)
                
                # บันทึกโดยรักษาโครงสร้างเดิม
                new_doc.save(output_path, garbage=3, deflate=True)
                new_doc.close()
                print(f"-> {output_filename}")

            doc.close()
        
        # ลบไฟล์ชั่วคราว
        if pdf_path == temp_pdf and os.path.exists(temp_pdf):
            try:
                os.remove(temp_pdf)
            except:
                pass

        print(f"สำเร็จ! ดูผลลัพธ์ได้ที่โฟลเดอร์: {os.path.basename(output_folder)}")

    except Exception as e:
        print(f"[X] เกิดข้อผิดพลาดกับไฟล์ {os.path.basename(file_path)}: {e}")

if __name__ == "__main__":
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.exists(arg):
                if os.path.isfile(arg):
                    process_file(arg)
                elif os.path.isdir(arg):
                    for f in os.listdir(arg):
                        full_path = os.path.join(arg, f)
                        if os.path.isfile(full_path):
                            process_file(full_path)
        print("\nเสร็จสิ้นทุกรายการ")
    else:
        print("กรุณาลากไฟล์มาวางบนไฟล์ .bat")
        input("กด Enter เพื่อปิด...")
