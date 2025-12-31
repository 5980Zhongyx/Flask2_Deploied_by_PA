#!/usr/bin/env python3
"""
Script to check poster display issues
Run on PythonAnywhere: python3 scripts/check_posters.py
"""
import os
from app import create_app

def check_static_posters():
    """检查静态文件夹中的海报文件"""
    static_dir = 'static'
    posters_dir = os.path.join(static_dir, 'posters')

    if not os.path.exists(posters_dir):
        print(f"❌ static/posters 目录不存在: {posters_dir}")
        return []

    posters = [f for f in os.listdir(posters_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    print(f"✓ 找到 {len(posters)} 个海报文件在 static/posters/:")
    for poster in sorted(posters)[:5]:  # 只显示前5个
        print(f"  - {poster}")
    if len(posters) > 5:
        print(f"  ... 还有 {len(posters) - 5} 个文件")
    return posters

def check_database_posters():
    """检查数据库中的海报URL"""
    app = create_app('production')
    with app.app_context():
        from models.film import Film
        films = Film.query.all()
        print(f"\n✓ 数据库中有 {len(films)} 部电影")

        local_posters = 0
        remote_posters = 0
        no_posters = 0

        for film in films:
            if not film.poster_url:
                no_posters += 1
            elif film.poster_url.startswith(('http://', 'https://', '//')):
                remote_posters += 1
            else:
                local_posters += 1

        print(f"  - {local_posters} 部有本地海报")
        print(f"  - {remote_posters} 部有远程海报")
        print(f"  - {no_posters} 部没有海报")

        if local_posters > 0:
            print("
前5个本地海报电影:"            for film in films[:5]:
                if film.poster_url and not film.poster_url.startswith(('http://', 'https://', '//')):
                    print(f"  {film.id}: {film.title[:25]}... -> {film.poster_url}")

def main():
    print("🔍 检查海报显示问题...\n")

    # 检查静态文件
    static_posters = check_static_posters()

    # 检查数据库
    check_database_posters()

    print("
💡 诊断结果:"    if not static_posters:
        print("❌ 问题：static/posters/ 目录为空或不存在")
        print("   解决：上传海报文件到 PythonAnywhere 的 static/posters/ 目录")
    else:
        print("✅ 海报文件存在于 static/posters/")

    print("\n🔧 如果海报仍然不显示，检查：")
    print("1. 海报文件是否上传到 PA 的 static/posters/ 目录")
    print("2. 数据库中 poster_url 字段是否正确指向文件名")
    print("3. 文件权限是否正确 (755)")

if __name__ == '__main__':
    main()
