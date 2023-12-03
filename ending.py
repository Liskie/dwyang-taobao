import gradio as gr


with gr.Blocks(title='模拟纠纷实验') as ending:
    gr.Markdown("""# <p style="text-align: center;">全部流程已经结束</p>
    
    # <p style="text-align: center;">感谢您的参与！</p>
    
    ### <span style="font-weight: normal;">我们会从填写了手机号的用户中抽取用户回访，并附有补贴。
    
    ### <span style="font-weight: normal;">如有问题或希望获得最后的结论，您可以添加微信号 13616330561 咨询。

    """)

if __name__ == '__main__':
    ending.launch(show_api=False, share=True)
