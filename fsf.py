from java.awt import *
from java.awt.event import *
from java.awt.geom import *
from javax.swing import JFrame
from math import sqrt, cos, sin, pi
from random import randint
from model import Model
from game_rules import GameRulesAlpha
from sxsw_twitter import Twitter, TwitterGameVotes
from sys import argv
from java.util import TimerTask, Timer

gWon = False

def make_arc_shape (x, y, inner_radius, outer_radius, start_angle, extent):
    path = GeneralPath()
    b2 = Rectangle2D.Double(x + outer_radius - inner_radius, y + outer_radius - inner_radius, inner_radius * 2, inner_radius * 2)
    arc2 = Arc2D.Double(b2, start_angle, extent, Arc2D.OPEN)
    path.append(arc2, False)

    b1 = Rectangle2D.Double(x, y, outer_radius * 2, outer_radius * 2)
    arc1 = Arc2D.Double(b1, start_angle + extent, -extent, Arc2D.OPEN)
    path.append(arc1, True)

    path.closePath()
    return path

class BlueArc (Component):
    def __init__(self, start_angle, pixels_per_unit = 1.0):
        Component.__init__(self)
        self.path = make_arc_shape(0, 0, 20 * pixels_per_unit, 40 * pixels_per_unit, start_angle, 40)
        self.pixels_per_unit = pixels_per_unit
    def set_center(self, x, y):
        self.setLocation(int(x - 40 * self.pixels_per_unit), int(y - 40 * self.pixels_per_unit))
    def paint(self, gc):
        print "bluearc paint"

        gc.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
        
        gc.setColor(Color(0, 0, 255, 120))
        gc.fill(self.path)

class WinView (Component):
    def __init__(self, center):
        Component.__init__(self)
        self.game_rules = None
        self.text = ""
        self.center = center
    def clear(self):
        self.text = ""
        self.setVisible(False)
    def update(self, model):
        global gWon
        if self.game_rules.did_win() and gWon == False:
            gWon = True
            print "win"
            self.text = "WE HAVE A WINNER"

        metrics = self.getGraphics().getFontMetrics(Font("Lucinda Grande", Font.BOLD, 40))
        width = metrics.stringWidth(self.text)
        
        self.setLocation(Point(int(self.center - 35 - width / 2), int(self.getLocation().getY())))
        self.setVisible(False)
        self.setVisible(True)
    def paint(self, gc):
        print "paint winview"
        if self.text == "":
            print "invisible"
        else:
            print "visible"
            # gc.setColor(Color.yellow)
            # gc.fillRect(0, 0, int(self.getBounds().getWidth()), int(self.getBounds().getHeight()))
            gc.setColor(Color.black)
            gc.setFont(Font("Lucinda Grande", Font.BOLD, 40))
            gc.drawString(self.text, 40, 80)

class Instructions (Component):
    def __init__(self, text):
        Component.__init__(self)
        self.game_rules = None
        self.text = text[:]
    def paint(self, gc):
        pos = 20
        for t in (self.text):
            if (type(t) == tuple):
                line = t[0]
                gc.setColor(t[1])
                gc.setFont(Font("Lucinda Grande", 0, t[2]))
                pos += int(t[2] * 1.5)
            else:
                gc.setColor(Color.black)
                gc.setFont(Font("Lucinda Grande", 0, 10))
                line = t
                pos += 15
            gc.drawString(line, 0, pos)

class VoteCounter (Component):
    def __init__(self, label, color, font, key):
        Component.__init__(self)
        self.label = label
        self.color = color
        self.font = font
        self.key = key
        self.text = ""
    def update(self, model):
        if (model.a + model.b + model.c > 0):
            self.text = "%s: %d (%d%%)"%(self.label, self.key(model), 100 * self.key(model) / (model.a + model.b + model.c))
        else:
            self.text = "%s: NO VOTES YET"%(self.label)
        self.repaint()
    def paint(self, gc):
        print "paint votecounter"
        gc.setColor(self.color)
        gc.setFont(self.font)
        gc.drawString(self.text, 0, self.getSize().getHeight())

class Label (Component):
    def __init__(self, label, color, font):
        Component.__init__(self)
        self.label = label
        self.color = color
        self.font = font
    def paint(self, gc):
        gc.setColor(self.color)
        gc.setFont(self.font)
        gc.drawString(self.label, 0, self.getSize().getHeight())

