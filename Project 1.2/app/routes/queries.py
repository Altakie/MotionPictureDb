from flask import Blueprint, render_template, request
from app.database import Database

queries_bp = Blueprint("query", __name__)


@queries_bp.route("/list_tables")
def list_tables():
    # >>>> TODO 1: Write a query to list all the tables in the database. <<<<

    query = """ show tables; """

    with Database() as db:
        tables = db.execute(query)
    return render_template("list_tables.html", tables=tables)


@queries_bp.route("/search_movie", methods=["POST"])
def search_movie():
    movie_name = request.form["movie_name"]

    # >>>> TODO 2: Search Motion Picture by Motion picture name (parameterized). <<<<
    #              List the motion picture name along with its rating, production, and budget.

    query = """
    SELECT name, rating, production, budget
    FROM MotionPicture
    WHERE name LIKE %s;
    """

    with Database() as db:
        movies = db.execute(query, (f"%{movie_name}%",))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_liked_movies", methods=["POST"])
def search_liked_movies():
    user_email = request.form["user_email"]

    # >>>> TODO 3: Find the movies that have been liked by a specific user. A user is uniquely identified by their email (parameterized). <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = """
    SELECT mp.name, mp.rating, mp.production, mp.budget
    FROM MotionPicture mp
    JOIN Movie m on mp.id = m.mpid
    JOIN Likes l ON m.mpid = l.mpid
    WHERE l.uemail = %s;
     """

    with Database() as db:
        movies = db.execute(query, (user_email,))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_by_country", methods=["POST"])
def search_by_country():
    country = request.form["country"]

    # >>>> TODO 4: Search motion pictures by their shooting location country. <<<<
    #              List only the motion picture names without any duplicates.

    query = """ 
    SELECT DISTINCT mp.name
    FROM MotionPicture mp
    JOIN Location l ON mp.id = l.mpid
    WHERE l.country = %s;
    """

    with Database() as db:
        movies = db.execute(query, (country,))
    return render_template("search_results_by_country.html", movies=movies)


@queries_bp.route("/search_directors_by_zip", methods=["POST"])
def search_directors_by_zip():
    zip_code = request.form["zip_code"]

    # >>>> TODO 5: List all directors who have directed a TV series shot in a specific zip code (parameterized). <<<<
    #              List the director’s name and TV series name only, without duplicates.

    query = """ 
    SELECT DISTINCT p.name, mp.name
    FROM People p
    JOIN Role r ON p.id = r.pid
    JOIN Series s ON r.mpid = s.mpid
    JOIN MotionPicture mp ON s.mpid = mp.id
    JOIN Location l ON s.mpid = l.mpid
    WHERE r.role_name = 'Director' AND l.zip = %s;
    """

    with Database() as db:
        results = db.execute(query, (zip_code,))
    return render_template("search_directors_results.html", results=results)


@queries_bp.route("/search_awards", methods=["POST"])
def search_awards():
    k = int(request.form["k"])

    # >>>> TODO 6: Identify the individuals who have received more than “k” (parameterized) awards for a single motion picture in the same year. <<<<
    #              Return the individual’s name, the motion picture’s name, the award year, and the award count.

    query = """
    SELECT p.name, mp.name, a.award_year, COUNT(*) as award_count
    FROM People p
    JOIN Award a ON p.id = a.pid
    JOIN MotionPicture mp ON a.mpid = mp.id
    GROUP BY p.id, mp.id, a.award_year
    HAVING COUNT(*) > %s;
    """

    with Database() as db:
        results = db.execute(query, (k,))
    return render_template("search_awards_results.html", results=results)


@queries_bp.route("/find_youngest_oldest_actors", methods=["GET"])
def find_youngest_oldest_actors():
    # >>>> TODO 7: Find the youngest and oldest actors who have won at least one award. <<<<
    #              List the actor names and their age at the time they received the award.
    #              Age must be computed using the actor’s date of birth and the award-year only.
    #              In case of a tie, list all tied actors.

    query = """
    SELECT p.name, (a.award_year - YEAR(p.dob)) AS age_at_award
    FROM People p
    JOIN Award a ON p.id = a.pid
    JOIN Role r ON p.id = r.pid
    WHERE r.role_name = 'Actor'
    GROUP BY p.id, a.award_year;
    """

    with Database() as db:
        actors = db.execute(query)

    # Filter out actors with null ages (if any)
    actors = [actor for actor in actors if actor[1] is not None]
    if actors:
        min_age = min(actors, key=lambda x: x[1])[1]
        max_age = max(actors, key=lambda x: x[1])[1]
        youngest_actors = [actor for actor in actors if actor[1] == min_age]
        oldest_actors = [actor for actor in actors if actor[1] == max_age]
        return render_template(
            "actors_by_age.html",
            youngest_actors=youngest_actors,
            oldest_actors=oldest_actors,
        )
    else:
        return render_template(
            "actors_by_age.html", youngest_actors=[], oldest_actors=[]
        )


@queries_bp.route("/search_producers", methods=["POST"])
def search_producers():
    box_office_min = float(request.form["box_office_min"])
    budget_max = float(request.form["budget_max"])

    # >>>> TODO 8: List the American producers whose movies achieved a box office collection greater than or equal to “X” (parameterized) with a budget less than or equal to “Y” (parameterized). <<<<
    #              List the producer’s name and movie name along with its box office collection and budget.

    query = """ 
    SELECT DISTINCT p.name, mp.name, m.boxoffice_collection, mp.budget
    FROM People p
    JOIN Role r ON p.id = r.pid
    JOIN Movie m ON r.mpid = m.mpid
    JOIN MotionPicture mp ON m.mpid = mp.id
    WHERE r.role_name = 'Producer'
        AND p.nationality = 'USA'
        AND m.boxoffice_collection >= %s
        AND mp.budget <= %s;
    """

    with Database() as db:
        results = db.execute(query, (box_office_min, budget_max))
    return render_template("search_producers_results.html", results=results)


@queries_bp.route("/search_multiple_roles", methods=["POST"])
def search_multiple_roles():
    rating_threshold = float(request.form["rating_threshold"])

    # >>>> TODO 9: List the individuals who played multiple roles in a motion picture with a rating greater than “X” (parameterized). <<<<
    #              List the individual’s name, the motion picture name, and the number of roles the individual played in that motion picture.

    query = """ 
    SELECT p.name, mp.name, COUNT(*) as role_count
    FROM People p
    JOIN Role r ON p.id = r.pid
    JOIN MotionPicture mp ON r.mpid = mp.id
    WHERE mp.rating > %s
    GROUP BY p.id, mp.id
    HAVING COUNT(*) > 1;
    """

    with Database() as db:
        results = db.execute(query, (rating_threshold,))
    return render_template("search_multiple_roles_results.html", results=results)


@queries_bp.route("/top_thriller_movies_boston", methods=["GET"])
def top_thriller_movies_boston():
    # >>>> TODO 10: Find the top 2 highest-rated thriller movies (genre: thriller) that were shot exclusively in Boston. <<<<
    #               “Exclusively” means that the movie may not have any other shooting location.
    #               List the movie names and their rating.

    query = """ 
    SELECT mp.name, mp.rating
    FROM MotionPicture mp
    JOIN Movie m ON mp.id = m.mpid
    JOIN Genre g ON m.mpid = g.mpid
    JOIN Location l ON m.mpid = l.mpid
    WHERE g.genre_name = 'Thriller' AND l.city = 'Boston'
    GROUP BY mp.id
    HAVING COUNT(DISTINCT l.city) = 1
    ORDER BY mp.rating DESC
    LIMIT 2;
    """

    with Database() as db:
        results = db.execute(query)
    return render_template("top_thriller_movies_boston.html", results=results)


@queries_bp.route("/search_movies_by_likes", methods=["POST"])
def search_movies_by_likes():
    min_likes = int(request.form["min_likes"])
    max_age = int(request.form["max_age"])

    # >>>> TODO 11: Find all the movies with more than “X” (parameterized) likes by users of age less than “Y” (parameterized). <<<<
    #               Return the movie names and the number of likes from that age group.

    query = """ 
    SELECT mp.name, COUNT(*) as like_count
    FROM MotionPicture mp
    JOIN Movie m ON mp.id = m.mpid
    JOIN Likes l ON m.mpid = l.mpid
    JOIN Users u ON l.uemail = u.email
    WHERE u.age < %s
    GROUP BY mp.id
    HAVING COUNT(*) > %s;
    """

    with Database() as db:
        results = db.execute(query, (max_age, min_likes))
    return render_template("search_movies_by_likes_results.html", results=results)


@queries_bp.route("/actors_marvel_warner", methods=["GET"])
def actors_marvel_warner():
    # >>>> TODO 12: Identify the actors who played a role in both “Marvel” and “Warner Bros” productions. <<<<
    #               List the actor names and the corresponding motion picture names.

    query = """ 
    SELECT a.name, m.name, wb.name
    FROM (SELECT name, mpid FROM People, Role WHERE id = pid AND role_name = "Actor") as a,
    (SELECT name, id FROM MotionPicture WHERE production = "Marvel") as m,
    (SELECT name, id FROM MotionPicture WHERE production = "Warner Bros") as wb
    WHERE a.mpid IN (SELECT id FROM MotionPicture WHERE production = "Marvel") 
    AND a.mpid IN (SELECT id FROM MotionPicture WHERE production = "Warner Bros");
    """

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_marvel_warner.html", results=results)


@queries_bp.route("/movies_higher_than_comedy_avg", methods=["GET"])
def movies_higher_than_comedy_avg():
    # >>>> TODO 13: Find the motion pictures with a higher rating than the average rating of all comedy (genre) motion pictures.  <<<<
    #               List the names and ratings, sorted in descending order of ratings.

    query = """ 
    SELECT mp.name, mp.rating
    FROM MotionPicture mp
    WHERE mp.rating > (
        SELECT AVG(mp2.rating)
        FROM MotionPicture mp2
        JOIN Genre g2 ON mp2.id = g2.mpid
        WHERE g2.genre_name = 'Comedy'
    )
    ORDER BY mp.rating DESC;
    """

    with Database() as db:
        results = db.execute(query)
    return render_template("movies_higher_than_comedy_avg.html", results=results)


# @queries_bp.route("/top_5_movies_people_roles", methods=["GET"])
# def top_5_movies_people_roles():
#     """
#     Display the top 5 movies that involve the most people and roles.
#     """

