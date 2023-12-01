import os
import time
from pathlib import Path

import gradio as gr

from db_manager import DBManager
from data_models import NeutralityEnum, ReplierEnum, SpeechEnum


def add_text(history, text=None):
    history = history + [[text, None]]
    return history


def confirm(history, confirm_input):
    history = history + [[confirm_input, None]]
    return history, gr.Button(visible=False)


def accept(history, accept_input, reject_input):
    if len(history) == 6:
        history = history + [[reject_input, None]]
    else:
        history = history + [[accept_input, None]]
    return history, gr.Column(visible=False)


def reject(history, reject_input):
    history = history + [[reject_input, None]]
    return history, gr.Column(visible=False)


def save_user_conversation(student_id, conversation):
    if not student_id:
        gr.Info(f"请先填写基本信息！")
        return
    with DBManager() as manager:
        if not manager.check_user_exists_by_student_id(student_id):
            gr.Info(f"请先填写基本信息！")
            return
        manager.update_user_conversation(student_id, conversation)
    gr.Info(f"提交成功！")


def get_current_message_to_say(history,
                               student_id: str,
                               neutrality_variable: NeutralityEnum,
                               replier_variable: ReplierEnum,
                               speech_variable: SpeechEnum) -> str:
    response: str = ''
    match len(history):
        case 1:  # 问候
            match neutrality_variable:
                case NeutralityEnum.COURT:
                    match replier_variable:
                        case ReplierEnum.HUMAN:
                            response += '人工裁决官程程（工号 203891）为您服务。'
                        case ReplierEnum.SYSTEM:
                            response += 'AI 裁决官为您服务。'
                    response += '您好，这里是淘宝法庭，我是您的裁决官，我将为您的购物的公平公正保驾护航。'
                case NeutralityEnum.CUSTOMER_SERVICE:
                    match replier_variable:
                        case ReplierEnum.HUMAN:
                            response += '人工客服程程（工号 203891）为您服务。'
                        case ReplierEnum.SYSTEM:
                            response += 'AI 客服为您服务。'
                    response += f'您好，尊贵的淘宝用户 {student_id}，我是您的专属管家，为您打造舒心的购物体验，请问有什么可以帮您的？'
            response += '您需要咨询的是这笔订单么？'
            # 弹出订单信息，用户点击按钮确认
        case 3:  # 诉求询问
            response += '您是对商家在什么方面有异议呢？'
            # 用户输入其异议
        case 4:  # 客服请求卖家回复
            match neutrality_variable:
                case NeutralityEnum.COURT:
                    response += '请稍后，请卖家进行发言陈述。'
                case NeutralityEnum.CUSTOMER_SERVICE:
                    response += '我需要去咨询一下卖家。'
            # 用户点击按钮确认“好的”，最好直接输出下一轮
        case 5:  # 卖家回复
            match neutrality_variable:
                case NeutralityEnum.COURT:
                    response += '卖家：我同意进行退款，但是不同意超额赔偿，他并没有提供假货证明，也没有提供开箱视频，不能证明假货就是我的。'
                case NeutralityEnum.CUSTOMER_SERVICE:
                    response += '卖家同意进行退款，但是不同意超额赔偿，他认为您并没有提供假货证明，也没有提供开箱视频，不能证明假货就是卖家的。'
        case 6:  # 一轮报价
            match neutrality_variable:
                case NeutralityEnum.COURT:
                    response += '法庭判决商家应该对您进行退款，由于无法证明是否为假货，法庭无法支持退一赔三。但是，平台为您扣除了商家的200元保证金作为警告，交还给您，一共1000元。'
                case NeutralityEnum.CUSTOMER_SERVICE:
                    response += '您的订单符合无理由退款的规则，所以为您退款800元，平台额外为您提供了200块钱的补助，希望您继续选择本平台。'
            # 弹出询问框：接受/不接受，小字提醒：出于实验需要，请您不要接受该报价
        case 7:  # 二轮争辩
            match neutrality_variable:
                case NeutralityEnum.COURT:
                    match speech_variable:
                        case SpeechEnum.FREE_TYPING:
                            response += '请陈述提交一下您的理由和证据。'  # 用户输入自己的理由
                        case SpeechEnum.CHOICES_ONLY:
                            response += '法庭已查询到您的这条订单记录，请确认。'  # 弹出对话框，用户点确认
                case NeutralityEnum.CUSTOMER_SERVICE:
                    match speech_variable:
                        case SpeechEnum.FREE_TYPING:
                            response += '亲亲您好，能不能再给管家发送一下您的购买记录呢。'  # 用户随便输入点什么
                        case SpeechEnum.CHOICES_ONLY:
                            response += '请亲亲稍等，我再去重新在系统里确认一下。'  # 弹出对话框，用户点确认
        case 8:  # 二轮报价
            match neutrality_variable:
                case NeutralityEnum.COURT:
                    response += '法庭审查了所有材料，现在支持退一赔三。2400元将打回给您，请问是否接受？'
                case NeutralityEnum.CUSTOMER_SERVICE:
                    response += '我们认为您的订单符合退一赔三的规则，由于您是我们的 VIP 客户，您享有极速退款，2400元将马上打回给您，希望您继续选择本平台。'
            # 弹出询问框：接受/不接受
        case 9:
            match history[-1][0]:
                case '[我接受]':
                    response += '纠纷完美解决，请填写我们的感受量表。'
                case '[我不接受]':
                    response += '之后，您又与平台进行了几轮沟通，但是没有取得实质性进展，最终获得了2400元的赔偿，请填写我们的感受量表。'
        case _:
            response += '服务已结束，谢谢！'
    return response


