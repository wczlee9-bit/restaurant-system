from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入路由
from routes.auth_routes import router as auth_router
from routes.menu_routes import router as menu_router
from routes.order_routes import router as order_router
from routes.stats_routes import router as stats_router
from routes.stock_routes import router as stock_router
from routes.member_routes import router as member_router

app = FastAPI(
    title="餐厅管理系统 API",
    description="多店铺扫码点餐系统后端 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(menu_router)
app.include_router(order_router)
app.include_router(stats_router)
app.include_router(stock_router)
app.include_router(member_router)

@app.get("/")
def root():
    return {
        "message": "餐厅管理系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