def make_axes_shape(scale):
    path = GeneralPath()

    pmid = Point2D.Double(-scale * 100 * cos(pi * 7 / 6), 100 * scale)
    pa = Point2D.Double(pmid.getX(), pmid.getY() - scale * 100)
    pb = Point2D.Double(pmid.getX() + scale * 100 * cos(pi * 7 / 6), pmid.getY() - (scale * 100 * sin(pi * 7 / 6)))
    pc = Point2D.Double(pmid.getX() + scale * 100 * cos(pi * 11 / 6), pmid.getY() - (scale * 100 * sin(pi * 11 / 6)))

    path.append(Line2D.Double(pmid, pa), False)
    path.append(Line2D.Double(pa, pmid), True)

    path.append(Line2D.Double(pmid, pb), True)
    path.append(Line2D.Double(pb, pmid), True)

    path.append(Line2D.Double(pmid, pc), True)
    path.append(Line2D.Double(pc, pmid), True)

    path.closePath()
    return path

class Axes (Component):
    def __init__(self, pixels_per_unit = 1.0):
        Component.__init__(self)
        self.path = make_axes_shape(pixels_per_unit)
        self.pixels_per_unit = pixels_per_unit
    def get_rel_mid_location(self):
        return (-self.pixels_per_unit * 100 * cos(pi * 7 / 6), 100 * self.pixels_per_unit)
    def get_mid_location(self):
        pmid = Point2D.Double(-self.pixels_per_unit * 100 * cos(pi * 7 / 6), 100 * self.pixels_per_unit)
        return (self.getLocation().getX() + pmid.getX(), self.getLocation().getY() + pmid.getY())
    def get_a_location(self, value):
        pmid = Point2D.Double(-self.pixels_per_unit * 100 * cos(pi * 7 / 6), 100 * self.pixels_per_unit)
        return (self.getLocation().getX() + pmid.getX(), self.getLocation().getY() + pmid.getY() - value * self.pixels_per_unit)
    def get_b_location(self, value):
        pmid = Point2D.Double(-self.pixels_per_unit * 100 * cos(pi * 7 / 6), 100 * self.pixels_per_unit)
        x = self.getLocation().getX() + pmid.getX() + self.pixels_per_unit * value * cos(pi * 7 / 6)
        y = self.getLocation().getY() + pmid.getY() - self.pixels_per_unit * value * sin(pi * 7 / 6)
        return (x, y)
    def get_c_location(self, value):
        pmid = Point2D.Double(-self.pixels_per_unit * 100 * cos(pi * 7 / 6), 100 * self.pixels_per_unit)
        x = self.getLocation().getX() + pmid.getX() + self.pixels_per_unit * value * cos(pi * 11 / 6)
        y = self.getLocation().getY() + pmid.getY() - self.pixels_per_unit * value * sin(pi * 11 / 6)
        return (x, y)
    def get_sum_location(self, value_a, value_b, value_c):
        pmid = Point2D.Double(-self.pixels_per_unit * 100 * cos(pi * 7 / 6), 100 * self.pixels_per_unit)
        x = self.getLocation().getX() + pmid.getX() + self.pixels_per_unit * value_b * cos(pi * 7 / 6) + self.pixels_per_unit * value_c * cos(pi * 11 / 6)
        y = self.getLocation().getY() + pmid.getY() - (value_a * self.pixels_per_unit + self.pixels_per_unit * value_b * sin(pi * 7 / 6) + self.pixels_per_unit * value_c * sin(pi * 11 / 6))
        return (x, y)
    def paint(self, gc):
        print "axes paint"

        gc.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)

        gc.setColor(Color.black)
        gc.draw(self.path)
       
class Circle (Component):
    def __init__(self, color, radius, title ="", title_distance = 0, title_angle = 0):
        Component.__init__(self)
        self.radius = radius
        self.color = color
        self.title = title
        # angle in radians
        self.title_angle = title_angle
        self.title_distance = title_distance
    def set_center(self, x, y):
        self.setLocation(int(x - self.radius), int(y - self.radius))
    def paint(self, gc):
        gc.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
        gc.setColor(self.color)
        gc.fillArc(0, 0, self.radius * 2, self.radius * 2, 0, 360)
        gc.setColor(Color.black)
        gc.setFont(Font("Lucinda Grande", 0, 20))
        gc.drawString(self.title, 25 + self.title_distance * cos(self.title_angle), 25 - self.title_distance * sin(self.title_angle))

        f = gc.getFont()
        print "font.style = ", f.getStyle()
        print "font.name = ", f.getName()

class PacMan (Component):
   def __init__(self):
       Component.__init__(self)
       self.pos = 0;
   def paint(self, gc):
       print "pacman paint"
       gc.setColor(Color.black)
       gc.fillArc(0, 0, 50, 50, 0, 270)

class TwitterTask (TimerTask):
    def __init__(self, fsf):
        TimerTask.__init__(self)
        self.fsf = fsf
    def run(self):
        print "beginning scheduled update"
        # only update if we haven't won yet
        if gWon == False:
            self.fsf.update_model_from_twitter()
        print "ending scheduled update"

