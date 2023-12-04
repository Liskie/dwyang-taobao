import os
import random
import time
from pathlib import Path

import gradio as gr

from db_manager import DBManager
from data_models import NeutralityEnum, ReplierEnum, SpeechEnum


def add_text(history, text=None):
    history = history + [[text, None]]
    return history


def add_file(history, file):
    history = history + [[(file.name, 'photo'), None]]
    return history


def confirm(history, confirm_input):
    history = history + [[confirm_input, None]]
    return history, gr.Button(visible=False)


def accept(history):
    if len(history) == 5:
        history = history + [['[我同意]', None]]
    else:
        history = history + [['[我接受]', None]]
    return history, gr.Button(visible=False), gr.Button(visible=False)


def reject(history):
    if len(history) == 5:
        history = history + [['[我不同意]', None]]
    else:
        history = history + [['[我不接受]', None]]
    return history, gr.Button(visible=False), gr.Button(visible=False)


def submit_refund_reason(history, refund_reason):
    history = history + [[refund_reason, None]]
    return history


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
                               speech_variable: SpeechEnum,
                               final_refund: str) -> str:
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
                    response += '法庭判决商家应该对您进行退款，由于无法证明是否为假货，法庭无法支持退一赔三。但是，平台支持为您退货退款，在您退货之后为您退还 800 元。'
                case NeutralityEnum.CUSTOMER_SERVICE:
                    response += '目前根据您提供的情况，我们可以提供退货退款服务，在您退货之后为您退还 800 元，希望您继续选择本平台。'
            # 弹出询问框：接受/不接受
        case 7:  # 二轮争辩
            match history[-1][0]:
                case '[我接受]':
                    response += '纠纷已解决，请填写我们的感受量表。'
                case '[我不接受]':
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
                    match final_refund:
                        case '2400':
                            response += '法庭审查了所有材料，现在支持退一赔三。2400 元将打回给您，请问是否接受？'
                        case '800':
                            response += '法庭审查了所有材料，认为您的证据不能支持退一赔三。800 元将打回给您，请问是否接受？'
                case NeutralityEnum.CUSTOMER_SERVICE:
                    match final_refund:
                        case '2400':
                            response += '我们认为您的订单符合退一赔三的规则，由于您是我们的 VIP 客户，您享有极速退款，2400 元将马上打回给您，希望您继续选择本平台。'
                        case '800':
                            response += '我们认为您的订单不符合退一赔三的规则，由于您是我们的 VIP 客户，您享有极速退款，800 元将马上打回给您，希望您继续选择本平台。'
            # 弹出询问框：接受/不接受
        case 9:
            match history[-1][0]:
                case '[我接受]':
                    response += '纠纷完美解决，请填写我们的感受量表。'
                case '[我不接受]':
                    match final_refund:
                        case '2400':
                            response += '之后，您又与平台进行了几轮沟通，但是没有取得实质性进展，最终获得了 2400 元的赔偿，请填写我们的感受量表。'
                        case '800':
                            response += '之后，您又与平台进行了几轮沟通，但是没有取得实质性进展，最终获得了 800 元的赔偿，请填写我们的感受量表。'
        case _:
            response += '服务已结束，谢谢！'
    return response


def bot(history, student_id, neutrality_variable, replier_variable, speech_variable, final_refund):
    neutrality_variable = NeutralityEnum(neutrality_variable)
    replier_variable = ReplierEnum(replier_variable)
    speech_variable = SpeechEnum(speech_variable)
    response = get_current_message_to_say(history, student_id,
                                          neutrality_variable, replier_variable, speech_variable, final_refund)
    match replier_variable:
        case ReplierEnum.HUMAN:
            history[-1][1] = '等待客服...'
            yield history
            time.sleep(3)
            history[-1][1] = '输入中...'
            yield history
            time.sleep(len(response) * 0.2)
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
            history[-1][1] = '等待卖家...'
            yield history
            time.sleep(10)
            response = get_current_message_to_say(history, student_id,
                                                  neutrality_variable, replier_variable, speech_variable, final_refund)
            match replier_variable:
                case ReplierEnum.HUMAN:
                    history[-1][1] = '输入中...'
                    yield history
                    time.sleep(len(response) * 0.2)
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
    document.querySelector('meta[name="viewport"]').setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
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
        case 5 | 6 | 8 | 9:
            return (gr.Textbox(value="", interactive=False, visible=False),
                    gr.Button(interactive=False, visible=False),
                    gr.UploadButton(interactive=False, visible=False))
        case 3:
            if speech_variable == SpeechEnum.CHOICES_ONLY.value:
                return (gr.Textbox(value="", interactive=False, visible=False),
                        gr.Button(interactive=False, visible=False),
                        gr.UploadButton(interactive=False, visible=False))
            return (gr.Textbox(value="", interactive=True, visible=True),
                    gr.Button(interactive=True, visible=True),
                    gr.UploadButton(interactive=True, visible=True))
        case 7:
            if speech_variable == SpeechEnum.CHOICES_ONLY.value or history[-1][0] == '[我接受]':
                return (gr.Textbox(value="", interactive=False, visible=False),
                        gr.Button(interactive=False, visible=False),
                        gr.UploadButton(interactive=False, visible=False))
            return (gr.Textbox(value="", interactive=True, visible=True),
                    gr.Button(interactive=True, visible=True),
                    gr.UploadButton(interactive=True, visible=True))
        case _:
            return (gr.Textbox(value="", interactive=True, visible=True),
                    gr.Button(interactive=True, visible=True),
                    gr.UploadButton(interactive=True, visible=True))


