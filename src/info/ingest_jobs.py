from pathlib import Path
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path("src/info/data")
PERSIST_DIR = "chroma_db"
EMBED_MODEL = "models/text-embedding-004"

if not DATA_DIR.exists():
    raise FileNotFoundError(f"❌ Không thấy {DATA_DIR}")

# Chỉ load cleaning.md và healthcare.md
job_files = ["cleaning.md", "healthcare.md"]
docs = []

for filename in job_files:
    file_path = DATA_DIR / filename
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        docs.append(Document(page_content=content, metadata={"source": filename}))
        print(f"📂 Loaded {filename}")

print(f"📂 Total: {len(docs)} docs")

def preprocess_keep_newlines(text: str) -> str:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    for i in range(1, 5):
        text = re.sub(
            rf"<h{i}[^>]*>(.*?)</h{i}>",
            lambda m: "\n" + ("#" * i) + " " + m.group(1).strip() + "\n",
            text,
            flags=re.IGNORECASE | re.DOTALL
        )
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>(.*?)</li>", lambda m: "- " + m.group(1).strip() + "\n", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"</?(ol|ul|p|div)[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r'\s*align="[^"]*"', '', text, flags=re.IGNORECASE)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = text.replace("✨", " ").replace("•", " ").replace("·", " ").replace("\u200b", "")
    text = text.replace("—", "-").replace("–", "-")
    text = "\n".join([re.sub(r"[ \t]+", " ", line).rstrip() for line in text.splitlines()])
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

heading_re = re.compile(r'^(##)\s*(.+)', re.MULTILINE)

def split_by_headings_regex(text: str, source: str):
    matches = list(heading_re.finditer(text))
    docs_out = []
    
    if not matches:
        docs_out.append(Document(page_content=text.strip(), metadata={"source": source, "heading": None}))
        return docs_out
    
    first = matches[0]
    intro = text[: first.start()].strip()
    if intro:
        docs_out.append(Document(page_content=intro, metadata={"source": source, "heading": "__INTRO__"}))
    
    for i, m in enumerate(matches):
        heading_line = m.group(0).strip()
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        content = text[start:end].strip()
        combined = heading_line + ("\n\n" + content if content else "")
        docs_out.append(Document(page_content=combined.strip(), metadata={"source": source, "heading": heading_line}))
    return docs_out

docs_by_heading = []
for d in docs:
    raw = d.page_content
    pre = preprocess_keep_newlines(raw)
    splitted = split_by_headings_regex(pre, d.metadata["source"])
    print(f" -> {d.metadata['source']}: {len(splitted)} sections")
    docs_by_heading.extend(splitted)

print(f"🔹 Total sections: {len(docs_by_heading)}")

recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
    add_start_index=True,
)

chunks = recursive_splitter.split_documents(docs_by_heading)
print(f"📑 Total chunks: {len(chunks)}")

for i, c in enumerate(chunks):
    c.metadata["chunk_id"] = f"{c.metadata.get('source','unk')}_{i}"

if not chunks:
    print("⚠️ No chunks")
else:
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=os.getenv("GOOGLE_API_KEY"))
    vs = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
    )
    print(f"✅ Ingest xong {len(chunks)} chunks. Chroma lưu tại: ./{PERSIST_DIR}")
