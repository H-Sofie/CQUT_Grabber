import utils

def course_list(keyword):
    # 查询课程列表，并显示课程信息
    print('正在查询课程...')
    response = User.get_course_list(keyword)
    courses = response.get('tmpList', [])
    
    if not courses:
        print('未找到课程/该课程名额已满')
        return []
    
    kch_ids = []
    print('---------------------------------------------------')
    for i, item in enumerate(courses):
        print(f'{i}: {item["jxbmc"]}')
        print(f'   {item["kzmc"]}\t{item["xf"]}学分\t{item["yxzrs"]}人已选')
        kch_ids.append({'id': item["kch_id"], 'name': item["jxbmc"]})
    print('---------------------------------------------------')
    return kch_ids

def display_courses(course_list, action='已选课程'):
    # 显示课程列表信息
    if not course_list:
        print(f'没有{action}')
        return
    
    print('---------------------------------------------------')
    for i, item in enumerate(course_list, 1):
        print(f'{i}: {item["jxbmc"]}')
    print('---------------------------------------------------')

def choose_course(kch_ids):
    # 选课流程，选择课程后提交选课请求
    try:
        index = int(input("请输入要选择的课程名字前的序号(-1退出选课): "))
        if index == -1:
            return
        if 0 <= index < len(kch_ids):
            course_name = kch_ids[index]['name']
            confirmation = input(f"确认选择课程 {course_name}? (Y/n,默认Y): ").strip().lower()
            if confirmation == 'n':
                return
            
            kch_id = kch_ids[index]['id']
            detail = User.get_course_detail(kch_id)
            if not detail:
                print('课程具体获取失败！')
                return
            
            jxb_ids = detail[0].get('do_jxb_id')
            res = User.choose_course(jxb_ids, kch_id)
            if res.get('flag') == '1':
                print("选课成功！")
            else:
                print(res.get('msg', '选课失败'))
        else:
            print('输入序号超出范围')
    except ValueError:
        print('输入无效，请输入正确的序号')

def quit_course(kch_ids):
    # 退课流程，选择课程后提交退课请求
    try:
        index = int(input("请输入要退选的课程名字前的序号(-1退出退课): "))
        if index == -1:
            return
        if 0 <= index < len(kch_ids):
            course_name = kch_ids[index]['name']
            confirmation = input(f"确认退选课程 {course_name}? (yes/N,默认N): ").strip().lower()
            if confirmation != 'yes':
                return
            
            kch_id = kch_ids[index]['id']
            detail = User.get_course_detail(kch_id)
            if not detail:
                print('课程具体获取失败！')
                return
            
            jxb_ids = detail[0].get('do_jxb_id')
            res = User.quit_course(jxb_ids)
            if res == '1':
                print('退课成功')
            else:
                print(res)
        else:
            print('输入序号超出范围')
    except ValueError:
        print('输入无效，请输入正确的序号')

if __name__ == '__main__':
    try:
        User = utils.User()
    except Exception as e:
        print(f'初始化失败: {e}')
        input('按任意键退出...')
        exit()

    print('''
    *********************************
    欢迎使用【西唯兵抢课小助手】
    Made By H·Sofie
    Github: https://github.com/shaxiu/njtech_grabber
    功能代码如下:
    ---------------------
    1. 选课
    2. 退课
    3. 已选课程查询
    4. 退出系统
    ---------------------
    ps:前方序号为功能代码
    *********************************
    ''')

    while True:
        code = input('\n请输入功能代码:')
        if code == '4':
            break

        if code == '1':
            print('进入选课功能')
            keyword = input("请输入要查询的课程关键字(为空则返回全部结果): ")
            kch_ids = course_list(keyword)
            if kch_ids:
                choose_course(kch_ids)

        elif code == '3':
            print('正在进行已选课程查询...')
            choosed_list = User.get_choosed_list()
            display_courses(choosed_list)

        elif code == '2':
            print('正在进行已选课程查询...')
            choosed_list = User.get_choosed_list()
            if choosed_list:
                display_courses(choosed_list, action='退选课程')
                kch_ids = [{'id': item['kch_id'], 'name': item['jxbmc']} for item in choosed_list]
                quit_course(kch_ids)
        else:
            print('无效的功能代码，请重新输入')
