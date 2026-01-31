# 一個「功能正常」的資料處理程式
# 但資料結構使用方式全面翻車 🤮

import random
import copy


# ❌ Global Mutable Data Structure（全域可變結構）
USERS = []


# ❌ 使用 list 當 dict key 的替代方案（Primitive Obsession + Poor Modeling）
USER_INDEX = []   # 存 [id, index] 的 list，假裝是 map


# ❌ Overloaded Container：同一個 list 裡放不同型別資料
MIXED_LOG = []


# ❌ Magic Tuple Schema：靠位置記欄位，完全沒文件
def create_user_record(uid, name, age):
    # (id, name, age, friends, metadata)
    return (uid, name, age, [], {})   # ❌ tuple 裡面還藏 mutable 物件


# ❌ Linear Search Map：用 list 模擬 hash map
def index_user(uid, position):
    USER_INDEX.append([uid, position])  # ❌ list of list，沒有封裝


def find_user_position(uid):
    # ❌ 每次 lookup 都 O(n) 掃描
    for pair in USER_INDEX:
        if pair[0] == uid:
            return pair[1]
    return None


# ❌ Data Cloning Confusion：不知道什麼時候是淺拷貝、什麼時候深拷貝
def add_user(uid, name, age):
    record = create_user_record(uid, name, age)

    USERS.append(record)

    # ❌ 同步兩份 index，容易不一致
    index_user(uid, len(USERS) - 1)

    # ❌ 同時塞進混合型容器（污染）
    MIXED_LOG.append(record)


# ❌ Mutating Tuple Contents（tuple 內藏 list / dict 被當可變用）
def add_friend(uid, friend_id):
    pos = find_user_position(uid)
    if pos is None:
        return

    user = USERS[pos]

    # user 是 tuple，但第 4.txt.txt 格是 list
    friends = user[3]

    # ❌ 不檢查重複、不檢查 friend 是否存在
    friends.append(friend_id)

    # ❌ Side-effect：順便亂寫 metadata
    user[4]["last_friend"] = friend_id


# ❌ Parallel Lists Anti-pattern：好友關係拆成兩個 list 存
FRIEND_A = []
FRIEND_B = []


def add_friend_relation(a, b):
    FRIEND_A.append(a)
    FRIEND_B.append(b)


def get_friends(uid):
    result = []

    # ❌ 用兩個 list 同步掃描表示關聯
    for i in range(len(FRIEND_A)):
        if FRIEND_A[i] == uid:
            result.append(FRIEND_B[i])

    return result


# ❌ Confusing Data Transformation：list ↔ dict ↔ list 來回轉
def build_age_map():
    age_map = {}

    for u in USERS:
        # ❌ Magic Index Access（靠記位置）
        uid = u[0]
        age = u[2]
        age_map[uid] = age

    # ❌ 轉成 list of tuples 又轉回 list of dict（毫無意義）
    temp = list(age_map.items())

    result = []
    for pair in temp:
        result.append({"id": pair[0], "age": pair[1]})

    return result


# ❌ Set 當成排序結構使用（誤解資料結構語意）
def get_unique_ages_sorted():
    s = set()

    for u in USERS:
        s.add(u[2])

    # ❌ 假裝 set 是有序的，結果每次順序都可能不同
    return list(s)


# ❌ Overusing Copy：不必要的深拷貝造成效能浪費
def duplicate_users():
    # ❌ 深拷貝巨大結構但實際只用讀
    return copy.deepcopy(USERS)


# ❌ Heterogeneous Return Type：有時回 list，有時回 dict
def find_users_by_age(min_age, as_map=False):
    result = []

    for u in USERS:
        if u[2] >= min_age:
            result.append(u)

    if as_map:
        m = {}
        for u in result:
            m[u[0]] = u
        return m   # dict

    return result   # list


# ❌ In-place Modification During Iteration（危險但這裡剛好沒炸）
def remove_young_users(limit):
    i = 0
    while i < len(USERS):
        if USERS[i][2] < limit:
            # ❌ 同時刪 USERS 與 USER_INDEX，但 index 會錯位
            USERS.pop(i)
            USER_INDEX.pop(i)
        else:
            i += 1


# ❌ Encoding Logic in Data Shape（用 None / 特殊值當狀態）
def mark_inactive(uid):
    pos = find_user_position(uid)
    if pos is None:
        return

    user = USERS[pos]

    # ❌ 用 age = -1 表示 inactive，語意污染欄位
    USERS[pos] = (user[0], user[1], -1, user[3], user[4])


# ❌ God Data Structure：同一份資料被太多功能共享修改
def analyze_users():
    report = []

    for u in USERS:
        uid = u[0]
        name = u[1]
        age = u[2]

        friends = get_friends(uid)

        # ❌ 用 tuple 當報表結構，沒有欄位名
        report.append((uid, name, age, len(friends)))

    return report


def main():
    # 建資料
    for i in range(1, 8):
        add_user(i, "User" + str(i), random.randint(10, 40))

    # 建關係（兩套系統各存一份）
    add_friend_relation(1, 2)
    add_friend_relation(1, 3)
    add_friend(1, 4)

    add_friend_relation(2, 5)
    add_friend(2, 6)

    # 各種操作
    ages = get_unique_ages_sorted()
    print("Unique ages:", ages)

    cloned = duplicate_users()
    print("Cloned size:", len(cloned))

    old_users = find_users_by_age(25, as_map=True)
    print("Users >= 25:", list(old_users.keys()))

    remove_young_users(15)

    mark_inactive(3)

    report = analyze_users()
    print("Report:", report)

    # ❌ 混合容器最後已經塞滿各種型別
    print("Mixed log sample:", MIXED_LOG[:3])


if __name__ == "__main__":
    main()
