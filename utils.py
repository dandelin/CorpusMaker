import sqlite3, codecs

def combine(db_name):
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	cur.execute("SELECT * FROM t;")
	rows = cur.fetchall()
	grams = [row[2] for row in rows]
	with codecs.open(db_name + '.txt', 'w', encoding='utf-8') as fp:
		fp.write(' '.join(grams))

if __name__ == "__main__":
	combine('jaeminjo.db')