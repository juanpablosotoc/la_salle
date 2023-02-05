
from flask import Flask, render_template, request, redirect, session, url_for
from mysql import connector

connection_args = {
    "user": "root",
    "host": "localhost",
    "password": "Joaqo1664",
    "database": "la_salle",
    "buffered": True,
}


class Mysql_fnc:
    def __init__(self, fnc, func_name) -> None:
        self.func_name = func_name
        self.__no_connect = fnc

    def no_connect(self, cursor, connection, **kwargs):
        print(self.func_name)
        return self.__no_connect(cursor, connection, **kwargs)

    def connect(self, **kwargs):
        print(self.func_name)
        try:
            connection = connector.connect(**connection_args)
            print(connection)
            if connection.is_connected():
                print("mysql session started")
                cursor = connection.cursor(dictionary=True) 
                return {"error": False, "data": self.__no_connect(connection=connection, cursor=cursor, **kwargs)}
        except connector.Error as e:
            connection.rollback()
            print(e)
            return {"error": True, "data": e}
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("mysql session ended")


def mysql_decorate(fnc):
    return Mysql_fnc(fnc, func_name=fnc.__name__)


@mysql_decorate
def insert_calendar(connection, cursor, **kwargs):
    beg_query = "insert into calendars ("
    mid_query = "values ("
    query = composite_insert(beg_query, mid_query, kwargs)
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def update_calendar(connection, cursor, **kwargs):
    days = ["mon", "tue", "wed", "thu", "fri"]
    for (key, value) in kwargs.items():
        if key not in days:
            continue
        query = f"""
        update calendars
        set {key} = "{value}"
        where username = "{kwargs["username"]}";
        """
        cursor.execute(query)
        connection.commit()


@mysql_decorate
def get_user_calendar(connection, cursor, **kwargs):
    query = f"""
    select cast(mon as decimal) as mon, cast(tue as decimal) as tue, cast(wed as decimal) as wed, cast(thu as decimal) as thu, cast(fri as decimal) as fri
    from calendars 
    where username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    return cursor.fetchall()[0]
    

@mysql_decorate
def get_normal_calendar(connection, cursor, **kwargs):
    query = f"""
    select DATE_FORMAT(mon, "%H:%i") AS mon, DATE_FORMAT(tue, "%H:%i") AS tue, DATE_FORMAT(wed, "%H:%i") AS wed, DATE_FORMAT(thu, "%H:%i") AS thu, DATE_FORMAT(fri, "%H:%i") AS fri
    from calendars 
    where username= "{kwargs["username"]}";
    """
    cursor.execute(query)
    return cursor.fetchall()[0]


@mysql_decorate
def select_curent_group(connection, cursor, **kwargs):
    current_group = None
    query = f"""
    select group_id 
    from grouping_t 
    where username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    response = cursor.fetchall()
    if len(response) != 0:
        current_group = response[0]["group_id"]
    return current_group


@mysql_decorate
def get_current_group_users_data(connection, cursor, **kwargs):
    current_group = select_curent_group.no_connect(connection, cursor, username=kwargs["username"])
    query = f"""
    select username
    from grouping_t
    where group_id = {current_group};
    """
    print(query)
    cursor.execute(query)
    users_data = [get_user_data.no_connect(connection, cursor, username=entry["username"])[0] for entry in cursor.fetchall()]
    return users_data


@mysql_decorate
def select_last_user_grouping_history(connection, cursor, **kwargs):
    query = f"""
    select username, f_group_id, t_group_id, TIMESTAMPDIFF(SECOND, date, current_timestamp) as time_since_last_modification
    from grouping_history
    where username = "{kwargs["username"]}"
    order by date desc
    limit 1;
    """
    cursor.execute(query)
    return cursor.fetchall()