#     # >>>> TODO 14: Find the top 5 movies with the highest number of people playing a role in that movie. <<<<
#     #               Show the `movie name`, `people count` and `role count` for the movies.

#     query = """ """

#     with Database() as db:
#         results = db.execute(query)
#     return render_template("top_5_movies_people_roles.html", results=results)


@queries_bp.route("/actors_with_common_birthday", methods=["GET"])
def actors_with_common_birthday():
    # >>>> TODO 14: Find actors who share the same birthday. <<<<
    #               List the actor names (actor 1, actor 2) and their common birthday.

    query = """ 
    SELECT DISTINCT p1.name, p2.name, p1.dob
    FROM People p1
    JOIN People p2 ON p1.dob = p2.dob AND p1.id < p2.id
    JOIN Role r1 ON p1.id = r1.pid
    JOIN Role r2 ON p2.id = r2.pid
    WHERE r1.role_name = 'Actor' AND r2.role_name = 'Actor' AND p1.name NOT LIKE p2.name;
    """

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_with_common_birthday.html", results=results)


@queries_bp.route("/top_production_by_genre", methods=["GET"])
def top_production_by_genre():
    # >>>> TODO 15: List the productions that have produced more than two movies in a given genre, where each movie has a rating higher than the average rating of that genre. <<<<
    #               List the `production company name`, `genre name` and the `count of movies` that meet the criteria, ordered by the count of movies in descending order.

    query = """ 
        SELECT mp.production, g.genre_name, COUNT(*) as movie_count
        FROM MotionPicture mp
        JOIN Movie m ON mp.id = m.mpid
        JOIN Genre g ON m.mpid = g.mpid
        WHERE mp.rating > (
            SELECT AVG(mp2.rating)
            FROM MotionPicture mp2
            JOIN Movie m2 ON mp2.id = m2.mpid
            JOIN Genre g2 ON m2.mpid = g2.mpid
            WHERE g2.genre_name = g.genre_name
        )
        GROUP BY mp.production, g.genre_name
        HAVING COUNT(*) > 2
        ORDER BY movie_count DESC;
    """

    with Database() as db:
        results = db.execute(query)
    return render_template(
        "generic_results.html", results=results, title="Consistent Genre Leaders"
    )


