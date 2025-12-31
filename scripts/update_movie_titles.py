#!/usr/bin/env python3
"""
Update movie titles in database to English
Run on PythonAnywhere: python3 scripts/update_movie_titles.py
"""
import os
import sys

from app import create_app, db

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_chinese_to_english_titles():
    """Mapping of Chinese movie titles to English"""
    return {
        "肖申克的救赎": "The Shawshank Redemption",
        "霸王别姬": "Farewell My Concubine",
        "阿甘正传": "Forrest Gump",
        "泰坦尼克号": "Titanic",
        "千与千寻": "Spirited Away",
        "这个杀手不太冷": "Léon: The Professional",
        "辛德勒的名单": "Schindler's List",
        "盗梦空间": "Inception",
        "星际穿越": "Interstellar",
        "寄生上流": "Parasite",
        "放牛班的春天": "The Chorus",
        "海上钢琴师": "The Legend of 1900",
        "怦然心动": "Flipped",
        "疯狂动物城": "Zootopia",
        "当幸福来敲门": "The Pursuit of Happyness",
        "龙猫": "My Neighbor Totoro",
        "忠犬八公的故事": "Hachi: A Dog's Tale",
        "大话西游": "Journey to the West: The Demons Strike Back",
        "美丽心灵": "A Beautiful Mind",
        "罗马假日": "Roman Holiday",
        "天堂电影院": "Cinema Paradiso",
        "小妇人": "Little Women",
        "寻梦环游记": "Coco",
        "教父": "The Godfather",
        "蝙蝠侠：黑暗骑士": "The Dark Knight",
        "指环王：王者归来": "The Lord of the Rings: The Return of the King",
        "阿凡达": "Avatar",
        "黑客帝国": "The Matrix",
        "搏击俱乐部": "Fight Club",
        "钢铁侠": "Iron Man",
        "复仇者联盟": "The Avengers",
        "速度与激情": "Fast & Furious",
        "007：大破天幕杀机": "Skyfall",
        "碟中谍": "Mission: Impossible",
        "飓风营救": "Taken",
        "变形金刚": "Transformers",
        "雷神": "Thor",
        "美国队长": "Captain America: The First Avenger",
        "绿巨人浩克": "The Incredible Hulk",
        "神奇四侠": "Fantastic Four",
        "X战警": "X-Men",
        "蜘蛛侠": "Spider-Man",
        "超人": "Superman",
        "蝙蝠侠": "Batman Begins",
        "神奇女侠": "Wonder Woman",
        "正义联盟": "Justice League",
        "蚁人": "Ant-Man",
        "死侍": "Deadpool",
        "守望者": "Watchmen",
        "浪客剑心": "Rurouni Kenshin",
        "幽游白书": "Yu Yu Hakusho",
        "海贼王": "One Piece",
        "火影忍者": "Naruto",
        "死神": "Bleach",
        "犬夜叉": "Inuyasha",
    }


def update_movie_titles():
    """Update all movie titles to English"""
    app = create_app("production")
    with app.app_context():
        from models.film import Film

        # Get title mapping
        chinese_to_english = get_chinese_to_english_titles()

        # Get all films
        films = Film.query.all()
        print(f"Database has {len(films)} films")

        updated = 0
        not_found = []

        for film in films:
            english_title = chinese_to_english.get(film.title)
            if english_title:
                if film.title != english_title:
                    old_title = film.title
                    film.title = english_title
                    updated += 1
                    print(f"✓ Updated: '{old_title}' -> '{english_title}'")
                else:
                    print(f"✓ Already English: '{film.title}'")
            else:
                not_found.append(film.title)
                print(f"⚠️  No English mapping found for: '{film.title}'")

        if not_found:
            print(f"\n⚠️  The following {len(not_found)} films have no "
                  "English mapping:")
            for title in not_found[:5]:
                print(f"   - {title}")
            if len(not_found) > 5:
                print(f"   ... and {len(not_found) - 5} more")

        if updated > 0:
            db.session.commit()
            print(f"\n✅ Successfully updated titles for {updated} films")
        else:
            print("\nℹ️  All film titles are already in English")

        # Show first 5 films
        print("\nFirst 5 films:")
        for film in films[:5]:
            print(f"  {film.title}")


if __name__ == "__main__":
    print("🔧 Update movie titles to English...\n")
    update_movie_titles()
