import os
import sys
import time
import io

# บังคับใช้ UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ตรวจสอบ Library และพยายามติดตั้งอัตโนมัติหากไม่พบ
try:
    import fitz  # PyMuPDF
except ImportError:
    import subprocess
    print("\n[*] ไม่พบไลบรารี PyMuPDF กำลังทำการติดตั้งให้โดยอัตโนมัติ...")
    try:
        # สั่งติดตั้งโดยใช้ Python ตัวปัจจุบันที่กำลังรันอยู่ (แก้ปัญหา Python หลายตัวในเครื่อง)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf"])
        import fitz
        print("[+] ติดตั้งสำเร็จ! กำลังดำเนินการต่อ...\n")
    except Exception as e:
        print(f"\n[X] ไม่สามารถติดตั้งอัตโนมัติได้: {e}")
        print("[*] กรุณารันคำสั่งนี้ด้วยตัวเอง: pip install pymupdf")
        print("-" * 50)
        input("กด Enter เพื่อปิด...")
        sys.exit(1)

def convert_image_to_pdf(input_path):
    try:
        ext = os.path.splitext(input_path)[1].lower().strip()
        valid_exts = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        if ext not in valid_exts:
            print(f"  [-] ข้ามไฟล์ (นามสกุล {ext} ไม่รองรับ): {os.path.basename(input_path)}")
            return None

        # ตั้งชื่อไฟล์ขาออก (เปลี่ยนนามสกุลเป็น .pdf)
        output_path = os.path.splitext(input_path)[0] + ".pdf"
        
        print(f"[*] กำลังแปลง: {os.path.basename(input_path)}")
        
        imgdoc = fitz.open(input_path)
        # ตรวจสอบว่ามีหน้าไหม (ปกติรูปภาพจะมี 1 หน้า)
        if len(imgdoc) == 0:
            imgdoc.close()
            return None
            
        pix = imgdoc[0].get_pixmap()
        
        # กำหนดความละเอียดสูงสุด (3000px) เพื่อความคมชัดของตัวหนังสือ
        MAX_DIM = 3000
        if pix.width > MAX_DIM or pix.height > MAX_DIM:
            scale = MAX_DIM / max(pix.width, pix.height)
            pix = imgdoc[0].get_pixmap(matrix=fitz.Matrix(scale, scale))
        
        # บีบอัดเป็น JPEG เพื่อลดขนาดไฟล์ (แต่ยังคงความชัด)
        img_data = pix.tobytes("jpg")
        
        pdf_doc = fitz.open()
        page = pdf_doc.new_page(width=pix.width, height=pix.height)
        page.insert_image(page.rect, stream=img_data)
        
        # บันทึกด้วยโหมดบีบอัดสูงสุด
        pdf_doc.save(output_path, garbage=4, deflate=True, clean=True, use_objstms=True)
        
        file_size = os.path.getsize(output_path) / 1024
        print(f"  [+] สำเร็จ: {os.path.basename(output_path)} ({file_size:.1f} KB)")
        
        pdf_doc.close()
        imgdoc.close()
        return output_path
        
    except Exception as e:
        print(f"  [X] ข้อผิดพลาด {os.path.basename(input_path)}: {e}")
        return None

def main():
    print(f"[*] เริ่มทำงาน (Python: {sys.version.split()[0]})")
    if len(sys.argv) < 2:
        print("[!] กรุณาลากไฟล์มาวางบนไอคอน")
        return

    inputs = sys.argv[1:]
    all_files = []
    
    for item in inputs:
        path = os.path.abspath(item.strip().strip('"'))
        if os.path.isfile(path):
            all_files.append(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    all_files.append(os.path.join(root, f))

    print(f"[*] ตรวจพบไฟล์ที่เข้าข่าย: {len(all_files)} รายการ")

    count = 0
    for f in all_files:
        if convert_image_to_pdf(f):
            count += 1
            
    if count > 0:
        print(f"\n[สำเร็จ] แปลงไฟล์ทั้งหมด {count} รายการ")
    else:
        print("\n[!] ไม่พบไฟล์ภาพที่รองรับ")

if __name__ == "__main__":
    main()
