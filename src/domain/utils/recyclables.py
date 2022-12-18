
#Put in start, below groups declaration
create_box = """_box = Rectangle(vec(50,120), (200,100), gravity_enabled = True, collision_enabled = True)
self.collision_group.add(_box)
self.test_objects.append(_box)"""