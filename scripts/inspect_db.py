import os, sqlite3
p = os.path.join('instance', 'gestionale.sqlite')
print('DB path:', p)
print('exists:', os.path.exists(p))
if not os.path.exists(p):
    raise SystemExit('Database not found')
conn = sqlite3.connect(p)
cur = conn.cursor()
print('\n--- cases ---')
for row in cur.execute('SELECT id, via, civico, author_id FROM "case"').fetchall():
    print(row)
print('\n--- offerte ---')
for row in cur.execute('SELECT id, case_id, user_id, nome, email, messaggio FROM offerte').fetchall():
    print(row)
conn.close()
