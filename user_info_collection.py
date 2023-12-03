import gradio as gr

from db_manager import DBManager


def submit_user_info(name: str, student_id: str, gender: str, phone: str = None,
                     has_solved_dispute: str = '否', dispute_times: str = '0') -> str:
    with DBManager() as manager:
        if manager.check_user_exists_by_student_id(student_id):
            gr.Info(f"用户 {student_id} 已存在！")
        manager.insert_user(name, student_id, gender, phone, has_solved_dispute, dispute_times)
        manager.update_user_variables(student_id)
    gr.Info(f"提交成功！")
    return 'True'

def update_dispute_times(has_solved_dispute):
    if has_solved_dispute == '是':
        return gr.Textbox(visible=True, interactive=True)
    return gr.Textbox(visible=False)

save_student_id_to_cookie_js = """
    function saveStudentIdCookie(name, student_id, gender, phone, has_solved_dispute, dispute_times) {
        var expires = new Date();
        expires.setTime(expires.getTime() + (7*24*60*60*1000)); // Set expiration to 7 days from now
        document.cookie = 'user_student_id=' + student_id + '; expires=' + expires.toUTCString() + '; path=/';
        return [name, student_id, gender, phone, has_solved_dispute, dispute_times];
    }
    """

with gr.Blocks(title='模拟纠纷实验') as user_info_collection:
    gr.Markdown("""# Step 1：基本信息填写
    """)

    name = gr.Textbox(label='姓名', lines=1, placeholder="张三")
    student_id = gr.Textbox(label='学号', lines=1, placeholder="20021827")
    gender = gr.Radio(label='性别', choices=['男', '女', '其他'])
    phone = gr.Textbox(label='电话', lines=1, placeholder="18868889888",
                       info="请填写11位手机号码, 如果抽到电话回访并参与会有50元红包赠送哦")
    has_solved_dispute = gr.Radio(label='您是否曾在网购平台上解决过纠纷？', choices=['是', '否'])
    dispute_times = gr.Textbox(visible=False, label="您在网购平台上尝试解决纠纷的次数", placeholder='0')

    has_solved_dispute.change(update_dispute_times, has_solved_dispute, dispute_times)

    submit_button = gr.Button("提交")
    submit_flag = gr.Textbox(value='False', visible=False)

    submit_button.click(submit_user_info,
                        inputs=[name, student_id, gender, phone, has_solved_dispute, dispute_times],
                        outputs=submit_flag,
                        js=save_student_id_to_cookie_js)
    submit_flag.change(fn=lambda x: x, inputs=submit_flag,
                       js="window.location.href = 'http://49.232.250.86/introduction'")


if __name__ == '__main__':
    user_info_collection.launch(show_api=False, share=True)
