import gradio as gr


def title(txt):
    gr.HTML(
        f'<h1 style="margin: 0.5rem 0; font-weight: bold; font-size: 1.5rem;">{txt}</h1>',
    )
