

import random


class UseError(Exception):
    pass


class Describable:

    def __init__(self, _name, _desc):
        self.name = _name
        self.desc = _desc

    def describe(self):
        return self.desc


class Container:

    def __init__(self, _contents=None):
        self.contents = {} if _contents is None else _contents

    def put(self, thing):
        self.contents[thing.name] = thing

    def get(self, thing_name):
        return self.contents.pop(thing_name)


class Location(Describable, Container):

    all = {}

    def __init__(self, _name, _desc, _scene=None, _contents=None, _connections=None):
        Describable.__init__(self, _name, _desc)
        Container.__init__(self, _contents)
        self.scene = {} if _scene is None else _scene
        self.connections = {} if _connections is None else _connections
        Location.all[_name] = self

    def describe(self):
        contents_desc = '\nYou can see:\n{}\n'.format('\n'.join(thing_name for thing_name in self.contents)) if len(self.contents) else ''
        return '\n{}\n{}'.format(self.desc, contents_desc)

    @staticmethod
    def directed_connect(loc1, direction1, loc2):
        loc1.connections[direction1] = loc2

    @staticmethod
    def connect(loc1, direction1, loc2, direction2):
        loc1.connections[direction1] = loc2
        loc2.connections[direction2] = loc1


class Attacker:

    def __init__(self, _damage):
        self.damage = _damage

    def attack(self, target):
        target.hurt(random.randint(0, self.damage))


class Thing(Describable):

    def __init__(self, _name, _desc):
        Describable.__init__(self, _name, _desc)

    def use(self, indirect_object):
        pass


class Weapon(Thing, Attacker):

    def __init__(selfself, _name, _desc, _damage):
        Thing.__init__(_name, _desc)
        Attacker.__init__(_damage)

    def use(self, target):
        try:
            self.attack(target)
        except AttributeError:
            raise UseError("target can't be hurt")


class Creature(Describable):

    def __init__(self, _name, _desc, _max_health, _alive=1, _health=-1):
        Describable.__init__(self, _name, _desc)
        self.alive = _alive
        self.max_health = _max_health
        self.health = _health if _health != -1 else _max_health

    def hurt(self, damage):
        self.health = self.health - damage if self.health > damage else 0
        if self.health == 0:
            self.alive = 0

    def heal(self, repair):
        self.health = self.health + repair if self.health < self.max_health else self.max_health


class Monster(Creature, Attacker):

    def __init__(self, _name, _desc, _max_health, _damage, _alive=1, _health=-1):
        Creature.__init__(self, _name, _desc, _alive, _health)
        Attacker.__init__(self, _damage)


class Character(Creature, Container):

    def __init__(self, _name, _desc, _location, _max_health, _contents=None, _alive=1, _health=-1):
        Creature.__init__(self, _name, _desc, _max_health, _alive, _health)
        Container.__init__(self, _contents)
        self.location = _location

    def go(self, direction):
        try:
            self.location = self.location.connections[direction]
        except KeyError:
            print("Ain't no such place as {}".format(direction))
        else:
            print("You went {} and are now in {}".format(direction, self.location.name))


class FindError(Exception):
    pass


def find(object_name):
    global player
    for place in [player.contents, player.location.contents, player.location.scene, {'me': player}]:
        if object_name in place:
            return place[object_name]
    raise FindError


def go(params):
    global player
    direction = params[0]
    player.go(direction)


def look(params):
    global player
    if len(params) == 0:
        print(player.location.describe())
    if len(params) == 1:
        object_name = params[0]
        try:
            obj = find(object_name)
        except FindError:
            print "Could not find a {} anywhere".format(object_name)
        else:
            print obj.describe()


def take(params):
    thing_name = params[0]
    global player
    try:
        player.put(player.location.get(thing_name))
    except KeyError:
        print 'There is no {} here'.format(thing_name)
    else:
        print 'Taking {}'.format(thing_name)


def put(params):
    thing_name = params[0]
    global player
    try:
        player.location.put(player.get(thing_name))
    except KeyError:
        print("You don't have a {}".format(thing_name))
    else:
        print('You put {} down'.format(thing_name))


def use(params):
    global player
    if len(params) == 1:
        direct_object_name = params[0]
        try:
            direct_object = player.contents[direct_object_name]
            direct_object.use()
        except KeyError:
            print "You don't have a %s" % direct_object_name
        except AttributeError:
            print "%s can't be used" % direct_object_name
        except UseError as ue:
            print "You can't use {}{} ".format(direct_object_name, (': ' if len(ue.args) else '') + ', '.join(ue.args))
    if len(params) == 2:
        direct_object_name, indirect_object_name = params[0:2]
        try:
            direct_object = player.contents[direct_object_name]
            indirect_object = find(indirect_object_name)
            direct_object.use(indirect_object)
        except KeyError:
            print "You don't have a %s" % direct_object_name
        except FindError:
            print "You couldn't find a %s anywhere" % indirect_object_name
        except AttributeError:
            print "%s can't be used" % direct_object_name
        except UseError as ue:
            ue_args = (': ' if len(ue.args) else '') + ', '.join(ue.args)
            print "You can't use {} on {}{} ".format(direct_object_name, indirect_object_name, ue_args)


def quit_game(params):
    global cont
    cont = 0


actions = {
    'go': go,
    'look': look,
    'take': take,
    'put': put,
    'use': use,
    'quit': quit_game
}

amulet = Thing('amulet', 'Amulet of Yendor')
start = Location('start', 'This is where it all begins.\nIn the forward direction you can see some other place.', {},  {amulet.name: amulet})
end   = Location('end',   'This is the end, my only friend')
Location.connect(start, 'forward', end, 'back')

player = Character('Dude', 'Just some guy', start, 10)

prompt = '> '
cont = 1
won = 0
dead = 0

while cont:
    tokens = raw_input(prompt).split()
    action_name, params = tokens[0], tokens[1:]
    if action_name in actions:
        actions[action_name](params)
    else:
        print("That doesn't seem to be an option")
    if amulet.name in end.contents:
        won = 1
    if not player.alive:
        dead = 1
    if dead or won:
        cont = 0

if dead:
    print "You been killed a lot :("
elif won:
    print "You win! Yay!"



