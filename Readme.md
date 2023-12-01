# dwyang-taobao

## Quickstart

Just run 

```uvicorn app:app --host='0.0.0.0' --port=8000``` 

or for production 

```gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000``` 

in the root directory of this project.