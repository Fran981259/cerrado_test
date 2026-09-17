import os
import tempfile
import uuid
import logging
from html2image import Html2Image

logger = logging.getLogger(__name__)

# Initialize html2image. We must disable sandbox in docker root environments.
try:
    hti = Html2Image(custom_flags=['--no-sandbox', '--disable-gpu', '--hide-scrollbars'])
except Exception as e:
    logger.error(f"Failed to initialize Html2Image: {e}")
    hti = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
body {
    margin: 0;
    padding: 0;
    width: 1200px;
    height: 675px;
    background: linear-gradient(135deg, #18181b 0%, #27272a 100%);
    font-family: 'Inter', sans-serif;
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    box-sizing: border-box;
    padding: 80px;
    position: relative;
}
.brand {
    position: absolute;
    top: 50px;
    left: 80px;
    font-size: 32px;
    font-weight: 900;
    letter-spacing: -1px;
    color: #10b981; /* Emerald */
}
.category {
    font-size: 24px;
    font-weight: 700;
    text-transform: uppercase;
    color: #a1a1aa;
    margin-bottom: 24px;
    border-left: 4px solid #10b981;
    padding-left: 12px;
}
.title {
    font-size: 64px;
    font-weight: 800;
    line-height: 1.15;
    text-align: left;
    width: 100%;
    margin-bottom: 40px;
}
.footer {
    position: absolute;
    bottom: 50px;
    left: 80px;
    font-size: 22px;
    color: #71717a;
    font-weight: 500;
}
</style>
</head>
<body>
    <div class="brand">Portal Cerrado</div>
    <div class="category">{category}</div>
    <div class="title">{title}</div>
    <div class="footer">Ler no portalcerrado.com.br</div>
</body>
</html>
"""

def generate_twitter_image(title: str, category: str) -> str:
    """Generates an image for Twitter using html2image and returns the temp file path."""
    if not hti:
        raise RuntimeError("html2image is not initialized")
    
    # Escape simple HTML entities in title
    safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_category = category.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html_content = HTML_TEMPLATE.format(title=safe_title, category=safe_category)
    output_filename = f"post_{uuid.uuid4().hex}.png"
    output_path = os.path.join(tempfile.gettempdir(), output_filename)
    
    hti.output_path = tempfile.gettempdir()
    hti.screenshot(html_str=html_content, save_as=output_filename, size=(1200, 675))
    
    if not os.path.exists(output_path):
        raise FileNotFoundError("Image was not generated correctly.")
        
    return output_path
