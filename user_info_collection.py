import gradio as gr

from data_models import User
from db_manager import DBManager


def submit_user_info(name: str, student_id: str, gender: str, phone: str = None) -> str:
    user = User(name=name, student_id=student_id, gender=gender, phone=phone)
    with DBManager() as manager:
        manager.insert_user(user)
        manager.update_user_variables(user)
    gr.Info(f"基本信息提交成功！")
    return 'success'


with gr.Blocks() as user_info_collection:
    gr.Markdown("""# Step 1：基本信息填写
    """)

    name = gr.Textbox(label='姓名', lines=1, placeholder="张三")
    student_id = gr.Textbox(label='学号', lines=1, placeholder="20021827")
    gender = gr.Radio(label='性别', choices=['男', '女', '其他'])
    phone = gr.Textbox(label='电话', lines=1, placeholder="18868889888",
                       info="请填写11位手机号码, 如果抽到电话回访并参与会有50元红包赠送哦")

    submit_button = gr.Button("提交")
    submit_flag = gr.Textbox(label='隐藏标识', lines=1, placeholder="请勿填写")
    save_student_id_to_cookie_js = """
    function saveStudentIdCookie(name, student_id, gender, phone) {
        var expires = new Date();
        expires.setTime(expires.getTime() + (7*24*60*60*1000)); // Set expiration to 7 days from now
        document.cookie = 'user_student_id=' + student_id + '; expires=' + expires.toUTCString() + '; path=/';
        return [name, student_id, gender, phone];
    }
    """
    submit_button.click(submit_user_info, inputs=[name, student_id, gender, phone], outputs=submit_flag,
                        js=save_student_id_to_cookie_js)
    submit_flag.change(fn=lambda x: x, inputs=submit_flag,
                       js="window.location.href = 'http://127.0.0.1:8000/introduction'")


if __name__ == '__main__':
    user_info_collection.launch(show_api=False, share=True)
