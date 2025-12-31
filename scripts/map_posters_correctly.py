#!/usr/bin/env python3
"""
Map poster files correctly based on movie titles
Run on PythonAnywhere: python3 scripts/map_posters_correctly.py
"""
import os, sys

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def get_title_to_filename_mapping():
    """Mapping of movie titles to poster filenames"""
    return {
        '肖申克的救赎': 'TheShawshankRedemption.jpg',
        '霸王别姬': 'FarewellMyConcubine.jpg',
        '阿甘正传': 'ForrestGump.jpg',
        '泰坦尼克号': 'Titanic.jpg',
        '千与千寻': 'SpiritedAway.jpg',
        '这个杀手不太冷': 'LeonTheProfessional.jpg',
        '辛德勒的名单': 'SchindlersList.jpg',
        '盗梦空间': 'Inception.jpg',
        '星际穿越': 'Interstellar.jpg',
        '寄生上流': 'Parasite.jpg',
        '放牛班的春天': 'TheChorus.jpg',
        '海上钢琴师': 'TheLegendOf1900.jpg',
        '怦然心动': 'Flipped.jpg',
        '疯狂动物城': 'Zootopia.jpg',
        '当幸福来敲门': 'ThePursuitOfHappyness.jpg',
        '龙猫': 'MyNeighborTotoro.jpg',
        '忠犬八公的故事': 'Hachi.jpg',
        '大话西游': 'JourneyToTheWest.jpg',
        '美丽心灵': 'ABeautifulMind.jpg',
        '罗马假日': 'RomanHoliday.jpg',
        '天堂电影院': 'CinemaParadiso.jpg',
        '小妇人': 'LittleWomen.jpg',
        '寻梦环游记': 'Coco.jpg',
        '教父': 'TheGodfather.jpg',
        '蝙蝠侠：黑暗骑士': 'TheDarkKnight.jpg',
        '指环王：王者归来': 'TheReturnOfTheKing.jpg',
        '阿凡达': 'Avatar.jpg',
        '黑客帝国': 'TheMatrix.jpg',
        '搏击俱乐部': 'FightClub.jpg',
        '钢铁侠': 'IronMan.jpg',
        '复仇者联盟': 'TheAvengers.jpg',
        '速度与激情': 'FastAndFurious.jpg',
        '007：大破天幕杀机': 'Skyfall.jpg',
        '碟中谍': 'MissionImpossible.jpg',
        '飓风营救': 'Taken.jpg',
        '变形金刚': 'Transformers.jpg',
        '雷神': 'Thor.jpg',
        '美国队长': 'CaptainAmerica.jpg',
        '绿巨人浩克': 'TheHulk.jpg',
        '神奇四侠': 'FantasticFour.jpg',
        'X战警': 'XMen.jpg',
        '蜘蛛侠': 'SpiderMan.jpg',
        '超人': 'Superman.jpg',
        '蝙蝠侠': 'Batman.jpg',
        '神奇女侠': 'WonderWoman.jpg',
        '正义联盟': 'JusticeLeague.jpg',
        '蚁人': 'AntMan.jpg',
        '死侍': 'Deadpool.jpg',
        '守望者': 'Watchmen.jpg',
        '浪客剑心': 'RurouniKenshin.jpg',
        '幽游白书': 'YuYuHakusho.jpg',
        '海贼王': 'OnePiece.jpg',
        '火影忍者': 'Naruto.jpg',
        '死神': 'Bleach.jpg',
        '犬夜叉': 'Inuyasha.jpg'
    }

def fix_poster_mapping():
    """Set poster URLs correctly based on movie titles"""
    app = create_app('production')
    with app.app_context():
        from models.film import Film

        # Get title to filename mapping
        title_to_file = get_title_to_filename_mapping()

        # Get all films
        films = Film.query.all()
        print(f"Database has {len(films)} films")

        updated = 0
        not_found = []

        for film in films:
            expected_filename = title_to_file.get(film.title)
            if expected_filename:
                if film.poster_url != expected_filename:
                    film.poster_url = expected_filename
                    updated += 1
                    print(f"✓ Update {film.id}: {film.title} -> {expected_filename}")
                else:
                    print(f"✓ Already correct: {film.title} -> {expected_filename}")
            else:
                not_found.append(film.title)
                print(f"⚠️  Mapping not found: {film.title}")

        if not_found:
            print(f"\n⚠️  The following {len(not_found)} films have no filename mapping:")
            for title in not_found[:5]:  # Show first 5 only
                print(f"   - {title}")
            if len(not_found) > 5:
                print(f"   ... and {len(not_found) - 5} more")

        if updated > 0:
            db.session.commit()
            print(f"\n✅ Successfully updated poster URLs for {updated} films")
        else:
            print("\nℹ️  All film poster URLs are already correct")

        # Verify first 5 films
        print("\nFirst 5 films' poster settings:")
        for film in films[:5]:
            status = "✓" if film.poster_url else "✗"
            print(f"  {status} {film.title} -> {film.poster_url or 'None'}")

if __name__ == '__main__':
    print("🔧 Map poster files correctly based on movie titles...\n")
    fix_poster_mapping()
