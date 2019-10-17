def get_tags_counts():
    query = "select t.tag_name, t.tag_id, count(bt.goodreads_book_id) \
        from book_tags as bt \
        inner join tags as t on bt.tag_id=t.tag_id \
        group by t.tag_name \
        order by count(bt.goodreads_book_id) desc limit 100;"
    c.execute(query)
    return c.fetchall()


def delete_tag(tag_id):
    print(f"Running delete tag queries for {tag_id}")
    del_tag_book_tags = "delete from book_tags where tag_id = ?"
    del_tag_tags = "delete from tags where tag_id = ?"

    c.execute(del_tag_book_tags, (tag_id,))
    c.execute(del_tag_tags, (tag_id,))
    conn.commit()


def combine_tags(old_tag, new_tag):
    print(f"Running combine tag for {old_tag} to {new_tag}")

    combine_tags_query = "update book_tags set tag_id = :new_tag \
    where tag_id = :old_tag"
    delete_old_tag_query = "delete from tags where tag_id = :old_tag"
    c.execute(combine_tags_query, {"new_tag": new_tag, "old_tag":old_tag})
    c.execute(delete_old_tag_query, {"old_tag":old_tag})
    conn.commit()


def find_similar_tags(tag_search):
    similar_tags_query = "select t.tag_name, t.tag_id, count(bt.goodreads_book_id) \
    from tags as t \
    inner join book_tags as bt on t.tag_id = bt.tag_id \
    WHERE t.tag_name like ? group by t.tag_name\
    limit 10"

    c.execute(similar_tags_query, (tag_search,))
    return c.fetchall()

def main():

    # It would be nice to iterate over groups of 10,
    # with all 10 visible initially in case it's nice to combine them

    tags_with_counts = get_tags_counts()

    # for row in get_tags_counts():
    for group in range(0, 100, 10):
        for g in range(0, 10):
            print(tags_with_counts[group + g])
        for k in range(0, 10):
            row = tags_with_counts[group + k]
            # ('divergent-series', '9604', 10),
            # (tag_name, tag_id, count)

            print("\n")
            print()
            print(f"Tag name {row[0]} has {row[2]} books.")
            userin = input("Will you [d]elete, [k]eep, [c]ombine, [s]kip?")
            while userin not in ("", "d", "c", "k", "s"):
                userin = input("Will you [d]elete, [k]eep [enter], or [c]ombine tags?")
            if userin == '':
                continue
            elif userin == "d":
                print(f"Deleting tag {row}")
                delete_tag(row[1])
            elif userin == "s":
                print("\n")
                break
            elif userin == "c":
                tag_search = input("What to search for?")
                if len(tag_search) < 3:
                    tag_search = input("What to search for?")
                else:
                    st = find_similar_tags(tag_search)
                    if len(st) < 1:
                        print("Sorry, no similar tags found")
                    else:
                        for i in range(0, len(st)):
                            print(f"{i}: Tag name {st[i][0]} has {st[i][2]} books.")
                        to_combine = int(input(f"Input the number of tag to combine {row[0]} into."))
                        if to_combine not in range(0, len(st)):
                            int(input(f"Input the number of tag to combine {row[0]} into."))
                        else:
                            print(f"Will combine {row[0]} into {st[to_combine][0]}")
                            combine_tags(row[1], st[to_combine][1])
    conn.close()

import sqlite3
DB_FILENAME = 'goodbooks_tagging.db'

conn = sqlite3.connect(DB_FILENAME)
c = conn.cursor()

if __name__ == "__main__":
    # execute only if run as a script
    main()
