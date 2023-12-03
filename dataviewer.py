import gradio as gr
import pandas as pd

from db_manager import DBManager


def get_all_data() -> (pd.DataFrame, int):
    with DBManager() as manager:
        data = manager.select_all_users()
        return data, gr.Markdown(f'目前共有 **{len(data)}** 位用户参与了本次实验。\n刷新本页面来获取最新数据。')


def dump_data_to_csv(data: pd.DataFrame) -> str:
    data_path = 'out/taobao_data.csv'
    with open(data_path, 'w', encoding='UTF-8') as writer:
        data.to_csv(writer, index=False)
    return data_path


with gr.Blocks(title='模拟纠纷实验') as dataviewer:
    gr.Markdown("""# 数据展示""")

    data = gr.DataFrame(interactive=False)

    user_counter = gr.Markdown('')

    dataviewer.load(
        get_all_data, None, [data, user_counter], queue=False
    )

    gr.Markdown('提示：先点击 **生成数据文件** 按钮，然后点击数据文件右侧 **蓝色链接** 即可下载。')
    download_button = gr.Button('生成数据文件')
    data_file = gr.File(label='数据文件')
    download_button.click(fn=dump_data_to_csv, inputs=data, outputs=data_file)

if __name__ == '__main__':
    dataviewer.launch(show_api=False, share=True)
