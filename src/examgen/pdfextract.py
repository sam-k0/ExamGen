import pypdf


class FileContent:
    def __init__(self) -> None:
        self.text_pages = []
    
    # Read fpath and write in text_pages
    def read_file(self, fpath = ""):
        for p in pypdf.PdfReader(fpath).pages:
            self.text_pages.append(p.extract_text() or "")

    def get_all_text(self) -> str:
        return "\n".join(self.text_pages)