@mysql_decorate
def delete_empty_groups(connection, cursor, **kwargs):
    query = f"""
    delete from groups_t
    where id not in (
        select distinct group_id 
        from grouping_t
    );
    """
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def insert_user_into_group(connection, cursor, **kwargs):
    query = f"""
    insert into grouping_t (username, group_id)
    values ("{kwargs["username"]}", {kwargs["group_id"]});
    """
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def update_user_into_group(connection, cursor, **kwargs):
    query = f"""
    update grouping_t
    set group_id = {kwargs["group_id"]}
    where username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def insert_update_user_into_group(connection, cursor, **kwargs):
    if kwargs["current_group"] == None:
        insert_user_into_group.no_connect(connection, cursor, username=kwargs["username"], group_id=kwargs["group_id"])
    else:
        update_user_into_group.no_connect(connection, cursor, username=kwargs["username"], group_id=kwargs["group_id"])
    insert_grouping_history.no_connect(connection, cursor, username=kwargs["username"], to_group_id=kwargs["group_id"])


@mysql_decorate
def select_avg_group(connection, cursor, **kwargs):
    available_groups = get_omit_string(kwargs["available_groups"])
    query = f"""
    select group_id, avg(mon) as mon, avg(tue) as tue, avg(wed) as wed, avg(thu) as thu, avg(fri) as fri
    from calendars
    inner join grouping_t
    using(username)
    where group_id in {available_groups}
    group by group_id;
    """
    cursor.execute(query)
    return cursor.fetchall()


@mysql_decorate 
def create_new_group(connection, cursor, **kwargs):
    query = f"""
    insert into groups_t(initial_grade)
    values ({kwargs["grade"]});
    """
    cursor.execute(query)
    connection.commit()
    query = """
    select LAST_INSERT_ID();
    """
    cursor.execute(query)
    return cursor.fetchall()[0]["LAST_INSERT_ID()"]

print
@mysql_decorate
def insert_grouping_history(connection, cursor, **kwargs):
    last_group = select_curent_group.no_connect(connection, cursor, username=kwargs["username"])
    if last_group == None:
        last_group = "null"
    query = f"""
    insert into grouping_history (username, f_group_id, t_group_id)
    values ("{kwargs["username"]}", {last_group}, {kwargs["to_group_id"]});
    """
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def get_available_groups_to_user(connection, cursor, **kwargs):
    omit_string = get_omit_string()
    if kwargs["force"] == True:
        if kwargs["current_group"] != None:
            omit_string = get_omit_string([kwargs["current_group"]])
    query = f"""
    select count(*) as amount_of_users_in_group, u.group_id
    from grouping_t u
    inner join groups_t g
    on g.id = u.group_id
    where ABS(g.initial_grade - {kwargs["grade"]}) <= 1
    and group_id not in {omit_string}
    group by group_id
    having amount_of_users_in_group < 5;
    """
    print(query)
    cursor.execute(query)
    available_groups = cursor.fetchall()
    return available_groups


@mysql_decorate
def check_if_should_group_again(connection, cursor, **kwargs):
    last_modification = select_last_user_grouping_history.no_connect(connection, cursor, username=kwargs["username"])
    if last_modification is None:
        return True
    if len(last_modification) != 0 and not kwargs["force"]:
        seconds_since_last_mod = last_modification[0]["time_since_last_modification"]
        if seconds_since_last_mod/3600 >= 24:
            return True
        return False
    return True


@mysql_decorate
def select_best_group_for_user(connection, cursor, **kwargs):
    available_groups_ids = [entry["group_id"] for entry in kwargs["available_groups"]]
    avg_time_of_all_groups = select_avg_group.no_connect(connection, cursor, available_groups=available_groups_ids)
    groups_similarity = get_difference_times_from_groups(avg_time_of_all_groups, kwargs["my_time"])
    best_group = None
    for group in groups_similarity:
        if best_group == None or best_group["difference_in_hours"] > group["difference_in_hours"]:
            best_group = group
    return best_group


@mysql_decorate
def place_user_into_best_group(connection, cursor, **kwargs):
    if not check_if_should_group_again.no_connect(connection, cursor, force=kwargs["force"], username=kwargs["username"]):
        return
    print('got here muthafleckaaa 281')
    current_group = select_curent_group.no_connect(connection, cursor, username=kwargs["username"])
    grade = get_user_data.no_connect(connection, cursor, username=kwargs["username"])[0]["grade_id"]
    available_groups = get_available_groups_to_user.no_connect(connection, cursor, username=kwargs["username"], force=kwargs["force"], grade=grade, current_group=current_group)
    my_time = get_user_calendar.no_connect(connection, cursor, username=kwargs["username"])
    best_group = select_best_group_for_user.no_connect(connection, cursor, available_groups=available_groups, my_time=my_time)
    if best_group == None:
        new_group_id = create_new_group.no_connect(connection, cursor, username=kwargs["username"], grade=grade)
        insert_update_user_into_group.no_connect(connection, cursor, username=kwargs["username"], group_id=new_group_id, current_group=current_group)
    else:
        if best_group["group_id"] != current_group:
            insert_update_user_into_group.no_connect(connection, cursor, username=kwargs["username"], group_id=best_group["group_id"], current_group=current_group)
            print(cursor.fetchall())
    delete_empty_groups.no_connect(connection, cursor)


@mysql_decorate
def search_profile_preview(connection, cursor, **kwargs):
    omit_string = get_omit_string(kwargs["omit"])
    def get_query(search_by, limit):
        return f"""
        select username, profile_photo, name
        from users 
        where {search_by} LIKE "%{kwargs["search_word"]}%"
        and username not in {omit_string}
        LIMIT {limit};
        """
    cursor.execute(get_query(search_by="username", limit=kwargs["limit"]))
    profiles_preview = cursor.fetchall()
    if len(profiles_preview) < kwargs["limit"]:
        omit_usernames = [*kwargs["omit"], *[entry["username"] for entry in profiles_preview]]
        omit_string = str(tuple(omit_usernames))
        if len(omit_usernames) == 1:
            omit_string = str(tuple(omit_usernames))[:-2] + ")"
        cursor.execute(get_query("name", limit=kwargs["limit"]-len(profiles_preview)))
        profiles_preview_by_name = cursor.fetchall()
        profiles_preview = [*profiles_preview, *profiles_preview_by_name]
    return profiles_preview


@mysql_decorate
def get_user_data(connection, cursor, **kwargs):
    query = f"""
    select username, password, name, grade_id, internship, profile_photo, bio
    from users 
    where username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    return cursor.fetchall()


