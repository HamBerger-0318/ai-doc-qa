# #切块练习
# full_text = "这是一个用于切块练习的文本,包含了多行内容.太阳当空照，花儿对我笑,小鸟说早早早,你为什么背上小书包.我背着小书包,去上学堂,老师夸我真聪明,我也要努力学本领.这是一个用于切块练习的文本,包含了多行内容.太阳当空照，花儿对我笑,小鸟说早早早,你为什么背上小书包.我背着小书包,去上学堂,老师夸我真聪明,我也要努力学本领. "
# chunks=[]
# chunk_size = 50  # 每个块的大小
# for i in range(0, len(full_text), chunk_size):
#     chunk = full_text[i:i + chunk_size]
#     chunks.append(chunk)
#     print(f"第{i//chunk_size + 1}块内容: {chunk }")
#     keyword = input("\n请输入你要搜索的关键词: ")
#     found = False
#     for c in chunks:
#         if keyword in c:
#             print(f"在第{chunks.index(c) + 1}块中找到了关键词: {keyword}")
#             found = True
#         if not found:
#             print(f"未在任何块中找到关键词: {keyword}")
#历史记录练习
history=[]
while True:
    user_input = input("请输入内容：")
    if user_input.lower() == "退出":
        break
        print(f"对话结束")
    history.append(user_input)
    recent_history =history[-2:]
    print("---------------")
    print(recent_history)
    print("========AI记忆区========")