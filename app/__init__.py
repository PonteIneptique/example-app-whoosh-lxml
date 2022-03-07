from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from whoosh.index import create_in
import os.path
from app.utils import get_lines
import shutil

app = Flask(
    "monapp",
    static_folder=os.path.join(os.path.dirname(__file__), "statics"),
    template_folder=os.path.join(os.path.dirname(__file__), "templates")
)
# On configure le secret
app.config['SECRET_KEY'] = "CHabadoubadou"
# On configure la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(os.path.dirname(__file__), "db.sqlite")
# On initie l'extension
db = SQLAlchemy(app)
app.config["WHOOSH-SCHEMA-DIR"] = os.path.join(os.path.dirname(__file__), "whoosh")

from app.models_sqlite import Livre, Page
from app.models_whoosh import PageWhoosh


@app.route("/livre/<int:livre_id>/page/<int:page_id>")
def get_page(livre_id: int, page_id: int):
    page = Page.query.filter(db.and_(Page.livre_id == livre_id, Page.page_id==page_id)).first()
    lines = get_lines(page.page_path)
    return render_template(
        "page.html",
        lines=[line for line in lines if line.type == "MainZone"]
    )

@app.route("/livre/<int:livre_id>")
def get_livre(livre_id: int):
    livre = Livre.query.get_or_404(livre_id)
    return render_template(
        "livre.html",
        livre=livre,
        page=Page.query.filter(Page.livre_id==livre.livre_id).all()
    )


from whoosh.qparser import QueryParser
import whoosh.index as index
@app.route("/search")
def search():
    ix = index.open_dir(app.config["WHOOSH-SCHEMA-DIR"])
    qp = QueryParser("content", schema=ix.schema)
    q = qp.parse(request.args.get("q", "charbon"))

    with ix.searcher() as s:
        results = s.search(q, terms=True)
        # print([r for r in results]) # hit.matched_terms()
        return render_template("results.html", results=results)

@app.cli.command("create")
def create():
    with app.app_context():
        db.create_all()
        os.makedirs(app.config["WHOOSH-SCHEMA-DIR"], exist_ok=True)
        ix = create_in(app.config["WHOOSH-SCHEMA-DIR"], PageWhoosh)


@app.cli.command("drop")
def drop():
    with app.app_context():
        db.drop_all()
        try:
            shutil.rmtree(app.config["WHOOSH-SCHEMA-DIR"])
        except Exception:
            print("Y a eu une erreur")


@app.cli.command("load")
def load():
    with app.app_context():
        db.session.add(Livre(
            livre_title="Titre",
            livre_path="./data/CREMMA-MSS-18/data/Abrege des Descriptions des Artes/"
        ))
        db.session.commit()


@app.cli.command("parse")
def load():
    with app.app_context():
        livre = Livre.query.get(1)
        livre.reset_pages()
