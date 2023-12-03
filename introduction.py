import gradio as gr

from db_manager import DBManager


def update_user_expected_compensation(user_student_id: str, expected_compensation: str) -> gr.Textbox:
    if not user_student_id:
        gr.Info(f"请先填写基本信息！")
        return gr.Textbox(value='False', visible=False)
    with DBManager() as manager:
        if not manager.check_user_exists_by_student_id(user_student_id):
            gr.Info(f"请先填写基本信息！")
            return gr.Textbox(value='False', visible=False)
        manager.update_user_expected_compensation(user_student_id, expected_compensation)
    gr.Info(f"提交成功！")
    return gr.Textbox(value='True', visible=False)


with gr.Blocks(title='模拟纠纷实验') as introduction:
    gr.Markdown("""# Step 2：场景简介
    
    你于淘宝平台“深圳电子零售店”以800的价格购买了无线耳机一副，使用感受很差，和朋友的正品耳机对比觉得存在明显不同，发现买到了假货。
    
    你找到店家沟通，要求按照店铺主页里写的假一赔十的规则赔付你8000元。
    
    但是店家称，假一赔十的规定不适用于你这款产品，因为产品页里没有写明。
    
    另外，他在没有官方鉴定的情况下不认可你说那是假货，但是提出，可以为你办理退款800元。
    
    你通过网络查询到，由于你买到了假货，《消费者权益保护法》将支持你假一赔三，也即2400元的主张，这是你通过诉讼所能获得的金额。
    
    你并不希望自己因为这种小事诉诸公堂，希望借助淘宝平台解决这一问题。
    
    于是，你联系了“店小二”客服。你的心理预期起码不能让这个假店铺随便把你糊弄过去，希望获得尽可能多的赔偿。
    
    这种情况下，你预期赔偿是多少呢？
    """)

    expected_compensation = gr.Textbox(label='预期赔偿金额', lines=1, placeholder="2400")

    submit_button = gr.Button("提交")
    submit_flag = gr.Textbox(value='False', visible=False)
    hidden_student_id = gr.Textbox(visible=False)

    get_user_student_id_from_cookie_js = """
    function getStudentIdAndExpectedCompensation(hidden_student_id, expected_compensation) {
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
    
        const student_id = getCookie('user_student_id');
        return [student_id, expected_compensation];
    }
    """
    submit_button.click(fn=update_user_expected_compensation,
                        inputs=[hidden_student_id, expected_compensation],
                        outputs=submit_flag,
                        js=get_user_student_id_from_cookie_js)
    submit_flag.change(None, None, None,
                       js="window.location.href = 'http://49.232.250.86/conversation'")

if __name__ == '__main__':
    introduction.launch(show_api=False, share=True)
