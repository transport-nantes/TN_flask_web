#!/usr/bin/env python

import argparse
import psycopg2
import subprocess
from hashlib import md5

def composite_image(commune, candidate, party_list, subject, filename):
    """Composite text onto image to make twitter card.
    """
    subprocess.call(["convert",
                     "app/templates/municipales/template.png",
                     "-font",
                     "Bitstream-Vera-Sans-Bold",
                     "-gravity",
                     "northwest   ",
                     "-pointsize",
                     "80",
                     "-draw",
                     "fill black text 140,150 '{subject}'".format(subject=subject),
                     "-pointsize",
                     "40",
                     "-draw",
                     "fill '#888888' text 101,220 '{commune}'".format(commune=commune),
                     "-pointsize",
                     "40",
                     "-draw",
                     "fill '#bbbbbb' text 101,150 '{party}'".format(party=party_list),
                     "-pointsize",
                     "40",
                     "-draw",
                     "fill '#888888' text 70,130 '{candidatename}'".format(
                         candidatename=candidate),
                     filename])

def make_cards(db_uri):
    """Make a twitter card for each candidate/question.
    """
    try:
        conn = psycopg2.connect(db_uri)
    except:
        print("Unable to connect to the database")
        return
    conn.set_session(autocommit=True)
    cursor = conn.cursor()
    sql = """SELECT id, commune, tete_de_liste, liste FROM survey_responder;"""
    ret = cursor.execute(sql)
    candidates = cursor.fetchall()
    questions = [('1', 'Vélopolitain'),
                 ('2', "Espace vert"),
                 ('3', "Signalisation"),
                 ('4', "TER et cars"),
                 ('5', "TER et cars"),
                 ('6', "Aéroport"),
                 ('7', "rues ou \nmobilité ?"),
                 ('8', "Usage officiel"),
                 ('9', "Police à vélo"),
                 ('10', "Ingénieurs"),
                 ('11', "Autres")]
    for candidate in candidates:
        for question in questions:
            commune = candidate[1]
            tete_de_liste = candidate[2]
            liste = candidate[3]
            the_question = question[1]
            print(commune, tete_de_liste, liste, the_question)
            filename_base = commune + tete_de_liste + liste
            filename = md5(filename_base.encode()).hexdigest() + '.png'
            print(filename)
            #composite_image(commune, tete_de_liste, liste, the_question,
            #                'app/templates/municipales/' + filename)

def main():
    """Fetch the party list names and their heads and make twitter cards
    for each question.

    In principle, we should fetch the questions, too, but we don't
    currently have a short version of the title.  So hard code this
    time around.

    To compute the db uri, do something like one of these:

    (cat config_local.py ; echo 'print(SQLALCHEMY_DATABASE_URI)') | python
    (cat /var/p27/config_tn_schema.py ; echo 'print(SQLALCHEMY_DATABASE_URI)') | python

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-uri', type=str, required=True,
                        help='PostgreSQL connection config')
    args = parser.parse_args()
    make_cards(args.db_uri)

if __name__ == '__main__':
    main()


    """
convert template.png -font "Helvetica-Bold" -gravity northwest    -pointsize 120 -draw "fill black text 140,170 'velo'"                -pointsize 40 -draw "fill '#bbbbbb' text 101,160 'Nantes en cacao'"                    -pointsize 40 -draw "fill '#888888' text 70,145 'Laurence GGG'" out.png


Bitstream-Vera-Sans-Bold

convert template.png -font "Bitstream-Vera-Sans-Bold" -gravity northwest    -pointsize 120 -draw "fill black text 140,170 'velo'"                -pointsize 40 -draw "fill '#bbbbbb' text 101,160 'Nantes en cacao'"                    -pointsize 40 -draw "fill '#888888' text 70,145 'Laurence GGG'" out.png




convert template.png -font "Bitstream-Vera-Sans-Bold" -gravity northwest    -pointsize 120 -draw "fill black text 140,150 'velo'"                -pointsize 40 -draw "fill '#bbbbbb' text 101,150 'Nantes en cacao'"                    -pointsize 40 -draw "fill '#888888' text 70,130 'Laurence GGG'" out.png




SELECT tete_de_liste, liste FROM survey_responder;
SELECT question_title FROM survey_question;
SELECT id, question_title FROM survey_question;

  1 | Vélopolitain : Réseau Express Vélo.  Sécurité piéton et cycliste.
  2 | Places et ronds-points.
  3 | Signalisation.
  4 | TER et cars.
  5 | TER et cars.
  6 | Aéroport.
  7 | Fournisseur de mobilité.
  8 | Usage officiel.
  9 | Police municipale à vélo.
 10 | Formation d'ingénieurs.
 11 | Autres propositions.

"""
