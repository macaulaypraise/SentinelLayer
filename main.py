from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from sentinellayer!"}


def main():
    print("CLI mode")


if __name__ == "__main__":
    main()