@mysql_decorate
def insert_user(connection, cursor, **kwargs):
    beg_query = "insert into users ("
    mid_query = "values ("
    query = composite_insert(beg_query, mid_query, kwargs)
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def login_user(connection, cursor, **kwargs):
    query = f"""
    select * from users
    where username = "{kwargs["username"]}" 
    and password = "{kwargs["password"]}";
    """
    cursor.execute(query)
    data = cursor.fetchall()
    if data == []:
        return False
    else:
        return True


@mysql_decorate
def update_bio(connection, cursor, **kwargs):
    query = f"""
    update users
    set bio = "{kwargs["bio"]}"
    where username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def update_profile_photo(connection, cursor, **kwargs):
    query = f"""
    update users
    set profile_photo = "{kwargs["profile_photo"]}"
    where username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def update_name(connection, cursor, **kwargs):
    query = f"""
    update users
    set name = "{kwargs["name"]}"
    where username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def update_internship(connection, cursor, **kwargs):
    query = f"""
    update users 
    set internship = "{kwargs["internship"]}"
    where username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def update_profile_photo_name_bio(connection, cursor, **kwargs):
    update_bio.no_connect(connection, cursor, **kwargs)
    update_profile_photo.no_connect(connection, cursor, **kwargs)
    update_name.no_connect(connection, cursor, **kwargs)


