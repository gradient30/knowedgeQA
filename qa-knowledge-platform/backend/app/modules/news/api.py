from fastapi import APIRouter

router = APIRouter()


@router.get("/items")
async def get_news_items():
    """获取资讯列表"""
    return {"message": "资讯列表功能开发中"}


@router.get("/sources")
async def get_news_sources():
    """获取资讯源列表"""
    return {"message": "资讯源列表功能开发中"}


@router.post("/sources")
async def create_news_source():
    """创建资讯源"""
    return {"message": "创建资讯源功能开发中"}