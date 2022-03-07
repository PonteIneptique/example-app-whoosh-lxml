import glob
import os
from app import db, app
import whoosh.index as index
from app.utils import get_lines


class Livre(db.Model):
    livre_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    livre_title = db.Column(db.Text, nullable=False)
    livre_path = db.Column(db.Text, nullable=False)

    def reset_pages(self):
        Page.query.filter(Page.livre_id==self.livre_id).delete()
        ix = index.open_dir(app.config["WHOOSH-SCHEMA-DIR"])
        writer = ix.writer()
        pages = []
        for file in glob.glob(os.path.join(self.livre_path, "*.xml")):
            pages.append(Page(livre_id=self.livre_id, page_path=file))
            db.session.add(pages[-1])
        db.session.flush()

        for page in pages:
            writer.add_document(
                livre_id=self.livre_id,
                page_id=page.page_id,
                content="\n".join([line.text for line in get_lines(page.page_path)])
            )
        db.session.commit()
        writer.commit()


class Page(db.Model):
    page_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    livre_id = db.Column(db.Integer, db.ForeignKey("livre.livre_id"))
    page_path = db.Column(db.Text, nullable=False)