def composite_insert(beg_query, mid_query, key_value):
    i = 0
    for key, value in key_value.items():
        i += 1
        if type(value) is str:
            value = f'"{value}"'
        if i == len(key_value):
            beg_query += f"{key}) "
            mid_query += f"{value});"
        else:
            beg_query += f"{key}, "
            mid_query += f"{value}, "
    return beg_query + mid_query


def get_omit_string(omit_usernames=[-1]):
    if omit_usernames == []:
        omit_usernames = [-1]
    omit_string = str(tuple(omit_usernames))
    if len(omit_usernames) == 1:
        omit_string = str(tuple(omit_usernames))[:-2] + ")"
    return omit_string


def get_difference_times_from_groups(avg_time_of_all_groups, my_time):
    groups_similarity = []
    for group in avg_time_of_all_groups:
        time_difference = 0
        for (key, value) in group.items():
            if key == "group_id":
                continue
            time_difference += abs(value - my_time[key])
        if time_difference > 75000:
            continue
        group_similarity = {
            "group_id": group["group_id"],
            "difference_in_hours": time_difference
        }
        groups_similarity.append(group_similarity)
    return groups_similarity
    

def get_latest_string_date(*args):
    latest_date = []
    index_of_latest_date = -1
    for date in args:
        year_hour_info = date.split(" ")
        year_info = year_hour_info[0].split("/")
        hour_info = year_hour_info[1].split(":")
        useful_info = [float(f"0.{value}") for value in [*year_info, *hour_info]]
        if len(latest_date) == 0:
            latest_date = useful_info
            index_of_latest_date += 1
        for i in range(len(latest_date)):
            if useful_info[i] > latest_date[i]:
                latest_date = useful_info
                index_of_latest_date += 1
    return index_of_latest_date        


