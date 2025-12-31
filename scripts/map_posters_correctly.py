#!/usr/bin/env python3
"""
Map poster files correctly based on movie titles
Run on PythonAnywhere: python3 scripts/map_posters_correctly.py
"""
import os
import sys

from app import create_app, db

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_title_to_filename_mapping():
    """Mapping of movie titles to poster filenames (using pinyin filenames)"""
    return {
        "The Shawshank Redemption": "Xiaoshenkedejiushu.jpg",
        "Farewell My Concubine": "Bawangbieji.jpg",
        "Forrest Gump": "Aganzhengzhuan.jpg",
        "Titanic": "Taitannikehao.jpg",
        "Spirited Away": "Qianyuqianxun.jpg",
        "Leon: The Professional": "Zhegeshashoubutaileng.jpg",
        "Schindler's List": "Xindeledemingdan.jpg",
        "Inception": "Daomengkongjian.jpg",
        "Interstellar": "Xingjichuanyue.jpg",
        "Parasite": "Jishengshangliu.jpg",
        "The Chorus": "Fangniubandechuntian.jpg",
        "The Legend of 1900": "Haishanggangqinshi.jpg",
        "Flipped": "Pengranxindong.jpg",
        "Zootopia": "Fengkuangdongwucheng.jpg",
        "The Pursuit of Happyness": "Dangxingfulaiqiaomen.jpg",
        "My Neighbor Totoro": "Longmao.jpg",
        "Hachi: A Dog's Tale": "Zhongquanbagongdegushi.jpg",
        "A Simple Wish": "Dahuaxiyou.jpg",
        "A Beautiful Mind": "Meilixinling.jpg",
        "Roman Holiday": "Luomajiari.jpg",
        "Cinema Paradiso": "Tiantangdianyingyuan.jpg",
        "Little Women": "Xiaofuren.jpg",
        "Coco": "Xunmenghuanyouji.jpg",
        "The Godfather": "Jiaofu.jpg",
        "The Dark Knight": "Bianfuxia.jpg",
        "The Lord of the Rings: The Return of the King": "Zhihuanwangwangzheguilai.jpg",
        "Avatar": "Afanda.jpg",
        "The Matrix": "Heikediguo.jpg",
        "Fight Club": "Bojijulebu.jpg",
        "Iron Man": "Gangtiexia.jpg",
        "The Avengers": "Fuchouzhelianmeng.jpg",
        "Fast & Furious": "Suduyujiqing.jpg",
        "Skyfall": "007dapotianmushaji.jpg",
        "Mission: Impossible": "Diezhongdie.jpg",
        "Taken": "Jufengyingjiu.jpg",
        "Transformers": "Bianxingjingang.jpg",
        "Thor": "Leishen.jpg",
        "Captain America: The First Avenger": "Meiguoduizhang.jpg",
        "The Incredible Hulk": "Lvjurenhaoke.jpg",
        "Fantastic Four": "Shenqisixia.jpg",
        "X-Men": "Xzhanjing.jpg",
        "Spider-Man": "Zhizhuxia.jpg",
        "Superman": "Chaoren.jpg",
        "Batman Begins": "Bianfuxia.jpg",
        "Wonder Woman": "Shenqinvxia.jpg",
        "Justice League": "Zhengyilianmeng.jpg",
        "Ant-Man": "Yiren.jpg",
        "Deadpool": "Sishi.jpg",
        "Watchmen": "Shouwangzhe.jpg",
        "Rurouni Kenshin": "Langkejianxin.jpg",
        "Yu Yu Hakusho": "Youyoubaishu.jpg",
        "One Piece": "Haizeiwang.jpg",
        "Naruto": "Huoyingrenzhe.jpg",
        "Bleach": "Sishen.jpg",
        "Inuyasha": "Quanyecha.jpg",
    }


def fix_poster_mapping():
    """Set poster URLs correctly based on movie titles"""
    app = create_app("production")
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
                    print(f"Update {film.id}: {film.title} -> {expected_filename}")
                else:
                    print(f"Already correct: {film.title} -> {expected_filename}")
            else:
                not_found.append(film.title)
                print(f"Mapping not found: {film.title}")

        if not_found:
            print(f"\nThe following {len(not_found)} films have no filename mapping:")
            for title in not_found[:5]:  # Show first 5 only
                print(f"   - {title}")
            if len(not_found) > 5:
                print(f"   ... and {len(not_found) - 5} more")

        if updated > 0:
            db.session.commit()
            print(f"\nSuccessfully updated poster URLs for {updated} films")
        else:
            print("\nAll film poster URLs are already correct")

        # Verify first 5 films
        print("\nFirst 5 films' poster settings:")
        for film in films[:5]:
            status = "OK" if film.poster_url else "MISSING"
            print(f"  {status} {film.title} -> {film.poster_url or 'None'}")


if __name__ == "__main__":
    print("Map poster files correctly based on movie titles...\n")
    fix_poster_mapping()
