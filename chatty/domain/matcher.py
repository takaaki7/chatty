import random


class Matcher(object):
    def __init__(self, randomnum=None):
        if randomnum is None:
            self.randomnum = random.random()
        else:
            self.randomnum = randomnum

    def should_match(self, user1, user2, cache, location_enabled):
        if user1.id == user2.id:
            return False
        if user1.last_matched == user2.id:
            return False

        def gendercond(a, b):
            fg = b.finding_genders.split(",")
            allgen = [None, "undefined", "male", "female"]
            if b.gender == "female":
                if len(fg) == 2:
                    if self.randomnum > 0.5:
                        fg = ["male"]
                    else:
                        fg = allgen
            elif b.gender == "male" or b.gender == "undefined":
                if len(fg) == 2:
                    if self.randomnum > 0.5:
                        fg = ["male"]
                    else:
                        fg = allgen
            return a.gender in fg

        if not and_for_both(user1, user2, gendercond):
            return False

        def locationcond(a, b):
            return (not a.location_enabled) or \
                   (not a.has_location()) or \
                   (b.has_location() and a.distance(b) < a.search_radius)

        if location_enabled and not and_for_both(user1, user2,
                                                 locationcond):
            return False

        if cache['my_langs'] & set(user2.languages):
            return True
        return False


def get():
    return Matcher()


def and_for_both(user1, user2, predicate):
    return predicate(user1, user2) and predicate(user2, user1)
