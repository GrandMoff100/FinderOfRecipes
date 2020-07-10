import time
from allrecipes import Recipe, scrapeRecipes
from threading import Thread
from flask import Flask, render_template, redirect, request

app = Flask(__name__)


def recipe_html(recipe_obj):
    image = f"""<img style="width: 300; height: 300;" src="{recipe_obj["image"]}" alt="Recipe Pic"><br><br>"""
    name = f"""<a class="recipe-name" href="{recipe_obj["url"]}?printview" target="_blank">{recipe_obj["name"]}</a>"""
    print(name)
    description = f"""<p style="width: 300; height: 30; text-wrap: normal; font-size: 12">{recipe_obj["description"]}</p>"""

    return f"""<div class="recipe-tile"> {image} {name} {description} <br><br></div><br><br>"""


@app.route('/')
def home():
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
    include, exclude, sort = request.args.values()

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


if __name__ == '__main__':
    app.run(port=5051, debug=True)
