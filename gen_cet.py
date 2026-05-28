#!/usr/bin/env python3
"""为 DualLingo 生成符合四六级考纲的中英互译题目"""
import json, os

CET_QUESTIONS = [
    # ========== 中国文化 (Chinese Culture) ==========
    # 四级翻译常考：传统节日、名胜古迹、饮食文化
    {"chinese": "春节是中国最重要的传统节日，人们通常会回家与家人团聚。", "english": "The Spring Festival is the most important traditional holiday in China, when people usually return home to reunite with their families."},
    {"chinese": "中秋节是家人团聚的时刻，人们一边赏月一边吃月饼。", "english": "The Mid-Autumn Festival is a time for family reunion, when people admire the full moon while eating mooncakes."},
    {"chinese": "红色在中国文化中象征着好运和幸福。", "english": "The color red symbolizes good luck and happiness in Chinese culture."},
    {"chinese": "中国书法是一门古老的艺术，有着数千年的历史。", "english": "Chinese calligraphy is an ancient art form with a history of thousands of years."},
    {"chinese": "故宫位于北京市中心，是中国古代建筑的杰出代表。", "english": "Located in the center of Beijing, the Forbidden City is an outstanding representative of ancient Chinese architecture."},
    {"chinese": "中国茶文化源远流长，喝茶已成为中国人日常生活的一部分。", "english": "Chinese tea culture has a long history, and drinking tea has become part of Chinese people's daily life."},
    {"chinese": "长城是世界上最伟大的建筑奇迹之一，每年吸引数百万游客。", "english": "The Great Wall is one of the greatest architectural wonders in the world, attracting millions of tourists every year."},
    {"chinese": "中国剪纸是一种民间艺术，常用于装饰窗户和墙壁。", "english": "Chinese paper-cutting is a folk art often used to decorate windows and walls."},
    {"chinese": "丝绸之路促进了中国与西方国家的文化和贸易交流。", "english": "The Silk Road promoted cultural and trade exchanges between China and Western countries."},
    {"chinese": "功夫不仅是一种武术，更是中国传统文化的重要组成部分。", "english": "Kung fu is not only a martial art but also an important part of traditional Chinese culture."},

    # ========== 教育 (Education) ==========
    {"chinese": "近年来，越来越多的中国学生选择出国留学。", "english": "In recent years, an increasing number of Chinese students have chosen to study abroad."},
    {"chinese": "高等教育在培养创新人才方面发挥着关键作用。", "english": "Higher education plays a key role in cultivating innovative talents."},
    {"chinese": "终身学习已成为现代社会发展的必然要求。", "english": "Lifelong learning has become an inevitable requirement for the development of modern society."},
    {"chinese": "许多家长非常重视孩子的教育，希望他们能考上好大学。", "english": "Many parents attach great importance to their children's education and hope they can enter a good university."},
    {"chinese": "读书不仅能增长知识，还能开阔视野。", "english": "Reading can not only increase knowledge but also broaden one's horizons."},
    {"chinese": "实践能力与理论知识同等重要，都应该在大学教育中得到重视。", "english": "Practical ability is as important as theoretical knowledge, and both should be emphasized in university education."},
    {"chinese": "考试分数不应成为评价学生的唯一标准。", "english": "Exam scores should not be the only criterion for evaluating students."},
    {"chinese": "兴趣是最好的老师，选择专业时应考虑自己的兴趣所在。", "english": "Interest is the best teacher, and one should consider their interests when choosing a major."},
    {"chinese": "网上学习为人们提供了灵活便捷的学习方式。", "english": "Online learning provides people with a flexible and convenient way to study."},
    {"chinese": "批判性思维是大学生必须具备的重要能力之一。", "english": "Critical thinking is one of the essential abilities that college students must possess."},

    # ========== 科技与互联网 (Technology & Internet) ==========
    {"chinese": "智能手机极大地改变了人们的沟通方式和生活方式。", "english": "Smartphones have greatly changed the way people communicate and live."},
    {"chinese": "人工智能正在被广泛应用于医疗、金融和交通等领域。", "english": "Artificial intelligence is being widely applied in fields such as healthcare, finance, and transportation."},
    {"chinese": "移动支付在中国已经非常普及，很多人出门几乎不带现金。", "english": "Mobile payment has become so widespread in China that many people hardly carry cash when going out."},
    {"chinese": "互联网让世界变成了一个地球村，信息传播更加迅速。", "english": "The Internet has turned the world into a global village, making information spread more rapidly."},
    {"chinese": "社交媒体改变了人们获取新闻和与他人交流的方式。", "english": "Social media has changed the way people get news and communicate with others."},
    {"chinese": "电子商务的快速发展给传统零售业带来了巨大挑战。", "english": "The rapid development of e-commerce has brought enormous challenges to the traditional retail industry."},
    {"chinese": "大数据分析可以帮助企业更好地了解消费者的需求。", "english": "Big data analysis can help companies better understand consumer needs."},
    {"chinese": "5G技术的普及将推动物联网和智慧城市的发展。", "english": "The popularization of 5G technology will drive the development of the Internet of Things and smart cities."},
    {"chinese": "虽然科技带来了便利，但我们也应该注意保护个人隐私。", "english": "Although technology brings convenience, we should also pay attention to protecting personal privacy."},
    {"chinese": "在线教育打破了时间和空间的限制，让优质教育资源得以共享。", "english": "Online education breaks the limitations of time and space, allowing high-quality educational resources to be shared."},

    # ========== 环境保护 (Environment) ==========
    {"chinese": "环境保护是每个公民应尽的责任和义务。", "english": "Environmental protection is the responsibility and duty of every citizen."},
    {"chinese": "政府已经采取了一系列措施来减少空气污染。", "english": "The government has taken a series of measures to reduce air pollution."},
    {"chinese": "垃圾分类有助于资源的回收利用，减少环境污染。", "english": "Garbage sorting helps recycle resources and reduce environmental pollution."},
    {"chinese": "使用公共交通工具是减少碳排放的有效方式之一。", "english": "Using public transportation is one of the effective ways to reduce carbon emissions."},
    {"chinese": "可再生能源如太阳能和风能将在未来发挥更重要的作用。", "english": "Renewable energy sources such as solar and wind power will play a more important role in the future."},
    {"chinese": "绿水青山就是金山银山，我们应该坚持可持续发展。", "english": "Lucid waters and lush mountains are invaluable assets, and we should adhere to sustainable development."},
    {"chinese": "全球变暖导致极端天气事件越来越频繁。", "english": "Global warming has led to increasingly frequent extreme weather events."},
    {"chinese": "保护濒危物种对于维护生态平衡至关重要。", "english": "Protecting endangered species is crucial for maintaining ecological balance."},

    # ========== 社会热点 (Social Issues) ==========
    {"chinese": "随着生活水平的提高，人们越来越注重健康和养生。", "english": "With the improvement of living standards, people are paying more and more attention to health and wellness."},
    {"chinese": "人口老龄化给社会保障体系带来了巨大压力。", "english": "The aging population has put enormous pressure on the social security system."},
    {"chinese": "志愿者活动不仅能帮助他人，也能丰富自己的人生经历。", "english": "Volunteer activities can not only help others but also enrich one's own life experience."},
    {"chinese": "年轻人应该学会平衡工作与生活，避免过度劳累。", "english": "Young people should learn to balance work and life and avoid overwork."},
    {"chinese": "城乡差距是当前中国社会发展面临的主要问题之一。", "english": "The urban-rural gap is one of the major issues facing China's social development today."},
    {"chinese": "网络谣言对社会秩序和个人名誉都会造成严重损害。", "english": "Online rumors can cause serious damage to social order and personal reputation."},
    {"chinese": "越来越多的人开始重视心理健康，寻求专业心理咨询。", "english": "More and more people are beginning to value mental health and seek professional psychological counseling."},
    {"chinese": "共享单车解决了城市出行的最后一公里问题。", "english": "Shared bicycles have solved the last-mile problem of urban transportation."},
    {"chinese": "食品安全直接关系到人民群众的身体健康。", "english": "Food safety is directly related to the health of the people."},
    {"chinese": "公共场合应该遵守秩序，尊重他人的权利和感受。", "english": "In public places, one should observe order and respect the rights and feelings of others."},

    # ========== 写作常用 (Writing Useful) ==========
    {"chinese": "凡事都有两面性，我们应该全面客观地看待问题。", "english": "Every coin has two sides, and we should look at issues comprehensively and objectively."},
    {"chinese": "实践是检验真理的唯一标准。", "english": "Practice is the sole criterion for testing truth."},
    {"chinese": "不积跬步无以至千里，成功需要日积月累的努力。", "english": "Without accumulating small steps, one cannot reach a thousand miles; success requires accumulated effort over time."},
    {"chinese": "与其抱怨现状，不如积极寻找解决问题的方法。", "english": "Instead of complaining about the current situation, it is better to actively seek solutions to problems."},
    {"chinese": "团队合作往往能产生一加一大于二的效果。", "english": "Teamwork often produces results where the whole is greater than the sum of its parts."},
    {"chinese": "面对困难时，积极乐观的心态是成功的一半。", "english": "When facing difficulties, a positive and optimistic attitude is half the battle."},
    {"chinese": "经验是最好的老师，但学费往往很贵。", "english": "Experience is the best teacher, but the tuition fee is often very high."},
    {"chinese": "良好的沟通能力是建立人际关系的基础。", "english": "Good communication skills are the foundation for building interpersonal relationships."},
    {"chinese": "学会独立思考比记住标准答案更加重要。", "english": "Learning to think independently is more important than memorizing standard answers."},
    {"chinese": "选择比努力更重要，但努力会让你的选择变得正确。", "english": "Choice is more important than effort, but effort will make your choice right."},
]

def main():
    all_cet = []
    for i, q in enumerate(CET_QUESTIONS):
        all_cet.append({
            "id": f"cet{i+1:03d}",
            "chinese": q["chinese"],
            "english": q["english"],
            "category": "cet"
        })

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cet_questions.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_cet, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(all_cet)} CET questions -> {out_path}")
    # Topic breakdown
    topics = ["中国文化", "教育", "科技与互联网", "环境保护", "社会热点", "写作常用"]
    for t in topics:
        print(f"  {t}")

if __name__ == "__main__":
    main()