def bot(history, student_id, neutrality_variable, replier_variable, speech_variable):
    neutrality_variable = NeutralityEnum(neutrality_variable)
    replier_variable = ReplierEnum(replier_variable)
    speech_variable = SpeechEnum(speech_variable)
    response = get_current_message_to_say(history, student_id,
                                          neutrality_variable, replier_variable, speech_variable)
    match replier_variable:
        case ReplierEnum.HUMAN:
            history[-1][1] = '输入中...'
            yield history
            time.sleep(5)
            history[-1][1] = response
            yield history
        case ReplierEnum.SYSTEM:
            history[-1][1] = ""
            for character in response:
                history[-1][1] += character
                time.sleep(0.02)
                yield history

    match len(history):
        case 1:  # Round 2: show order info (a picture)
            history.append([None, (Path('pics/earphone.png'), 'figure')])
            yield history
            # 弹出订单信息，用户点击按钮确认
        case 4:  # Round 5: the seller reply
            time.sleep(3)
            history.append([None, ''])
            response = get_current_message_to_say(history, student_id,
                                                  neutrality_variable, replier_variable, speech_variable)
            match replier_variable:
                case ReplierEnum.HUMAN:
                    history[-1][1] = '输入中...'
                    yield history
                    time.sleep(5)
                    history[-1][1] = response
                    yield history
                case ReplierEnum.SYSTEM:
                    history[-1][1] = ""
                    for character in response:
                        history[-1][1] += character
                        time.sleep(0.02)
                        yield history


