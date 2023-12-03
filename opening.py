import gradio as gr


with gr.Blocks(title='模拟纠纷实验') as opening:
    gr.Markdown("""# <p style="text-align: center;">欢迎！</p>
    
    ### <span style="font-weight: normal;">感谢您参与本次实验，该实验的目的是探知消费者在线平台购物的公正感受。</span>
    
    ### <span style="font-weight: normal;">你被邀请参与一次模拟的线上维权，预计耗时5分钟。</span>
    
    ### <span style="font-weight: normal;">请您充分想象实验中场景，依照现实中会有的反应给出真实的评价。</span>
    """)

    start_button = gr.Button('进入实验')

    start_button.click(None, None, None,
                       js="window.location.href = 'http://49.232.250.86/user-info-collection'")

if __name__ == '__main__':
    opening.launch(show_api=False, share=True)