class FullScreenFrame (JFrame, KeyListener):
   def __init__(self, screen = None):
       self.setBackground(Color.white)
       # self.setBackground(Color(0, 0, 0, 0))

       self.addKeyListener(self)
       self.setUndecorated(True)
       gd = None
       if screen:
           try:
               gd = GraphicsEnvironment.getLocalGraphicsEnvironment().getScreenDevices()[screen]
           except:
               gd = GraphicsEnvironment.getLocalGraphicsEnvironment().getDefaultScreenDevice()
       else:
           gd = GraphicsEnvironment.getLocalGraphicsEnvironment().getDefaultScreenDevice()
       if (gd.isFullScreenSupported()):
           gd.setFullScreenWindow(self)
       else:
           self.setSize(400, 400)

       self.twitter = Twitter()

   def set_game_rules(self, rules):
       self.winview.game_rules = rules

   def setup(self):
       self.setVisible(True)
       
       self.pacman = PacMan()
       self.pacman.setSize(50,50)
       self.pacman.setLocation(0, 0)
       self.pacman.setVisible(False)
       self.add(self.pacman)

       self.axes = Axes(2.0)
       self.add(self.axes)
       self.axes.setSize(500, 500)
       self.axes.setLocation(int(self.getSize().getWidth() / 2 - self.axes.get_rel_mid_location()[0]), int(self.getSize().getHeight() / 2 - self.axes.get_rel_mid_location()[0]))
       self.axes.setVisible(True)

       label_color = Color.black
       label_font = Font("Lucinda Grande", 0, 20)

       self.a_label = Label("A", label_color, label_font)
       self.add(self.a_label)
       self.a_label.setLocation(int(self.axes.get_a_location(115)[0] - 7), int(self.axes.get_a_location(115)[1]))
       self.a_label.setSize(20, 20)
       self.a_label.setVisible(True)

       self.b_label = Label("B", label_color, label_font)
       self.add(self.b_label)
       self.b_label.setLocation(*[int(i) for i in self.axes.get_b_location(105)])
       self.b_label.setSize(20, 20)
       self.b_label.setVisible(True)

       self.c_label = Label("C", label_color, label_font)
       self.add(self.c_label)
       self.c_label.setLocation(int(self.axes.get_c_location(105)[0] - 7), int(self.axes.get_c_location(105)[1]))
       self.c_label.setSize(20, 20)
       self.c_label.setVisible(True)

       self.redcircle = Circle(Color(255, 0, 0, 127), 10)
       self.redcircle.setSize(50,50)
       self.add(self.redcircle)
       self.redcircle.set_center(*self.axes.get_a_location(20))
       self.redcircle.setVisible(True)

       self.greencircle = Circle(Color(0, 255, 0, 127), 10)
       self.greencircle.setSize(50,50)
       self.add(self.greencircle)
       self.greencircle.set_center(*self.axes.get_b_location(20))
       self.greencircle.setVisible(True)

       self.bluecircle = Circle(Color(0, 0, 255, 127), 10)
       self.bluecircle.setSize(50,50)
       self.add(self.bluecircle)
       self.bluecircle.set_center(*self.axes.get_c_location(20))
       self.bluecircle.setVisible(True)

       self.greycircle = Circle(Color(0, 0, 0, 127), 5)
       self.greycircle.setSize(10,10)
       self.add(self.greycircle)
       self.greycircle.set_center(*self.axes.get_sum_location(5, 5, 5))
       self.greycircle.setVisible(True)
       
       axesmid = self.axes.get_mid_location()

       self.safezone1 = BlueArc(10, 2.0)
       self.add(self.safezone1)
       self.safezone1.setBounds(0, 0, 500, 500)
       self.safezone1.set_center(*axesmid)
       self.safezone1.setVisible(True)

       self.safezone2 = BlueArc(130, 2.0)
       self.add(self.safezone2)
       self.safezone2.setBounds(0, 0, 500, 500)
       self.safezone2.set_center(*axesmid)
       self.safezone2.setVisible(True)

       self.safezone3 = BlueArc(250, 2.0)
       self.add(self.safezone3)
       self.safezone3.setBounds(0, 0, 500, 500)
       self.safezone3.set_center(*axesmid)
       self.safezone3.setVisible(True)

       votecounter_font = Font("Lucinda Grande", 0, 20)

       self.votecounter_a = VoteCounter("A", Color.red, votecounter_font, lambda m:m.a)
       self.add(self.votecounter_a)
       self.votecounter_a.setBounds(0, 0, 250, 40)
       self.votecounter_a.setVisible(True)

       self.votecounter_b = VoteCounter("B", Color.green, votecounter_font, lambda m:m.b)
       self.add(self.votecounter_b)
       self.votecounter_b.setBounds(0, 40, 250, 40)
       self.votecounter_b.setVisible(True)

       self.votecounter_c = VoteCounter("C", Color.blue, votecounter_font, lambda m:m.c)
       self.add(self.votecounter_c)
       self.votecounter_c.setBounds(0, 80, 250, 40)
       self.votecounter_c.setVisible(True)

       self.winview = WinView(int(self.getWidth() / 2))
       self.add(self.winview)
       self.winview.setBounds(0, 0, 800, 200)
       self.winview.setVisible(False)

       self.instructions = Instructions([("To vote, send a tweet like this:", Color.black, 10), 
                                         ("  #incol A 1", Color.red, 20),
                                         ("  #incol B 1", Color.red, 20),
                                         ("  #incol C 1", Color.red, 20)])
       self.add(self.instructions)
       self.instructions.setBounds(int(self.getSize().getWidth() / 2 + 250), 200, 800, 800)
       self.instructions.setVisible(True)

   def update(self, model):
       total = model.a + model.b + model.c
       pct_a = 0
       pct_b = 0
       pct_c = 0
       if not total == 0:
           pct_a = 100 * model.a / total
           pct_b = 100 * model.b / total
           pct_c = 100 * model.c / total

       self.redcircle.set_center(*self.axes.get_a_location(pct_a))
       self.greencircle.set_center(*self.axes.get_b_location(pct_b))
       self.bluecircle.set_center(*self.axes.get_c_location(pct_c))

       self.greycircle.set_center(*[int(i) for i in self.axes.get_sum_location(pct_a, pct_b, pct_c)])

   def paint(self, gc):
       print "fsf paint"
   def keyTyped(self, e):
       pass
   def keyPressed(self, e):
       pass
   def keyReleased(self, e):
       if (e.getKeyChar() == "q"):
           self.setVisible(False)
           self.dispose()
       elif (e.getKeyChar() == "n"):
           self.pacman.pos += 1
           self.pacman.setLocation(self.pacman.pos, self.pacman.pos)
           self.bluearc.setBounds(100, 100, 50, 50)
       elif (e.getKeyChar() == "r"):
           if self.model:
               self.update(self.model.random())

       elif (e.getKeyChar() == "a"):
           if self.model:
               self.model.set_a(self.model.a - 1)

       elif (e.getKeyChar() == "b"):
           if self.model:
               self.model.set_b(self.model.b - 1)

       elif (e.getKeyChar() == "c"):
           if self.model:
               self.model.set_c(self.model.c - 1)

       elif (e.getKeyChar() == "A"):
           if self.model:
               self.model.set_a(self.model.a + 1)

       elif (e.getKeyChar() == "B"):
           if self.model:
               self.model.set_b(self.model.b + 1)

       elif (e.getKeyChar() == "C"):
           if self.model:
               self.model.set_c(self.model.c + 1)

       elif (e.getKeyChar() == "x"):
           if self.model:
               self.model.set(0, 0, 0)
               self.winview.clear()

       elif (e.getKeyChar() in ["1", "2", "3", "4", "5", "6", "7", "8"]):
           self.update_model_from_twitter(int(e.getKeyChar()))

       elif (e.getKeyChar() == "i"):
           f = open("votes.txt")
           t = f.read()
           f.close()
           v = eval(t)
           self.model.set(v['A'], v['B'], v['C'])

   def update_model_from_twitter(self, game_number = 1):
       tgv = TwitterGameVotes(self.twitter, game_number)
       v = tgv.retrieve()

       try:
           f = open("votes.txt")
           try:
               t = f.read()
               try:
                   v2 = eval(t)
                   v['A'] += v2['A']
                   v['B'] += v2['B']
                   v['C'] += v2['C']
               except:
                   pass
           finally:
               f.close()
       except:
           pass

       print "votes:", v
       self.model.set(v['A'], v['B'], v['C'])


if __name__ == "__main__":
    model = Model()
    if (len(argv) == 2):
        fsf = FullScreenFrame(int(argv[1]))
    else:
        fsf = FullScreenFrame()
    fsf.setup()
    model.add_observer(fsf)
    model.add_observer(fsf.votecounter_a)
    model.add_observer(fsf.votecounter_b)
    model.add_observer(fsf.votecounter_c)
    fsf.model = model
    fsf.set_game_rules(GameRulesAlpha(model))
    twitter_task = TwitterTask(fsf)
    twitter_timer = Timer()
    twitter_timer.scheduleAtFixedRate(twitter_task, 5000, 5000)
    model.add_observer(fsf.winview)
