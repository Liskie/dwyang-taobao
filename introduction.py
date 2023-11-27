import gradio as gr

from data_models import User
from db_manager import DBManager


def update_user_expected_compensation(user: User, expected_compensation: str):
    user.expected_compensation = expected_compensation
    gr.Info(f"预期补偿金额提交成功！")


with gr.Blocks() as introduction:
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
    submit_button.click(update_user_expected_compensation, inputs=[expected_compensation],
                        js="window.location.href = 'http://127.0.0.1:7862'")


if __name__ == '__main__':
    introduction.launch(show_api=False, share=True)
