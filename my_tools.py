from pypdf import PdfReader

def read_file(file_path):
    full_text = ""
    
    # 判断是否为pdf文件
    if file_path.lower().endswith(".pdf"):
        try:
            reader = PdfReader(file_path)
            # 循环读取每一页的内容
            for page in reader.pages:
                text = page.extract_text()
                print("我正在读第", page, "页")
                if text:
                    full_text += text
        except Exception as e:
           raise Exception(f"读取失败: {e}")
    else:
        # 如果不是PDF，就当作txt文本读取（多层兜底防崩溃）
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                full_text = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="gbk") as f:
                    full_text = f.read()
            except UnicodeDecodeError:
                # 终极兜底：忽略无法解析的字符，强行读取
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    full_text = f.read()

    # 👇 这一行必须顶格！不管前面经历了什么，最后必须把篮子交出去！
    return full_text
