"""Render Word-exported PDFs and audit Phase 6 artifacts without printing secrets."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile
from xml.etree import ElementTree as ET

from docx import Document
from PIL import Image
from pdf2image import convert_from_path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--poppler-path', required=True)
    args = parser.parse_args()
    qa = ROOT / '.qa/phase6-render'
    env_text = (ROOT / '.env').read_text(encoding='utf-8-sig')
    secret_match = re.search(r'^NEO4J_PASSWORD\s*=\s*(.+)$', env_text, flags=re.M)
    assert secret_match, 'Configured password required for private comparison'
    password = secret_match.group(1).strip().strip('\"\'')
    artifacts = []
    for base in ['TONG_QUAN_DU_AN','HUONG_DAN_SU_DUNG']:
        path = ROOT / f'docs/{base}.docx'
        # Word supplies the current Windows user in metadata on Save. Replace that
        # field with the same explicit personal placeholder used on the cover.
        doc = Document(path)
        doc.core_properties.last_modified_by = '[Họ tên sinh viên]'
        doc.save(path)
        with zipfile.ZipFile(path) as z:
            xmls = [z.read(name) for name in z.namelist() if name.endswith(('.xml','.rels'))]
            all_xml = '\n'.join(part.decode('utf-8') for part in xmls)
            assert password not in all_xml, 'Secret detected: withheld from output'
            tree = ET.fromstring(z.read('word/document.xml'))
            visible = ' '.join(node.text or '' for node in tree.findall('.//w:t', NS))
            assert not re.search(r'\bTODO\b|AI generated|CHÈN ẢNH',visible,re.I)
            assert not tree.findall('.//w:pBdr', NS), 'Decorative paragraph border remains'
            pictures = len(tree.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline'))
            assert pictures >= (5 if base=='TONG_QUAN_DU_AN' else 13)
            assert 'Tứ giác' in visible and 'quadrilateral' in visible
            for placeholder in ['[Trường]','[Khoa]','[Họ tên sinh viên]','[MSSV]','[Giảng viên]','[Năm học]']:
                assert placeholder in visible
        pdf = qa / f'{base}.pdf'
        pages = PdfReader(pdf).pages
        out = qa / base; out.mkdir(exist_ok=True)
        pngs = convert_from_path(str(pdf),dpi=125,poppler_path=args.poppler_path)
        assert len(pngs)==len(pages)
        page_texts = []
        for i,(png,page) in enumerate(zip(pngs,pages),1):
            png.save(out / f'page-{i:02d}.png')
            text = page.extract_text()
            assert len(text.strip())>100, f'Possible blank page {base}/{i}'
            assert password not in text
            page_texts.append({'page':i,'characters':len(text)})
        artifacts.append({'file':str(path.relative_to(ROOT)).replace('\\','/'),'pages':len(pages),'embedded_images':pictures,'page_text_checks':page_texts,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    readme = (ROOT/'README.md').read_text(encoding='utf-8')
    assert len(re.findall(r'^## \d+\.',readme,re.M))==26
    assert password not in readme
    for target in re.findall(r'\]\(([^)]+)\)',readme):
        if not target.startswith(('http','mailto','#')):
            assert (ROOT/target.split('#')[0]).exists(), f'Missing README link: {target}'
    images = []
    for path in sorted((ROOT/'docs/images/phase5').glob('*.jpg')) + [ROOT/'docs/images/04_search_hinh_vuong.jpg']:
        with Image.open(path) as im:
            images.append({'file':str(path.relative_to(ROOT)).replace('\\','/'),'width':im.width,'height':im.height,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    original = json.loads((ROOT/'docs/PHASE_5_RESULTS.json').read_text(encoding='utf-8'))
    for prior in original['screenshots']:
        assert hashlib.sha256((ROOT/prior['file']).read_bytes()).hexdigest()==prior['sha256']
    result={'status':'STRUCTURAL_PASS','renderer':'Microsoft Word ExportAsFixedFormat + bundled Poppler','packaged_renderer_limitation':'LibreOffice soffice.exe missing','artifacts':artifacts,'screenshot_count':len(images),'secret_value_matches':0,'readme_sections':26,'readme_local_links':'PASS','visual_review':'pending'}
    (ROOT/'docs/PHASE_6_IMAGE_MANIFEST.json').write_text(json.dumps(images,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'docs/PHASE_6_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'pages':[a['pages'] for a in artifacts],'images':len(images),'secret_value_matches':0},ensure_ascii=False))


if __name__=='__main__':
    main()