prepare_cookie_loading_js = """
function prepareCookieLoading(student_id) {
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


def get_user_variables_by_student_id(student_id):
    with DBManager() as manager:
        if not manager.check_user_exists_by_student_id(student_id):
            gr.Info(f"请先填写基本信息！")
        return student_id, *list(manager.select_user_variables_by_student_id(student_id).values())


def update_text_input(history, speech_variable):
    match len(history):
        case 6 | 8 | 9:
            return gr.Textbox(value="", interactive=False, visible=False)
        case 7:
            if speech_variable == SpeechEnum.CHOICES_ONLY.value:
                return gr.Textbox(value="", interactive=False, visible=False)
            return gr.Textbox(value="", interactive=True, visible=True)
        case _:
            return gr.Textbox(value="", interactive=True, visible=True)


def update_accept_reject_buttons(history):
    match len(history):
        case 6:
            return gr.Row(visible=True), gr.Markdown(value='', visible=True)
        case 8:
            return gr.Row(visible=True), gr.Markdown(value='', visible=False)
        case _:
            return gr.Row(visible=False), gr.Markdown(value='', visible=False)


def update_confirm_button(history, speech_variable):
    if len(history) == 7 and speech_variable == SpeechEnum.CHOICES_ONLY.value:
        return gr.Button(visible=True)
    return gr.Button(visible=False)


def update_next_page_button(history):
    if len(history) == 9:
        return gr.Button(visible=True)
    return gr.Button(visible=False)


with gr.Blocks() as conversation:
    gr.Markdown("""# Step 3：对话""")

    with gr.Row(visible=True) as debug_settings:
        student_id = gr.Textbox(label='student_id')
        neutrality_variable = gr.Radio(label='neutrality_variable', choices=[item.value for item in NeutralityEnum])
        replier_variable = gr.Radio(label='replier_variable', choices=[item.value for item in ReplierEnum])
        speech_variable = gr.Radio(label='speech_variable', choices=[item.value for item in SpeechEnum])

    chatbot = gr.Chatbot(
        [[None, '']],
        elem_id="客服",
        label="客服",
        show_label=False,
        container=True,
        layout='bubble',
        bubble_full_width=False,
        avatar_images=("pics/user.png", "pics/customer_service.jpeg")
    )

    with gr.Row():
        text_input = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Enter text here...",
            container=False,
            interactive=False
        )

    confirm_button = gr.Button('确认', visible=False)
    confirm_input = gr.Textbox(value='[我已确认]', visible=False)

    hint = gr.Markdown('出于实验需要，请您不要接受该报价。', visible=False)

    with gr.Row(visible=False) as accept_reject_buttons:
        accept_button = gr.Button('接受')
        reject_button = gr.Button('不接受')
    accept_input = gr.Textbox(value='[我接受]', visible=False)
    reject_input = gr.Textbox(value='[我不接受]', visible=False)

    next_page_button = gr.Button('填写量表', visible=False)
    is_user_conversation_saved = gr.Textbox(value='False', visible=False)

    conversation.load(
        inputs=[student_id],
        outputs=[student_id, neutrality_variable, replier_variable, speech_variable],
        js=prepare_cookie_loading_js,
        fn=get_user_variables_by_student_id,
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable], chatbot
    ).then(
        lambda: gr.Textbox(visible=False), None, text_input, queue=False
    ).then(
        lambda: gr.Button(visible=True), None, confirm_button, queue=False
    )

    confirm_button.click(
        confirm, [chatbot, confirm_input], [chatbot, confirm_button], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, [text_input], queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], text_input, queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_reject_buttons, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    text_input.submit(
        add_text, [chatbot, text_input], chatbot, queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, [text_input], queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], text_input, queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_reject_buttons, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    accept_button.click(
        accept, [chatbot, accept_input, reject_input], [chatbot, accept_reject_buttons], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, [text_input], queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], text_input, queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_reject_buttons, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    reject_button.click(
        reject, [chatbot, reject_input], [chatbot, accept_reject_buttons], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, [text_input], queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], text_input, queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_reject_buttons, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    next_page_button.click(
        save_user_conversation, [student_id, chatbot], None, queue=False
    ).then(
        lambda: gr.Textbox(value='True'), None, is_user_conversation_saved, queue=False
    )

    is_user_conversation_saved.change(
        None, None, None, js="window.location.href = 'http://127.0.0.1:8000/scale'"
    )

if __name__ == '__main__':
    conversation.launch(show_api=False, share=True)
