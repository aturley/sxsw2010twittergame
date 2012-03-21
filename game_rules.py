import math

def vec_to_angle(x, y):
    if (x == 0):
        if (y > 0):
            return math.pi / 2
        else:
            return math.pi * 3 / 2
    if (y == 0):
        if (x > 0):
            return 0
        else:
            return math.pi

    angle = math.atan(y / x)

    if (x > 0 and y < 0):
        return math.pi * 2 + angle
    if (x < 0 and y < 0):
        return math.pi + angle
    if (x < 0 and y > 0):
        return math.pi + angle

    return angle

class ValueRange (object):
    def __init__(self, low, high):
        object.__init__(self)
        self.low = low
        self.high = high
    def in_range(self, val):
        return (val < self.high) and (val > self.low)

class GameRulesAlpha (object):
   def __init__(self, model):
       self.model = model
       self.min_ball_dist = 0.22
       self.max_ball_dist = 0.38
       self.angle_ranges = [ValueRange(math.pi * 7.4 / 18, math.pi * 10.6 / 18), 
                            ValueRange(math.pi * 19.4 / 18, math.pi * 22.6 / 18), 
                            ValueRange(math.pi * 31.4 / 18, math.pi * 34.6 / 18)]

   def radius_ok(self, radius):
       print "radius_ok:", (radius >= self.min_ball_dist) and (radius <= self.max_ball_dist)
       return (radius >= self.min_ball_dist) and (radius <= self.max_ball_dist)
   def angle_ok(self, angle):
       print "angle:%f, %f"%(angle, angle / (math.pi * 2) * 360)
       print "angle_ok:", any([r.in_range(angle) for r in self.angle_ranges])
       return any([r.in_range(angle) for r in self.angle_ranges])

   def did_win(self):
       total = self.model.a + self.model.b + self.model.c
       if (total > 0):
           fa = float(self.model.a) / total
           fb = float(self.model.b) / total
           fc = float(self.model.c) / total

           ball_pos_x = fc * math.cos(math.pi / 6) + fb * math.cos(math.pi * 5 / 6)
           ball_pos_y = -fa + fc * math.sin(math.pi / 6) + fb * math.sin(math.pi * 5 / 6)
           ball_dist = math.sqrt(ball_pos_x ** 2 + ball_pos_y ** 2)
           ball_angle = vec_to_angle(ball_pos_x, ball_pos_y)

           print "fa", fa
           print "fb", fb
           print "fc", fc
           print "ball_pos_x:", ball_pos_x
           print "ball_pos_y:", ball_pos_y
           print "ball_dist:", ball_dist
           print "ball_angle:", ball_angle

           return self.radius_ok(ball_dist) and self.angle_ok(ball_angle)
       return False
           
