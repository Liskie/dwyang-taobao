from fastapi import FastAPI, Depends, Cookie, Response
from fastapi.responses import HTMLResponse
import gradio as gr

from user_info_collection import user_info_collection
from introduction import introduction

app = FastAPI()


@app.get("/")
def read_main():
    return {"message": "This is your main app"}


app = gr.mount_gradio_app(app, user_info_collection, path='/user-info-collection')
app = gr.mount_gradio_app(app, introduction, path='/introduction')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
