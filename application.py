import datetime
import os
import sqlite3 as sql

from flask import Flask, render_template, request

from allrecipes import scrapeRecipes

from spellchecker import SpellChecker

app = Flask(__name__)


def track_usage(db_name, user_request):
    storage_conn = sql.connect(db_name)
    c = storage_conn.cursor()

    c.execute(f'''
    insert into users VALUES ('{user_request.environ.get('HTTP_ORIGIN', 'Not Provided')}', '{user_request.user_agent}', '{user_request.method}', '{datetime.datetime.now()}')
    ''')

    storage_conn.commit()
    storage_conn.close()


def get_usage(db_name):
    storage_conn = sql.connect(db_name)
    c = storage_conn.cursor()

    rows = [row for row in c.execute('SELECT * FROM users ORDER BY timestamp')]

    storage_conn.close()

    return rows


def reset_usage(db_name):
    os.remove(db_name)
    storage_conn = sql.connect(db_name)
    c = storage_conn.cursor()

    c.execute('create table users (ip, user_agent, method, timestamp)')

    storage_conn.commit()
    storage_conn.close()


def recipe_html(recipe_obj):
    image = f"""<img style="width: 300; height: 300;" src="{recipe_obj["image"]}" alt="Recipe Pic"><br><br>"""
    name = f"""<a class="recipe-name" href="{recipe_obj["url"]}?printview" target="_blank">{recipe_obj["name"]}</a>"""
    print(name)
    description = f"""<p style="width: 300; height: 30; text-wrap: normal; font-size: 12">{recipe_obj["description"]}</p>"""

    return f"""<div class="recipe-tile"> {image} {name} {description} <br><br></div><br><br>"""


@app.route('/')
def home():
    track_usage('usage.db', request)
    return render_template('home.html')


@app.route('/loading')
def recipe():
    include, exclude, sort = request.args.values()

    return render_template("searching.html", **{
        "include": include,
        "exclude": exclude,
        "sort": sort,
        "host": request.host
    })


@app.route('/recipes')
def recipes():
    track_usage('usage.db', request)
    include, exclude, sort = request.args.values()
    spell = SpellChecker()

    if include.lower() == exclude.lower():
        exclude = ""

    if isinstance(include, str):
        include = " ".join(
            [spell.correction(word) for word in spell.unknown(include.split(' '))]
        )

    if isinstance(exclude, str):
        if exclude != "":
            exclude = " ".join(
                [spell.correction(word) for word in spell.unknown(exclude.split(' '))]
            )

    found_recipes = scrapeRecipes(include, exclude, sort)

    return f"""
            <title>Your Recipes</title>
            <link rel="icon" href="/static/img/tomato.png">
            <link rel="stylesheet" href="/static/css/recipes.css">
            <body>
            <h1>Your Recipes</h1><br><br><a href="/" class="back">Back</a><br><br><br><br>
            {"".join([recipe_html(recipe_obj) + "<br>" for recipe_obj in found_recipes])}
            </body>
            """


@app.route('/uhyoweuislaflaoi')
def users():
    return "".join([
        "    |||    ".join([
            data for data in row
        ]) + "<br><br>" for row in get_usage('usage.db')
    ])


if __name__ == '__main__':
    # reset_usage('usage.db')
    app.run(port=5051, debug=True)
