import json
import random
import re
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Concrete Poetry Studio", layout="wide")


def extract_words(text):
    return re.findall(r"\S+", text)


def clean_words(words):
    cleaned = []
    for w in words:
        w = w.strip()
        if w:
            cleaned.append(w)
    return cleaned


st.title("Concrete Poetry Studio")
st.write(
    "Upload a text file, then drag words around the canvas to create a concrete poem. "
    "You can start from the poem's original layout or from a scattered layout."
)

uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])

default_text = """Concrete poetry bends language into visible form.
Words can scatter, collapse, climb, tilt, float, fracture, bloom, and echo across the page."""

use_sample = st.checkbox("Use sample text if no file is uploaded", value=True)
background_color = st.color_picker("Canvas background color", "#ffffff")
default_text_color = st.color_picker("Default word color", "#111111")

canvas_width = 1100
canvas_height = 700

if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8", errors="ignore")
elif use_sample:
    text = default_text
else:
    text = ""

if not text.strip():
    st.info("Upload a text file or enable sample text to begin.")
    st.stop()

words = clean_words(extract_words(text))

if not words:
    st.info("The text file does not contain readable words.")
    st.stop()

random_words_layout = []
for i, word in enumerate(words):
    random_words_layout.append(
        {
            "id": i,
            "text": word,
            "x": random.randint(20, max(20, canvas_width - 120)),
            "y": random.randint(20, max(20, canvas_height - 80)),
            "size": random.randint(18, 36),
            "rotation": random.randint(-20, 20),
            "color": default_text_color,
            "z": i + 1,
            "fontFamily": "Arial, sans-serif",
        }
    )

original_layout = []
line_spacing = 52
word_spacing_factor = 0.62
left_margin = 30
top_margin = 30
current_id = 0

for line_index, line in enumerate(text.splitlines()):
    line_words = clean_words(extract_words(line))
    x_cursor = left_margin
    y_cursor = top_margin + (line_index * line_spacing)

    for word in line_words:
        approx_width = max(20, int(len(word) * 24 * word_spacing_factor))
        original_layout.append(
            {
                "id": current_id,
                "text": word,
                "x": x_cursor,
                "y": y_cursor,
                "size": 24,
                "rotation": 0,
                "color": default_text_color,
                "z": current_id + 1,
                "fontFamily": "Arial, sans-serif",
            }
        )
        x_cursor += approx_width + 12
        current_id += 1