@queries_bp.route("/versatile_talent", methods=["GET"])
def versatile_talent():
    # >>>> TODO 16: Find individuals who have acted, directed, and produced motion pictures, and have won at least one award against one of those roles. <<<<
    #               List the person’s `name` and `nationality`.

    query = """ 
    SELECT 
    FROM 
    (SELECT pid FROM Role WHERE role_name = "Actor") a,
    (SELECT pid FROM Role WHERE role_name = "Director") d,
    (SELECT pid FROM Role WHERE role_name = "Producer") p,
    Award aw
    WHERE 
    """

    with Database() as db:
        results = db.execute(query)
    return render_template(
        "generic_results.html",
        results=results,
        title="Versatile Talent (Triple Threats)",
    )


@queries_bp.route("/high_roi_movies", methods=["GET"])
def high_roi_movies():
    # >>>> TODO 17: Find the top 5 movies produced(shooted) in the USA with a “Return on Investment” (Box Office/Budget) higher than the average return on investment of all Marvel movies. <<<<
    #               Only include movies that have an ROI greater than the average ROI of all Marvel movies
    #               First column should be the movie name, second column should be country, and third column should be the ROI.

    # This runs but returns nothing, so something's wrong
    query = """ 
    SELECT mp.name, l.country, (m.boxoffice_collection / mp.budget) AS roi
    FROM MotionPicture mp
    JOIN Movie m ON mp.id = m.mpid
    JOIN Location l ON mp.id = l.mpid
    WHERE l.country = 'USA' AND (m.boxoffice_collection / mp.budget) > (
        SELECT AVG(m2.boxoffice_collection / mp2.budget)
        FROM MotionPicture mp2
        JOIN Movie m2 ON mp2.id = m2.mpid
        JOIN Genre g2 ON m2.mpid = g2.mpid
        WHERE g2.genre_name = 'Marvel'
    )
    ORDER BY roi DESC
    LIMIT 5;
    """

    with Database() as db:
        results = db.execute(query)
    return render_template(
        "generic_results.html", results=results, title="Highest ROI (vs Marvel Average)"
    )


