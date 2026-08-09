import unicodedata
import re
import pdfplumber


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKD", text)


def _table_to_chunks(table: list, table_title: str = "") -> list[str]:
    """
    Tablo satırlarını 'Başlık: değer | ...' formatında chunk'lara çevirir.
    """
    if not table or len(table) < 1:
        return []

    prefix = f"{table_title} — " if table_title else ""

    # İlk dolu satırı header olarak al
    header_row = None
    data_start = 0
    for idx, row in enumerate(table):
        cleaned = [(c or "").strip() for c in row]
        if any(cleaned):
            header_row = [h.replace("\n", " ").strip() for h in cleaned]
            data_start = idx + 1
            break

    if header_row is None:
        return []

    chunks = []
    for row in table[data_start:]:
        cells = [(c or "").replace("\n", " ").strip() for c in row]
        if not any(cells):
            continue
        parts = [
            f"{h}: {c}" if h else c
            for h, c in zip(header_row, cells)
            if c
        ]
        if parts:
            chunks.append(_normalize(prefix + " | ".join(parts)))

    return chunks


def _find_table_title(page, bbox: tuple, prev_page=None) -> str:
    """
    Tablo bbox'ının hemen üstündeki 'Tablo/Table' içeren satırı döndürür.
    Tablo sayfanın çok üstündeyse bir önceki sayfanın sonuna bakar.
    """
    table_top = bbox[1]
    words = page.extract_words()

    above = [
        w for w in words
        if w["bottom"] <= table_top and w["bottom"] >= table_top - 60
    ]
    line = " ".join(
        w["text"] for w in sorted(above, key=lambda w: (w["top"], w["x0"]))
    )

    if re.search(r"(tablo|table)", line, re.IGNORECASE):
        return line[:200]

    # Tablo sayfanın tepesindeyse önceki sayfanın sonuna bak
    if table_top < 100 and prev_page is not None:
        prev_words = prev_page.extract_words()
        if prev_words:
            page_bottom = max(w["bottom"] for w in prev_words)
            bottom_words = [
                w for w in prev_words
                if w["bottom"] >= page_bottom - 60
            ]
            prev_line = " ".join(
                w["text"] for w in sorted(bottom_words, key=lambda w: (w["top"], w["x0"]))
            )
            if re.search(r"(tablo|table)", prev_line, re.IGNORECASE):
                return prev_line[:200]

    return line[:200] if line.strip() else ""


def extract_pdf_content(file_or_path) -> tuple[str, list[str]]:
    """
    PDF'den (düz_metin, tablo_chunk_listesi) döndürür.
    Tablo alanları metin çıkarımından hariç tutulur.

    ⚠️ Closure bug düzeltmesi:
    pdfplumber.filter() fonksiyonuna geçirilen lambda her sayfa için
    ayrı bir 'bboxes' kopyası yakalar; böylece sonraki sayfa işlenirken
    önceki sayfanın bbox listesi kullanılmaz.
    """
    text_parts = []
    table_chunks = []

    with pdfplumber.open(file_or_path) as pdf:
        pages = pdf.pages
        for i, page in enumerate(pages):
            prev_page = pages[i - 1] if i > 0 else None
            tables = page.find_tables()

            # ✅ FIX: bboxes'i fonksiyon parametresi olarak yakala
            # (closure bug: lambda içinde doğrudan 'bboxes' kullanılırsa
            #  döngü bitince tüm sayfalar son sayfanın bboxes'ını görür)
            bboxes = [t.bbox for t in tables]

            def make_filter(bboxes_snapshot):
                def outside_tables(obj):
                    v_mid = (obj["top"] + obj["bottom"]) / 2
                    h_mid = (obj["x0"] + obj["x1"]) / 2
                    for x0, top, x1, bottom in bboxes_snapshot:
                        if x0 <= h_mid <= x1 and top <= v_mid <= bottom:
                            return False
                    return True
                return outside_tables

            page_text = page.filter(make_filter(bboxes)).extract_text()
            if page_text:
                text_parts.append(page_text)

            for t in tables:
                title = _find_table_title(page, t.bbox, prev_page)
                table_chunks.extend(_table_to_chunks(t.extract(), title))

    full_text = _normalize("\n".join(text_parts))
    return full_text, table_chunks
