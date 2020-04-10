#!/usr/bin/env python3
from unqlite import UnQLite


class test:
    def __init__(self):
        self.db = UnQLite('output/benchmark_results.unqlite')

    def myselect(self):
        run_statistic = self.db.collection('RunStatisticExtended')
        # if not run_statistic.exists():
        #     run_statistic.create()  # Create the collection.

        run_statistic.store({'name': 'Leslie'})
        run_statistic.store({'name': 'Leslie'})

        for item in run_statistic.all():
            print(item)


c=test()
c.myselect()

# db = UnQLite('/tmp/test3.db')

# db.update({'huey': 'kitty', 'mickey': 'puppy'})
# print([item for item in db])

# @db.commit_on_success
# ... def save_value(key, value, exc=False):
# ...     db[key] = value
# ...     if exc:
# ...         raise Exception('uh-oh')


# users = db.collection('users')

# users = db.collection('users')

# with db.transaction():
# db.begin()
#
# if not users.exists():
#     users.create()  # Create the collection.
# users.store({'name': 'Leslie'})
# users.store({'name': 'Leslie'})
# users.store({'name': 'Leslie'})
# users.store({'name': 'Leslie'})

# users.store([{'name': 'Leslie'}, {'name': 'Connor', 'type': 'baby'}])
# users.update(1, {'name': 'Leslie', 'favorite_color': 'green'})
# db.commit()

# print(users.all())
