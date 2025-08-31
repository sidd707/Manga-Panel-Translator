import cv2, numpy as np
from PIL import Image
import gradio as gr

from src.detect_bubbles import detect_bubbles
from src.process_bubble import process_bubble
from src.translator import MangaTranslator
from src.add_text import add_text
from src.mocr_local import LocalMangaOcr

MODEL_PATH = "models/bubble_detector.pt"
FONT_PATH = "Fonts/mangati.ttf"

LOCAL_MOCR_DIR = "/Users/sarthak/Desktop/Translator/models/manga_ocr"

manga_translator = MangaTranslator()
mocr = LocalMangaOcr(LOCAL_MOCR_DIR)


def translate_manga(image, translator_choice, progress=gr.Progress()):
    img_pil = image.convert("RGB")
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    progress(0.05, desc="Detecting bubbles...")
    results = detect_bubbles(MODEL_PATH, img_cv)

    n = max(1, len(results))
    for i, result in enumerate(results):
        progress((i + 1, n), desc=f"Processing bubble {i + 1}/{n}")
        x1, y1, x2, y2, score, class_id = result
        detected_image = img_cv[int(y1) : int(y2), int(x1) : int(x2)]
        im = Image.fromarray(np.uint8(detected_image * 255))
        text = mocr(im)
        detected_image, cont = process_bubble(detected_image)
        translated = manga_translator.translate(text, method=translator_choice)
        crop = add_text(detected_image, translated, FONT_PATH, cont)
        img_cv[int(y1) : int(y2), int(x1) : int(x2)] = crop

    progress(1.0, desc="Done")
    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))


theme = gr.themes.Soft()

with gr.Blocks(theme=theme, title="Manga Translator") as demo:
    gr.Markdown("## Manga Translator")
    gr.Markdown(
        "Detects speech bubbles, extracts Japanese text, translates it, and redraws the translation.",
    )

    with gr.Row():
        with gr.Column(scale=1, min_width=320):
            inp_image = gr.Image(
                type="pil",
                label="Upload Manga Page",
                sources=["upload", "clipboard"],  # removed 'drag-and-drop'
                height=420,
            )

            translator = gr.Dropdown(
                ["google", "hf"], value="google", label="Translator"
            )

            with gr.Row():
                run_btn = gr.Button("Translate", variant="primary")
                clear_btn = gr.Button("Clear")

            gr.Examples(
                examples=[
                    "demo/0.png",
                    "demo/1.jpg",
                    "demo/2.jpg",
                ],
                inputs=[inp_image],
                label="Examples",
                examples_per_page=6,
            )

            gr.Markdown(
                "Tip: Use high-resolution pages for better OCR and translation results."
            )

        with gr.Column(scale=1, min_width=360):
            out_image = gr.Image(type="pil", label="Translated Image", height=420)
            status = gr.Markdown("")

    # Wire actions
    run_btn.click(
        fn=translate_manga, inputs=[inp_image, translator], outputs=[out_image]
    )
    clear_btn.click(lambda: (None, ""), inputs=None, outputs=[inp_image, status])

# Enable queue for smoother UX on heavy images
demo.queue(max_size=8).launch()