def update_accept_reject_buttons(history):
    match len(history):
        case 5:
            return gr.Button(value='我同意', visible=True, interactive=False), gr.Button(value='我不同意',
                                                                                         visible=True), gr.Markdown(
                value='', visible=False)
        case 6:
            return gr.Button(value='我接受', visible=True, interactive=True), gr.Button(value='我不接受',
                                                                                        visible=True), gr.Markdown(
                value='', visible=True)
        case 8:
            return gr.Button(value='我接受', visible=True, interactive=True), gr.Button(value='我不接受',
                                                                                        visible=True), gr.Markdown(
                value='', visible=False)
        case _:
            return gr.Button(value='我接受', visible=False), gr.Button(value='我不接受', visible=False), gr.Markdown(
                value='', visible=False)


def update_confirm_button(history, speech_variable):
    if len(history) == 7 and history[-1][0] == '[我接受]':
        return gr.Button(visible=False)
    if len(history) == 7 and speech_variable == SpeechEnum.CHOICES_ONLY.value:
        return gr.Button(visible=True, interactive=True)
    return gr.Button(visible=False)


def update_refund_reason_dropdown(history, speech_variable):
    if len(history) == 3 and speech_variable == SpeechEnum.CHOICES_ONLY.value:
        return gr.Dropdown(visible=True, interactive=True)
    return gr.Dropdown(visible=False)


def update_next_page_button(history):
    if len(history) == 9 or len(history) == 7 and history[-1][0] == '[我接受]':
        return gr.Button(visible=True)
    return gr.Button(visible=False)


def update_final_refund():
    refund = 2400 if random.random() > 0.3 else 800
    return gr.Textbox(value=f'{refund}', visible=False)


def update_logo(neutrality_variable):
    match neutrality_variable:
        case NeutralityEnum.COURT.value:
            return gr.Image('pics/logo_court.png', visible=True)
        case NeutralityEnum.CUSTOMER_SERVICE.value:
            return gr.Image('pics/logo_customer_service.png', visible=True)
        case _:
            raise ValueError(f"Unknown neutrality variable: {neutrality_variable}")


def update_system_description(replier_variable):
    match replier_variable:
        case ReplierEnum.SYSTEM.value:
            return gr.Markdown(visible=True)
        case ReplierEnum.HUMAN.value:
            return gr.Markdown(visible=False)


