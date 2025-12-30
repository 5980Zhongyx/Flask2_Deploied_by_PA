"""
数据库预填充脚本
导入电影数据到数据库中，用于演示和测试
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models import Film, User, UserFilmInteraction

def load_movie_data():
    """加载电影数据"""
    # 这里使用预定义的电影数据，实际项目中可以从CSV/JSON文件或API导入
    movies_data = [
        {
            "title": "肖申克的救赎",
            "genre": "剧情",
            "year": 1994,
            "director": "弗兰克·达拉邦特",
            "description": "银行家安迪被诬陷杀人，被判无期徒刑。在肖申克监狱中，他结识了瑞德，两人成为挚友。安迪凭借智慧和勇气，在狱中建立了图书室，并最终通过自己的方式获得了自由。",
            "poster_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"
        },
        {
            "title": "霸王别姬",
            "genre": "剧情",
            "year": 1993,
            "director": "陈凯歌",
            "description": "讲述了两位京剧艺人半世纪的悲欢离合。从民国初年到文化大革命，两人从相识、相知到相离，谱写了一段刻骨铭心的爱情故事。",
            "poster_url": "https://image.tmdb.org/t/p/w500/3J8XKUfz9ZQj5Q0OqrqfL8GFJ.jpg"
        },
        {
            "title": "阿甘正传",
            "genre": "剧情",
            "year": 1994,
            "director": "罗伯特·泽米吉斯",
            "description": "阿甘是一个智商只有75的低能儿，但他凭借着坚持不懈的毅力和单纯善良的心，经历了美国历史上许多重大事件，见证了时代的变迁。",
            "poster_url": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg"
        },
        {
            "title": "泰坦尼克号",
            "genre": "爱情",
            "year": 1997,
            "director": "詹姆斯·卡梅隆",
            "description": "1912年，泰坦尼克号邮轮在 maiden voyage 中撞上冰山沉没。船上的一对青年男女坠入爱河，在生死考验中谱写了一段凄美的爱情故事。",
            "poster_url": "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg"
        },
        {
            "title": "千与千寻",
            "genre": "动画",
            "year": 2001,
            "director": "宫崎骏",
            "description": "少女千寻意外来到神灵世界的汤屋工作。为了拯救父母，她必须通过重重考验。在这个奇幻的世界中，她学会了勇敢和善良。",
            "poster_url": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuNKq.jpg"
        },
        {
            "title": "这个杀手不太冷",
            "genre": "动作",
            "year": 1994,
            "director": "吕克·贝松",
            "description": "杀手莱昂收留了邻居孤儿玛蒂尔达。在相处中，两人建立了深厚的感情。莱昂教会玛蒂尔达生存的技巧，而玛蒂尔达带给莱昂温暖和欢乐。",
            "poster_url": "https://image.tmdb.org/t/p/w500/yI6X2cCM5YPJtxMhWdENlY1aV0.jpg"
        },
        {
            "title": "辛德勒的名单",
            "genre": "历史",
            "year": 1993,
            "director": "史蒂文·斯皮尔伯格",
            "description": "二战期间，德国商人奥斯卡·辛德勒目睹了犹太人的遭遇。他利用自己的工厂拯救了上千犹太人的生命，成为人道主义的典范。",
            "poster_url": "https://image.tmdb.org/t/p/w500/c8Ass7acuOe4za6DhSattE359gr.jpg"
        },
        {
            "title": "盗梦空间",
            "genre": "科幻",
            "year": 2010,
            "director": "克里斯托弗·诺兰",
            "description": "盗梦师 Cobb 带领团队进入他人梦境窃取机密。但一次任务失败让他失去了妻子，他必须完成最后一次任务来拯救自己。",
            "poster_url": "https://image.tmdb.org/t/p/w500/7WcNkYY0nYV8veGNITwM9nDzd2U.jpg"
        },
        {
            "title": "星际穿越",
            "genre": "科幻",
            "year": 2014,
            "director": "克里斯托弗·诺兰",
            "description": "地球面临灭绝危机，前NASA宇航员库珀带领团队穿越虫洞寻找新家园。在旅途中，他们面临时空相对论带来的各种挑战。",
            "poster_url": "https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg"
        },
        {
            "title": "寄生上流",
            "genre": "惊悚",
            "year": 2019,
            "director": "奉俊昊",
            "description": "贫民窟家庭通过精心策划，成功渗透到富豪家庭中工作。他们原本的计划因为意外事件而逐渐失控，最终引发一系列悲剧。",
            "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"
        },
        {
            "title": "放牛班的春天",
            "genre": "音乐",
            "year": 2004,
            "director": "克里斯托夫·巴拉蒂",
            "description": "音乐老师克莱门特来到纪律严苛的寄宿学校，用音乐唤醒了学生们沉睡的心灵。他独特的教学方式改变了学校，也改变了学生的人生。",
            "poster_url": "https://image.tmdb.org/t/p/w500/5Jv1XwH9aUH0R3O0qCxN4J1QXw.jpg"
        },
        {
            "title": "海上钢琴师",
            "genre": "剧情",
            "year": 1998,
            "director": "朱塞佩·托纳多雷",
            "description": "天才钢琴师1900出生在邮轮上，一生从未踏上陆地。他在船上谱写了一生的音乐，见证了时代的变迁，最终选择留在船上。",
            "poster_url": "https://example.com/posters/legend.jpg"
        },
        {
            "title": "怦然心动",
            "genre": "爱情",
            "year": 2010,
            "director": "罗伯·莱纳",
            "description": "少年朱尔斯暗恋邻居女孩阿梅莉。他通过观察和记录阿梅莉的生活点滴，逐渐了解她的内心，最终赢得了她的芳心。",
            "poster_url": "https://example.com/posters/flipped.jpg"
        },
        {
            "title": "疯狂动物城",
            "genre": "动画",
            "year": 2016,
            "director": "拜伦·霍华德",
            "description": "兔子朱迪成为动物城第一位兔子警官，与狐狸尼克一起调查神秘案件。他们揭开了城市中隐藏的阴谋。",
            "poster_url": "https://example.com/posters/zootopia.jpg"
        },
        {
            "title": "当幸福来敲门",
            "genre": "传记",
            "year": 2006,
            "director": "加布里埃莱·穆奇诺",
            "description": "克里斯·加德纳失业后带着儿子流落街头。他凭借坚韧不拔的精神和对儿子的爱，最终成为成功的股票经纪人。",
            "poster_url": "https://example.com/posters/pursuit.jpg"
        },
        {
            "title": "龙猫",
            "genre": "动画",
            "year": 1988,
            "director": "宫崎骏",
            "description": "姐妹俩在乡下与神秘的龙猫成为朋友。在龙猫的陪伴下，她们度过了快乐的暑假，也学会了珍惜身边的人和事。",
            "poster_url": "https://example.com/posters/totoro.jpg"
        },
        {
            "title": "忠犬八公的故事",
            "genre": "剧情",
            "year": 2009,
            "director": "西川美和",
            "description": "教授收养了一只秋田犬八公。八公每天在车站等待主人归来，即使主人已经去世，它仍坚持了十年。这种忠诚感动了无数人。",
            "poster_url": "https://example.com/posters/hachi.jpg"
        },
        {
            "title": "大话西游",
            "genre": "喜剧",
            "year": 1995,
            "director": "刘镇伟",
            "description": "至尊宝爱上了紫霞仙子，为了救她，他穿越时空，经历了无数磨难。最终他明白了什么是真爱，什么是责任。",
            "poster_url": "https://example.com/posters/journey.jpg"
        },
        {
            "title": "美丽心灵",
            "genre": "传记",
            "year": 2001,
            "director": "朗·霍华德",
            "description": "数学家约翰·纳什患有精神分裂症，但他凭借强大的意志战胜了疾病，最终获得了诺贝尔经济学奖。",
            "poster_url": "https://example.com/posters/beautiful.jpg"
        },
        {
            "title": "罗马假日",
            "genre": "爱情",
            "year": 1953,
            "director": "威廉·惠勒",
            "description": "安妮公主微服出访罗马，与记者乔相遇。他们在罗马度过了难忘的一天，但身份的差异让他们最终分离。",
            "poster_url": "https://example.com/posters/roman.jpg"
        },
        {
            "title": "天堂电影院",
            "genre": "剧情",
            "year": 1988,
            "director": "朱塞佩·托纳多雷",
            "description": "少年托托在小镇电影院长大，电影放映员阿尔弗雷多成为他的导师。多年后，托托回到小镇，回忆起童年的时光。",
            "poster_url": "https://example.com/posters/cinema.jpg"
        },
        {
            "title": "小妇人",
            "genre": "剧情",
            "year": 2019,
            "director": "格蕾塔·葛韦格",
            "description": "19世纪，美国南北战争期间，四姐妹在家乡度过了青春时光。她们经历成长、爱情和磨难，最终走向各自的人生道路。",
            "poster_url": "https://example.com/posters/little.jpg"
        },
        {
            "title": "寻梦环游记",
            "genre": "动画",
            "year": 2017,
            "director": "李·昂克里奇",
            "description": "少年米格尔梦想成为音乐家，但在家族禁令下无法追梦。他意外进入亡灵世界，与已故祖先相遇，开启了自我发现之旅。",
            "poster_url": "https://example.com/posters/coco.jpg"
        },
        {
            "title": "教父",
            "genre": "犯罪",
            "year": 1972,
            "director": "弗朗西斯·福特·科波拉",
            "description": "黑手党家族的继承人迈克尔原本不想涉足家族生意，但哥哥被暗杀让他不得不接手。他在复仇的道路上逐渐堕落。",
            "poster_url": "https://example.com/posters/godfather.jpg"
        },
        {
            "title": "蝙蝠侠：黑暗骑士",
            "genre": "动作",
            "year": 2008,
            "director": "克里斯托弗·诺兰",
            "description": "蝙蝠侠面对小丑的疯狂挑战。小丑企图摧毁哥谭市的法治，而蝙蝠侠必须在正义与秩序之间做出选择。",
            "poster_url": "https://example.com/posters/dark.jpg"
        },
        {
            "title": "指环王：王者归来",
            "genre": "奇幻",
            "year": 2003,
            "director": "彼得·杰克逊",
            "description": "魔戒远征队在末日火山的决战中对抗黑暗力量。弗罗多必须摧毁魔戒，而阿拉贡要成为王者。",
            "poster_url": "https://example.com/posters/return.jpg"
        },
        {
            "title": "阿凡达",
            "genre": "科幻",
            "year": 2009,
            "director": "詹姆斯·卡梅隆",
            "description": "人类士兵杰克通过阿凡达项目进入潘多拉星球。他逐渐认同纳美族的文化，最终成为他们的领袖对抗人类入侵。",
            "poster_url": "https://example.com/posters/avatar.jpg"
        },
        {
            "title": "黑客帝国",
            "genre": "科幻",
            "year": 1999,
            "director": "华卓斯基姐妹",
            "description": "程序员尼奥发现现实世界是虚拟的矩阵。他加入反抗军对抗机器统治，开启了觉醒之路。",
            "poster_url": "https://example.com/posters/matrix.jpg"
        },
        {
            "title": "搏击俱乐部",
            "genre": "剧情",
            "year": 1999,
            "director": "大卫·芬奇",
            "description": "白领杰克生活乏味，他参加搏击俱乐部释放压力。俱乐部逐渐演变为地下组织，引发了一系列混乱事件。",
            "poster_url": "https://example.com/posters/fight.jpg"
        },
        {
            "title": "钢铁侠",
            "genre": "动作",
            "year": 2008,
            "director": "乔恩·费儒",
            "description": "天才发明家托尼·斯塔克被绑架后制造了钢铁战衣。他从花花公子转变为超级英雄，保护世界和平。",
            "poster_url": "https://example.com/posters/ironman.jpg"
        },
        {
            "title": "复仇者联盟",
            "genre": "动作",
            "year": 2012,
            "director": "乔斯·韦登",
            "description": "神盾局局长招集钢铁侠、美国队长、雷神等超级英雄，组成复仇者联盟对抗外星入侵者洛基。",
            "poster_url": "https://example.com/posters/avengers.jpg"
        },
        {
            "title": "速度与激情",
            "genre": "动作",
            "year": 2001,
            "director": "罗布·科恩",
            "description": "街头赛车手多米尼克和他的团队进行地下赛车比赛。他们卷入一起劫案，最终与FBI展开追逐战。",
            "poster_url": "https://example.com/posters/fast.jpg"
        },
        {
            "title": "007：大破天幕杀机",
            "genre": "动作",
            "year": 2012,
            "director": "萨姆·门德斯",
            "description": "詹姆斯·邦德调查神秘组织，揭开了一个全球性的恐怖阴谋。他必须阻止核武器扩散危机。",
            "poster_url": "https://example.com/posters/skyfall.jpg"
        },
        {
            "title": "碟中谍",
            "genre": "动作",
            "year": 1996,
            "director": "布莱恩·德·帕尔玛",
            "description": "特工伊森·亨特带领团队执行不可能的任务。他们擅长高科技装备和精密计划，拯救世界于危难之中。",
            "poster_url": "https://example.com/posters/mission.jpg"
        },
        {
            "title": "飓风营救",
            "genre": "动作",
            "year": 2008,
            "director": "路易斯·莱特里尔",
            "description": "退休特工布莱恩营救被绑架的女儿。他孤身闯入敌营，展开惊心动魄的救援行动。",
            "poster_url": "https://example.com/posters/taken.jpg"
        },
        {
            "title": "变形金刚",
            "genre": "科幻",
            "year": 2007,
            "director": "迈克尔·贝",
            "description": "少年山姆意外卷入汽车人和霸天虎的战争。变形金刚们为了地球的命运展开激烈战斗。",
            "poster_url": "https://example.com/posters/transformers.jpg"
        },
        {
            "title": "雷神",
            "genre": "动作",
            "year": 2011,
            "director": "肯尼思·布拉纳",
            "description": "北欧神话中的雷神托尔被放逐地球。他必须证明自己的价值，重新获得父亲的认可。",
            "poster_url": "https://example.com/posters/thor.jpg"
        },
        {
            "title": "美国队长",
            "genre": "动作",
            "year": 2011,
            "director": "乔·约翰斯顿",
            "description": "二战时期，史蒂夫·罗杰斯成为超级士兵美国队长。他带领咆哮突击队对抗纳粹组织的邪恶计划。",
            "poster_url": "https://example.com/posters/captain.jpg"
        },
        {
            "title": "绿巨人浩克",
            "genre": "动作",
            "year": 2003,
            "director": "李·安",
            "description": "科学家班纳博士意外获得超能力，每次愤怒都会变成绿巨人。他必须控制自己的力量，寻找治愈方法。",
            "poster_url": "https://example.com/posters/hulk.jpg"
        },
        {
            "title": "神奇四侠",
            "genre": "动作",
            "year": 2005,
            "director": "蒂姆·斯托瑞",
            "description": "四名科学家在宇宙辐射实验中获得超能力。他们组成神奇四侠团队，保护地球免受各种威胁。",
            "poster_url": "https://example.com/posters/fantastic.jpg"
        },
        {
            "title": "X战警",
            "genre": "动作",
            "year": 2000,
            "director": "布莱恩·辛格",
            "description": "变种人教授X创办学校培养年轻变种人。他们必须对抗反变种人组织，维护变种人的权益。",
            "poster_url": "https://example.com/posters/xmen.jpg"
        },
        {
            "title": "蜘蛛侠",
            "genre": "动作",
            "year": 2002,
            "director": "山姆·雷米",
            "description": "高中生彼得被放射蜘蛛咬伤获得超能力。他成为蜘蛛侠，与绿魔展开激烈战斗，保护纽约市民。",
            "poster_url": "https://example.com/posters/spiderman.jpg"
        },
        {
            "title": "超人",
            "genre": "动作",
            "year": 1978,
            "director": "理查德·唐纳",
            "description": "外星婴儿卡尔·艾尔被送到地球，取名克拉克·肯特。他长大后成为超人，用超能力维护正义。",
            "poster_url": "https://example.com/posters/superman.jpg"
        },
        {
            "title": "蝙蝠侠",
            "genre": "动作",
            "year": 1989,
            "director": "蒂姆·波顿",
            "description": "亿万富翁布鲁斯·韦恩亲眼目睹父母被杀。他成为蝙蝠侠，与小丑和企鹅人等罪犯展开斗争。",
            "poster_url": "https://example.com/posters/batman.jpg"
        },
        {
            "title": "神奇女侠",
            "genre": "动作",
            "year": 2017,
            "director": "帕蒂·杰金斯",
            "description": "亚马逊公主戴安娜离开天堂岛，来到人类世界。她发现一战正在进行，成为神奇女侠对抗邪恶势力。",
            "poster_url": "https://example.com/posters/wonder.jpg"
        },
        {
            "title": "正义联盟",
            "genre": "动作",
            "year": 2017,
            "director": "扎克·施奈德",
            "description": "超人去世后，蝙蝠侠召集神奇女侠、闪电侠等英雄组成正义联盟，对抗入侵地球的外星威胁。",
            "poster_url": "https://example.com/posters/justice.jpg"
        },
        {
            "title": "蚁人",
            "genre": "科幻",
            "year": 2015,
            "director": "佩顿·里德",
            "description": "小偷斯科特获得蚁人战衣，可以缩小身体。他加入复仇者联盟，用独特方式对抗威胁。",
            "poster_url": "https://example.com/posters/antman.jpg"
        },
        {
            "title": "死侍",
            "genre": "动作",
            "year": 2016,
            "director": "蒂姆·米勒",
            "description": "雇佣兵韦德·威尔逊患癌后接受实验获得超能力。他成为死侍，展开疯狂的复仇之旅。",
            "poster_url": "https://example.com/posters/deadpool.jpg"
        },
        {
            "title": "守望者",
            "genre": "剧情",
            "year": 2009,
            "director": "扎克·施奈德",
            "description": "一群退役超级英雄重出江湖调查同伴之死。他们揭开了一个威胁全人类的巨大阴谋。",
            "poster_url": "https://example.com/posters/watchmen.jpg"
        },
        {
            "title": "浪客剑心",
            "genre": "动作",
            "year": 1996,
            "director": "大友克洋",
            "description": "前刺客绯村剑心放下杀戮之剑，成为流浪剑客。他在新时代中寻找自己的定位和救赎。",
            "poster_url": "https://example.com/posters/rurouni.jpg"
        },
        {
            "title": "幽游白书",
            "genre": "动画",
            "year": 1992,
            "director": "冨永恒雄",
            "description": "不良少年浦饭幽助意外死亡后成为灵界侦探。他必须完成各种任务，证明自己的价值。",
            "poster_url": "https://example.com/posters/yuyu.jpg"
        },
        {
            "title": "海贼王",
            "genre": "动画",
            "year": 1999,
            "director": "宇田钢之介",
            "description": "少年路飞为了成为海贼王，踏上伟大航路。他组建草帽海贼团，寻找传说中的宝藏。",
            "poster_url": "https://example.com/posters/onepiece.jpg"
        },
        {
            "title": "火影忍者",
            "genre": "动画",
            "year": 2002,
            "director": "岸本齐史",
            "description": "孤儿鸣人梦想成为火影。他通过努力和友情，成为木叶村最强的忍者。",
            "poster_url": "https://example.com/posters/naruto.jpg"
        },
        {
            "title": "死神",
            "genre": "动画",
            "year": 2004,
            "director": "阿部记之",
            "description": "高中生黑崎一护意外获得死神力量。他必须保护人类世界免受虚的侵袭。",
            "poster_url": "https://example.com/posters/bleach.jpg"
        },
        {
            "title": "犬夜叉",
            "genre": "动画",
            "year": 2000,
            "director": "高桥留美子",
            "description": "少女戈薇穿越到战国时代，与半妖犬夜叉一起寻找四魂之玉的碎片。",
            "poster_url": "https://example.com/posters/inuyasha.jpg"
        }
    ]

    return movies_data

def seed_database():
    """填充数据库"""
    app = create_app()

    with app.app_context():
        print("开始填充数据库...")

        # 检查是否已有数据
        if Film.query.count() > 0:
            print("数据库中已有电影数据，跳过填充。")
            return

        # 加载电影数据
        movies_data = load_movie_data()
        print(f"加载了 {len(movies_data)} 部电影数据")

        # 批量插入电影
        films = []
        for movie_data in movies_data:
            film = Film(
                title=movie_data["title"],
                genre=movie_data["genre"],
                year=movie_data["year"],
                director=movie_data["director"],
                description=movie_data["description"],
                poster_url=movie_data["poster_url"]
            )
            films.append(film)

        # 批量插入
        db.session.bulk_save_objects(films)
        db.session.commit()

        print(f"成功插入 {len(films)} 部电影")

        # 创建一些示例用户和交互（用于演示推荐系统）
        create_sample_interactions()

        print("数据库填充完成！")

def create_sample_interactions():
    """创建示例用户交互，用于演示推荐系统"""
    print("创建示例用户交互...")

    # 创建一些测试用户
    test_users = [
        User(username="movie_fan", email="fan@example.com", password_hash="pbkdf2:sha256:150000$dummy$dummy"),
        User(username="action_lover", email="action@example.com", password_hash="pbkdf2:sha256:150000$dummy$dummy"),
        User(username="anime_kid", email="anime@example.com", password_hash="pbkdf2:sha256:150000$dummy$dummy"),
    ]

    for user in test_users:
        if not User.query.filter_by(username=user.username).first():
            db.session.add(user)

    db.session.commit()

    # 为用户创建一些交互
    movie_fan = User.query.filter_by(username="movie_fan").first()
    action_lover = User.query.filter_by(username="action_lover").first()
    anime_kid = User.query.filter_by(username="anime_kid").first()

    # movie_fan 喜欢经典电影
    classic_movies = Film.query.filter(Film.year < 2000).limit(10).all()
    for movie in classic_movies[:5]:  # 喜欢其中5部
        interaction = UserFilmInteraction(
            user_id=movie_fan.id,
            film_id=movie.id,
            liked=True,
            rating=4
        )
        db.session.add(interaction)

    # action_lover 喜欢动作片
    action_movies = Film.query.filter(Film.genre.contains("动作")).limit(10).all()
    for movie in action_movies[:6]:  # 喜欢其中6部
        interaction = UserFilmInteraction(
            user_id=action_lover.id,
            film_id=movie.id,
            liked=True,
            rating=5
        )
        db.session.add(interaction)

    # anime_kid 喜欢动画片
    anime_movies = Film.query.filter(Film.genre.contains("动画")).limit(10).all()
    for movie in anime_movies[:4]:  # 喜欢其中4部
        interaction = UserFilmInteraction(
            user_id=anime_kid.id,
            film_id=movie.id,
            liked=True,
            rating=5,
            review_text="超级好看！"
        )
        db.session.add(interaction)

    # 创建一些共同偏好，让推荐系统能找到相似用户
    shared_movies = Film.query.filter(Film.genre.contains("剧情")).limit(5).all()
    for movie in shared_movies:
        # movie_fan 和 action_lover 都喜欢一些剧情片
        for user in [movie_fan, action_lover]:
            interaction = UserFilmInteraction(
                user_id=user.id,
                film_id=movie.id,
                liked=True,
                rating=4
            )
            db.session.add(interaction)

    db.session.commit()
    print("示例用户交互创建完成")

if __name__ == "__main__":
    seed_database()