@mysql_decorate
def select_user_recent_searches(connection, cursor, **kwargs):
    query = f"""
    select u.username, u.profile_photo, u.name
    from users u
    inner join searches s
    on u.username = s.t_username
    where s.f_username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    return cursor.fetchall()


@mysql_decorate
def insert_user_recent_searches(connection, cursor, **kwargs):
    beg_query = f"""
    select * 
    from searches 
    where f_username = "{kwargs["f_username"]}"
    and t_username = "{kwargs["t_username"]}";
    """
    cursor.execute(beg_query)
    previous_search = cursor.fetchall()
    end_query = f"""
        update searches 
        set date = current_timestamp
        where f_username = "{kwargs["f_username"]}"
        and t_username = "{kwargs["t_username"]}";
        """
    if previous_search == []:
        end_query = f"""
        insert into searches (f_username, t_username)
        values ("{kwargs["f_username"]}", "{kwargs["t_username"]}");
        """
    cursor.execute(end_query)
    connection.commit()


@mysql_decorate
def delete_all_user_recent_searches(connection, cursor, **kwargs):
    query = f"""
    delete from searches 
    where f_username = "{kwargs["username"]}";
    """
    cursor.execute(query)
    connection.commit()


@mysql_decorate
def delete_specific_user_recent_searches(connection, cursor, **kwargs):
    query = f"""
    delete from searches
    where f_username = "{kwargs["f_username"]}"
    and t_username = "{kwargs["t_username"]}";
    """
    cursor.execute(query)
    connection.commit()







app = Flask(__name__)
app.config["SECRET_KEY"] = "Joaqo1664"


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "GET":
        session.pop("username", None)
        error = session.get("error")
        if error == None:
            error = ""
        else: 
            session.pop("error")
        return render_template("login.html", error=error)
    username = request.form.get("username")
    password = request.form.get("password")
    if login_user.connect(username=username, password=password)["data"]:
        session["username"] = username
        place_user_into_best_group.connect(username=username, force=False)
        return redirect("/account")
    else:
        session["error"] = "Username or Password incorrect. Try again!"
        return redirect("/")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        error = session.get("error")
        if error == None:
            error = ""
        else: 
            session.pop("error")
        return render_template("signup.html", error=error)
    data = {"username": request.form.get("username"), 
    "password": request.form.get("password"), 
    "name": request.form.get("name"), 
    "grade_id": int(request.form.get("grade_id")),
    "internship": str(request.form.get("internship"))}
    result = insert_user.connect(**data)
    if result["error"]:
        print(result, result["error"])
        session["error"] = "That username already exists. Try another one!"
        return redirect("/signup")
    else:
        session["username"] = data["username"]
        session["name"] = data["name"]
        return redirect("/signup_part2")


@app.route("/signup_part2", methods=["GET", "POST"])
def signup_part2():
    username = session.get("username")
    if username == None:
        return redirect("/signup")
    if request.method == "GET":
        error = session.get("error")
        if error == None:
            error = ""
        else: 
            session.pop("error")
        return render_template("signup_part2.html", error=error)
    data = {
    "username": username,
    "mon": request.form.get("mon"),
    "tue": request.form.get("tue"),
    "wed": request.form.get("wed"),
    "thu": request.form.get("thu"),
    "fri": request.form.get("fri"),
    }
    response = insert_calendar.connect(**data)
    if response["error"]:
        session["error"] = "Having some issues inserting calendar, try again"
        return redirect("/signup_part2")
    place_user_into_best_group.connect(username=username, force=False)
    return redirect("/signup_part3")



@app.route("/signup_part3/", methods=["GET", "POST"])
def signup_part3():
    username = session.get("username")
    name = session.get("name")
    if username == None:
        return redirect("/signup")
    if request.method == "GET":
        error = session.get("error")
        if error == None:
            error = ""
        else: 
            session.pop("error")
        return render_template("signup_part3.html", error=error, first_letter=name[0].upper())
    data = {"bio": request.form.get("bio"), "profile_photo_base64": request.form.get("profile_photo_base64")}
    for key, value in data.items():
        if value == "":
            continue
        if key == "bio":
            response = update_bio.connect(bio = value, username = username)
            if response["error"]:
                session["error"] = "Having some issues inserting bio, try again"
                return redirect("/signup_part3")
            continue
        response = update_profile_photo.connect(profile_photo = value, username = username)
        if response["error"]:
            session["error"] = "Having some issues inserting profile photo, try again"
            return redirect("/signup_part3")
    return redirect("/account")


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    username = session.get("username")
    if username == None:
        return redirect("/")
    if request.method == "GET":
        data = get_user_data.connect(username=username)["data"][0]
        for (key, value) in data.items():
            if value == None:
                data[key] = ""
        calendar= get_normal_calendar.connect(username=username)["data"]
        return render_template("edit_profile.html", username=username, bio=data["bio"], name=data["name"], profile_photo_base64=data["profile_photo"], lundi=calendar["mon"], mardi=calendar["tue"], mercredi=calendar["wed"], jeudi=calendar["thu"], vendredi=calendar["fri"], internship=data["internship"])
    data = {"profile_photo": request.form.get("profile_photo_base64"), 
    "name": request.form.get("name"),
    "bio": request.form.get("bio"),
    "username": username
    }
    update_profile_photo_name_bio.connect(**data)
    calendar = {
    "mon": request.form.get("mon"),
    "tue": request.form.get("tue"),
    "wed": request.form.get("wed"),
    "thu": request.form.get("thu"),
    "fri": request.form.get("fri"),
    }
    new_calendar = {}
    for (key, value) in calendar.items():
        if value != "":
            new_calendar[key] = value
    if new_calendar != {}:
        update_calendar.connect(username=username, **calendar)
    internship = request.form.get("internship")
    update_internship.connect(username=username, internship=internship)
    return redirect("/account")


@app.route("/account", methods=["GET", "POST", "DELETE"])
def account():
    username = session.get("username")
    if username == None:
        return redirect("/")
    error = session.get("error")
    if error == None:
        error = ""
    else: 
        session.pop("error")
    if request.method == "GET":
        user_data = get_user_data.connect(username=username)["data"][0]
        profile_photo_base64 = user_data["profile_photo"]
        name = user_data["name"]
        bio = user_data["bio"]
        internship = user_data["internship"]
        calendar = get_normal_calendar.connect(username=username)["data"]
        return render_template("account.html", error=error, username=username, his_username=username, profile_photo_base64=profile_photo_base64, his_profile_photo_base64 = profile_photo_base64, his_bio=bio, his_name=name, lundi=calendar["mon"], mardi=calendar["tue"], mercredi=calendar["wed"], jeudi=calendar["thu"], vendredi=calendar["fri"], his_internship=internship)


@app.route("/search", methods=["GET", "POST", "DELETE"])
def search():
    username = session.get("username")
    if username == None:
        return redirect("/")
    if request.method == "GET":
        profile_photo_base64 = get_user_data.connect(username=username)["data"][0]["profile_photo"]
        recent_searches = select_user_recent_searches.connect(username=username)["data"]
        return render_template("search.html", recent_searches=recent_searches, username=username, profile_photo_base64 = profile_photo_base64)
    if request.method == "DELETE":
        delete_all = request.json["delete_all_searches"]
        if delete_all:
            return delete_all_user_recent_searches.connect(username=username)
        delete_specific_user = request.json["delete_specific_searches"]
        return delete_specific_user_recent_searches.connect(f_username=username, t_username=delete_specific_user)
    search_word = request.json["search_word"]
    profiles_preview = search_profile_preview.connect(search_word=search_word, limit=10, omit=[])["data"]
    return profiles_preview
    

@app.route("/search/<seeing_username>", methods=["GET"])
def view_search_user(seeing_username):
    username = session.get("username")
    if username == None:
        return redirect("/")
    insert_user_recent_searches.connect(f_username=username, t_username=seeing_username)
    session["go_back"] = False
    return redirect("/view_user/" + seeing_username)


@app.route("/view_user/<seeing_username>", methods=["GET"])
def view_user(seeing_username):
    username = session.get("username")
    if username == None:
        return redirect("/")
    if request.method == "GET":
        if seeing_username == username:
            return redirect("/account")
        user_data = get_user_data.connect(username=seeing_username)["data"][0]
        options = {
            "username": username,
            "his_username": user_data["username"],
            "his_name": user_data["name"],
            "his_bio": user_data["bio"],
            "his_internship": user_data["internship"],
            "go_back": session.get("go_back")
        }
        if user_data["profile_photo"] != None:
            options["his_profile_photo_base64"] = user_data["profile_photo"]
        my_data = get_user_data.connect(username=username)["data"][0]
        if my_data["profile_photo"] != None:
            options["profile_photo_base64"] = my_data["profile_photo"]
        calendar = get_normal_calendar.connect(username=username)["data"]
        options["lundi"] = calendar["mon"]
        options["mardi"] = calendar["tue"]
        options["mercredi"] = calendar["wed"]
        options["jeudi"] = calendar["thu"]
        options["vendredi"] = calendar["fri"]
        return render_template("view_user.html", **options)
    

@app.route("/group", methods=["GET"])
def group():
    username = session.get("username")
    if username == None:
        return redirect("/")
    if request.method == "GET":
        users = get_current_group_users_data.connect(username=username)["data"]
        profile_photo_base64 = None
        for entry in users:
            if entry["username"] != username:
                continue
            profile_photo_base64 = entry["profile_photo"]
        return render_template("groups.html", profile_photo_base64=profile_photo_base64, users=users, username=username)


@app.route("/find_new_group", methods=["GET"])
def find_new_group():
    username = session.get("username")
    if username == None:
        return redirect("/")
    place_user_into_best_group.connect(username=username, force=True)
    return redirect("/group")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
