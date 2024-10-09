


```python
from modelscope.hub.snapshot_download import snapshot_download
from transformers import AutoTokenizer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import PyPDF2


def extract_text_from_pdf(pdf_file):
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text


pdf_text = extract_text_from_pdf('/Users/xiniao/Downloads/FATF-ME-FATF-HK-FUR-4-1-202302.pdf')
print(pdf_text)

if __name__ == '__main__':
    model_id = 'Qwen/Qwen2.5-72B-Instruct'
    # cache_dir = './models'
    ignore_patterns=['*.safetensors']
    print("开始下载模型")
    model_dir = snapshot_download(model_id, ignore_patterns=ignore_patterns)
    print(model_dir)
    print("开始加载tokenizer")

    tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    print(tokenizer)
    encode = tokenizer.encode('你好')

    print(encode)

    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer, chunk_size=1000, chunk_overlap=100
    )
    texts = text_splitter.split_text(pdf_text)

    for t in texts:
        print("-" * 80)
        print()
        print(t)

```