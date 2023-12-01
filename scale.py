import gradio as gr

from db_manager import DBManager

get_user_student_id_from_cookie_js = """
    function getStudentId(student_id) {
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                let cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    let cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        return getCookie('user_student_id');
    }
    """


def submit_scale(student_id, authority_level, consideration_level, respect_level, future_choice, evidence_opportunity,
                 influence_level, fairness_perception, most_unsatisfied_point, improvement_suggestion):
    if not student_id:
        gr.Info(f"请先填写基本信息！")
        return
    with DBManager() as manager:
        if not manager.check_user_exists_by_student_id(student_id):
            gr.Info(f"请先填写基本信息！")
        manager.update_user_scale(student_id, authority_level, consideration_level, respect_level, future_choice,
                                  evidence_opportunity, influence_level, fairness_perception, most_unsatisfied_point,
                                  improvement_suggestion)
    gr.Info(f"提交成功！")


with gr.Blocks() as scale:
    gr.Markdown("""# Step 4：填写量表
    请根据你的实际感受，为每个维度填写合适的分数。
    
    **评分参考**：
    0分 完全不符合 / 5分 基本符合 / 10分 完全符合 
    """)

    student_id = gr.Textbox(visible=False)

    gr.Markdown('### 纠纷平台')
    authority_level = gr.Slider(label='你认为客服店小二/小法庭在多大程度上有权限处理你的纠纷？', minimum=0, maximum=10,
                                step=1, value=5)
    consideration_level = gr.Slider(label='你认为它在过程中多大程度上慎重地考虑了你的诉求？', minimum=0, maximum=10,
                                    step=1, value=5)

    gr.Markdown('### 纠纷过程')
    respect_level = gr.Slider(label='你在多大程度上感觉自己被尊重，以致有一次愉快的维权经历？', minimum=0, maximum=10,
                              step=1, value=5)
    future_choice = gr.Slider(label='若未来有类似的纠纷，你在多大程度上愿意选择类似的程序？', minimum=0, maximum=10,
                              step=1, value=5)

    gr.Markdown('### 话语权')
    evidence_opportunity = gr.Slider(label='你认为你获得机会展示你的证据和事实了吗？', minimum=0, maximum=10, step=1,
                                     value=5)
    influence_level = gr.Slider(label='你认为你的参与多大程度上影响了最后的结果？', minimum=0, maximum=10, step=1,
                                value=5)

    gr.Markdown('### 直接评价')
    fairness_perception = gr.Slider(label='你认为刚才经历的纠纷解决程序是否公平？', minimum=0, maximum=10, step=1,
                                    value=5)

    gr.Markdown('### 开放问题')
    most_unsatisfied_point = gr.Textbox(label='作为消费者，您觉得这个过程中最令您不满意的地方是哪里？', lines=3)
    improvement_suggestion = gr.Textbox(label='如果您可以改进这个系统，您会在哪些方面努力？', lines=3)

    submit_button = gr.Button("提交")
    submit_flag = gr.Textbox(value='False', visible=False)

    scale.load(
        lambda x: x, student_id, student_id, js=get_user_student_id_from_cookie_js
    )

    submit_button.click(
        fn=submit_scale,
        inputs=[student_id, authority_level, consideration_level, respect_level, future_choice, evidence_opportunity,
                influence_level, fairness_perception, most_unsatisfied_point, improvement_suggestion]
    ).then(
        lambda: gr.Textbox(value='True', visible=False), None, submit_flag, queue=False
    )
    submit_flag.change(
        None, None, None,
        js="window.location.href = 'http://127.0.0.1:8000/ending'"
    )

if __name__ == '__main__':
    scale.launch(show_api=False, share=True)
