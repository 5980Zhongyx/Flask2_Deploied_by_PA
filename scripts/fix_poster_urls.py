#!/usr/bin/env python3
"""
修复数据库中的 poster_url 字段
在 PythonAnywhere 上运行：python3 scripts/fix_poster_urls.py
"""
import os, sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def get_local_posters():
    """获取本地海报文件列表"""
    posters_dir = 'static/posters'
    if not os.path.exists(posters_dir):
        print(f"❌ posters 目录不存在: {posters_dir}")
        return []

    posters = [f for f in os.listdir(posters_dir) if f.lower().endswith('.jpg')]
    return sorted(posters)

def fix_poster_urls():
    """根据电影ID重新设置 poster_url"""
    app = create_app('production')
    with app.app_context():
        from models.film import Film

        # 获取本地海报文件
        local_posters = get_local_posters()
        print(f"找到 {len(local_posters)} 个本地海报文件")

        # 获取所有电影
        films = Film.query.order_by(Film.id).all()
        print(f"数据库中有 {len(films)} 部电影")

        # 为每部电影设置正确的 poster_url
        updated = 0
        for i, film in enumerate(films):
            if i < len(local_posters):
                expected_filename = local_posters[i]
                if film.poster_url != expected_filename:
                    film.poster_url = expected_filename
                    updated += 1
                    print(f"更新 {film.id}: {film.title[:20]}... -> {expected_filename}")
            else:
                print(f"⚠️  电影 {film.id} 没有对应的海报文件")

        if updated > 0:
            app.db.session.commit()
            print(f"\n✅ 成功更新了 {updated} 部电影的海报URL")
        else:
            print("\nℹ️  所有电影的海报URL都已经正确")

        # 显示前5个电影的设置
        print("\n前5个电影的海报设置:")
        for film in films[:5]:
            status = "✓" if film.poster_url else "✗"
            print(f"  {status} {film.id}: {film.title[:20]}... -> {film.poster_url or '无'}")

if __name__ == '__main__':
    print("🔧 修复电影海报URL...\n")
    fix_poster_urls()
