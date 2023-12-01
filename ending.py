import gradio as gr


with gr.Blocks() as ending:
    gr.Markdown("""# 感谢您的参与！
    
    全部流程已经结束，感谢您的参与！
    我们会从全部填写了手机号的用户中抽取10名用户，每人奖励50元红包。
    """)

if __name__ == '__main__':
    ending.launch(show_api=False, share=True)
