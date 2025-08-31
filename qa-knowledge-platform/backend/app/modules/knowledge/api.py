from fastapi import APIRouter

router = APIRouter()


@router.get("/articles")
async def get_articles():
    """获取文章列表"""
    return {"message": "文章列表功能开发中"}


@router.post("/articles")
async def create_article():
    """创建文章"""
    return {"message": "创建文章功能开发中"}


@router.get("/categories")
async def get_categories():
    """获取分类列表"""
    return {"message": "分类列表功能开发中"}


@router.get("/search")
async def search_articles():
    """搜索文章"""
    return {"message": "搜索功能开发中"}