from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

# 加载环境变量
load_dotenv()

# 导入路由
from api.chat_api import router as chat_router

# 创建FastAPI应用
app = FastAPI(
    title=os.getenv("APP_NAME", "FastAPI AI Assistant"),
    description="基于LangChain和FastAPI的智能助手API",
    version="0.1.0",
    debug=os.getenv("DEBUG", "False").lower() == "true"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to FastAPI AI Assistant",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