random_words_json = json.dumps(random_words_layout)
original_layout_json = json.dumps(original_layout)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<title>Concrete Poetry Canvas</title>
<style>
    * {{
        box-sizing: border-box;
        -webkit-user-select: none;
        user-select: none;
    }}

    html, body {{
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        background: #f4f4f4;
    }}

    .wrap {{
        display: flex;
        gap: 16px;
        align-items: flex-start;
        padding: 10px;
    }}

    .panel {{
        width: 280px;
        min-width: 280px;
        background: white;
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}

    .panel h3 {{
        margin-top: 0;
        margin-bottom: 8px;
        font-size: 20px;
    }}

    .panel p {{
        margin-top: 0;
        color: #444;
        font-size: 14px;
        line-height: 1.4;
    }}

    .control-group {{
        margin-bottom: 14px;
    }}

    .control-group label {{
        display: block;
        font-size: 14px;
        margin-bottom: 6px;
        font-weight: 600;
    }}

    .control-group input[type="range"],
    .control-group input[type="color"],
    .control-group input[type="text"],
    .control-group button,
    .control-group select {{
        width: 100%;
    }}

    .control-group input[type="text"],
    .control-group select {{
        padding: 8px;
        border: 1px solid #ccc;
        border-radius: 8px;
        font-size: 14px;
    }}

    .control-group button {{
        padding: 10px 12px;
        border: none;
        border-radius: 10px;
        background: #111111;
        color: white;
        cursor: pointer;
        font-size: 14px;
        margin-top: 6px;
    }}

    .control-group button:hover {{
        opacity: 0.9;
    }}

    .small-note {{
        font-size: 12px;
        color: #666;
        line-height: 1.4;
    }}

    .canvas-wrap {{
        flex: 1;
    }}

    .canvas {{
        position: relative;
        width: {canvas_width}px;
        height: {canvas_height}px;
        background: {background_color};
        border: 2px solid #111;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        user-select: none;
        -webkit-user-select: none;
        touch-action: none;
    }}

    .word {{
        position: absolute;
        display: inline-block;
        cursor: grab;
        white-space: nowrap;
        transform-origin: center center;
        padding: 2px 4px;
        border-radius: 6px;
        user-select: none;
        -webkit-user-select: none;
        touch-action: none;
    }}

    .word:active {{
        cursor: grabbing;
    }}

    .word.selected {{
        outline: 2px dashed #1e88e5;
        outline-offset: 3px;
    }}

    .status {{
        font-size: 13px;
        color: #333;
        margin-top: 6px;
        min-height: 18px;
    }}
</style>
</head>
<body>
<div class="wrap">
    <div class="panel">
        <h3>Word Controls</h3>
        <p>Click a word on the canvas, then change its appearance or move it by dragging.</p>

        <div class="control-group">
            <button id="pasteOriginalBtn">Paste Poem in Original Form</button>
            <button id="scatterBtn">Scatter Words Randomly</button>
        </div>

        <div class="control-group">
            <label for="wordText">Selected word text</label>
            <input type="text" id="wordText" placeholder="No word selected" />
        </div>

        <div class="control-group">
            <label for="fontSize">Font size</label>
            <input type="range" id="fontSize" min="10" max="120" value="24" />
        </div>

        <div class="control-group">
            <label for="rotation">Rotation (degrees)</label>
            <input type="range" id="rotation" min="-180" max="180" value="0" />
        </div>

        <div class="control-group">
            <label for="wordColor">Word color</label>
            <input type="color" id="wordColor" value="{default_text_color}" />
        </div>

        <div class="control-group">
            <label for="fontFamily">Font family</label>
            <select id="fontFamily">
                <option value="Arial, sans-serif">Arial</option>
                <option value="'Times New Roman', serif">Times New Roman</option>
                <option value="'Courier New', monospace">Courier New</option>
                <option value="Georgia, serif">Georgia</option>
                <option value="Verdana, sans-serif">Verdana</option>
                <option value="'Trebuchet MS', sans-serif">Trebuchet MS</option>
            </select>
        </div>

        <div class="control-group">
            <button id="bringFrontBtn">Bring Selected Word to Front</button>
            <button id="deleteBtn">Delete Selected Word</button>
        </div>

        <div class="control-group">
            <button id="randomizeBtn">Randomize Layout</button>
            <button id="resetBtn">Reset to Starting Layout</button>
        </div>

        <div class="control-group">
            <button id="downloadHtmlBtn">Download Poem as HTML</button>
            <button id="downloadJsonBtn">Download Layout as JSON</button>
        </div>

        <div class="small-note">
            Tips:<br>
            • Use "Paste Poem in Original Form" to begin with the poem laid out normally.<br>
            • Drag words to move them.<br>
            • Click a word to edit it.<br>
            • Use large and rotated text to create concrete shapes.
        </div>

        <div class="status" id="status"></div>
    </div>

    <div class="canvas-wrap">
        <div class="canvas" id="canvas"></div>
    </div>
</div>

<script>
    const randomStartWords = {random_words_json};
    const originalLayoutWords = {original_layout_json};

    let words = JSON.parse(JSON.stringify(randomStartWords));
    let selectedId = null;
    let currentZ = words.length + 1;

    const canvas = document.getElementById("canvas");
    const fontSizeInput = document.getElementById("fontSize");
    const rotationInput = document.getElementById("rotation");
    const wordColorInput = document.getElementById("wordColor");
    const wordTextInput = document.getElementById("wordText");
    const fontFamilyInput = document.getElementById("fontFamily");
    const status = document.getElementById("status");

    const wordElements = new Map();

    function clamp(value, min, max) {{
        return Math.max(min, Math.min(max, value));
    }}

    function getWordById(id) {{
        return words.find(w => w.id === id);
    }}

    function updateStatus(message) {{
        status.textContent = message;
    }}

    function applyWordStyle(el, word) {{
        el.textContent = word.text;
        el.style.left = word.x + "px";
        el.style.top = word.y + "px";
        el.style.fontSize = word.size + "px";
        el.style.color = word.color;
        el.style.zIndex = word.z;
        el.style.fontFamily = word.fontFamily || "Arial, sans-serif";
        el.style.transform = `rotate(${{word.rotation}}deg)`;
        el.classList.toggle("selected", word.id === selectedId);
    }}

    function renderWords() {{
        canvas.innerHTML = "";
        wordElements.clear();

        words.forEach(word => {{
            const el = document.createElement("div");
            el.className = "word";
            el.dataset.id = word.id;
            applyWordStyle(el, word);
            el.addEventListener("pointerdown", startDrag);
            canvas.appendChild(el);
            wordElements.set(word.id, el);
        }});
    }}

    function refreshAllWords() {{
        words.forEach(word => {{
            const el = wordElements.get(word.id);
            if (el) {{
                applyWordStyle(el, word);
            }}
        }});
    }}

    function selectWord(id) {{
        selectedId = id;
        const word = getWordById(id);
        if (!word) return;

        fontSizeInput.value = word.size;
        rotationInput.value = word.rotation;
        wordColorInput.value = word.color;
        wordTextInput.value = word.text;
        fontFamilyInput.value = word.fontFamily || "Arial, sans-serif";

        refreshAllWords();
        updateStatus(`Selected: "${{word.text}}"`);
    }}

    function replaceLayout(newLayout, statusMessage) {{
        words = JSON.parse(JSON.stringify(newLayout));
        selectedId = null;
        currentZ = words.length + 1;
        wordTextInput.value = "";
        renderWords();
        updateStatus(statusMessage);
    }}

    canvas.addEventListener("pointerdown", (e) => {{
        if (e.target === canvas) {{
            selectedId = null;
            wordTextInput.value = "";
            refreshAllWords();
            updateStatus("No word selected");
        }}
    }});

    let isDragging = false;
    let dragId = null;
    let dragMoved = false;
    let offsetX = 0;
    let offsetY = 0;

    function startDrag(e) {{
        const target = e.currentTarget;
        const id = Number(target.dataset.id);
        const word = getWordById(id);
        if (!word) return;

        e.preventDefault();
        e.stopPropagation();

        selectWord(id);

        isDragging = true;
        dragId = id;
        dragMoved = false;

        const rect = target.getBoundingClientRect();
        offsetX = e.clientX - rect.left;
        offsetY = e.clientY - rect.top;

        currentZ += 1;
        word.z = currentZ;
        applyWordStyle(target, word);

        target.setPointerCapture(e.pointerId);
        target.addEventListener("pointermove", dragMove);
        target.addEventListener("pointerup", stopDrag);
        target.addEventListener("pointercancel", stopDrag);
    }}

    function dragMove(e) {{
        if (!isDragging || dragId === null) return;

        const word = getWordById(dragId);
        const el = wordElements.get(dragId);
        if (!word || !el) return;

        const canvasRect = canvas.getBoundingClientRect();

        let newX = e.clientX - canvasRect.left - offsetX;
        let newY = e.clientY - canvasRect.top - offsetY;

        newX = clamp(newX, 0, canvas.clientWidth - 20);
        newY = clamp(newY, 0, canvas.clientHeight - 20);

        if (Math.abs(newX - word.x) > 1 || Math.abs(newY - word.y) > 1) {{
            dragMoved = true;
        }}

        word.x = newX;
        word.y = newY;
        el.style.left = word.x + "px";
        el.style.top = word.y + "px";
    }}

    function stopDrag(e) {{
        const target = e.currentTarget;
        target.removeEventListener("pointermove", dragMove);
        target.removeEventListener("pointerup", stopDrag);
        target.removeEventListener("pointercancel", stopDrag);

        isDragging = false;
        dragId = null;

        if (dragMoved) {{
            updateStatus("Word moved");
        }}
    }}

    fontSizeInput.addEventListener("input", () => {{
        if (selectedId === null) return;
        const word = getWordById(selectedId);
        const el = wordElements.get(selectedId);
        if (!word || !el) return;
        word.size = Number(fontSizeInput.value);
        applyWordStyle(el, word);
    }});

    rotationInput.addEventListener("input", () => {{
        if (selectedId === null) return;
        const word = getWordById(selectedId);
        const el = wordElements.get(selectedId);
        if (!word || !el) return;
        word.rotation = Number(rotationInput.value);
        applyWordStyle(el, word);
    }});

    wordColorInput.addEventListener("input", () => {{
        if (selectedId === null) return;
        const word = getWordById(selectedId);
        const el = wordElements.get(selectedId);
        if (!word || !el) return;
        word.color = wordColorInput.value;
        applyWordStyle(el, word);
    }});

    fontFamilyInput.addEventListener("change", () => {{
        if (selectedId === null) return;
        const word = getWordById(selectedId);
        const el = wordElements.get(selectedId);
        if (!word || !el) return;
        word.fontFamily = fontFamilyInput.value;
        applyWordStyle(el, word);
    }});

    wordTextInput.addEventListener("input", () => {{
        if (selectedId === null) return;
        const word = getWordById(selectedId);
        const el = wordElements.get(selectedId);
        if (!word || !el) return;
        word.text = wordTextInput.value;
        applyWordStyle(el, word);
    }});

    document.getElementById("pasteOriginalBtn").addEventListener("click", () => {{
        replaceLayout(originalLayoutWords, "Poem placed in original form");
    }});

    document.getElementById("scatterBtn").addEventListener("click", () => {{
        replaceLayout(randomStartWords, "Words scattered randomly");
    }});

    document.getElementById("bringFrontBtn").addEventListener("click", () => {{
        if (selectedId === null) return;
        const word = getWordById(selectedId);
        const el = wordElements.get(selectedId);
        if (!word || !el) return;
        currentZ += 1;
        word.z = currentZ;
        applyWordStyle(el, word);
        updateStatus(`Brought "${{word.text}}" to front`);
    }});

    document.getElementById("deleteBtn").addEventListener("click", () => {{
        if (selectedId === null) return;
        const word = getWordById(selectedId);
        if (!word) return;

        words = words.filter(w => w.id !== selectedId);
        selectedId = null;
        wordTextInput.value = "";
        renderWords();
        updateStatus(`Deleted "${{word.text}}"`);
    }});

    document.getElementById("randomizeBtn").addEventListener("click", () => {{
        words.forEach((word, index) => {{
            word.x = Math.floor(Math.random() * Math.max(40, canvas.clientWidth - 140));
            word.y = Math.floor(Math.random() * Math.max(40, canvas.clientHeight - 70));
            word.size = Math.floor(Math.random() * 50) + 16;
            word.rotation = Math.floor(Math.random() * 361) - 180;
            word.z = index + 1;
        }});
        currentZ = words.length + 1;
        renderWords();
        updateStatus("Layout randomized");
    }});

    document.getElementById("resetBtn").addEventListener("click", () => {{
        replaceLayout(randomStartWords, "Reset to starting scattered layout");
    }});

    function buildHtmlExport() {{
        const items = words.map(word => {{
            return `
                <div style="
                    position:absolute;
                    left:${{word.x}}px;
                    top:${{word.y}}px;
                    font-size:${{word.size}}px;
                    color:${{word.color}};
                    z-index:${{word.z}};
                    font-family:${{word.fontFamily || "Arial, sans-serif"}};
                    transform:rotate(${{word.rotation}}deg);
                    transform-origin:center center;
                    white-space:nowrap;
                ">${{escapeHtml(word.text)}}</div>
            `;
        }}).join("");

        return `
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Concrete Poem</title>
</head>
<body style="margin:0; padding:20px; background:#f2f2f2; font-family:Arial, sans-serif;">
<div style="
    position:relative;
    width:{canvas_width}px;
    height:{canvas_height}px;
    background:{background_color};
    border:2px solid #111;
    border-radius:10px;
    overflow:hidden;
">
${{items}}
</div>
</body>
</html>`;
    }}

    function escapeHtml(text) {{
        const div = document.createElement("div");
        div.innerText = text;
        return div.innerHTML;
    }}

    function downloadFile(filename, content, mimeType) {{
        const blob = new Blob([content], {{ type: mimeType }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }}

    document.getElementById("downloadHtmlBtn").addEventListener("click", () => {{
        const html = buildHtmlExport();
        downloadFile("concrete_poem.html", html, "text/html");
        updateStatus("Downloaded HTML version");
    }});

    document.getElementById("downloadJsonBtn").addEventListener("click", () => {{
        downloadFile("concrete_poem_layout.json", JSON.stringify(words, null, 2), "application/json");
        updateStatus("Downloaded JSON layout");
    }});

    renderWords();
    updateStatus("Click and drag words to begin");
</script>
</body>
</html>
"""

components.html(html_code, height=canvas_height + 60, scrolling=True)
