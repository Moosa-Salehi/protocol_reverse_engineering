"""Screenshot one element of a protocol_report.html with Windows headless Chrome (case-study figures of the thesis).
Every sibling along the element's ancestor path is hidden, so the element keeps its page context and styles; the
image is then trimmed to the content (plus a margin) and optionally cropped to a width.
usage: python3 shoot.py <report.html> <element id> <out.png> [--width CSS_PX] [--crop-width PX] [--crop-height PX]"""
import argparse, os, subprocess, tempfile
from PIL import Image, ImageChops

CHROME = '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'
HERE = os.path.dirname(os.path.abspath(__file__))
ISOLATE = """<style>html, body { background: #f3f3f1 !important; background-image: none !important; }
body::before, body::after { display: none !important; }</style><script>
window.addEventListener('load', () => {
  let el = document.getElementById(%r);
  for (let node = el; node && node.parentElement; node = node.parentElement)
    for (const sib of node.parentElement.children) if (sib !== node && sib.tagName !== 'SCRIPT' && sib.tagName !== 'STYLE') sib.style.display = 'none';
  el.style.marginTop = '24px'; window.scrollTo(0, 0);
  document.querySelectorAll('details').forEach(d => d.open = true);
});
</script>"""

def win(path):
    path = os.path.abspath(path)
    assert path.startswith('/mnt/'), path
    return path[5].upper() + ':' + path[6:].replace('/', '\\')

ap = argparse.ArgumentParser()
ap.add_argument('html'); ap.add_argument('element'); ap.add_argument('out')
ap.add_argument('--width', type=int, default=960); ap.add_argument('--crop-width', type=int); ap.add_argument('--crop-height', type=int)
a = ap.parse_args()
work = os.path.join(HERE, 'shots'); os.makedirs(work, exist_ok=True)
page = os.path.join(work, 'page.html'); raw = os.path.join(work, 'raw.png')
html = open(a.html, encoding='utf-8').read().replace('</body>', ISOLATE % a.element + '</body>')
open(page, 'w', encoding='utf-8').write(html)
if os.path.exists(raw):
    os.remove(raw)
subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=2', '--blink-settings=preferredColorScheme=1',
                f'--window-size={a.width},4000', '--virtual-time-budget=4000', f'--screenshot={win(raw)}',
                'file:///' + win(page).replace('\\', '/')], check=True, capture_output=True, timeout=120)
img = Image.open(raw).convert('RGB')
bg = Image.new('RGB', img.size, (0xf3, 0xf3, 0xf1))
box = ImageChops.difference(img, bg).point(lambda v: 255 if v > 12 else 0).getbbox()
left, top, right, bottom = box
img = img.crop((max(0, left - 20), max(0, top - 20), min(img.width, right + 20), min(img.height, bottom + 20)))
if a.crop_width or a.crop_height:
    img = img.crop((0, 0, min(img.width, a.crop_width or img.width), min(img.height, a.crop_height or img.height)))
img.save(a.out)
print(a.out, img.size)
