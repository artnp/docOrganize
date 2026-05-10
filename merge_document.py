import os
import sys
import time
import io
import shutil
import re

# บังคับใช้ UTF-8 เพื่อรองรับภาษาไทย
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# พยายามโหลด library สำคัญ
try:
    import fitz  # PyMuPDF
except Exception as e:
    print(f"[X] ไม่สามารถโหลด PyMuPDF (fitz): {e}")
    sys.exit(1)

try:
    from docx2pdf import convert as docx_to_pdf
except ImportError:
    docx_to_pdf = None

try:
    import win32com.client
    win32_client = win32com.client
except ImportError:
    win32_client = None

def natural_sort_key(s):
    """ฟังก์ชันช่วยเรียงลำดับชื่อไฟล์ที่มีตัวเลขให้ถูกต้อง (เช่น 1, 2, 10 แทนที่จะเป็น 1, 10, 2)"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def convert_to_pdf(input_path, temp_folder):
    """แปลงไฟล์เป็น PDF"""
    try:
        ext = os.path.splitext(input_path)[1].lower().strip()
        temp_pdf = os.path.join(temp_folder, f"temp_{int(time.time()*1000)}.pdf")
        
        if ext == '.pdf':
            return input_path
        
        if ext in ['.jpg', '.jpeg', '.png']:
            imgdoc = fitz.open(input_path)
            # อ่านขนาดรูปภาพต้นฉบับ
            pix = imgdoc[0].get_pixmap()
            
            # กำหนดขนาดสูงสุด (3000px คือคุณภาพสูงมากเพียงพอสำหรับตัวหนังสือเล็กๆ)
            MAX_DIM = 3000
            if pix.width > MAX_DIM or pix.height > MAX_DIM:
                scale = MAX_DIM / max(pix.width, pix.height)
                pix = imgdoc[0].get_pixmap(matrix=fitz.Matrix(scale, scale))
            
            # บีบอัดข้อมูลรูปภาพเป็น JPEG
            img_data = pix.tobytes("jpg")
            
            pdf_doc = fitz.open()
            page = pdf_doc.new_page(width=pix.width, height=pix.height)
            page.insert_image(page.rect, stream=img_data)
            
            pdf_doc.save(temp_pdf, garbage=4, deflate=True)
            pdf_doc.close()
            imgdoc.close()
            return temp_pdf

        if ext in ['.doc', '.docx']:
            if docx_to_pdf:
                docx_to_pdf(input_path, temp_pdf)
                return temp_pdf

        elif ext in ['.xls', '.xlsx'] and win32_client:
            excel = win32_client.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            try:
                wb = excel.Workbooks.Open(os.path.abspath(input_path))
                wb.ExportAsFixedFormat(0, os.path.abspath(temp_pdf))
                wb.Close(False)
                return temp_pdf
            finally:
                excel.Quit()

        elif ext in ['.ppt', '.pptx'] and win32_client:
            powerpoint = win32_client.DispatchEx("Powerpoint.Application")
            try:
                deck = powerpoint.Presentations.Open(os.path.abspath(input_path), WithWindow=False)
                deck.SaveAs(os.path.abspath(temp_pdf), 32)
                deck.Close()
                return temp_pdf
            finally:
                powerpoint.Quit()
    except Exception as e:
        print(f"  [X] Error ในการแปลง {os.path.basename(input_path)}: {e}")
    return None

def main():
    raw_inputs = sys.argv[1:]
    
    if not raw_inputs:
        print("[!] ไม่มีไฟล์หรือโฟลเดอร์ถูกส่งเข้ามา")
        return

    all_files_list = []
    # สแกนหาไฟล์ทั้งหมด
    for item in raw_inputs:
        # ทำความสะอาด path (ลบเครื่องหมายคำพูดและช่องว่าง)
        path = os.path.abspath(item.strip().strip('"'))
        
        if os.path.isfile(path):
            all_files_list.append(path)
        elif os.path.isdir(path):
            print(f"[*] ตรวจพบโฟลเดอร์: {path}")
            folder_files = []
            for root, dirs, files in os.walk(path):
                for f in files:
                    folder_files.append(os.path.join(root, f))
            
            # เรียงลำดับไฟล์ภายในโฟลเดอร์แบบ Natural Sort
            folder_files.sort(key=natural_sort_key)
            all_files_list.extend(folder_files)
        else:
            print(f"[?] ไม่รู้จักเส้นทางนี้: {path}")

    # กรองไฟล์ซ้ำ และเรียงลำดับไฟล์ทั้งหมดอีกครั้งเพื่อความแน่ใจ
    all_files = []
    seen = set()
    for f in all_files_list:
        if f not in seen:
            all_files.append(f)
            seen.add(f)
    
    # หากผู้ใช้ลากไฟล์มาหลายไฟล์ (ไม่ใช่ลากทั้งโฟลเดอร์) ให้เรียงลำดับตามชื่อไฟล์ด้วย
    # เพื่อป้องกันปัญหาการลากคลุมไฟล์แล้ว Windows ส่งลำดับมาแบบสุ่ม
    all_files.sort(key=natural_sort_key)

    if not all_files:
        print("[!] ไม่พบไฟล์ใดๆ ให้ประมวลผล")
        return

    # กำหนดที่เก็บไฟล์ Output (ข้างๆ ไฟล์/โฟลเดอร์แรกที่ลากมา)
    first_item_path = os.path.abspath(raw_inputs[0].strip().strip('"'))
    output_dir = os.path.dirname(first_item_path)
    
    # สร้างโฟลเดอร์ชั่วคราว
    temp_folder = os.path.join(output_dir, "_temp_work_files")
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    merged_doc = fitz.open()
    count = 0
    valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.jpg', '.jpeg', '.png']

    print(f"[*] เริ่มประมวลผลไฟล์รวม {len(all_files)} รายการ...")

    for f in all_files:
        ext = os.path.splitext(f)[1].lower().strip()
        if ext in valid_extensions:
            # ข้ามไฟล์ที่ชื่อมี _Merged_ เพื่อไม่ให้วนกลับมารวมตัวเอง
            if "_Merged_" in f: continue
            
            print(f"  > Processing: {os.path.basename(f)}")
            pdf_path = convert_to_pdf(f, temp_folder)
            if pdf_path and os.path.exists(pdf_path):
                try:
                    current_pdf = fitz.open(pdf_path)
                    merged_doc.insert_pdf(current_pdf)
                    current_pdf.close()
                    count += 1
                except Exception as e:
                    print(f"  [X] รวมไม่ได้: {f} ({e})")
        else:
            # ไม่ต้องแสดงไฟล์ที่ไม่รองรับเพื่อลดความรกรุงรัง ยกเว้นเป็นไฟล์ที่ตั้งใจลากมา
            pass

    if count > 0:
        # สร้างชื่อไฟล์ผลลัพธ์ตามเวลา
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"Document_Merged_{timestamp}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"[*] กำลังบันทึกและบีบอัดไฟล์รวม...")
        # ใช้ garbage=4, deflate=True, clean=True, และ use_objstms=True เพื่อบีบอัดขนาดไฟล์ให้เล็กที่สุด
        merged_doc.save(output_path, garbage=4, deflate=True, clean=True, use_objstms=True)
        merged_doc.close()
        
        # คำนวณขนาดไฟล์
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"\n" + "="*50)
        print(f"[สำเร็จ] รวมไฟล์ทั้งหมด {count} รายการ")
        print(f"ไฟล์ที่ได้: {output_filename}")
        print(f"ขนาดไฟล์: {file_size:.2f} MB")
        print(f"อยู่ที่: {output_dir}")
        print("="*50)
    else:
        print("\n[!] ไม่มีไฟล์ที่รองรับการรวม")

    # ล้างไฟล์ชั่วคราว
    shutil.rmtree(temp_folder, ignore_errors=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[CRITICAL ERROR] เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
        import traceback
        traceback.print_exc()