# @queries_bp.route("/super_fans", methods=["POST"])
# def super_fans():
#     """
#     Find users who have liked all movies from a specific production company.
#     """
#     # >>>> TODO 19: Find the users who have liked all the movies produced by a specific production company. <<<<
#     #               List the user `name` and `email`.

#     production = request.form["production"]
#     query = """ """

#     with Database() as db:
#         results = db.execute(query, (production,))
#     return render_template(
#         "generic_results.html", results=results, title=f"Super-fans of {production}"
#     )


@queries_bp.route("/awarded_series_growth", methods=["GET"])
def awarded_series_growth():
    # >>>> TODO 18: Find all TV series that have more seasons than the average season count of all series, and have at least one award-winning person after the year 2010. <<<<
    #               List the TV series `name`, `season count` and the `number of awards won`, ordered by season count in descending order.

    query = """ 
    SELECT mp.name, s.season_count, COUNT(a.mpid) as award_count
    FROM Series s
    JOIN MotionPicture mp ON s.mpid = mp.id
    JOIN Role r ON mp.id = r.mpid
    JOIN People p ON r.pid = p.id
    JOIN Award a ON p.id = a.pid AND a.award_year > 2010
    GROUP BY s.mpid
    HAVING s.season_count > (
        SELECT AVG(season_count)
        FROM Series
    )
    ORDER BY s.season_count DESC;
    """

    with Database() as db:
        results = db.execute(query)
    return render_template(
        "generic_results.html",
        results=results,
        title="Award-Winning Long-Running Series",
    )
