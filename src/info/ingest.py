# ingest.py — robust, regex-based splitting + normalize (keep newlines)
from pathlib import Path
import re
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

# --------- Config ---------
DATA_DIR = Path("src/info/data")
PERSIST_DIR = "chroma_db"
EMBED_MODEL = "models/text-embedding-004"

# --------- Load docs (keep raw markdown) ---------
if not DATA_DIR.exists() or not DATA_DIR.is_dir():
    raise FileNotFoundError(f"❌ Không thấy thư mục {DATA_DIR.resolve()} — hãy tạo và đặt file .md vào đó.")

loader = DirectoryLoader(
    str(DATA_DIR),
    glob="*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
docs = loader.load()

for d in docs:
    d.metadata["source"] = Path(d.metadata.get("source", "")).name

print(f"📂 Loaded {len(docs)} docs từ {len(list(DATA_DIR.glob('*.md')))} file")

# --------- Preprocess / Normalize (keep newlines!) ---------
def preprocess_keep_newlines(text: str) -> str:
    # normalize newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # convert HTML headings <h1..h4> to markdown headings with newline padding
    for i in range(1, 5):
        text = re.sub(
            rf"<h{i}[^>]*>(.*?)</h{i}>",
            lambda m: "\n" + ("#" * i) + " " + m.group(1).strip() + "\n",
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

    # replace <br> with newline
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    # convert <li>...</li> to "- ..." (preserve lines)
    text = re.sub(r"<li[^>]*>(.*?)</li>", lambda m: "- " + m.group(1).strip() + "\n", text, flags=re.IGNORECASE | re.DOTALL)

    # remove container tags but keep contents/newlines
    text = re.sub(r"</?(ol|ul|p|div)[^>]*>", "\n", text, flags=re.IGNORECASE)

    # remove align attr occurrences (leave tag content unchanged)
    text = re.sub(r'\s*align="[^"]*"', '', text, flags=re.IGNORECASE)

    # remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # remove a few decorative chars (safe list)
    text = text.replace("✨", " ").replace("•", " ").replace("·", " ").replace("\u200b", "")
    text = text.replace("—", "-").replace("–", "-")

    # collapse multiple spaces on each line, trim trailing spaces per line
    text = "\n".join([re.sub(r"[ \t]+", " ", line).rstrip() for line in text.splitlines()])

    # collapse 3+ blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # strip outer
    return text.strip()

# --------- Regex split by heading lines (robust) ---------
heading_re = re.compile(r'^(##)\s*(.+)', re.MULTILINE)

def split_by_headings_regex(text: str, source: str):
    """
    Chia văn bản thành các Document khi gặp heading cấp 2 (## ...)
    Giữ phần mở đầu (trước heading đầu tiên) nếu có.
    Heading khác (#, ###, ####...) không tách riêng mà nằm trong phần nội dung.
    """
    matches = list(heading_re.finditer(text))
    docs_out = []

    if not matches:
        # no heading found -> return whole doc
        docs_out.append(Document(page_content=text.strip(), metadata={"source": source, "heading": None}))
        return docs_out

    # capture intro before first heading
    first = matches[0]
    intro = text[: first.start()].strip()
    if intro:
        docs_out.append(Document(page_content=intro, metadata={"source": source, "heading": "__INTRO__"}))

    # for each heading, slice up to next heading
    for i, m in enumerate(matches):
        heading_line = m.group(0).strip()
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        content = text[start:end].strip()
        combined = heading_line + ("\n\n" + content if content else "")
        docs_out.append(Document(page_content=combined.strip(), metadata={"source": source, "heading": heading_line}))
    return docs_out

# --------- Run preprocess + split ---------
docs_by_heading = []
for d in docs:
    raw = d.page_content
    pre = preprocess_keep_newlines(raw)
    # debug: show first 200 chars of preprocessed
    print(f"\n--- {d.metadata['source']} (preview 200 chars) ---\n{pre[:200].replace(chr(10),'↵')}\n")
    splitted = split_by_headings_regex(pre, d.metadata["source"])
    print(f" -> splitted into {len(splitted)} sections")
    docs_by_heading.extend(splitted)

print(f"\n🔹 Total sections after heading-split -> {len(docs_by_heading)}")

# If nothing (very unlikely), create doc per original file
if not docs_by_heading:
    for d in docs:
        docs_by_heading.append(Document(page_content=d.page_content, metadata={"source": d.metadata.get("source"), "heading": None}))

# --------- Further chunking by token/characters ---------
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
    add_start_index=True,
)

chunks = recursive_splitter.split_documents(docs_by_heading)
print(f"📑 Total chunks after recursive split -> {len(chunks)}")

# debug print few chunk headings
for i, c in enumerate(chunks[:10]):
    print(f"CHUNK {i}: source={c.metadata.get('source')} heading={c.metadata.get('heading')} preview={c.page_content[:100].replace(chr(10),'↵')}")

# --------- Add chunk_id metadata ---------
for i, c in enumerate(chunks):
    c.metadata["chunk_id"] = f"{c.metadata.get('source','unk')}_{i}"

# --------- Embeddings + persist ---------
if not chunks:
    print("⚠️ No chunks to embed — aborting.")
else:
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=os.getenv("GOOGLE_API_KEY"))
    vs = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
    )
    vs.persist()
    print(f"\n✅ Ingest xong {len(chunks)} chunks. Chroma lưu tại: ./{PERSIST_DIR}")