with (gr.Blocks(title='模拟纠纷实验') as conversation):
    gr.Markdown("""# Step 3：对话""")

    with gr.Row(visible=True) as debug_settings:
        student_id = gr.Textbox(label='student_id')
        neutrality_variable = gr.Radio(label='neutrality_variable', choices=[item.value for item in NeutralityEnum])
        replier_variable = gr.Radio(label='replier_variable', choices=[item.value for item in ReplierEnum])
        speech_variable = gr.Radio(label='speech_variable', choices=[item.value for item in SpeechEnum])

    with gr.Row():
        logo = gr.Image('pics/logo_court.png',
                        height=60,
                        width=60,
                        scale=1,
                        visible=False,
                        interactive=False,
                        show_label=False,
                        show_download_button=False,
                        label='logo')

    system_description = gr.Markdown("""
    <div style="display: flex; align-items: center; justify-content: center;">
        <img src="http://49.232.250.86/static/system_profile.png" alt="GPT-4 Logo" style="height: 20px; width: 20px; margin-right: 10px;">
        <span>Powered by ChatGPT 4</span>
    </div>
    """, visible=False)

    chatbot = gr.Chatbot(
        [[None, '']],
        elem_id="客服",
        label="客服",
        show_label=False,
        container=True,
        height=550,
        layout='bubble',
        bubble_full_width=False,
        avatar_images=("pics/user.png", "pics/customer_service_profile.jpeg")
    )

    with gr.Row() as text_input:
        text_input_box = gr.Textbox(
            scale=5,
            show_label=False,
            placeholder="Enter text here...",
            container=False,
            interactive=False,
        )
        send_button = gr.Button('发送', visible=True, interactive=False, scale=1, min_width=20)
        upload_button = gr.UploadButton('上传', visible=True, interactive=False, file_types=['image'], scale=1,
                                        min_width=20)

    confirm_button = gr.Button('确认', visible=False)
    confirm_input = gr.Textbox(value='[我已确认]', visible=False)

    hint = gr.Markdown('出于实验需要，请您不要接受该报价。', visible=False)

    with gr.Row():
        accept_button = gr.Button('接受', visible=False)
        reject_button = gr.Button('不接受', visible=False)

    next_page_button = gr.Button('填写量表', visible=False)
    is_user_conversation_saved = gr.Textbox(value='False', visible=False)

    refund_reason = gr.Dropdown(label='退款原因', visible=False,
                                choices=['拍错/多拍/不喜欢', '大小/尺寸与商品描述不符', '颜色/图案/款式与商品描述不符',
                                         '材质与商品描述不符', '功能与商品描述不符', '做工瑕疵', '假货投诉'])

    final_refund = gr.Textbox(value='', visible=False)

    conversation.load(
        inputs=[student_id],
        outputs=[student_id, neutrality_variable, replier_variable, speech_variable],
        js=prepare_cookie_loading_js,
        fn=get_user_variables_by_student_id,
    ).then(
        update_system_description, replier_variable, system_description, queue=False
    ).then(
        update_final_refund, None, final_refund, queue=False
    ).then(
        update_logo, neutrality_variable, logo, queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable, final_refund], chatbot
    ).then(
        lambda: gr.Row(visible=False), None, text_input, queue=False
    ).then(
        lambda: gr.Button(visible=True), None, confirm_button, queue=False
    )

    confirm_button.click(
        confirm, [chatbot, confirm_input], [chatbot, confirm_button], queue=False
    ).then(
        update_refund_reason_dropdown, [chatbot, speech_variable], refund_reason, queue=False
    ).then(
        lambda: gr.Row(visible=True), None, [text_input], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, text_input_box, queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable, final_refund], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], [text_input_box, send_button, upload_button], queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_button, reject_button, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    text_input_box.submit(
        add_text, [chatbot, text_input_box], chatbot, queue=False
    ).then(
        update_refund_reason_dropdown, [chatbot, speech_variable], refund_reason, queue=False
    ).then(
        lambda: gr.Row(visible=True), None, [text_input], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, text_input_box, queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable, final_refund], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], [text_input_box, send_button, upload_button], queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_button, reject_button, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    send_button.click(
        add_text, [chatbot, text_input_box], chatbot, queue=False
    ).then(
        update_refund_reason_dropdown, [chatbot, speech_variable], refund_reason, queue=False
    ).then(
        lambda: gr.Row(visible=True), None, [text_input], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, text_input_box, queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable, final_refund], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], [text_input_box, send_button, upload_button], queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_button, reject_button, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    upload_button.upload(
        add_file, [chatbot, upload_button], chatbot, queue=False
    ).then(
        update_refund_reason_dropdown, [chatbot, speech_variable], refund_reason, queue=False
    ).then(
        lambda: gr.Row(visible=True), None, [text_input], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, text_input_box, queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable, final_refund], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], [text_input_box, send_button, upload_button], queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_button, reject_button, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    accept_button.click(
        accept, chatbot, [chatbot, accept_button, reject_button], queue=False
    ).then(
        update_refund_reason_dropdown, [chatbot, speech_variable], refund_reason, queue=False
    ).then(
        lambda: gr.Row(visible=True), None, [text_input], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, text_input_box, queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable, final_refund], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], [text_input_box, send_button, upload_button], queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_button, reject_button, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    reject_button.click(
        reject, chatbot, [chatbot, accept_button, reject_button], queue=False
    ).then(
        update_refund_reason_dropdown, [chatbot, speech_variable], refund_reason, queue=False
    ).then(
        lambda: gr.Row(visible=True), None, [text_input], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, text_input_box, queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable, final_refund], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], [text_input_box, send_button, upload_button], queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_button, reject_button, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    refund_reason.change(
        submit_refund_reason, [chatbot, refund_reason], chatbot, queue=False
    ).then(
        update_refund_reason_dropdown, [chatbot, speech_variable], refund_reason, queue=False
    ).then(
        lambda: gr.Row(visible=True), None, [text_input], queue=False
    ).then(
        lambda: gr.Textbox(value='', interactive=False, visible=True), None, text_input_box, queue=False
    ).then(
        bot, [chatbot, student_id, neutrality_variable, replier_variable, speech_variable, final_refund], chatbot
    ).then(
        update_text_input, [chatbot, speech_variable], [text_input_box, send_button, upload_button], queue=False
    ).then(
        update_confirm_button, [chatbot, speech_variable], confirm_button, queue=False
    ).then(
        update_accept_reject_buttons, chatbot, [accept_button, reject_button, hint], queue=False
    ).then(
        update_next_page_button, chatbot, [next_page_button], queue=False
    )

    next_page_button.click(
        save_user_conversation, [student_id, chatbot], None, queue=False
    ).then(
        lambda: gr.Textbox(value='True'), None, is_user_conversation_saved, queue=False
    )

    is_user_conversation_saved.change(
        None, None, None, js="window.location.href = 'http://49.232.250.86/scale'"
    )

if __name__ == '__main__':
    conversation.launch(show_api=False, share=True)
