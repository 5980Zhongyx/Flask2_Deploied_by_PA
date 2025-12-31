#!/usr/bin/env python3
"""
根据电影标题正确映射海报文件
在 PythonAnywhere 上运行：python3 scripts/map_posters_correctly.py
"""
import os, sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def get_title_to_filename_mapping():
    """电影标题到文件名的映射"""
    return {
        '肖申克的救赎': 'Xiaoshenkedejiushu.jpg',
        '霸王别姬': 'Bawangbieji.jpg',
        '阿甘正传': 'Aganzhengzhuan.jpg',
        '泰坦尼克号': 'Taitannikehao.jpg',
        '千与千寻': 'Qianyuqianxun.jpg',
        '这个杀手不太冷': 'Zhegeshashoubutaileng.jpg',
        '辛德勒的名单': 'Xindeledemingdan.jpg',
        '盗梦空间': 'Daomengkongjian.jpg',
        '星际穿越': 'Xingjichuanyue.jpg',
        '寄生上流': 'Jishengshangliu.jpg',
        '放牛班的春天': 'Fangniubandechuntian.jpg',
        '海上钢琴师': 'Haishanggangqinshi.jpg',
        '怦然心动': 'Pengranxindong.jpg',
        '疯狂动物城': 'Fengkuangdongwucheng.jpg',
        '当幸福来敲门': 'Dangxingfulaiqiaomen.jpg',
        '龙猫': 'Longmao.jpg',
        '忠犬八公的故事': 'Zhongquanbagongdegushi.jpg',
        '大话西游': 'Dahuaxiyou.jpg',
        '美丽心灵': 'Meilixinling.jpg',
        '罗马假日': 'Luomajiari.jpg',
        '天堂电影院': 'Tiantangdianyingyuan.jpg',
        '小妇人': 'Xiaofuren.jpg',
        '寻梦环游记': 'Xunmenghuanyouji.jpg',
        '教父': 'Jiaofu.jpg',
        '蝙蝠侠：黑暗骑士': 'Bianfuxia.jpg',
        '指环王：王者归来': 'Zhihuanwangwangzheguilai.jpg',
        '阿凡达': 'Afanda.jpg',
        '黑客帝国': 'Heikediguo.jpg',
        '搏击俱乐部': 'Bojijulebu.jpg',
        '钢铁侠': 'Gangtiexia.jpg',
        '复仇者联盟': 'Fuchouzhelianmeng.jpg',
        '速度与激情': 'Suduyujiqing.jpg',
        '007：大破天幕杀机': 'Linglingqidapotianmushaji.jpg',
        '碟中谍': 'Diezhongdie.jpg',
        '飓风营救': 'Jufengyingjiu.jpg',
        '变形金刚': 'Bianxingjingang.jpg',
        '雷神': 'Leishen.jpg',
        '美国队长': 'Meiguoduizhang.jpg',
        '绿巨人浩克': 'Lvjurenhaoke.jpg',
        '神奇四侠': 'Shenqisixia.jpg',
        'X战警': 'Xzhanjing.jpg',
        '蜘蛛侠': 'Zhizhuxia.jpg',
        '超人': 'Chaoren.jpg',
        '蝙蝠侠': 'Bianfuxiaheianqishi.jpg',
        '神奇女侠': 'Shenqinvxia.jpg',
        '正义联盟': 'Zhengyilianmeng.jpg',
        '蚁人': 'Yiren.jpg',
        '死侍': 'Sishi.jpg',
        '守望者': 'Shouwangzhe.jpg',
        '浪客剑心': 'Langkejianxin.jpg',
        '幽游白书': 'Youyoubaishu.jpg',
        '海贼王': 'Haizeiwang.jpg',
        '火影忍者': 'Huoyingrenzhe.jpg',
        '死神': 'Sishen.jpg',
        '犬夜叉': 'Quanyecha.jpg'
    }

def fix_poster_mapping():
    """根据电影标题正确设置海报URL"""
    app = create_app('production')
    with app.app_context():
        from models.film import Film

        # 获取标题到文件名的映射
        title_to_file = get_title_to_filename_mapping()

        # 获取所有电影
        films = Film.query.all()
        print(f"数据库中有 {len(films)} 部电影")

        updated = 0
        not_found = []

        for film in films:
            expected_filename = title_to_file.get(film.title)
            if expected_filename:
                if film.poster_url != expected_filename:
                    film.poster_url = expected_filename
                    updated += 1
                    print(f"✓ 更新 {film.id}: {film.title} -> {expected_filename}")
                else:
                    print(f"✓ 已经正确: {film.title} -> {expected_filename}")
            else:
                not_found.append(film.title)
                print(f"⚠️  未找到映射: {film.title}")

        if not_found:
            print(f"\n⚠️  以下 {len(not_found)} 部电影没有找到对应的文件名:")
            for title in not_found[:5]:  # 只显示前5个
                print(f"   - {title}")
            if len(not_found) > 5:
                print(f"   ... 还有 {len(not_found) - 5} 部")

        if updated > 0:
            db.session.commit()
            print(f"\n✅ 成功更新了 {updated} 部电影的海报URL")
        else:
            print("\nℹ️  所有电影的海报URL都已经正确")

        # 验证前5个电影
        print("\n前5个电影的海报设置:")
        for film in films[:5]:
            status = "✓" if film.poster_url else "✗"
            print(f"  {status} {film.title} -> {film.poster_url or '无'}")

if __name__ == '__main__':
    print("🔧 根据电影标题正确映射海报文件...\n")
    fix_poster_mapping()
