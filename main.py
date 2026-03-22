from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from api.router.vectorRouter import router as vector_router
from api.router.queryRouter import router as query_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vector_router, prefix="/vector") #You can pass the table path (XXXX.pdf) in the request body, and this endpoint will create a chunked vector store in the database for that pdf. It will again return the table path (XXXXX.pdf)
app.include_router(query_router, prefix="/query") # You can pass a query and the table path (XXXX.pdf) in the request body, and this endpoint will return the answer to the query by first finding the relevant chunks from the vector store of XXXXX.pdf

default_message = {"message": "API is running"}
@app.get("/")
def read_root():
    return default_message


if __name__ == "__main__":
    port = 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port)
