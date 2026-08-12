import os
import fitz
from app.core.logger import log_event, STATUS_SUCCESS, STATUS_FAILURE

def search_pdf(
    pdf_path: str,
    query: str,
    case_sensitive: bool = False
) -> list[dict]:
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")
            
        if not query:
            raise ValueError("Query string cannot be empty")
            
        results = []
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            
            search_text = text if case_sensitive else text.lower()
            search_query = query if case_sensitive else query.lower()
            
            start_idx = 0
            while True:
                match_pos = search_text.find(search_query, start_idx)
                if match_pos == -1:
                    break
                
                start_context = max(0, match_pos - 50)
                end_context = min(len(text), match_pos + len(query) + 50)
                snippet = text[start_context:end_context].strip()
                
                results.append({
                    "page": page_num + 1,
                    "snippet": snippet
                })
                
                start_idx = match_pos + len(query)
                
        doc.close()
        
        log_event("search_pdf", "search", STATUS_SUCCESS, f"Found {len(results)} matches for '{query}' in {pdf_path}")
        return results
        
    except (FileNotFoundError, ValueError):
        raise
    except Exception as e:
        log_event("search_pdf", "search", STATUS_FAILURE, str(e))
        raise RuntimeError(f"Failed to search PDF: {e}") from e
